# 书签数据清洗管道方案

> 针对 100+ 条书签的批量导入清洗流程

---

## 1. 整体流程

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. 解析     │ →  │  2. 预处理   │ →  │  3. 清洗     │ →  │  4. 分析     │
│  Parse       │    │  Pre-process │    │  Clean       │    │  Analyze     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                  ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  8. 导入     │ ←  │  7. 审核     │ ←  │  6. 建议     │ ←  │  5. 质量检查 │
│  Import      │    │  Review      │    │  Suggest     │    │  Quality     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

---

## 2. 各阶段详解

### 阶段 1：解析（Parse）

**现有能力**：`bookmark_parser.py` 已可完成

```python
# 输入：Chrome/Firefox 导出的 bookmarks.html
# 输出：结构化 JSON
[
  {
    "title": "GitHub - xxx",
    "url": "https://github.com/xxx",
    "date": "2026-04-01T10:00:00+00:00",
    "tags": ["开发工具", "GitHub"],      # 来自文件夹路径
    "group": "开发工具",                  # 直接父文件夹
    "alias": "",
    "description": ""
  }
]
```

**关键改进建议**：
1. **保留原始文件夹结构** → 作为后续分类的参考
2. **提取添加时间** → 用于趋势分析
3. **记录解析日志** → 方便排查解析失败的书签

---

### 阶段 2：预处理（Pre-process）

**目标**：标准化原始数据，准备清洗

#### 2.1 URL 标准化
```python
def normalize_url(url: str) -> str:
    """URL 标准化处理"""
    # 1. 移除跟踪参数
    tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 
                       'fbclid', 'gclid', 'ref']
    
    # 2. 统一协议（https 优先）
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    
    # 3. 移除尾部斜杠
    url = url.rstrip('/')
    
    # 4. 统一小写域名
    parsed = urlparse(url)
    normalized = parsed._replace(
        netloc=parsed.netloc.lower(),
        # 移除跟踪参数
        query='&'.join(p for p in parsed.query.split('&') 
                      if not any(t in p for t in tracking_params))
    )
    
    return urlunparse(normalized)
```

#### 2.2 标题清洗
```python
def clean_title(title: str) -> str:
    """标题清洗"""
    # 1. 移除常见的垃圾前缀
    garbage_prefixes = [
        r'^\d+\.\s*',           # "1. " "2. "
        r'^【.*?】',            # 【紧急】
        r'^\[.*?\]',           # [置顶]
        r'^\(.*?\)',           # (推荐)
    ]
    
    for pattern in garbage_prefixes:
        title = re.sub(pattern, '', title)
    
    # 2. 统一空格
    title = re.sub(r'\s+', ' ', title).strip()
    
    # 3. 截断超长标题
    if len(title) > 200:
        title = title[:197] + '...'
    
    return title
```

#### 2.3 提取元数据
```python
def extract_metadata(bookmark: dict) -> dict:
    """从 URL 和标题中提取元数据"""
    url = bookmark['url']
    title = bookmark['title']
    
    metadata = {
        'domain': extract_domain(url),           # github.com
        'path_parts': extract_path_parts(url),   # ['user', 'repo']
        'has_chinese': has_chinese(title),       # 是否中文内容
        'is_github': 'github.com' in url,
        'is_docs': any(kw in url for kw in ['docs', 'documentation']),
        'is_blog': any(kw in url for kw in ['blog', 'posts']),
    }
    
    return metadata
```

---

### 阶段 3：清洗（Clean）

这是核心阶段，解决数据质量问题。

#### 3.1 去重策略

**层级 1：精确去重（自动）**
```python
def exact_deduplicate(bookmarks: list) -> tuple:
    """基于 URL 精确去重"""
    seen_urls = set()
    unique = []
    duplicates = []
    
    for bm in bookmarks:
        normalized_url = normalize_url(bm['url'])
        if normalized_url in seen_urls:
            duplicates.append(bm)
        else:
            seen_urls.add(normalized_url)
            unique.append(bm)
    
    return unique, duplicates
```

