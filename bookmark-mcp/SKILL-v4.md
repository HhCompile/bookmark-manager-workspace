---
name: bookmark-manager
description: 智能管理浏览器书签 - 搜索、整理、AI 建议、分类、Chrome 同步、数据清洗。复用 bookmark-manager-admin 现有端点。当用户提到书签、收藏、URL、tag、分类、Chrome 同步、整理、清理、去重、智能分类、死链检测时主动使用。
---

# Bookmark Manager 技能（v4）

⚠️ **重要原则**：本技能**复用 admin 已有端点**，不重新实现。

admin 后端已经提供了**完整**的清洗/分析/同步能力。MCP 工具是 admin 端点的"薄包装"。

## 🎯 适用场景

- 书签/收藏/Chrome 同步
- 整理/清理/去重/归档
- Tag/分类/标签（含嵌套层级）
- 智能分类/AI 整理
- 死链检测/相似检测
- HTML 文件解析导入

## 🛠 可用工具（22 个，全部映射到 admin 端点）

### 📂 查询类（5 个）
| 工具 | admin 端点 | 用途 |
|---|---|---|
| `list_bookmarks(limit, offset)` | `GET /v1/bookmarks` | 列出全部 |
| `search_bookmarks(keyword, limit)` | `GET /v1/bookmarks?q=` | 关键字搜索 |
| `get_bookmarks_by_tag(tag, limit)` | `GET /v1/bookmarks/tag/<tag>` | 按 tag（快）|
| `get_bookmarks_by_category(category, limit)` | `GET /v1/bookmarks/category/<cat>` | 按分类（多层级）|
| `get_folder_tree()` | `GET /v1/folders` | 文件夹树 |

### ✏️ 操作类（5 个）
| 工具 | admin 端点 | 用途 |
|---|---|---|
| `add_bookmark(url, title, ...)` | `POST /v1/bookmark` | 新增 |
| `update_bookmark(id, ...)` | `POST /v1/bookmark/update` | 更新 |
| `delete_bookmark(id)` | `POST /v1/bookmark/delete` | 删除（不可逆）|
| `batch_organize(ids, action, params)` | `POST /v1/bookmarks/batch` | 批量 |
| `batch_delete(ids)` | `POST /v1/bookmarks/batch-delete` | 批量删 |
| `batch_update_bookmarks(ids, updates)` | `POST /v1/bookmarks/batch-update` | 批量改 |

### 🤖 智能类（3 个）
| 工具 | admin 端点 | 用途 |
|---|---|---|
| `ai_suggest_one(url, title, type)` | `POST /v1/ai/suggest` | 单条 AI 优化 |
| `ai_suggest_batch(ids, type)` | `POST /v1/tags/batch-generate` | 批量 AI 建议 |
| `analyze_bookmarks(scope, ids)` | `POST /v1/scripts/analyze` | 整体分析 |

### 🧹 清洗类（4 个）— v4 新增，复用 admin
| 工具 | admin 端点 | 用途 |
|---|---|---|
| `deduplicate_bookmarks()` | `POST /v1/bookmarks/deduplicate` | URL 精确去重 |
| `parse_bookmark_html(file_path)` | `POST /v1/scripts/parse` | HTML 文件解析 |
| `list_tags(limit, offset)` | `GET /v1/tags` | 列出所有 tag |
| `merge_tags(src_id, tgt_id)` | `POST /v1/tags/<id>/merge` | tag 合并 |

### 🔄 同步类（1 个）
| 工具 | admin 端点 | 用途 |
|---|---|---|
| `sync_status()` | `GET /v1/bookmark/sync-status` | Chrome 扩展同步状态 |

### 🌲 分类类（4 个，v3）
| 工具 | admin 端点 | 用途 |
|---|---|---|
| `categorize_bookmark(...)` | `POST /v1/bookmark/categorize` | 单条分类（嵌套层数可配）|
| `batch_categorize(...)` | `POST /v1/bookmarks/categorize-batch` | 批量分类 |
| `get_categorization_config()` | `GET /v1/categorization/config` | 查看配置 |
| `update_categorization_config(...)` | `POST /v1/categorization/config` | 动态更新 |

