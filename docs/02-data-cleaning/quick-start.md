# 数据清洗功能快速参考指南

> 用于快速查阅核心信息，详细内容请参考 PRD 文档

---

## 📋 核心信息速查

### 清洗程度定义

| 级别 | 自动/手动 | 核心功能 | 数据留存率 |
|------|-----------|----------|------------|
| **L1 精确清洗** | ✅ 自动 | URL去重、标准化、标题清洗 | 90-95% |
| **L2 质量清洗** | ⚡ 半自动 | 相似合并、失效检测、分类标准化 | 80-90% |
| **L3 智能优化** | 💡 推荐 | AI分类、标签建议、别名生成 | 100% |

### 关键接口

```
POST   /v1/bookmarks/clean/upload      # 上传并启动清洗
WS     /ws/clean/:task_id              # 实时进度推送
GET    /v1/bookmarks/clean/:task_id/report   # 获取清洗报告
POST   /v1/bookmarks/clean/:task_id/import   # 确认导入
```

---

## 🔄 完整流程（8步）

```
用户上传 HTML
    ↓
后端解析 HTML → 提取书签数据
    ↓
预处理 → URL标准化、标题清洗
    ↓
精确去重（自动）→ 标记完全重复的URL
    ↓
相似检测（需确认）→ 标题相似度>85%的组
    ↓
URL检查（可选）→ 检测失效链接
    ↓
智能分析 → 推荐分类、标签、别名
    ↓
生成报告 → 用户确认 → 导入系统
```

---

## 📦 数据结构流转

```
原始HTML
    ↓ 解析
原始数据 [{title, url, add_date, folder_path}]
    ↓ 预处理
标准数据 [{title, url, domain, added_date}]
    ↓ 清洗
清洗数据 [+duplicate_group, +url_status, +normalized_category]
    ↓ 分析
分析数据 [+suggested_category, +suggested_tags, +confidence]
    ↓ 报告
报告数据 {summary, duplicates, suggestions, bookmarks}
    ↓ 导入
最终书签 → 存储系统
```

---

## 🛠️ 后端实现清单

### 新增文件

```
app/
├── services/
│   └── data_cleaning_service.py      # [新建] 清洗管道核心
├── api/
│   └── clean_api.py                  # [新建] 清洗相关接口
│       ├── upload()                  # 上传文件
│       ├── get_report()              # 获取报告
│       └── import_bookmarks()        # 导入书签
└── utils/
    ├── cleaning/
    │   ├── __init__.py
    │   ├── parser.py                 # HTML解析增强
    │   ├── normalizer.py             # URL/标题标准化
    │   ├── deduplicator.py           # 去重算法
    │   ├── validator.py              # URL验证
    │   └── analyzer.py               # 智能分析
    └── websocket.py                  # WebSocket管理
```

### 核心类设计

```python
# DataCleaningPipeline 主类
class DataCleaningPipeline:
    def __init__(self):
        self.parser = BookmarkParser()
        self.normalizer = DataNormalizer()
        self.deduplicator = Deduplicator()
        self.validator = URLValidator()
        self.analyzer = BookmarkAnalyzer()
    
    async def process(self, html_file: str, options: dict) -> dict:
        """执行完整清洗流程"""
        # 1. 解析
        raw_bookmarks = self.parser.parse_file(html_file)
        
        # 2. 预处理
        normalized = [self.normalizer.normalize(bm) for bm in raw_bookmarks]
        
        # 3. 精确去重
        unique, exact_dups = self.deduplicator.exact_deduplicate(normalized)
        
        # 4. 相似检测
        similar_groups = self.deduplicator.similar_grouping(unique)
        
        # 5. URL验证（可选）
        if options.get('check_urls'):
            url_status = await self.validator.batch_check([bm['url'] for bm in unique])
        
        # 6. 智能分析
        analyzed = self.analyzer.analyze_bookmarks(unique)
        
        # 7. 生成报告
        return self._build_report(analyzed, exact_dups, similar_groups, url_status)
```

---

## 🎨 前端实现清单

### 新增页面/组件

```
src/
├── pages/
│   └── import/
│       ├── ImportWizard.tsx          # [新建] 导入向导主页面
│       ├── steps/
│       │   ├── UploadStep.tsx        # 步骤1: 上传
│       │   ├── ProcessingStep.tsx    # 步骤2: 处理中
│       │   └── ReportStep.tsx        # 步骤3: 清洗报告
│       └── components/
│           ├── DuplicateGroup.tsx    # 重复项处理组件
│           ├── SuggestionCard.tsx    # 建议卡片组件
│           ├── InvalidUrlList.tsx    # 失效链接列表
│           └── SummaryCards.tsx      # 统计概览卡片
├── hooks/
│   ├── useCleaningProgress.ts        # WebSocket进度hook
│   └── useCleaningReport.ts          # 报告数据hook
└── api/
    └── cleaning.ts                   # 清洗相关API
```

### 关键状态管理

```typescript
// 清洗流程状态
interface CleaningState {
  step: 'upload' | 'processing' | 'report' | 'importing' | 'done';
  taskId: string | null;
  progress: {
    stage: string;
    current: number;
    total: number;
    message: string;
  };
  report: CleaningReport | null;
  decisions: {
    similarGroups: SimilarGroupDecision[];
    invalidUrls: InvalidUrlDecision[];
    suggestions: SuggestionDecision[];
  };
}
```

---

## 🔌 接口详细定义

### 1. 上传并启动清洗