**层级 2：相似去重（需确认）**
```python
from difflib import SequenceMatcher

def similarity_deduplicate(bookmarks: list, threshold=0.85) -> list:
    """基于标题相似度的去重"""
    groups = []
    
    for bm in bookmarks:
        found = False
        for group in groups:
            # 与组内第一个比较相似度
            sim = SequenceMatcher(None, bm['title'], group[0]['title']).ratio()
            if sim > threshold:
                group.append(bm)
                found = True
                break
        
        if not found:
            groups.append([bm])
    
    # 返回：单条组（唯一）vs 多条组（相似待确认）
    unique = [g[0] for g in groups if len(g) == 1]
    similar_groups = [g for g in groups if len(g) > 1]
    
    return unique, similar_groups
```

**层级 3：语义去重（高级）**
```python
def semantic_deduplicate(bookmarks: list) -> list:
    """
    基于内容的语义去重
    例如：
    - "React 官方文档" vs "React Documentation"
    - "GitHub - facebook/react" vs "facebook/react: A declarative..."
    """
    # 简化实现：提取核心关键词匹配
    def extract_keywords(title: str) -> set:
        # 移除停用词
        stop_words = {'的', '了', '和', '是', '在', '有', '我', 'the', 'a', 'an'}
        words = re.findall(r'[\w\u4e00-\u9fa5]+', title.lower())
        return set(w for w in words if w not in stop_words)
    
    # 分组逻辑类似相似去重，但比较关键词重叠度
    # ...
```

#### 3.2 无效链接检测

```python
import asyncio
import aiohttp

async def validate_urls(bookmarks: list, max_concurrent=10) -> dict:
    """
    批量验证 URL 可访问性
    注意：仅检查状态，不实际请求内容（避免耗时）
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def check_one(bookmark):
        async with semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.head(
                        bookmark['url'], 
                        timeout=5,
                        allow_redirects=True
                    ) as resp:
                        return {
                            'url': bookmark['url'],
                            'status': resp.status,
                            'valid': 200 <= resp.status < 400,
                            'redirect': resp.history
                        }
            except Exception as e:
                return {
                    'url': bookmark['url'],
                    'status': 0,
                    'valid': False,
                    'error': str(e)
                }
    
    tasks = [check_one(bm) for bm in bookmarks]
    results = await asyncio.gather(*tasks)
    
    return {
        'valid': [r for r in results if r['valid']],
        'invalid': [r for r in results if not r['valid']],
        'total': len(results)
    }
```

**URL 健康分级**：
- 🟢 健康：200 OK
- 🟡 警告：301/302 重定向（建议更新 URL）
- 🔴 失效：4xx/5xx/超时
- ⚪ 未知：无法验证（内网链接、特殊协议）

#### 3.3 分类标准化

**问题**：用户原始的文件夹结构可能混乱
```
原始结构：
├── 技术/          → 保留
├── tech/          → 合并到"技术"
├── 开发工具/      → 保留
├── tools/         → 合并到"开发工具"
├── 未分类/        → 需要重新分类
├── 临时/          → 需要重新分类
└── New Folder/    → 需要重新分类
```

**标准化策略**：
```python
CATEGORY_MAPPING = {
    # 同义词合并
    'tech': '技术',
    'technology': '技术',
    '编程': '技术',
    
    # 子类合并
    '前端': '开发',
    '后端': '开发',
    '移动端': '开发',
    'dev': '开发',
    
    # 废弃分类重新分配
    '未分类': None,      # 触发自动分类
    '临时': None,
    'New Folder': None,
}

def standardize_category(category: str) -> str:
    """标准化分类名称"""
    if not category:
        return None
    
    category = category.strip()
    return CATEGORY_MAPPING.get(category.lower(), category)
```

---

### 阶段 4：分析（Analyze）

使用现有的 `bookmark_analyzer.py` 能力，但增强处理。

#### 4.1 批量分析优化

