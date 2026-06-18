# 🔌 bookmark-mcp

> 把 [bookmark-manager-admin](https://github.com/HhCompile/bookmark-manager-admin) 的 10+ REST API 暴露为 MCP 工具，让 Claude Code 直接管理你的书签

## 🎯 这是什么

**这是一个 MCP Server**——独立进程，跑起来后 Claude Code 能像调内置工具一样调你的书签管理能力：

> 用户："帮我找出所有 Python 机器学习的书签"
> Claude：调用 `get_bookmarks_by_tag("Python")` → 返回结果

**关键优势**：
- ✅ **不侵入原项目**：bookmark-manager-web/admin 代码完全不动
- ✅ **类型安全**：每个工具有明确的参数/返回值类型
- ✅ **10 个工具**：覆盖查询/操作/智能/导入
- ✅ **附赠 Skill**：教 Claude 怎么"聪明地"用工具

## 🏗️ 架构

```
┌──────────────────┐
│   Claude Code    │  (MCP Client)
└────────┬─────────┘
         │ stdio + MCP 协议
         ▼
┌──────────────────┐
│  bookmark-mcp    │  ← 本项目（独立进程）
│  (Python)        │
└────────┬─────────┘
         │ HTTP
         ▼
┌──────────────────┐
│  bookmark-       │  ← 你的原仓（代码不动）
│  manager-admin   │
│  (Flask)         │
└──────────────────┘
```

## 🚀 快速开始

### 前置要求
- Python 3.10+
- bookmark-manager-admin 跑起来（默认 `http://localhost:9001`）

### 安装

```bash
cd bookmark-mcp
pip install -r requirements.txt
```

### 启动

```bash
python server.py
```

启动后，server 会**监听 stdio**，等待 Claude Code 连接。

### 接入 Claude Code

编辑 `~/.claude/mcp.json`：

```json
{
  "mcpServers": {
    "bookmark": {
      "command": "python",
      "args": ["/绝对路径/bookmark-mcp/server.py"],
      "env": {
        "BOOKMARK_API_BASE": "http://localhost:9001/v1"
      }
    }
  }
}
```

重启 Claude Code，工具就自动可用了。

## 🛠 可用工具（10 个）

### 查询类（4 个）
| 工具 | 用途 |
|---|---|
| `list_bookmarks(limit, offset)` | 列出所有 |
| `search_bookmarks(keyword, limit)` | 关键字搜索 |
| `get_bookmarks_by_tag(tag, limit)` | 按 tag 查（推荐，索引快）|
| `get_bookmarks_by_category(category, limit)` | 按分类查 |

### 操作类（4 个）
| 工具 | 用途 | 警告 |
|---|---|---|
| `add_bookmark(url, title, description, tags, category)` | 新增 | - |
| `update_bookmark(bookmark_id, ...)` | 更新（只改传入字段）| - |
| `delete_bookmark(bookmark_id)` | 删除 | ⚠️ 不可逆 |
| `batch_organize(bookmark_ids, action, params)` | 批量整理 | ⚠️ 影响多条 |

### 智能类（2 个）
| 工具 | 用途 |
|---|---|
| `ai_suggest(bookmark_id, scope)` | AI 建议（不修改数据）|
| `import_from_file(file_path, format)` | 从文件导入 |

### batch_organize 的 action 取值
- `add_tag` - 加 tag
- `remove_tag` - 删 tag
- `move_category` - 改分类
- `archive` - 归档
- `vault` - 移入保险箱

### ai_suggest 的 scope 取值
- `all` - 所有建议
- `duplicates` - 重复书签
- `dead_links` - 死链
- `untagged` - 未打 tag 的

## 🎓 Skill 引导

`SKILL.md` 是一个 Claude Code Skill，让 Claude 知道"什么时候用 bookmark-mcp、怎么用更聪明"。

Skill 内容包含：
- 5 大智能使用原则
- 4 个典型工作流
- 输出格式建议
- 错误处理约束

## 📦 项目结构

```
bookmark-mcp/
├── server.py            # MCP server 主入口
├── SKILL.md             # Claude Code Skill 定义
├── requirements.txt     # Python 依赖
├── README.md            # 本文件
└── .gitignore
```

## 🔧 配置

### 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `BOOKMARK_API_BASE` | `http://localhost:9001/v1` | bookmark-admin 地址 |
| `BOOKMARK_TIMEOUT` | `30` | HTTP 超时（秒）|
| `LOG_LEVEL` | `INFO` | 日志级别 |

### 自定义

如果要接入不同地址的 bookmark-admin：

```bash
export BOOKMARK_API_BASE="https://my-bookmark.example.com/v1"
python server.py
```

## 🧪 测试

启动后，在 Claude Code 里输入：

```
用 bookmark 工具找出我所有 Python 教程
```

Claude 应该会自动调 `get_bookmarks_by_tag("Python")` 或 `search_bookmarks("Python")`。

## 🛡️ 约束

- **不修改原项目**：bookmark-manager-web/admin 代码 100% 不动
- **写操作前确认**：`delete_bookmark` / `update_bookmark` / `batch_organize` 调用前 Claude 会跟用户确认
- **批量上限 50 条/次**：超过则分批处理
- **错误友好**：API 错误返回结构化 `{status: error, error: msg}`

## 📝 License

MIT

## 🔗 相关

- 📦 [bookmark-manager-admin](https://github.com/HhCompile/bookmark-manager-admin) - 后端 API
- 🌐 [bookmark-manager-web](https://github.com/HhCompile/bookmark-manager-web) - 前端 Web
- 📚 [bookmark-manager-workspace](https://github.com/HhCompile/bookmark-manager-workspace) - 产品工作区
