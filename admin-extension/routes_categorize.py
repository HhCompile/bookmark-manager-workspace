#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分类 API 路由

- POST /v1/bookmark/categorize         # 单条
- POST /v1/bookmarks/categorize-batch  # 批量
- GET  /v1/categorization/config        # 查看配置
- POST /v1/categorization/config        # 更新配置（max_depth / 策略启停）
"""

from flask import Blueprint, request, jsonify
import logging

from app.config import config
from app.services.categorizer import get_categorizer

logger = logging.getLogger('api.categorize')
cat_bp = Blueprint('categorize', __name__)


@cat_bp.route(f'/{config.API_VERSION}/bookmark/categorize', methods=['POST'])
def categorize_one():
    """对单个书签分类"""
    data = request.get_json(silent=True) or {}
    url = data.get('url', '').strip()
    title = data.get('title', '').strip()
    if not url or not title:
        return jsonify({"status": "error", "error": "url 和 title 必填"}), 400

    bookmark = {
        "url": url,
        "title": title,
        "description": data.get('description', ''),
        "folder_path": data.get('folder_path', ''),
    }

    categorizer = get_categorizer()
    category = categorizer.categorize(bookmark)
    matched = None
    for s in categorizer.strategies:
        try:
            r = s.match(bookmark)
            if r and categorizer._validate_depth(r):
                matched = s.name
                break
        except Exception:
            continue

    return jsonify({
        "status": "success",
        "category": category,
        "strategy": matched or "fallback",
        "max_depth": categorizer.max_depth,
    })


@cat_bp.route(f'/{config.API_VERSION}/bookmarks/categorize-batch', methods=['POST'])
def categorize_batch():
    """批量分类（最多 500 条/次）"""
    data = request.get_json(silent=True) or {}
    bookmarks = data.get('bookmarks', [])
    dry_run = data.get('dry_run', True)

    if not isinstance(bookmarks, list) or not bookmarks:
        return jsonify({"status": "error", "error": "bookmarks 必须是非空数组"}), 400
    if len(bookmarks) > 500:
        return jsonify({"status": "error", "error": "单次最多 500 条"}), 400

    categorizer = get_categorizer()
    results = categorizer.categorize_batch(bookmarks)

    # 统计
    strategy_count = {}
    for r in results:
        s = r['strategy']
        strategy_count[s] = strategy_count.get(s, 0) + 1

    # dry_run=False 时写回
    if not dry_run:
        # 这里需要 load + update + save 逻辑
        from app.api.routes_sync import load_bookmarks, save_bookmarks
        all_bms = load_bookmarks()
        bm_by_id = {b.get('id'): b for b in all_bms if b.get('id')}

        for r in results:
            bm_id = r['bookmark'].get('id')
            if bm_id in bm_by_id:
                bm_by_id[bm_id]['category'] = r['category']
                bm_by_id[bm_id]['category_strategy'] = r['strategy']

        save_bookmarks(all_bms)

    return jsonify({
        "status": "success",
        "dry_run": dry_run,
        "stats": {
            "total": len(results),
            "by_strategy": strategy_count,
        },
        "results": results[:50],  # 只返回前 50 条详情
    })


@cat_bp.route(f'/{config.API_VERSION}/categorization/config', methods=['GET'])
def get_config():
    """查看当前分类配置"""
    return jsonify({
        "status": "success",
        "config": get_categorizer().get_config(),
    })


@cat_bp.route(f'/{config.API_VERSION}/categorization/config', methods=['POST'])
def update_config():
    """动态更新分类配置（无需重启）"""
    data = request.get_json(silent=True) or {}
    categorizer = get_categorizer()

    if 'max_depth' in data:
        try:
            categorizer.update_max_depth(int(data['max_depth']))
        except ValueError as e:
            return jsonify({"status": "error", "error": str(e)}), 400

    if 'strategies' in data:
        for name, conf in data['strategies'].items():
            if name in categorizer.config['strategies']:
                if 'enabled' in conf:
                    categorizer.config['strategies'][name]['enabled'] = bool(conf['enabled'])
                if 'priority' in conf:
                    categorizer.config['strategies'][name]['priority'] = int(conf['priority'])
        categorizer._build_strategy_chain()  # 重建策略链

    return jsonify({
        "status": "success",
        "config": categorizer.get_config(),
        "message": "配置已更新",
    })
