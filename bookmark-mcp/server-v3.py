#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bookmark Manager MCP Server v3

v3 新增：
- categorize_bookmark: 单条分类
- batch_categorize: 批量分类
- get_categorization_config: 查看分类配置
- update_categorization_config: 动态更新配置（max_depth / 策略启停）

v2 工具保留：sync_status, detect_dead_links
v1 工具保留：10 个核心工具
"""

import os
import logging
from typing import Optional, List, Dict, Any

import httpx
from mcp.server.fastmcp import FastMCP

BOOKMARK_API_BASE = os.environ.get(
    "BOOKMARK_API_BASE",
    "http://localhost:9001/v1"
)
REQUEST_TIMEOUT = float(os.environ.get("BOOKMARK_TIMEOUT", "30"))

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bookmark-mcp")

mcp = FastMCP(
    "Bookmark Manager",
    instructions="Bookmark MCP v3 (含 sync + 分类引擎)",
)

client = httpx.AsyncClient(
    base_url=BOOKMARK_API_BASE,
    timeout=REQUEST_TIMEOUT,
    headers={"Content-Type": "application/json"},
)


async def _call_api(method, path, *, params=None, json_body=None):
    try:
        resp = await client.request(method, path, params=params, json=json_body)
        resp.raise_for_status()
        return {"status": "success", "data": resp.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "error": f"API {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# v1 + v2 工具（保留）
# ============================================================================


@mcp.tool()
async def list_bookmarks(limit: int = 50, offset: int = 0):
    """列出书签"""
    return await _call_api("GET", "/bookmarks", params={"limit": min(limit, 500), "offset": max(offset, 0)})


@mcp.tool()
async def search_bookmarks(keyword: str, limit: int = 30):
    """关键字搜索"""
    if not keyword.strip():
        return {"status": "error", "error": "keyword 不能为空"}
    return await _call_api("GET", "/bookmarks", params={"q": keyword, "limit": min(limit, 200)})


@mcp.tool()
async def get_bookmarks_by_tag(tag: str, limit: int = 50):
    """按 tag 查（推荐）"""
    return await _call_api("GET", f"/bookmarks/tag/{tag}", params={"limit": min(limit, 200)})


@mcp.tool()
async def get_bookmarks_by_category(category: str, limit: int = 50):
    """按分类查（支持多层级路径如 "技术/前端"）"""
    return await _call_api("GET", f"/bookmarks/category/{category}", params={"limit": min(limit, 200)})


@mcp.tool()
async def add_bookmark(url: str, title: str, description: str = "", tags: Optional[List[str]] = None, category: str = ""):
    """新增书签"""
    if not url.strip() or not title.strip():
        return {"status": "error", "error": "url 和 title 必填"}
    return await _call_api("POST", "/bookmark", json_body={
        "url": url, "title": title, "description": description,
        "tags": tags or [], "category": category,
    })


@mcp.tool()
async def update_bookmark(bookmark_id: str, title=None, description=None, tags=None, category=None):
    """更新书签（只改传入字段）"""
    updates = {k: v for k, v in {"title": title, "description": description, "tags": tags, "category": category}.items() if v is not None}
    if not updates:
        return {"status": "error", "error": "至少要传一个字段"}
    updates["id"] = bookmark_id
    return await _call_api("POST", "/bookmark/update", json_body=updates)


@mcp.tool()
async def delete_bookmark(bookmark_id: str):
    """删除书签（**不可逆**）"""
    return await _call_api("POST", "/bookmark/delete", json_body={"id": bookmark_id})


@mcp.tool()
async def batch_organize(bookmark_ids: List[str], action: str, params: Optional[Dict] = None):
    """批量操作"""
    return await _call_api("POST", "/bookmarks/batch", json_body={"ids": bookmark_ids, "action": action, "params": params or {}})


@mcp.tool()
async def ai_suggest(bookmark_id: Optional[str] = None, scope: str = "all"):
    """AI 建议（不修改数据）"""
    return await _call_api("POST", "/ai/suggest", json_body={"bookmark_id": bookmark_id, "scope": scope})


@mcp.tool()
async def import_from_file(file_path: str, format: str = "html"):
    """从文件导入"""
    from pathlib import Path
    if not Path(file_path).exists():
        return {"status": "error", "error": f"文件不存在: {file_path}"}
    return await _call_api("POST", "/bookmark/upload", json_body={"content": Path(file_path).read_text(encoding="utf-8"), "format": format})


@mcp.tool()
async def sync_status():
    """查询 Chrome 扩展同步状态"""
    return await _call_api("GET", "/bookmark/sync-status")


# ============================================================================
# v3 新增工具 - 分类引擎
# ============================================================================


@mcp.tool()
async def categorize_bookmark(
    url: str,
    title: str,
    description: str = "",
    folder_path: str = "",
    max_depth: int = 2,
) -> Dict[str, Any]:
    """对单个书签分类（支持自定义嵌套层数）

    Args:
        url: 书签 URL
        title: 标题
        description: 描述
        folder_path: 浏览器文件夹路径（如 "技术/前端"）
        max_depth: 分类嵌套层数（1-5，默认 2）

    Returns:
        {
            "category": "技术/前端",
            "strategy": "DomainStrategy",
            "max_depth": 2
        }
    """
    return await _call_api("POST", "/bookmark/categorize", json_body={
        "url": url,
        "title": title,
        "description": description,
        "folder_path": folder_path,
        "max_depth": max_depth,
    })


@mcp.tool()
async def batch_categorize(
    bookmark_ids: Optional[List[str]] = None,
    max_depth: int = 2,
    strategy_priority: Optional[List[str]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """批量分类

    Args:
        bookmark_ids: 要分类的书签 ID 列表（None = 全部）
        max_depth: 嵌套层数（1-5，默认 2）
        strategy_priority: 临时覆盖策略优先级
            例：["folder_path", "domain", "keyword", "ai"]
        dry_run: True=只看不改，False=写回

    Returns:
        {total, by_strategy: {strategy: count}, results: [...]}
    """
    return await _call_api("POST", "/bookmarks/categorize-batch", json_body={
        "bookmark_ids": bookmark_ids,
        "max_depth": max_depth,
        "strategy_priority": strategy_priority,
        "dry_run": dry_run,
    })


@mcp.tool()
async def get_categorization_config() -> Dict[str, Any]:
    """查看当前分类配置

    Returns:
        {
            max_depth: 2,
            separator: "/",
            default_category: "未分类",
            strategies_order: [...],
            domain_count: 23,
            keyword_rules: [...]
        }
    """
    return await _call_api("GET", "/categorization/config")


@mcp.tool()
async def update_categorization_config(
    max_depth: Optional[int] = None,
    strategy_enabled: Optional[Dict[str, bool]] = None,
    strategy_priority: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """动态更新分类配置（无需重启）

    Args:
        max_depth: 新嵌套层数（1-5）
        strategy_enabled: 启用/禁用策略
            例：{"folder_path": True, "ai": False}
        strategy_priority: 调整策略优先级
            例：{"ai": 1, "domain": 3}

    Returns:
        更新后的配置
    """
    body = {}
    if max_depth is not None:
        body["max_depth"] = max_depth
    strategies_update = {}
    if strategy_enabled:
        for k, v in strategy_enabled.items():
            strategies_update.setdefault(k, {})["enabled"] = v
    if strategy_priority:
        for k, v in strategy_priority.items():
            strategies_update.setdefault(k, {})["priority"] = v
    if strategies_update:
        body["strategies"] = strategies_update

    return await _call_api("POST", "/categorization/config", json_body=body)


if __name__ == "__main__":
    logger.info(f"Starting Bookmark MCP v3, API: {BOOKMARK_API_BASE}")
    mcp.run()
