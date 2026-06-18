# 📦 Bookmark Manager Workspace

> 产品级 monorepo 工作区，围绕"浏览器书签管理"产品的所有资产：前端 / 后端 / Chrome 扩展 / 设计 / 文档 / AI 协作配置

## 🎯 这是什么

**这不是单一项目，而是一个完整的产品工作区**。日常开发中关于"书签管理"这个产品主题的所有资产（代码 + 设计 + 文档 + 启动脚本 + AI 协作配置）都在这个工作区里管理。

> 💡 简单类比：这是产品的"项目管理根目录"，不是单一代码仓。

## 🏗️ 组件清单

| 组件 | 仓库 | 简介 |
| --- | --- | --- |
| 🌐 **前端 Web** | [HhCompile/bookmark-manager-web](https://github.com/HhCompile/bookmark-manager-web) | React 18 + Vite 6 + Tailwind 4 + TypeScript |
| ⚙️ **后端 API** | [HhCompile/bookmark-manager-admin](https://github.com/HhCompile/bookmark-manager-admin) | Flask 2.3 + Python + REST API |
| 🧩 **Chrome 扩展** | `OKComputer_Chrome书签整理工具/` | 浏览器书签同步（Manifest V3）|
| 🎨 **UI 设计资源** | `UI/` | 产品设计截图、Figma 资源 |
| 🤖 **AI 协作配置** | `.claude/` `.kimi/` `.reasonix/` | 多 AI 工具配置（Claude / Kimi / Reasonix）|
| 📚 **完整文档体系** | `docs/00-99` 7 个子目录 | 索引 / 指南 / 数据清洗 / API / 架构 / 规范 / agents |

## 🤖 AI 协作特色

- 📄 **工作区级 AGENTS.md**（744 行）— 任何 AI agent 进入工作区必读
- 📁 **多 AI 工具配置**：Claude（`.claude/`）、Kimi（`.kimi/`）、Reasonix（`.reasonix/`）
- 📚 **`docs/99-agents/`** 专门给 agent 看的文档
- 🔍 **`.codegraph/`** 代码图谱索引（加速 AI 理解代码）
- 🤖 **`ui-design-agent/`** 第三方 MCP UI 设计 agent（声明引用，不含源码）

## 🚀 一键启动

```bash
# macOS / Linux
./start.sh

# Windows
start.bat

# Python 跨平台
python3 start.py
```

启动后会同时拉起：
- 后端 API（Flask，9001 端口）
- 前端 Web（Vite，3000 端口）

## 📚 文档体系结构

```
docs/
├── 00-index/          # 导航 + 总览（从这里开始）
├── 01-guides/         # 快速上手指南
├── 02-data-cleaning/  # 数据清洗 pipeline / PRD / flow
├── 03-api/            # API 对接 + 集成方案
├── 04-architecture/   # 架构设计 + 数据 schema
├── 05-conventions/    # 命名规范 / 别名约定
└── 99-agents/         # 专门给 AI agent 的文档
```

## ✨ 核心能力

- 🔄 **浏览器书签同步**（Chrome 扩展）
- 🤖 **AI 智能整理**（自动分类 / Tag 建议 / 死链检测）
- 📊 **数据可视化**（健康度 / 活跃度分析）
- 🔐 **私密保险箱**（加密书签）
- 📖 **阅读模式**（书签文章转阅读视图）
- 🛠️ **批量任务管理**

## 🛠️ 技术栈总览

| 层 | 技术 |
|---|---|
| **前端** | React 18 · TypeScript · Vite 6 · Tailwind 4 · Radix UI · shadcn/ui 模式 · Motion |
| **后端** | Flask 2.3 · flask-cors · flask-limiter · BeautifulSoup · lxml |
| **浏览器** | Chrome Extension (Manifest V3) |
| **AI 工具** | Claude · Kimi · Reasonix · MCP · FastAPI |
| **测试** | Jest（前端）· pytest（后端）|
| **协作** | pnpm workspace · 多 AI agent · 代码图谱 |

## 📝 License

MIT

## 🔗 相关链接

- 📄 [AGENTS.md](./AGENTS.md) — 工作区级 AI 协作指南（744 行）
- 📚 [docs/00-index/README.md](./docs/00-index/README.md) — 文档入口
- 🚀 [start.py](./start.py) — 一键启动脚本（Python 跨平台）
