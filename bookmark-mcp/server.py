#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bookmark Manager MCP Server

把 bookmark-manager-admin 的 REST API 暴露为 MCP 工具，
让 Claude Code 能直接调你的书签管理能力。

设计原则：
- 每个工具对应一个 bookmark-admin API 端点
- 工具命名清晰（动词+名词）
- 错误处理友好（返回 status + message）
- 通过 HTTP 调原服务，bookmark-admin 代码完全不动

启动：python server.py
配置：~/.claude/mcp.json 加 entry 即可
"""

import os
import sys
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# ============================================================================
# 配置
# ============================================================================

BOOKMARK_API_BASE = os.environ.get(
    "BOOKMARK_API_BASE",
    "http://localhost:9001/v1"  # bookmark-manager-admin 默认端口
)
REQUEST_TIMEOUT = float(os.environ.get("BOOKMARK_TIMEOUT", "30"))

# 日志
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bookmark-mcp")

# MCP Server
mcp = FastMCP(
    "Bookmark Manager",
    instructions="""
Bookmark Manager MCP Server

提供 10 个工具让你的 Claude 能直接管理书签：
- 查询：list / search / by_tag / by_category
- 操作：add / update / delete / batch
- 智能：ai_suggest / import

使用建议：
1. 搜索时优先用 by_tag（快）而非 search（全字段，慢）
2. 批量操作前先用 list_bookmarks 确认范围
3. 改/删操作不可逆，请明确告诉用户
4. ai_suggest 不修改数据，只给建议
""",
)

# HTTP 客户端（长连接）
client = httpx.AsyncClient(
    base_url=BOOKMARK_API_BASE,
    timeout=REQUEST_TIMEOUT,
    headers={"Content-Type": "application/json"},
)


async def _call_api(
    method: str,
    path: str,
    *,
    params: Optional[Dict] = None,
    json_body: Optional[Dict] = None,
) -> Dict[str, Any]:
    """统一 API 调用：处理错误、返回友好消息"""
    try:
        logger.info(f"API call: {method} {path}")
        resp = await client.request(
            method, path, params=params, json=json_body
        )
        resp.raise_for_status()
        return {"status": "success", "data": resp.json()}
    except httpx.HTTPStatusError as e:
        logger.error(f"API error {e.response.status_code}: {e.response.text}")
        return {
            "status": "error",
            "error": f"API {e.response.status_code}: {e.response.text}",
        }
    except Exception as e:
        logger.exception("Unexpected error")
        return {"status": "error", "error": str(e)}


# ============================================================================
# 1️⃣ 查询类工具
# ============================================================================


@mcp.tool()
async def list_bookmarks(
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    列出所有书签

    Args:
        limit: 返回数量（默认 50，最大 500）
        offset: 跳过数量（分页用）

    Returns:
        status + bookmarks 列表
    """
    return await _call_api(
        "GET", "/bookmarks",
        params={"limit": min(limit, 500), "offset": max(offset, 0)},
    )


@mcp.tool()
async def search_bookmarks(
    keyword: str,
    limit: int = 30,
) -> Dict[str, Any]:
    """
    关键字搜索书签（标题 + URL + 描述 + tag）

    Args:
        keyword: 搜索关键字（不区分大小写）
        limit: 返回数量（默认 30）

    Returns:
        匹配的书签列表
    """
    if not keyword.strip():
        return {"status": "error", "error": "keyword 不能为空"}
    return await _call_api(
        "GET", "/bookmarks",
        params={"q": keyword, "limit": min(limit, 200)},
    )


