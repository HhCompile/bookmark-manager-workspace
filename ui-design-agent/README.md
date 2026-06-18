# UI Design Agent - 智能 UI 设计助手

专业的 AI 驱动 UI 设计 Agent，用于辅助前端开发、组件生成和页面调整。

## 功能特性

### 1. 智能 UI 分析
- 分析现有 React/Tailwind 组件结构
- 提取设计 tokens（颜色、间距、字体）
- 识别组件模式和可复用性

### 2. 组件生成
- 根据自然语言描述生成组件
- 支持 Tailwind CSS v4
- 生成类型安全的 TypeScript 代码
- 自动添加无障碍属性

### 3. 样式调整
- 实时修改颜色、间距、布局
- 一键切换主题（亮色/暗色）
- 响应式断点优化

### 4. 设计系统管理
- 集中管理设计 tokens
- 组件变体统一管理
- 样式一致性检查

## 架构

```
ui-design-agent/
├── src/
│   ├── server/           # MCP 服务器
│   │   └── mcp_server.py
│   ├── tools/            # Agent 工具
│   │   ├── ui_analyzer.py
│   │   ├── component_generator.py
│   │   ├── style_modifier.py
│   │   └── design_system_manager.py
│   └── prompts/          # LLM Prompts
│       └── ui_design_prompts.py
├── frontend/             # 前端界面
│   └── agent-panel.tsx
├── config/
│   └── design_tokens.json
└── docs/
    └── API.md
```

## 快速开始

### 安装依赖
```bash
cd ui-design-agent
pip install -r requirements.txt
```

### 启动 MCP 服务器
```bash
python src/server/mcp_server.py
```

### 集成到书签管理器
在书签管理器前端添加 Agent 面板组件。

## 使用方法

### 1. 分析现有组件
```
/agent 分析组件 FeaturesSection.tsx
```

### 2. 生成新组件
```
/agent 创建一个带搜索和过滤的书签列表组件
```

### 3. 修改样式
```
/agent 把卡片改成玻璃拟态风格
```

### 4. 管理设计系统
```
/agent 添加新的主色调 #3B82F6
```

## 技术栈

- **后端**: Python + MCP (Model Context Protocol)
- **前端**: React + TypeScript + Tailwind CSS
- **AI**: Claude / OpenAI GPT-4
- **解析**: AST 分析、正则匹配

## License

MIT
