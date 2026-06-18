#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bookmark Manager MCP Server v4

v4 修正：不再自造清洗逻辑，直接调用 admin 已有端点
- 复用 /v1/bookmarks/deduplicate（去重）
- 复用 /v1/scripts/analyze（分析）
- 复用 /v1/scripts/parse（解析 HTML）
- 复用 /v1/ai/suggest（AI 建议）
- 复用 /v1/tags/batch-generate（批量生成 tag）
- 复用 /v1/tags/<id>/merge（tag 合并）

v3 分类工具保留（嵌套层级 + 优先级）
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
    instructions="Bookmark MCP v4 - 完整查询/操作/分类/清洗（复用 admin 现有端点）",
)

client = httpx.AsyncClient(
    base_url=BOOKMARK_API_BASE,
    timeout=REQUEST_TIMEOUT,
    headers={"Content-Type": "application/json"},
)


async def _call_api(method, path, *, params=None, json_body=None, files=None):
    """统一 API 调用（支持文件上传）"""
    try:
        if files:
            # 文件上传模式
            resp = await client.request(method, path, files=files)
        else:
            resp = await client.request(method, path, params=params, json=json_body)
        resp.raise_for_status()
        return {"status": "success", "data": resp.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "error": f"API {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# v1 工具（保留）
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
    """按 tag 查（推荐，索引快）"""
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
async def import_from_file(file_path: str, format: str = "html"):
    """从 HTML 文件导入（复用 /v1/scripts/parse）"""
    from pathlib import Path
    if not Path(file_path).exists():
        return {"status": "error", "error": f"文件不存在: {file_path}"}
    return await _call_api("POST", "/scripts/process", json_body={"file": file_path})


# ============================================================================
# v2 工具
# ============================================================================


@mcp.tool()
async def sync_status():
    """Chrome 扩展同步状态"""
    return await _call_api("GET", "/bookmark/sync-status")


# ============================================================================
# v3 工具 - 分类引擎
# ============================================================================


@mcp.tool()
async def categorize_bookmark(url: str, title: str, description: str = "", folder_path: str = "", max_depth: int = 2):
    """对单个书签分类（自定义嵌套层数）"""
    return await _call_api("POST", "/bookmark/categorize", json_body={
        "url": url, "title": title, "description": description,
        "folder_path": folder_path, "max_depth": max_depth,
    })


@mcp.tool()
async def batch_categorize(bookmark_ids: Optional[List[str]] = None, max_depth: int = 2, strategy_priority: Optional[List[str]] = None, dry_run: bool = True):
    """批量分类"""
    return await _call_api("POST", "/bookmarks/categorize-batch", json_body={
        "bookmark_ids": bookmark_ids, "max_depth": max_depth,
        "strategy_priority": strategy_priority, "dry_run": dry_run,
    })


@mcp.tool()
async def get_categorization_config():
    """查看分类配置"""
    return await _call_api("GET", "/categorization/config")


@mcp.tool()
async def update_categorization_config(max_depth: Optional[int] = None, strategy_enabled: Optional[Dict[str, bool]] = None, strategy_priority: Optional[Dict[str, int]] = None):
    """动态更新分类配置"""
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


# ============================================================================
# v4 工具 - 复用 admin 现有清洗端点（不再自造）
# ============================================================================


@mcp.tool()
async def deduplicate_bookmarks() -> Dict[str, Any]:
    """去重书签（复用 admin `/v1/bookmarks/deduplicate`）

    按 URL 精确去重，保留第一个出现的。

    Returns:
        {original_count, duplicate_count, current_count, message}
    """
    return await _call_api("POST", "/bookmarks/deduplicate")


@mcp.tool()
async def analyze_bookmarks(
    scope: str = "all",
    bookmark_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """AI 智能分析书签（复用 `/v1/scripts/analyze`）

    Args:
        scope: 分析范围
            - all: 全部
            - duplicates: 只分析重复
            - dead_links: 只分析死链
            - untagged: 只分析未打 tag 的
        bookmark_ids: 自定义范围（None = 全部）

    Returns:
        suggestions 列表
    """
    # 复用 AI suggest 端点
    if scope == "duplicates":
        return await _call_api("POST", "/ai/suggest", json_body={"scope": "duplicates"})
    elif scope == "dead_links":
        return await _call_api("POST", "/ai/suggest", json_body={"scope": "dead_links"})
    elif scope == "untagged":
        return await _call_api("POST", "/ai/suggest", json_body={"scope": "untagged"})
    else:
        return await _call_api("POST", "/scripts/analyze", json_body={"scope": "all"})


@mcp.tool()
async def parse_bookmark_html(file_path: str) -> Dict[str, Any]:
    """解析 HTML 书签文件（复用 `/v1/scripts/parse`）

    Args:
        file_path: Chrome/Firefox 导出的 HTML 文件路径
    """
    from pathlib import Path
    if not Path(file_path).exists():
        return {"status": "error", "error": f"文件不存在: {file_path}"}

    # 直接调用 scripts/parse（需要 multipart 上传）
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'text/html')}
            resp = await client.post("/scripts/parse", files=files)
            resp.raise_for_status()
            return {"status": "success", "data": resp.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def list_scripts() -> Dict[str, Any]:
    """列出 admin 已注册的分析脚本（复用 `/v1/scripts`）

    Returns:
        scripts: [{name, description, author, ...}]
    """
    return await _call_api("GET", "/scripts")


@mcp.tool()
async def list_tags(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """列出所有 tag（复用 `/v1/tags`）"""
    return await _call_api("GET", "/tags", params={"limit": min(limit, 500), "offset": max(offset, 0)})


@mcp.tool()
async def ai_suggest_one(
    url: str,
    title: str,
    suggest_type: str = "title",  # title/alias/tags/category/summary
) -> Dict[str, Any]:
    """AI 优化单个书签（复用 `/v1/ai/suggest`）

    Args:
        url: 书签 URL
        title: 当前标题
        suggest_type: 建议类型
            - title: 优化标题
            - alias: 生成别名
            - tags: 推荐 tag
            - category: 推荐分类
            - summary: 生成摘要
    """
    return await _call_api("POST", "/ai/suggest", json_body={
        "type": suggest_type,
        "url": url,
        "title": title,
    })


@mcp.tool()
async def ai_suggest_batch(
    bookmark_ids: List[str],
    suggest_type: str = "tags",
) -> Dict[str, Any]:
    """批量 AI 建议（复用 `/v1/tags/batch-generate`）"""
    return await _call_api("POST", "/tags/batch-generate", json_body={
        "bookmark_ids": bookmark_ids,
        "type": suggest_type,
    })


@mcp.tool()
async def merge_tags(source_tag_id: str, target_tag_id: str) -> Dict[str, Any]:
    """合并 tag（复用 `/v1/tags/<id>/merge`）"""
    return await _call_api("POST", f"/tags/{source_tag_id}/merge", json_body={"target_id": target_tag_id})


@mcp.tool()
async def batch_delete(bookmark_ids: List[str]) -> Dict[str, Any]:
    """批量删除书签（复用 `/v1/bookmarks/batch-delete`，**不可逆**）"""
    return await _call_api("POST", "/bookmarks/batch-delete", json_body={"ids": bookmark_ids})


@mcp.tool()
async def batch_update_bookmarks(
    bookmark_ids: List[str],
    updates: Dict[str, Any],
) -> Dict[str, Any]:
    """批量更新书签字段（复用 `/v1/bookmarks/batch-update`）"""
    return await _call_api("POST", "/bookmarks/batch-update", json_body={
        "ids": bookmark_ids,
        "updates": updates,
    })


@mcp.tool()
async def export_bookmarks(
    format: str = "html",
    bookmark_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """导出书签（复用 `/v1/bookmarks/export`）

    Args:
        format: 导出格式（html / json / csv）
        bookmark_ids: 自定义范围（None = 全部）
    """
    return await _call_api("POST", "/bookmarks/export", json_body={
        "format": format,
        "ids": bookmark_ids,
    })


@mcp.tool()
async def get_stats() -> Dict[str, Any]:
    """书签统计（复用 `/v1/bookmarks/stats`）"""
    return await _call_api("GET", "/bookmarks/stats")


@mcp.tool()
async def get_folder_tree() -> Dict[str, Any]:
    """文件夹树（复用 `/v1/folders`）"""
    return await _call_api("GET", "/folders")


@mcp.tool()
async def fetch_metadata(url: str) -> Dict[str, Any]:
    """抓取 URL 元数据（复用 `/v1/bookmark/<url>/metadata` GET）

    实际抓取网页 og:title / description / image。
    """
    return await _call_api("GET", f"/bookmark/{url}/metadata")


@mcp.tool()
async def record_visit(url: str) -> Dict[str, Any]:
    """记录书签访问（复用 `/v1/bookmark/<url>/visit`）"""
    return await _call_api("POST", f"/bookmark/{url}/visit")


if __name__ == "__main__":
    logger.info(f"Starting Bookmark MCP v4, API: {BOOKMARK_API_BASE}")
    mcp.run()