```python
def batch_analyze(bookmarks: list, batch_size=20) -> list:
    """
    分批分析，避免内存占用过高
    同时支持进度回调
    """
    results = []
    total = len(bookmarks)
    
    for i in range(0, total, batch_size):
        batch = bookmarks[i:i+batch_size]
        
        # 调用现有分析器
        batch_results = analyzer.analyze_bookmarks(batch)
        results.extend(batch_results)
        
        # 进度回调
        progress = (i + len(batch)) / total * 100
        print(f"分析进度: {progress:.1f}%")
    
    return results
```

#### 4.2 分析结果整合

```python
def merge_analysis(bookmark: dict, analysis: dict) -> dict:
    """将分析结果合并到书签数据"""
    return {
        **bookmark,
        'suggested_category': analysis['category_suggestions'][0],
        'suggested_tags': analysis['category_suggestions'],  # 分类作为标签
        'suggested_alias': analysis['alias_suggestions'][0],
        'confidence': calculate_confidence(analysis),  # 置信度分数
    }

def calculate_confidence(analysis: dict) -> float:
    """计算分类建议的置信度"""
    # 基于关键词匹配数量、标题清晰度等因素
    score = 0.5  # 基础分
    
    # 有明确分类建议加分
    if analysis['category_suggestions']:
        score += 0.3
    
    # 有别名建议加分
    if analysis['alias_suggestions']:
        score += 0.2
    
    return min(score, 1.0)
```

---

### 阶段 5：质量检查（Quality Check）

```python
def quality_check(bookmarks: list) -> dict:
    """
    生成数据质量报告
    """
    report = {
        'total': len(bookmarks),
        'categories': {},
        'issues': {
            'no_title': [],
            'no_url': [],
            'short_title': [],  # 标题过短可能无意义
            'suspicious_url': [],  # 可疑链接
        },
        'stats': {
            'avg_title_length': 0,
            'domain_distribution': {},
        }
    }
    
    title_lengths = []
    
    for bm in bookmarks:
        # 检查问题
        if not bm.get('title'):
            report['issues']['no_title'].append(bm)
        elif len(bm['title']) < 5:
            report['issues']['short_title'].append(bm)
        
        if not bm.get('url'):
            report['issues']['no_url'].append(bm)
        
        # 统计
        title_lengths.append(len(bm.get('title', '')))
        
        domain = extract_domain(bm.get('url', ''))
        report['stats']['domain_distribution'][domain] = \
            report['stats']['domain_distribution'].get(domain, 0) + 1
    
    if title_lengths:
        report['stats']['avg_title_length'] = sum(title_lengths) / len(title_lengths)
    
    return report
```

---

### 阶段 6：建议生成（Suggest）

基于分析结果，为用户提供批量操作建议。

```python
def generate_suggestions(bookmarks: list) -> list:
    """
    生成清洗建议列表
    """
    suggestions = []
    
    for bm in bookmarks:
        item_suggestions = []
        
        # 分类冲突建议
        if bm.get('original_category') != bm.get('suggested_category'):
            item_suggestions.append({
                'type': 'category_change',
                'field': 'category',
                'from': bm['original_category'],
                'to': bm['suggested_category'],
                'reason': f"基于内容分析，建议从'{bm['original_category']}'改为'{bm['suggested_category']}'",
                'confidence': bm['confidence']
            })
        
        # 标签补充建议
        if bm.get('suggested_tags'):
            current_tags = set(bm.get('tags', []))
            suggested_tags = set(bm['suggested_tags'])
            missing = suggested_tags - current_tags
            
            if missing:
                item_suggestions.append({
                    'type': 'tag_add',
                    'field': 'tags',
                    'add': list(missing),
                    'reason': f"建议添加标签: {', '.join(missing)}"
                })
        
        # 别名建议
        if bm.get('suggested_alias') and not bm.get('alias'):
            item_suggestions.append({
                'type': 'alias_add',
                'field': 'alias',
                'value': bm['suggested_alias'],
                'reason': f"建议添加别名便于搜索"
            })
        
        if item_suggestions:
            suggestions.append({
                'bookmark': bm,
                'suggestions': item_suggestions
            })
    
    return suggestions
```

---

### 阶段 7：审核（Review）

