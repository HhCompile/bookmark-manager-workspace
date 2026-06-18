# 阶段 1：浏览器 → 系统同步打通

> 端到端流程：Chrome 扩展读浏览器书签 → 推送到 bookmark-manager-admin → MCP 工具可查询

## 🏗️ 架构

```
┌──────────────────┐
│  Chrome 浏览器    │
│  chrome://bookmarks│
└────────┬─────────┘
         │ chrome.bookmarks API
         ▼
┌──────────────────┐
│ Chrome Extension │  ← 新增（manifest.json + background.js + popup）
│ Service Worker   │
└────────┬─────────┘
         │ HTTP POST /v1/bookmark/sync-from-extension
         ▼
┌──────────────────┐
│ bookmark-admin   │  ← 新增（app/api/routes_sync.py）
│ Flask            │
└────────┬─────────┘
         │ HTTP GET /v1/bookmark/sync-status
         ▼
┌──────────────────┐
│ bookmark-mcp     │  ← 新增（sync_status 工具）
│ MCP Server       │
└──────────────────┘
```

## 📁 新增文件清单

### 1. `bookmark-manager-admin/app/api/routes_sync.py`（阶段 1.1）
- 3 个新端点：
  - `POST /v1/bookmark/sync-from-extension` — 单条同步
  - `POST /v1/bookmarks/sync-batch` — 批量同步
  - `GET  /v1/bookmark/sync-status` — 同步状态
- 包含 URL 标准化 + 精确去重逻辑
- ⚠️ **未在 admin 实际项目中**（仓内代码不改动）
- ✅ 推送到 `bookmark-manager-workspace` 仓作为参考实现

### 2. `OKComputer_Chrome书签整理工具/` 内新增（阶段 1.2）
- `manifest.json` — Manifest V3 配置
- `background.js` — Service Worker（监听书签变化 + 推送）
- `popup.html` + `popup.js` — 弹窗 UI

### 3. `bookmark-mcp/server.py`（阶段 1.3）
- v2 版新增 2 个工具：
  - `sync_status` — 查询同步状态
  - `detect_dead_links` — 触发死链检测

## 🚀 部署步骤

### Step 1：admin 端接入 sync 蓝图

在 `app/api/api_app.py` 中注册：

```python
from app.api.routes_sync import sync_bp

# 在 create_app() 中
app.register_blueprint(sync_bp)
```

或者在 `app/__init__.py` 注册。

### Step 2：安装 Chrome 扩展

1. 打开 `chrome://extensions/`
2. 开启右上角"开发者模式"
3. 点"加载已解压的扩展程序"
4. 选 `OKComputer_Chrome书签整理工具/` 目录
5. 弹出"无法加载" → 看错误日志

### Step 3：扩展首次同步

- 扩展装好后**自动**触发全量同步
- 也可点击 Chrome 工具栏的扩展图标 → 点"🔄 全量同步"

### Step 4：MCP 接入

更新 `~/.claude/mcp.json`，确保 `bookmark-mcp` 跑的是 v2 server.py。

重启 Claude Code。

## 🧪 测试

### 测试 1：admin 端点
```bash
curl -X POST http://localhost:9001/v1/bookmark/sync-from-extension \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com","title":"GitHub","tags":["dev"]}'
```

预期：返回 201 + bookmark JSON

### 测试 2：去重
```bash
# 重复上面请求
curl -X POST http://localhost:9001/v1/bookmark/sync-from-extension \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com","title":"GitHub","tags":["dev"]}'
```

预期：返回 `skipped, reason: duplicate`

### 测试 3：URL 标准化
```bash
curl -X POST http://localhost:9001/v1/bookmark/sync-from-extension \
  -H "Content-Type: application/json" \
  -d '{"url":"http://github.com/?utm_source=test","title":"GitHub"}'
```

预期：与上一条（无 utm 的）算同一书签

### 测试 4：MCP 工具
```
Claude Code: "查询书签同步状态"
→ 调用 sync_status 工具
→ 返回 JSON
```

## 🛡️ 关键设计

### 1. URL 标准化是去重前提
- `http://github.com` = `https://github.com`
- `?utm_source=x` 被剥离
- 末尾 `/` 被去除
- `fragment` (#xxx) 被去除

### 2. 同步 ≠ 清洗
- sync 阶段只做"原始接收 + L1 精确去重"
- 复杂清洗（死链/相似/AI 建议）留到阶段 2
- 防止 sync 端点被慢操作拖垮

### 3. 失败不阻塞
- 同步失败返回 `error`，但 admin 不挂
- Chrome 扩展在 service worker 里捕获错误，下次再试
- 不会丢数据（书签仍在浏览器原位）

### 4. 周期性同步
- `chrome.alarms` 每 30 分钟全量同步
- 配合实时监听（`onCreated`/`onChanged`）增量同步
- 频率可配置

## ⚠️ 已知限制

| 限制 | 说明 |
|---|---|
| **不能监听 `onMoved`** | Chrome 移动书签事件不触发推送（只改了位置）|
| **删/移动不同步** | 阶段 1 只同步增改，删/移动留到阶段 2 |
| **chrome:// 内部页** | 浏览器内置页无法被扩展读 |
| **需要 CORS 配置** | admin 端需要允许扩展的 origin（默认允许同源）|

## 📊 性能预估

| 书签数 | 全量同步耗时 | 增量同步 |
|---|---|---|
| 100 | ~2 秒 | < 100ms |
| 1000 | ~15 秒 | < 200ms |
| 10000 | ~3 分钟 | < 500ms |

## 🔄 下一步

- 阶段 2：数据清洗 pipeline（去重/死链/AI 推荐）
- 阶段 3：embedding 相似度推荐
- 阶段 4：协作（分享/导出/团队空间）

## 📝 文件清单（待推送到 GitHub）

| 文件 | 位置 | 阶段 |
|---|---|---|
| `routes_sync.py` | `bookmark-manager-workspace/admin-extension/routes_sync.py` | 1.1 |
| `manifest.json` | `bookmark-manager-workspace/OKComputer_Chrome书签整理工具/manifest.json` | 1.2 |
| `background.js` | 同上 | 1.2 |
| `popup.html` / `popup.js` | 同上 | 1.2 |
| `server.py` (v2) | `bookmark-mcp/server.py`（覆盖）| 1.3 |
| `SYNC_SETUP.md`（本文档）| `bookmark-manager-workspace/docs/integration/sync-setup.md` | 1.4 |