@mcp.tool()
async def get_bookmarks_by_tag(
    tag: str,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    按 tag 查书签（推荐，索引快）

    Args:
        tag: 标签名（精确匹配）
        limit: 返回数量

    Returns:
        该 tag 下所有书签
    """
    if not tag.strip():
        return {"status": "error", "error": "tag 不能为空"}
    return await _call_api(
        "GET", f"/bookmarks/tag/{tag}",
        params={"limit": min(limit, 200)},
    )


@mcp.tool()
async def get_bookmarks_by_category(
    category: str,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    按分类查书签

    Args:
        category: 分类名
        limit: 返回数量

    Returns:
        该分类下所有书签
    """
    if not category.strip():
        return {"status": "error", "error": "category 不能为空"}
    return await _call_api(
        "GET", f"/bookmarks/category/{category}",
        params={"limit": min(limit, 200)},
    )


# ============================================================================
# 2️⃣ 操作类工具（写操作）
# ============================================================================


@mcp.tool()
async def add_bookmark(
    url: str,
    title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    category: str = "",
) -> Dict[str, Any]:
    """
    新增一个书签

    Args:
        url: 书签 URL
        title: 标题
        description: 描述（可选）
        tags: 标签列表（可选）
        category: 分类（可选）

    Returns:
        新创建的书签信息（含 id）
    """
    if not url.strip() or not title.strip():
        return {"status": "error", "error": "url 和 title 必填"}
    return await _call_api(
        "POST", "/bookmark",
        json_body={
            "url": url,
            "title": title,
            "description": description,
            "tags": tags or [],
            "category": category,
        },
    )


@mcp.tool()
async def update_bookmark(
    bookmark_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """
    更新一个书签的字段（只改传入的字段）

    Args:
        bookmark_id: 书签 ID
        title: 新标题（可选）
        description: 新描述（可选）
        tags: 新标签列表（可选）
        category: 新分类（可选）

    Returns:
        更新后的书签
    """
    if not bookmark_id.strip():
        return {"status": "error", "error": "bookmark_id 必填"}

    updates = {
        k: v for k, v in {
            "title": title,
            "description": description,
            "tags": tags,
            "category": category,
        }.items() if v is not None
    }
    if not updates:
        return {"status": "error", "error": "至少要传一个要改的字段"}

    updates["id"] = bookmark_id
    return await _call_api("POST", "/bookmark/update", json_body=updates)


@mcp.tool()
async def delete_bookmark(bookmark_id: str) -> Dict[str, Any]:
    """
    删除一个书签（**不可逆**，请确认）

    Args:
        bookmark_id: 书签 ID

    Returns:
        删除结果
    """
    if not bookmark_id.strip():
        return {"status": "error", "error": "bookmark_id 必填"}
    return await _call_api(
        "POST", "/bookmark/delete",
        json_body={"id": bookmark_id},
    )


@mcp.tool()
async def batch_organize(
    bookmark_ids: List[str],
    action: str,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    批量操作（打 tag / 改分类 / 归档 / 移入保险箱等）

    Args:
        bookmark_ids: 书签 ID 列表
        action: 操作类型（add_tag / remove_tag / move_category / archive / vault）
        params: 操作参数（如 {"tag": "Python"} / {"category": "技术"}）

    Returns:
        批量操作结果
    """
    if not bookmark_ids:
        return {"status": "error", "error": "bookmark_ids 不能为空"}
    valid_actions = {"add_tag", "remove_tag", "move_category", "archive", "vault"}
    if action not in valid_actions:
        return {
            "status": "error",
            "error": f"action 必须是 {valid_actions} 之一",
        }
    return await _call_api(
        "POST", "/bookmarks/batch",
        json_body={
            "ids": bookmark_ids,
            "action": action,
            "params": params or {},
        },
    )


# ============================================================================
# 3️⃣ 智能类工具
# ============================================================================


@mcp.tool()
async def ai_suggest(
    bookmark_id: Optional[str] = None,
    scope: str = "all",
) -> Dict[str, Any]:
    """
    AI 智能建议（不修改数据，只给建议）

    Args:
        bookmark_id: 单个书签 ID（可选）
        scope: 范围 all / duplicates / dead_links / untagged

    Returns:
        AI 建议列表
    """
    return await _call_api(
        "POST", "/ai/suggest",
        json_body={
            "bookmark_id": bookmark_id,
            "scope": scope,
        },
    )


@mcp.tool()
async def import_from_file(
    file_path: str,
    format: str = "html",  # html / json / csv
) -> Dict[str, Any]:
    """
    从浏览器书签导出文件导入

    Args:
        file_path: 文件绝对路径
        format: 文件格式 html (Chrome) / json / csv

    Returns:
        导入结果（含成功数/失败数）
    """
    if not Path(file_path).exists():
        return {"status": "error", "error": f"文件不存在: {file_path}"}

    # 读取文件内容并上传
    try:
        file_content = Path(file_path).read_text(encoding="utf-8")
        return await _call_api(
            "POST", "/bookmark/upload",
            json_body={"content": file_content, "format": format},
        )
    except Exception as e:
        return {"status": "error", "error": f"读取文件失败: {e}"}


# ============================================================================
# 启动入口
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting Bookmark MCP Server, API base: {BOOKMARK_API_BASE}")
    logger.info("Available tools: list_bookmarks, search_bookmarks, get_bookmarks_by_tag, "
                "get_bookmarks_by_category, add_bookmark, update_bookmark, "
                "delete_bookmark, batch_organize, ai_suggest, import_from_file")
    try:
        mcp.run()
    finally:
        import asyncio
        asyncio.run(client.aclose())
