#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome 扩展同步入口

接收 Chrome 扩展推送的书签，写入 bookmarks.json。
- 阶段 1：基础接收 + URL 标准化 + 精确去重
- 阶段 2+：交给数据清洗 pipeline 处理

API：
- POST /v1/bookmark/sync-from-extension    # 单条
- POST /v1/bookmarks/sync-batch            # 批量
- GET  /v1/bookmark/sync-status            # 同步状态
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from flask import Blueprint, request, jsonify

from app.config import config

logger = logging.getLogger('api.sync')
sync_bp = Blueprint('sync', __name__)


# ============================================================================
# 工具函数
# ============================================================================

def canonicalize_url(url: str) -> str:
    """URL 标准化：去 utm、统一 https、strip 末尾 /

    Examples:
        >>> canonicalize_url("http://github.com/foo/?utm_source=x")
        'https://github.com/foo'
        >>> canonicalize_url("https://github.com/foo/")
        'https://github.com/foo'
    """
    if not url:
        return url

    p = urlparse(url.strip())
    if not p.scheme:
        return url

    # 强制 https（http 也升级）
    scheme = 'https' if p.scheme in ('http', 'https') else p.scheme

    # 过滤 utm_* / fbclid / gclid 等跟踪参数
    params = parse_qs(p.query)
    TRACKING_PARAMS = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                       'fbclid', 'gclid', 'mc_cid', 'mc_eid', '_ga'}
    clean_params = {k: v for k, v in params.items() if k not in TRACKING_PARAMS}

    return urlunparse((
        scheme,
        p.netloc.lower(),
        p.path.rstrip('/'),
        p.params,
        urlencode(clean_params, doseq=True),
        ''  # 去掉 fragment
    ))


def url_hash(url: str) -> str:
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def now_iso() -> str:
    return datetime.utcnow().isoformat() + 'Z'


def generate_id() -> str:
    return hashlib.sha1(os.urandom(16)).hexdigest()[:16]


def load_bookmarks() -> List[Dict]:
    """读取 bookmarks.json"""
    data_file = Path(config.DATA_FILE)
    if not data_file.exists():
        return []
    try:
        with data_file.open('r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else data.get('bookmarks', [])
    except Exception as e:
        logger.error(f"读取 bookmarks.json 失败: {e}")
        return []


def save_bookmarks(bookmarks: List[Dict]) -> None:
    """写回 bookmarks.json（带 .bak 备份）"""
    data_file = Path(config.DATA_FILE)
    if data_file.exists():
        backup = data_file.with_suffix(f'.json.{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
        data_file.rename(backup)

    with data_file.open('w', encoding='utf-8') as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)


# ============================================================================
# API 端点
# ============================================================================

@sync_bp.route(f'/{config.API_VERSION}/bookmark/sync-from-extension', methods=['POST'])
def sync_from_extension():
    """Chrome 扩展推送单条书签

    Body:
        {
            "url": "https://github.com/xxx",
            "title": "GitHub - xxx",
            "description": "...",        # 可选
            "tags": ["dev"],             # 可选
            "category": "技术",          # 可选
            "folder_path": "技术/前端"   # 可选
        }

    Returns:
        {status: success|skipped|error, ...}
    """
    data = request.get_json(silent=True) or {}

    url = (data.get('url') or '').strip()
    title = (data.get('title') or '').strip()

    if not url or not title:
        return jsonify({
            "status": "error",
            "error": "url 和 title 必填"
        }), 400

    # 标准化
    canonical = canonicalize_url(url)
    h = url_hash(canonical)

    # 读取
    bookmarks = load_bookmarks()

    # L1 精确去重
    if any(b.get('url_hash') == h for b in bookmarks):
        return jsonify({
            "status": "skipped",
            "reason": "duplicate",
            "canonical_url": canonical,
            "message": f"已存在（hash={h[:8]}）"
        }), 200

    # 构造新书签
    new_bm = {
        "id": generate_id(),
        "url": url,
        "canonical_url": canonical,
        "url_hash": h,
        "title": title,
        "description": data.get('description', ''),
        "tags": data.get('tags', []),
        "category": data.get('category', '未分类'),
        "folder_path": data.get('folder_path', ''),
        "source": "chrome-extension",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "metadata": {},          # 待 routes_metadata 填充
        "is_dead_link": None,    # 待 l2_detect_dead_links 检测
    }

    bookmarks.append(new_bm)
    save_bookmarks(bookmarks)

    logger.info(f"Synced bookmark: {title} ({h[:8]})")

    return jsonify({
        "status": "success",
        "bookmark": new_bm,
        "message": "已同步，建议运行数据清洗（POST /v1/bookmarks/clean）"
    }), 201


@sync_bp.route(f'/{config.API_VERSION}/bookmarks/sync-batch', methods=['POST'])
def sync_batch_from_extension():
    """Chrome 扩展批量推送（一次推多条）

    Body:
        {
            "bookmarks": [
                {"url": "...", "title": "...", "tags": [...], "category": "..."},
                ...
            ]
        }

    Returns:
        {status, stats: {total, added, skipped, errors}}
    """
    data = request.get_json(silent=True) or {}
    items = data.get('bookmarks', [])

    if not isinstance(items, list) or not items:
        return jsonify({
            "status": "error",
            "error": "bookmarks 必须是非空数组"
        }), 400

    bookmarks = load_bookmarks()
    existing_hashes = {b.get('url_hash') for b in bookmarks if b.get('url_hash')}

    added, skipped, errors = [], [], []

    for item in items:
        try:
            url = (item.get('url') or '').strip()
            title = (item.get('title') or '').strip()
            if not url or not title:
                errors.append({"item": item, "error": "url/title 缺失"})
                continue

            canonical = canonicalize_url(url)
            h = url_hash(canonical)

            if h in existing_hashes:
                skipped.append({"title": title, "reason": "duplicate"})
                continue

            new_bm = {
                "id": generate_id(),
                "url": url,
                "canonical_url": canonical,
                "url_hash": h,
                "title": title,
                "description": item.get('description', ''),
                "tags": item.get('tags', []),
                "category": item.get('category', '未分类'),
                "folder_path": item.get('folder_path', ''),
                "source": "chrome-extension",
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "metadata": {},
                "is_dead_link": None,
            }
            bookmarks.append(new_bm)
            existing_hashes.add(h)
            added.append(new_bm)
        except Exception as e:
            errors.append({"item": item, "error": str(e)})

    save_bookmarks(bookmarks)

    return jsonify({
        "status": "success",
        "stats": {
            "total": len(items),
            "added": len(added),
            "skipped": len(skipped),
            "errors": len(errors),
        },
        "added_ids": [b['id'] for b in added],
        "skipped": skipped[:20],  # 只返回前 20 个
        "errors": errors[:20],
    }), 200


@sync_bp.route(f'/{config.API_VERSION}/bookmark/sync-status', methods=['GET'])
def sync_status():
    """同步状态查询"""
    bookmarks = load_bookmarks()
    from_extension = [b for b in bookmarks if b.get('source') == 'chrome-extension']

    return jsonify({
        "status": "success",
        "total_bookmarks": len(bookmarks),
        "from_extension": len(from_extension),
        "other_sources": len(bookmarks) - len(from_extension),
        "last_sync": max(
            (b.get('created_at') for b in from_extension),
            default=None
        )
    })
