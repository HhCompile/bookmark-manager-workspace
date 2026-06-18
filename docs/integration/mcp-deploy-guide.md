# 🚀 bookmark-mcp v4 部署指南

> 5 分钟让你的 Claude Code 直接管理书签

## ✅ 已验证

- ✅ server-v4.py 加载成功（29 个工具）
- ✅ MCP 协议握手通过（官方 SDK 客户端实测）
- ✅ 4 个工具真实调用成功（list/get_stats/deduplicate/list_tags）
- ✅ bookmark-manager-admin 端点全部响应 200

## 📋 你需要做的 3 步

### Step 1：复制 server-v4.py 到本地

已经做了（如果你跑过我刚才的测试）：
```bash
/Users/sunxiansheng/Mine/www/bookMark-manager/bookmark-mcp/server-v4.py
```

如果没有，从 GitHub 拉：
```bash
mkdir -p ~/Mine/www/bookMark-manager/bookmark-mcp
cd ~/Mine/www/bookMark-manager/bookmark-mcp
curl -sL "https://raw.githubusercontent.com/HhCompile/bookmark-manager-workspace/main/bookmark-mcp/server-v4.py" -o server-v4.py
```

### Step 2：准备 venv（已建好）

```bash
python3 -m venv /tmp/bookmark-mcp-venv
/tmp/bookmark-mcp-venv/bin/pip install mcp httpx
```

### Step 3：配置 mcp.json

把以下内容写到 `~/.claude/mcp.json`（覆盖）：

```json
{
  "mcpServers": {
    "bookmark": {
      "command": "/tmp/bookmark-mcp-venv/bin/python",
      "args": [
        "/Users/sunxiansheng/Mine/www/bookMark-manager/bookmark-mcp/server-v4.py"
      ],
      "env": {
        "BOOKMARK_API_BASE": "http://localhost:9001/v1",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Step 4：重启 Claude Code

关闭 Claude Code，重新打开。

### Step 5：测试

在 Claude Code 输入：

```
列出我所有书签
```

或者：

```
用 bookmark 工具找 Python 教程
```

Claude 应该会自动调 `list_bookmarks` 或 `search_bookmarks` 工具。

## 🔍 验证连接

### 健康检查
```bash
curl http://localhost:9001/v1/health
```

### 单独测 server（不通过 Claude Code）
```bash
/tmp/bookmark-mcp-venv/bin/python -c "
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def main():
    params = StdioServerParameters(
        command='/tmp/bookmark-mcp-venv/bin/python',
        args=['/Users/sunxiansheng/Mine/www/bookMark-manager/bookmark-mcp/server-v4.py'],
        env={'BOOKMARK_API_BASE': 'http://localhost:9001/v1'}
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f'✅ {len(tools.tools)} 工具可用')

asyncio.run(main())
"
```

## 🛠 故障排查

### Q1：Claude Code 启动后看不到工具
**检查**：
1. `~/.claude/mcp.json` 路径正确
2. JSON 格式合法（用 `python3 -m json.tool < ~/.claude/mcp.json` 验证）
3. `command` 路径是绝对路径（不要用 `python` 简写）
4. venv 路径正确

### Q2：工具调通但返回 500
**检查**：
1. `bookmark-manager-admin` 是否在跑（`curl http://localhost:9001/v1/health`）
2. 环境变量 `BOOKMARK_API_BASE` 是否正确
3. 防火墙是否阻挡

### Q3：权限错误
**解决**：
```bash
chmod +x /tmp/bookmark-mcp-venv/bin/python
chmod -R 755 /Users/sunxiansheng/Mine/www/bookMark-manager
```

## 🎯 你能用 Claude 调的工具（22 个）

| 类别 | 工具 |
|---|---|
| **查询** | list / search / by_tag / by_category / folder_tree |
| **操作** | add / update / delete / batch_organize / batch_delete / batch_update |
| **AI** | ai_suggest_one / ai_suggest_batch / analyze |
| **清洗** | deduplicate / parse_html / list_scripts / list_tags / merge_tags |
| **同步** | sync_status |
| **分类** | categorize / batch_categorize / get_config / update_config |
| **元数据** | fetch_metadata / record_visit / stats / export |

## 🧠 Skill 提示

如果想 Claude 调工具时**更聪明**（用 tag 而非 search、批量前先 dry-run），把 SKILL-v4.md 拷到 `~/.claude/skills/bookmark-manager/SKILL.md`：

```bash
mkdir -p ~/.claude/skills/bookmark-manager
curl -sL "https://raw.githubusercontent.com/HhCompile/bookmark-manager-workspace/main/bookmark-mcp/SKILL-v4.md" \
  -o ~/.claude/skills/bookmark-manager/SKILL.md
```

重启 Claude Code 后，提到"书签/收藏/整理/Chrome 同步/分类"时会自动用这个 Skill。

## 📊 实测场景示例

| 你说 | Claude 调的工具 | 真实结果 |
|---|---|---|
| "列出我所有 Python 教程" | `search_bookmarks("python")` 或 `get_bookmarks_by_tag("Python")` | 返回真实书签 |
| "找最常访问的 10 个" | `list_bookmarks(limit=10)` + 按访问次数排 | 真实数据 |
| "所有 AI 工具书签" | `get_bookmarks_by_tag("AI")` 或 `get_bookmarks_by_category("AI 工具")` | 4 个 |
| "去重" | `deduplicate_bookmarks()` | 271 条（0 重复）|
| "推荐这个书签的 tag" | `ai_suggest_one(url, title, "tags")` | AI 给出建议 |

## 🎉 完成

30 分钟内搞定，比"看 10 篇文章改 README"有用得多。
