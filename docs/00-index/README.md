# Bookmark Manager 文档中心

> 项目文档的统一入口和导航页面

## 📚 文档结构

```
docs/
├── 00-index/              # 本文档 - 导航中心
├── 01-guides/             # 使用指南
├── 02-data-cleaning/      # 数据清理专题
├── 03-api/                # API 相关文档
├── 04-architecture/       # 架构设计
├── 05-conventions/        # 命名规范和约定
└── 99-agents/             # AI 代理指南
```

## 🚀 快速开始

| 文档 | 说明 | 目标读者 |
|------|------|----------|
| [快速开始](./01-guides/quick-start.md) | 项目安装和启动 | 新用户 |
| [书签组织指南](./01-guides/bookmark-organization-guide.md) | 如何组织和管理书签 | 用户 |
| [数据清理快速开始](./02-data-cleaning/quick-start.md) | 数据清理功能使用 | 用户 |

## 📊 按主题浏览

### 1️⃣ 使用指南 (01-guides)
面向用户的操作手册：
- [快速开始](./01-guides/quick-start.md) - 5 分钟上手
- [书签组织指南](./01-guides/bookmark-organization-guide.md) - 最佳实践

### 2️⃣ 数据清理 (02-data-cleaning)
数据清理功能的完整文档：
- [PRD - 产品需求文档](./02-data-cleaning/PRD.md)
- [Pipeline - 管道架构](./02-data-cleaning/pipeline.md)
- [Flow - 处理流程](./02-data-cleaning/flow.md)
- [Quick Start - 快速开始](./02-data-cleaning/quick-start.md)

### 3️⃣ API 文档 (03-api)
前后端接口相关：
- [集成计划](./03-api/integration-plan.md)
- [API 对齐](./03-api/alignment.md)

### 4️⃣ 架构设计 (04-architecture)
系统架构和设计文档：
- [数据架构设计](./04-architecture/data-schema.md)
- [MVP 完成报告](./04-architecture/mvp-completion-report.md)

### 5️⃣ 命名规范 (05-conventions)
开发规范和约定：
- [命名规范](./05-conventions/naming-conventions.md)
- [别名命名指南](./05-conventions/alias-naming-guide.md)

### 9️⃣ AI 代理指南 (99-agents)
AI 开发助手参考：
- [根目录 AGENTS.md](/AGENTS.md) - 项目级 AI 指南
- [后端 AGENTS.md](/bookmark-manager-admin/AGENTS.md) - Flask 后端指南
- [前端 AGENTS.md](/bookmark-manager-web/AGENTS.md) - React 前端指南

## 🏗️ 项目模块

| 模块 | 技术栈 | 文档入口 |
|------|--------|----------|
| bookmark-manager-web | React + TypeScript + Vite | [README](/bookmark-manager-web/README.md) |
| bookmark-manager-admin | Flask + Python | [README](/bookmark-manager-admin/README.md) |
| ui-design-agent | 设计系统 | [README](/ui-design-agent/README.md) |

## 📝 文档维护

### 命名规范
- 文件名使用小写字母和连字符（kebab-case）
- 大写缩写保持大写（如 PRD, API, MVP）
- 目录编号表示优先级/顺序

### 添加新文档
1. 确定文档类型，放入对应分类目录
2. 更新本文档的导航链接
3. 保持一致的 Markdown 格式

---

*最后更新: 2026-04-06*