**UI 呈现形式建议**：

```
┌─────────────────────────────────────────────────────────────┐
│ 数据清洗报告 - 共 128 条书签                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📊 统计概览                                                  │
│ ├── ✅ 精确重复: 12 条已自动合并                             │
│ ├── ⚠️  相似标题: 8 组需要确认 (16 条)                       │
│ ├── 🔴 失效链接: 5 条建议删除                                │
│ └── 🟡 建议修改: 45 条分类/标签可优化                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🔍 相似标题组 (需要确认)                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 组 1: "React 官方文档" vs "React Documentation"          │ │
│ │   [保留第一个]  [合并]  [都保留]  [忽略]                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 组 2: "GitHub - facebook/react" vs "facebook/react"      │ │
│ │   [保留第一个]  [合并]  [都保留]  [忽略]                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📝 建议修改 (按置信度排序)                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [高置信度] React 教程                                      │ │
│ │   分类: 未分类 → 前端开发 ✓                               │ │
│ │   标签: +React, +教程                                     │ │
│ │   [应用]  [忽略]  [编辑]                                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [中置信度] 某某博客                                        │ │
│ │   分类: 临时 → 技术博客 ?                                 │ │
│ │   [应用]  [忽略]  [编辑]                                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [全部应用]  [全部忽略]  [逐个确认]  [导出报告]                │
└─────────────────────────────────────────────────────────────┘
```

---

### 阶段 8：导入（Import）

```python
def import_bookmarks(bookmarks: list, options: dict) -> dict:
    """
    将清洗后的书签导入系统
    """
    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }
    
    for bm in bookmarks:
        try:
            # 检查是否已存在
            if manager.has_bookmark(bm['url']):
                if options.get('skip_existing'):
                    results['skipped'].append(bm)
                    continue
                elif options.get('update_existing'):
                    # 更新现有书签
                    manager.update_bookmark(bm['url'], bm)
                    results['success'].append({**bm, 'action': 'updated'})
                    continue
            
            # 创建新书签
            bookmark_obj = Bookmark(
                url=bm['url'],
                title=bm['title'],
                tags=bm.get('tags', []),
                category=bm.get('category')
            )
            
            manager.add_bookmark(bookmark_obj)
            results['success'].append({**bm, 'action': 'created'})
            
        except Exception as e:
            results['failed'].append({**bm, 'error': str(e)})
    
    # 保存到存储
    storage.save_bookmarks(manager.get_bookmarks())
    
    return results
```

---

## 3. 实现架构

### 3.1 后端服务扩展

```python
# app/services/data_cleaning_service.py

class DataCleaningPipeline:
    """数据清洗管道"""
    
    def __init__(self):
        self.parser = BookmarkParser()
        self.analyzer = BookmarkAnalyzer()
        self.classifier = Classifier()
    
    async def process(self, html_file: str, options: dict) -> dict:
        """
        执行完整清洗流程
        
        Args:
            html_file: 上传的 HTML 文件路径
            options: 清洗选项
                - auto_deduplicate: 是否自动精确去重
                - check_urls: 是否检查链接有效性
                - auto_classify: 是否自动分类
                
        Returns:
            清洗结果报告
        """
        # 阶段 1: 解析
        raw_bookmarks = self.parser.parse_file(html_file)
        
        # 阶段 2: 预处理
        normalized = [self._preprocess(bm) for bm in raw_bookmarks]
        
        # 阶段 3: 清洗
        if options.get('auto_deduplicate'):
            normalized, duplicates = exact_deduplicate(normalized)
        
        if options.get('check_urls'):
            url_status = await validate_urls(normalized)
        
        # 阶段 4: 分析
        analyzed = self.analyzer.analyze_bookmarks(normalized)
        
        # 阶段 5: 质量检查
        quality_report = quality_check(normalized)
        
        return {
            'total': len(raw_bookmarks),
            'after_cleaning': len(normalized),
            'duplicates_removed': len(duplicates) if options.get('auto_deduplicate') else 0,
            'invalid_urls': len(url_status['invalid']) if options.get('check_urls') else 0,
            'suggestions': generate_suggestions(analyzed),
            'quality': quality_report,
            'bookmarks': analyzed  # 带建议的书签数据
        }
```

