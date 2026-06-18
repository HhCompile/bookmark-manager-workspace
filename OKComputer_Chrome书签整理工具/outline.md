# Chrome书签整理工具 - 项目大纲

## 文件结构
```
/mnt/okcomputer/output/
├── index.html              # 主页面 - 文件上传和分类
├── results.html            # 结果展示页面
├── main.js                 # 主要JavaScript逻辑
├── resources/              # 资源文件夹
│   ├── hero-bg.jpg        # Hero背景图片
│   └── icons/             # 图标文件
└── README.md              # 项目说明
```

## 页面功能分配

### index.html - 主页面
**功能模块：**
- 导航栏：简洁的导航，包含Logo和功能说明
- Hero区域：动态背景效果，标题和上传区域
- 上传功能：拖拽文件上传，支持Chrome书签HTML文件
- 分类处理：实时显示处理进度和状态
- 预览区域：显示书签统计信息和分类预览

**交互组件：**
- 文件拖拽上传器
- 进度指示器
- 分类设置面板
- 快速预览卡片

### results.html - 结果展示页面
**功能模块：**
- 分类结果展示：按类别显示书签
- 编辑功能：重分类、删除、重命名
- 统计图表：书签分布可视化
- 导出功能：多种格式下载

**交互组件：**
- 分类标签页
- 书签卡片网格
- 搜索和筛选
- 导出选项面板

### main.js - 核心逻辑
**主要功能：**
- 文件解析：解析Chrome书签HTML格式
- 智能分类：基于URL、标题、关键词的分类算法
- 数据处理：书签数据结构化和统计
- 可视化：图表生成和动画效果
- 导出功能：生成各种格式的输出文件

## 技术实现

### 前端技术栈
- HTML5 + CSS3 (Tailwind CSS)
- JavaScript ES6+
- 动画库：Anime.js
- 图表库：ECharts.js
- 轮播库：Splide.js
- 物理效果：Matter.js
- 着色器效果：Shader-park

### 核心算法
- HTML解析：DOMParser API
- 分类算法：基于规则的分类 + 关键词匹配
- 数据统计：JavaScript数据处理
- 文件生成：Blob API + FileSaver

### 设计特色
- 现代极简设计风格
- 响应式布局
- 流畅的动画过渡
- 直观的用户界面
- 专业的视觉效果