```http
POST /v1/bookmarks/clean/upload
Content-Type: multipart/form-data

请求体:
{
    "file": File,                       // HTML文件
    "options": {
        "auto_dedup": true,             // 自动去重
        "check_urls": true,             // 检查URL
        "similar_threshold": 0.85       // 相似度阈值
    }
}

响应:
{
    "success": true,
    "data": {
        "task_id": "clean_abc123",
        "status": "processing",
        "ws_url": "ws://localhost:9001/ws/clean/clean_abc123"
    }
}
```

### 2. WebSocket 进度推送

```javascript
// 服务端 → 客户端
{
    "type": "progress",
    "stage": "cleaning",        // parsing | cleaning | analyzing | validating
    "current": 50,
    "total": 150,
    "percentage": 33.3,
    "message": "正在分析书签分类..."
}

// 完成推送
{
    "type": "complete",
    "task_id": "clean_abc123",
    "summary": {
        "total": 150,
        "after_cleaning": 138,
        "exact_duplicates": 5,
        "similar_groups": 3,
        "invalid_urls": 2
    }
}
```

### 3. 获取清洗报告

```http
GET /v1/bookmarks/clean/clean_abc123/report

响应:
{
    "success": true,
    "data": {
        "summary": {
            "original_count": 150,
            "after_cleaning": 138,
            "exact_duplicates_removed": 5,
            "similar_groups_pending": 3,
            "invalid_urls_found": 2
        },
        "exact_duplicates": [...],      // 已自动合并的重复项
        "similar_groups": [...],        // 需用户确认的相似组
        "invalid_urls": [...],          // 失效链接列表
        "suggestions": [...],           // 优化建议列表
        "bookmarks": [...]              // 清洗后的完整数据
    }
}
```

### 4. 确认导入

```http
POST /v1/bookmarks/clean/clean_abc123/import

请求体:
{
    "similar_groups_decisions": [
        {
            "group_id": "sim_1",
            "action": "merge",          // merge | keep_all | delete_specific
            "keep_id": "1",
            "delete_ids": ["2"]
        }
    ],
    "invalid_url_decisions": [
        {"bookmark_id": "3", "action": "delete"}
    ],
    "applied_suggestions": [
        {
            "bookmark_id": "4",
            "suggestion_type": "category_change",
            "apply": true
        }
    ],
    "import_settings": {
        "skip_existing": false,
        "update_existing": true
    }
}

响应:
{
    "success": true,
    "data": {
        "imported": 125,
        "updated": 5,
        "skipped": 3,
        "failed": 0
    }
}
```

---

## ⚙️ 配置参数

### 清洗策略配置

```python
CLEANING_CONFIG = {
    # L1: 自动处理
    'auto': {
        'exact_dedup': True,
        'normalize_url': True,
        'clean_title': True,
        'standardize_time': True,
        'category_mapping': True,
    },
    
    # L2: 半自动
    'semi_auto': {
        'similar_dedup': {
            'enabled': True,
            'threshold': 0.85,          # 相似度阈值
            'auto_merge_below': 0.95,   # >95%自动合并
        },
        'url_validation': {
            'enabled': True,
            'timeout': 5,               # 秒
            'max_concurrent': 10,
            'auto_remove_dead': False,  # 不自动删除
        },
    },
    
    # L3: 推荐
    'suggestions': {
        'category': {
            'enabled': True,
            'min_confidence': 0.6,
        },
        'tags': {
            'enabled': True,
            'max_suggestions': 5,
        },
    }
}
```

### 分类映射表

```python
CATEGORY_MAPPING = {
    'tech': '技术',
    'technology': '技术',
    'programming': '编程',
    'frontend': '前端',
    'backend': '后端',
    'temp': None,           # None表示触发自动分类
    '未分类': None,
}
```

---

## 📊 性能指标

| 场景 | 目标 | 说明 |
|------|------|------|
| 100条书签 | < 3秒 | 不含URL检查 |
| 500条书签 | < 10秒 | 不含URL检查 |
| URL检查 | 50条/秒 | 10并发 |
| 内存占用 | < 500MB | 1000条数据 |
| 缓存时间 | 15分钟 | 清洗结果保留 |

---

## ✅ 实施检查清单

### 后端

- [ ] 创建 `DataCleaningPipeline` 主类
- [ ] 实现 HTML 解析增强（保留文件夹结构）
- [ ] 实现 URL 标准化和标题清洗
- [ ] 实现精确去重和相似检测
- [ ] 实现异步 URL 检查（带并发控制）
- [ ] 集成现有的 `BookmarkAnalyzer`
- [ ] 实现 WebSocket 进度推送
- [ ] 实现清洗报告生成
- [ ] 实现确认导入逻辑
- [ ] 添加缓存和临时文件清理

### 前端

- [ ] 创建导入向导页面
- [ ] 实现文件上传和验证
- [ ] 实现清洗选项配置
- [ ] 实现 WebSocket 进度接收和展示
- [ ] 创建清洗报告页面
- [ ] 实现重复项处理组件
- [ ] 实现失效链接处理组件
- [ ] 实现优化建议列表
- [ ] 实现导入确认和结果展示

---

## 🚨 常见问题处理

| 问题 | 解决方案 |
|------|----------|
| URL 检查太慢 | 限制并发10个，超时5秒 |
| 内存占用过高 | 分批处理，每批50条 |
| 相似度计算慢 | 只对同域名或同分类的计算 |
| 大文件上传失败 | 限制10MB，前端预检查 |
| 清洗结果过期 | 15分钟后清理，提示重新上传 |

---

## 🔗 相关文档

- `DATA_CLEANING_PRD.md` - 完整产品需求文档
- `DATA_CLEANING_FLOW.md` - 详细流程图（Mermaid）
- `API_INTEGRATION_PLAN.md` - API 对接方案

---

*最后更新: 2026-04-01*