### 3.2 API 接口

```python
# 新增接口
@app.route(f'{API_PREFIX}/bookmarks/clean', methods=['POST'])
def clean_bookmarks():
    """
    数据清洗接口
    
    流程：
    1. 上传 HTML 文件
    2. 异步执行清洗流程
    3. 返回清洗报告（不直接导入）
    """
    pass

@app.route(f'{API_PREFIX}/bookmarks/clean/<task_id>', methods=['GET'])
def get_cleaning_status(task_id):
    """查询清洗任务状态"""
    pass

@app.route(f'{API_PREFIX}/bookmarks/import', methods=['POST'])
def import_cleaned_bookmarks():
    """
    导入已清洗的书签
    
    请求体包含清洗后的书签列表和用户确认的建议
    """
    pass
```

### 3.3 前端交互流程

```
用户操作：
1. 上传 HTML 文件
   ↓
2. 显示"正在分析..."进度条
   ↓
3. 展示清洗报告页面
   ├── 显示统计概览
   ├── 列出需要确认的项目
   └── 提供批量操作按钮
   ↓
4. 用户确认/修改建议
   ↓
5. 点击"确认导入"
   ↓
6. 导入完成，显示结果
```

---

## 4. 性能优化

### 4.1 大数据量处理（500+ 书签）

```python
# 分页处理
PAGE_SIZE = 50

def process_large_dataset(bookmarks: list):
    """大数据集分页处理"""
    for i in range(0, len(bookmarks), PAGE_SIZE):
        page = bookmarks[i:i+PAGE_SIZE]
        # 处理当前页
        yield process_page(page)

# 异步 URL 检查
async def batch_check_urls(urls: list, concurrency=10):
    """限制并发避免被封"""
    semaphore = asyncio.Semaphore(concurrency)
    
    async def check_with_limit(url):
        async with semaphore:
            return await check_url(url)
    
    tasks = [check_with_limit(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### 4.2 缓存机制

```python
# 缓存 URL 检查结果（24小时）
url_check_cache = {}

async def check_url_cached(url: str) -> dict:
    if url in url_check_cache:
        return url_check_cache[url]
    
    result = await check_url(url)
    url_check_cache[url] = result
    return result
```

---

## 5. 配置选项

```python
CLEANING_CONFIG = {
    # 去重设置
    'deduplication': {
        'exact_enabled': True,           # 精确去重
        'similar_enabled': True,         # 相似去重
        'similar_threshold': 0.85,       # 相似度阈值
    },
    
    # URL 检查设置
    'url_validation': {
        'enabled': True,
        'timeout': 5,                    # 秒
        'max_concurrent': 10,
        'check_redirects': True,         # 检查重定向
    },
    
    # 分类设置
    'classification': {
        'use_ai': True,
        'use_rules': True,
        'min_confidence': 0.6,           # 最低置信度
        'fallback_category': '未分类',
    },
    
    # 导入设置
    'import': {
        'skip_existing': False,
        'update_existing': True,
        'batch_size': 100,
    }
}
```

---

## 6. 总结

| 阶段 | 自动/手动 | 处理时间（100条）| 关键产出 |
|------|-----------|------------------|----------|
| 解析 | 自动 | <1s | 结构化数据 |
| 预处理 | 自动 | <1s | 标准化数据 |
| 清洗 | 半自动 | 1-10s | 去重结果、无效链接 |
| 分析 | 自动 | 2-5s | 分类/标签建议 |
| 质量检查 | 自动 | <1s | 质量报告 |
| 审核 | 手动 | 用户决定 | 确认后的建议 |
| 导入 | 自动 | <1s | 入库结果 |

**推荐实施优先级**：
1. 🔴 高：基础解析 + 精确去重 + 分类标准化
2. 🟡 中：相似去重 + 自动分类
3. 🟢 低：URL 有效性检查 + 语义去重
