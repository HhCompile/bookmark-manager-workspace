---
name: bookmark-manager
description: 智能管理浏览器书签 - 搜索、整理、AI 建议、分类、Chrome 同步。当用户提到书签、收藏、URL、tag、分类、Chrome 同步、整理、清理、去重、智能分类时主动使用。
---

# Bookmark Manager 技能

本技能让 Claude 通过 MCP 工具**智能地**管理你的浏览器书签。

## 🌲 多层嵌套分类（v3 新增）

书签分类支持**动态层数**（默认 2 层），用 `/` 分隔路径：

### 配置位置
`bookmark-manager-admin/config/categorization.json`

### 关键配置项

#### `max_depth`：嵌套层数
- 默认：**2**
- 范围：1-5
- 1 = 单层（如 `技术`）
- 2 = 双层（如 `技术/前端`）← 推荐
- 3 = 三层（如 `技术/前端/React`）
- 5 = 五层（不推荐，过细）

#### `strategies`：4 种策略，按 priority 排序
| priority | 策略 | 说明 |
|---|---|---|
| 0 | `folder_path` | 浏览器文件夹结构（最高优先）|
| 1 | `domain` | 域名精确匹配 |
| 2 | `keyword` | 关键字匹配 |
| 3 | `ai` | AI 推荐（最低优先）|

每个策略可独立 `enabled` 和 `priority`。

### 分类示例

**max_depth=2**：
- `github.com/facebook/react` → `技术/代码托管`（来自 domain）
- `bilibili.com/video/xxx` → `娱乐/视频`（来自 domain）
- 含 "react hooks" → `技术/前端/React` ← 会被截断为 `技术/前端`

**max_depth=3**：
- 含 "react hooks" → `技术/前端/React`（完整保留）

### 用户询问"改嵌套层数"时

1. 调 `get_categorization_config` 查看当前配置
2. 调 `update_categorization_config(max_depth=3)` 改层数
3. 调 `batch_categorize(dry_run=False)` 重新分类
4. 调 `categorize_bookmark` 验证单条结果

### 临时覆盖（不修改配置）

调 `categorize_bookmark(max_depth=3)` 或 `batch_categorize(max_depth=3)` 临时覆盖。

### 分类路径查询

- `get_bookmarks_by_category("技术")` 查所有"技术"下
- `get_bookmarks_by_category("技术/前端")` 精确查"技术/前端"
- 注意：当前 API 是精确匹配，**不包含**子分类（如查"技术"不会包含"技术/前端"）

### 调整策略优先级

```python
# 让 AI 推荐优先于 domain
update_categorization_config(
    strategy_priority={"ai": 0, "domain": 3}
)
```

## 🎯 适用场景

- 书签/收藏/Chrome 同步
- 整理/清理/去重/归档
- Tag/分类/标签
- 智能分类/AI 整理
- 嵌套分类层级调整

## 🛠 可用工具（17 个）

### 查询类（4 个）
- `list_bookmarks(limit, offset)` - 列出全部
- `search_bookmarks(keyword, limit)` - 关键字搜索
- `get_bookmarks_by_tag(tag, limit)` - 按 tag 查（快）
- `get_bookmarks_by_category(category, limit)` - 按分类查（支持多层级）

### 操作类（4 个）
- `add_bookmark(url, title, description, tags, category)` - 新增
- `update_bookmark(bookmark_id, ...)` - 更新
- `delete_bookmark(bookmark_id)` - 删除
- `batch_organize(bookmark_ids, action, params)` - 批量

### 智能类（2 个）
- `ai_suggest(bookmark_id, scope)` - AI 建议
- `import_from_file(file_path, format)` - 导入

### 同步类（1 个）
- `sync_status()` - Chrome 扩展同步状态

### 分类类（4 个，v3 新增）
- `categorize_bookmark(url, title, max_depth)` - 单条分类
- `batch_categorize(bookmark_ids, max_depth, strategy_priority, dry_run)` - 批量分类
- `get_categorization_config()` - 查看配置
- `update_categorization_config(max_depth, ...)` - 动态更新配置

## 🧠 智能使用原则

### 1. 搜索时优先用 tag
`get_bookmarks_by_tag` 比 `search_bookmarks` 快得多。

### 2. 分类时先 dry_run
`batch_categorize(dry_run=True)` 先看结果，确认后再 `dry_run=False`。

### 3. 写操作前明确告知
- `delete_bookmark` - 不可逆
- `update_bookmark` - 改了哪些字段
- `batch_organize` - 影响多少条

### 4. 配置变更不重启
`update_categorization_config` 立即生效，无需重启服务。

### 5. 嵌套深度按需调整
- 简单分类：max_depth=1
- 一般场景：max_depth=2（推荐）
- 精细管理：max_depth=3
- 不建议 >3（路径过长难以阅读）

## 📋 典型工作流

### 工作流 1：智能分类
```
用户："把所有书签按多层分类整理"
   ↓
1. get_categorization_config()  # 看当前配置
2. 告诉用户：当前 max_depth=2，4 个策略启用
3. batch_categorize(dry_run=True)  # 预览
4. 显示统计：domain 匹配 50%，keyword 30%，AI 15%，fallback 5%
5. 用户确认
6. batch_categorize(dry_run=False)  # 写回
```

### 工作流 2：调整嵌套层数
```
用户："我要 3 层嵌套分类"
   ↓
1. update_categorization_config(max_depth=3)
2. batch_categorize(max_depth=3, dry_run=True)
3. 展示新分类结果
4. 用户确认
5. batch_categorize(max_depth=3, dry_run=False)
```

### 工作流 3：调整策略优先级
```
用户："我想让 AI 推荐比 domain 优先"
   ↓
1. update_categorization_config(
     strategy_priority={"ai": 1, "domain": 3}
   )
2. batch_categorize(dry_run=True)
3. 展示新结果
```

## ⚠️ 重要约束

1. **永远不擅自删除**
2. **批量操作前先 dry_run**
3. **配置变更前先 get_categorization_config 确认现状**
4. **嵌套深度不超过 5**（API 校验）
5. **批量分类不超过 500 条/次**

## 🔗 相关资源

- bookmark-manager-admin：https://github.com/HhCompile/bookmark-manager-admin
- bookmark-manager-workspace：https://github.com/HhCompile/bookmark-manager-workspace
- 分类配置：`config/categorization.json`
