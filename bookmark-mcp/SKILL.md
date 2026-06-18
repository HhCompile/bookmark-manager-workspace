---
name: bookmark-manager
description: 智能管理浏览器书签 - 搜索、整理、AI 建议。当用户提到书签、收藏、URL、tag、分类、Chrome 同步、整理、清理、去重、智能分类时主动使用。
---

# Bookmark Manager 技能

本技能让 Claude 通过 MCP 工具**智能地**管理你的浏览器书签，而不是机械地调用工具。

## 🎯 适用场景

当用户提到以下内容时使用本技能：
- 书签 / 收藏 / bookmark
- 浏览器同步 / Chrome 同步
- 整理 / 清理 / 去重 / 归档
- Tag / 分类 / 标签
- "找出我收藏的 XX" / "最近收藏" / "未读的书签"
- 智能分类 / AI 整理

## 🛠 可用工具（MCP 自动暴露）

| 工具 | 用途 | 性能 |
|---|---|---|
| `list_bookmarks` | 列出全部 | 中（数据量大时慢） |
| `search_bookmarks` | 关键字搜索 | 中（全字段扫描）|
| `get_bookmarks_by_tag` | 按 tag 查 | **快**（索引查询）|
| `get_bookmarks_by_category` | 按分类查 | **快**（索引查询）|
| `add_bookmark` | 新增 | - |
| `update_bookmark` | 更新 | - |
| `delete_bookmark` | 删除 | ⚠️ 不可逆 |
| `batch_organize` | 批量整理 | ⚠️ 影响多条 |
| `ai_suggest` | AI 建议 | - |
| `import_from_file` | 导入文件 | - |

## 🧠 智能使用原则

### 1. 搜索时优先用 tag
**不要**：用户说"找 Python 教程"→ `search_bookmarks(keyword="Python")`（慢）
**应该**：先列 tag 找 Python 相关 tag → `get_bookmarks_by_tag("Python")`（快）

### 2. 批量操作前先 dry-run
**不要**：`batch_organize(all_ids, "add_tag", {"tag": "Python"})`
**应该**：先 `list_bookmarks()` → 找到目标 → 给用户看预览 → 用户确认 → 再批量

### 3. 写操作前明确告知
- `delete_bookmark`：明确告诉用户"删除后不可逆"
- `update_bookmark`：告诉用户改了哪些字段
- `batch_organize`：告诉用户影响多少条

### 4. 用 AI 建议而非直接改
- 用户说"整理重复书签"→ 先 `ai_suggest(scope="duplicates")` → 给用户看重复对 → 让用户决定删哪个

### 5. 模糊查询时分步
**不要**："找出我最近 7 天收藏的关于 React 的教程"→ 一次 `search_bookmarks("React 最近 7 天")`
**应该**：先 `list_bookmarks(limit=100)` → 客户端过滤日期和主题 → 总结

## 📋 典型工作流

### 工作流 1：智能搜索
```
用户："帮我找出我所有 Python 机器学习的书签"
   ↓
1. get_bookmarks_by_tag("Python")  // 拿 Python 标签下所有
2. 客户端过滤"机器学习"相关的
3. 整理输出
```

### 工作流 2：批量整理
```
用户："把'教程'分类下的所有书签加上'2024'标签"
   ↓
1. get_bookmarks_by_category("教程")  // 预览
2. 告诉用户："共找到 X 个，确认加 tag '2024'？"
3. 用户确认
4. batch_organize(...)
```

### 工作流 3：清理重复
```
用户："清理我重复的书签"
   ↓
1. ai_suggest(scope="duplicates")  // AI 找重复
2. 展示重复对给用户
3. 用户决定保留哪个
4. delete_bookmark(...)  // 逐个删
```

### 工作流 4：定期复盘
```
用户："分析我这周收藏的习惯"
   ↓
1. list_bookmarks(limit=100)  // 拿最近 100 个
2. 客户端分析：哪些 tag 多 / 哪些分类多 / 时间分布
3. 总结 + 建议
```

## ⚠️ 重要约束

1. **永远不擅自删除** - 删前必须确认
2. **批量操作不超过 50 条/次** - 超过则分批
3. **URL 必填** - add_bookmark 必须有 url
4. **错误处理** - API 返回 error 时清晰告知用户
5. **不要无限循环** - 一次任务最多 5 轮工具调用

## 🎨 输出建议

- 搜索结果用**列表**展示（含标题 + URL + tag + 收藏时间）
- 批量操作前用**预览**（"将影响 X 条：..."）
- 统计用**简短总结**（"共 23 个，主要分布：Python 12 / React 8 / 其他 3"）
- 错误用**清晰说明**（"API 500：服务器内部错误，请稍后重试"）

## 🔗 相关资源

- bookmark-manager-admin（后端）：https://github.com/HhCompile/bookmark-manager-admin
- bookmark-manager-web（前端）：https://github.com/HhCompile/bookmark-manager-web
- 工作区：https://github.com/HhCompile/bookmark-manager-workspace