### 📊 元数据/统计类（3 个）
| 工具 | admin 端点 | 用途 |
|---|---|---|
| `fetch_metadata(url)` | `GET /v1/bookmark/<url>/metadata` | 抓取网页 og: 等 |
| `record_visit(url)` | `POST /v1/bookmark/<url>/visit` | 记录访问 |
| `get_stats()` | `GET /v1/bookmarks/stats` | 统计 |
| `export_bookmarks(format, ids)` | `POST /v1/bookmarks/export` | 导出 |
| `list_scripts()` | `GET /v1/scripts` | 列出已注册脚本 |

## 🌲 多层嵌套分类（v3+ 保留）

### 配置
`bookmark-manager-admin/config/categorization.json`

### 关键配置项
- `max_depth`：默认 2，范围 1-5
- `strategies`：4 种 + priority 可调
  - `folder_path` (0) - 浏览器文件夹
  - `domain` (1) - 域名匹配
  - `keyword` (2) - 关键字
  - `ai` (3) - AI 推荐

### 调整示例
- "我要 3 层" → `update_categorization_config(max_depth=3)` + `batch_categorize(dry_run=False)`
- "让 AI 优先" → `update_categorization_config(strategy_priority={"ai": 1, "domain": 3})`

## 🧠 智能使用原则

### 1. 复用优先
**不要**建议用户"打开网页操作"，所有 admin 已有的能力都能用 MCP 调。

### 2. 写操作前确认
- `delete_*` / `batch_delete` - 不可逆
- `batch_organize` - 影响多条
- 清洗类默认先 dry_run（如果 admin 支持）

### 3. 死链检测
调 `fetch_metadata(url)` 实际抓页面，返回失败即视为死链。

### 4. AI 建议类型
`ai_suggest_one` 的 type 必须是 admin 支持的 5 种之一：
`title / alias / tags / category / summary`

### 5. 嵌套分类
- 简单分类：`max_depth=1`
- 一般：`max_depth=2`（默认）
- 精细：`max_depth=3`
- 不建议 >3

## 📋 典型工作流

### 工作流 1：完整清洗
```
用户："把所有书签清洗一遍"
   ↓
1. deduplicate_bookmarks()  # URL 去重
2. analyze_bookmarks(scope="all")  # AI 分析
3. ai_suggest_batch(ids, type="tags")  # 推荐 tag
4. 展示报告 + 让用户决定应用哪些
5. 调 update/batch_update 写回
```

### 工作流 2：调整嵌套层数
```
用户："我要 3 层分类"
   ↓
1. get_categorization_config()
2. update_categorization_config(max_depth=3)
3. batch_categorize(dry_run=True)  # 预览
4. 展示新分类结果
5. batch_categorize(dry_run=False)  # 写回
```

### 工作流 3：HTML 导入 + 自动清洗
```
用户："导入我的 Chrome 书签并整理"
   ↓
1. parse_bookmark_html(file_path)  # 解析
2. deduplicate_bookmarks()  # 去重
3. analyze_bookmarks(scope="all")  # 分析建议
4. 展示建议，让用户决定
5. 应用建议（update + tag 合并 + 分类）
```

### 工作流 4：死链清理
```
用户："清理我所有死链"
   ↓
1. list_bookmarks(limit=500)  # 拿所有
2. 逐个 fetch_metadata(url)  # 检查
3. 收集死链 IDs
4. 展示给用户确认
5. batch_delete(dead_link_ids)
```

## ⚠️ 重要约束

1. **永远不擅自删除** - 删前必须确认
2. **批量前先 dry_run**（如果 admin 端支持）
3. **复用 admin 端点** - 不重新实现
4. **嵌套深度 1-5**（API 校验）
5. **批量上限 500 条/次**（admin 限制）

## 🔗 相关资源

- bookmark-manager-admin：https://github.com/HhCompile/bookmark-manager-admin
- bookmark-manager-workspace：https://github.com/HhCompile/bookmark-manager-workspace
- 分类配置：`config/categorization.json`
- 数据清洗 PRD：`docs/02-data-cleaning/PRD.md`
