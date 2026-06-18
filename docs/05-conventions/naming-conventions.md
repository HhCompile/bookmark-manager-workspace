# 书签命名规范与最佳实践

> 统一的命名规范让书签更易于管理和检索

---

## 1. 别名命名规范

### 1.1 基础规则

```
✅ 推荐格式:
react-tutorial
python-best-practices
github-facebook-react
mdn-js-promise

❌ 避免格式:
react_tutorial          # 下划线（不易读）
ReactTutorial           # 大写（不易输入）
react--tutorial         # 连续横线
reacttutorial           # 无分隔（难理解）
20240401-bookmark       # 纯日期（无意义）
```

### 1.2 命名模板

| 场景 | 模板 | 示例 |
|------|------|------|
| 技术文档 | `{tech}-docs` | `react-docs`, `vue-docs` |
| 教程指南 | `{tech}-tutorial` / `{tech}-guide` | `react-tutorial`, `go-guide` |
| 官方站点 | `{tech}-official` | `react-official`, `python-official` |
| GitHub仓库 | `gh-{owner}-{repo}` | `gh-facebook-react`, `gh-golang-go` |
| 博客文章 | `{author}-{topic}` | `ruanyf-react`, `dan-react-hooks` |
| 工具站点 | `{type}-tool` / `{name}-tool` | `regex-tool`, `json-tool` |
| 在线课程 | `{tech}-course` / `{platform}-{topic}` | `react-course`, `udemy-python` |
| 速查表 | `{tech}-cheatsheet` | `git-cheatsheet`, `docker-cheatsheet` |
| API文档 | `{service}-api` | `stripe-api`, `github-api` |

### 1.3 长度规范

```python
ALIAS_LENGTH_GUIDE = {
    'optimal': (10, 25),      # 最佳长度
    'acceptable': (5, 40),    # 可接受范围
    'max_limit': 50,          # 最大限制
    
    'rules': [
        '少于5字符：难以表达含义',
        '10-25字符：最佳平衡点',
        '超过30字符：输入繁琐',
        '超过50字符：强制截断'
    ]
}
```

### 1.4 词汇表

#### 技术栈缩写（推荐使用）

| 全称 | 缩写 | 说明 |
|------|------|------|
| JavaScript | `js` | 最常用缩写 |
| TypeScript | `ts` | 官方缩写 |
| Python | `py` | 官方缩写 |
| React | `react` | 保持全称（短） |
| Vue.js | `vue` | 保持全称 |
| Angular | `ng` | 官方缩写 |
| Docker | `docker` | 保持全称 |
| Kubernetes | `k8s` | 官方缩写 |
| PostgreSQL | `pg` / `postgres` | 常用缩写 |
| MongoDB | `mongo` | 常用缩写 |
| JavaScript Object Notation | `json` | 官方缩写 |
| Regular Expression | `regex` | 标准缩写 |
| Command Line Interface | `cli` | 标准缩写 |
| Application Programming Interface | `api` | 标准缩写 |

#### 常见后缀

| 后缀 | 含义 | 示例 |
|------|------|------|
| `-docs` | 官方文档 | `react-docs` |
| `-tutorial` | 教程 | `python-tutorial` |
| `-guide` | 指南 | `vue-guide` |
| `-examples` | 示例代码 | `go-examples` |
| `-best-practices` | 最佳实践 | `react-best-practices` |
| `-patterns` | 设计模式 | `js-patterns` |
| `-internals` | 内部原理 | `vue-internals` |
| `-source` | 源码 | `react-source` |
| `-tools` | 工具集 | `docker-tools` |
| `-resources` | 资源汇总 | `frontend-resources` |
| `-awesome` |  awesome列表 | `python-awesome` |
| `-cheatsheet` | 速查表 | `git-cheatsheet` |
| `-faq` | 常见问题 | `django-faq` |
| `-migration` | 迁移指南 | `vue2-vue3-migration` |
| `-performance` | 性能优化 | `react-performance` |
| `-security` | 安全相关 | `node-security` |
| `-testing` | 测试相关 | `go-testing` |

---

## 2. 标题命名规范

### 2.1 标题清洗规则

```python
TITLE_CLEANING_RULES = {
    # 移除前缀
    'remove_prefixes': [
        r'^\[.*?\]',           # [推荐]
        r'^【.*?】',           # 【精选】
        r'^（.*?）',           # （转载）
        r'^\(.*?\)',           # (Recommended)
        r'^[★☆◆◇▲▼●○]+',      # 各种符号
        r'^\d+\.\s*',          # 1. 2. 3.
        r'^(推荐|精选|热门|最新)\s*',
    ],
    
    # 移除后缀
    'remove_suffixes': [
        r'\s*-\s*.*?(博客|博客园|CSDN|掘金|知乎)$',  # 平台标识
        r'\s*\|.*$',           # | 网站名
        r'\s*-.*?(官网|官方)$',
    ],
    
    # 规范化
    'normalize': [
        (r'\s+', ' '),         # 多个空格合并
        (r'[–—]', '-'),        # 统一横线
        (r'[""''"']', '"'),   # 统一引号
    ]
}
```

### 2.2 标题优化示例

| 原标题 | 优化后 | 操作 |
|--------|--------|------|
| 【强烈推荐】React 18 新特性详解 - 掘金 | React 18 新特性详解 | 移除前缀和平台 |
| [译] JavaScript 异步编程指南 | JavaScript 异步编程指南 | 移除标记 |
| ★★★ Vue3 源码分析 | Vue3 源码分析 | 移除星级 |
| 1. Python 入门教程 | Python 入门教程 | 移除序号 |
| React 教程 \| Facebook 官方 | React 教程 | 移除后缀 |

---

## 3. 标签命名规范

### 3.1 标签体系

```
三层标签体系:
├── 技术栈（必需）
│   ├── 前端: react, vue, angular, svelte
│   ├── 后端: python, go, java, node
│   ├── 数据库: postgres, mysql, mongo, redis
│   └── 基础设施: docker, k8s, aws
│
├── 内容类型（推荐）
│   ├── 学习: tutorial, guide, course, book
│   ├── 参考: docs, api, reference, cheatsheet
│   ├── 资源: awesome, tools, examples
│   └── 社区: blog, forum, news
│
└── 元信息（可选）
    ├── 难度: beginner, intermediate, advanced
    ├── 状态: todo, reading, done, archived
    └── 评级: favorite, useful, archive
```

### 3.2 标签命名规则

```python
TAG_NAMING_RULES = {
    'format': 'lowercase-with-hyphen',
    'examples': {
        'good': [
            'react-hooks',
            'state-management',
            'error-handling',
            'performance-optimization'
        ],
        'bad': [
            'ReactHooks',       # 大写+无分隔
            'state_management',  # 下划线
            'Error Handling',   # 空格+大写
        ]
    },
    'max_length': 30,
    'max_per_bookmark': 10
}
```

### 3.3 推荐标签组合

| 书签类型 | 推荐标签 |
|----------|----------|
| React 官方教程 | `react`, `tutorial`, `javascript`, `frontend` |
| Python 数据分析 | `python`, `data-analysis`, `pandas`, `tutorial` |
| Git 速查表 | `git`, `cheatsheet`, `cli`, `reference` |
| Docker 最佳实践 | `docker`, `best-practices`, `devops`, `container` |
| Vue3 源码分析 | `vue`, `vue3`, `source-code`, `advanced` |
| 算法面试题 | `algorithm`, `interview`, `leetcode`, `preparation` |

---

## 4. 分类命名规范

### 4.1 标准分类体系

```
技术/
├── 前端开发/
│   ├── React/
│   ├── Vue/
│   ├── Angular/
│   ├── 工程化/
│   └── 性能优化/
│
├── 后端开发/
│   ├── Python/
│   ├── Go/
│   ├── Java/
│   ├── Node.js/
│   └── API设计/
│
├── 数据库/
│   ├── 关系型/
│   ├── NoSQL/
│   └── 缓存/
│
├── 基础设施/
│   ├── Docker/
│   ├── Kubernetes/
│   ├── CI/CD/
│   └── 云服务/
│
├── 人工智能/
│   ├── 机器学习/
│   ├── 深度学习/
│   ├── LLM/
│   └── 工具框架/
│
└── 开发工具/
    ├── IDE/
    ├── 编辑器/
    ├── 命令行/
    └── 效率工具/

产品/
├── 设计/
│   ├── UI设计/
│   ├── UX设计/
│   └── 设计工具/
│
├── 运营/
├── 数据分析/
└── 项目管理/

资源/
├── 工具集合/
├── 技术博客/
├── 在线课程/
├── 电子书籍/
└── 开源项目/

个人/
├── 待阅读/
├── 收藏/
└── 归档/
```

### 4.2 分类映射表

```python
CATEGORY_NORMALIZATION = {
    # 前端
    '前端': '前端开发',
    'frontend': '前端开发',
    'web': '前端开发',
    'reactjs': 'React',
    'vuejs': 'Vue',
    
    # 后端
    '后端': '后端开发',
    'backend': '后端开发',
    'server': '后端开发',
    '服务端': '后端开发',
    
    # 数据库
    'db': '数据库',
    'database': '数据库',
    'sql': '关系型',
    'nosql': 'NoSQL',
    
    # 基础设施
    'devops': '基础设施',
    '运维': '基础设施',
    'cloud': '云服务',
    
    # 废弃分类 → 重新分类
    'temp': None,
    'temporary': None,
    'misc': None,
    '未分类': None,
    '新建文件夹': None,
    'New Folder': None,
}
```

---

## 5. URL 规范

### 5.1 URL 标准化规则

```python
URL_NORMALIZATION = {
    # 协议统一
    'protocol': 'https',
    
    # 移除的参数
    'remove_params': [
        'utm_source', 'utm_medium', 'utm_campaign',
        'utm_content', 'utm_term',
        'fbclid', 'gclid',
        'ref', 'referrer',
        'source', 'from',
        'spm', 'seid',  # 中文站点
    ],
    
    # 域名处理
    'remove_www': True,
    'lowercase_domain': True,
    
    # 路径处理
    'remove_trailing_slash': True,
    'remove_fragment': False,  # 保留锚点
}
```

### 5.2 特殊站点处理

```python
SPECIAL_URL_RULES = {
    'github.com': {
        'keep_params': ['tab', 'branch', 'path'],
        'remove_params': ['utm_source', 'source'],
        'normalize': lambda url: normalize_github_url(url)
    },
    
    'stackoverflow.com': {
        'keep_params': ['answertab'],
        'remove_params': ['utm_source', 'r'],
    },
    
    'zhihu.com': {
        'remove_params': ['utm_id', 'utm_source'],
    },
    
    'juejin.cn': {
        'remove_params': ['source'],
    },
    
    'youtube.com': {
        'keep_params': ['t', 'list'],
        'remove_params': ['feature', 'ab_channel'],
    }
}
```

---

## 6. 命名冲突解决

### 6.1 别名冲突处理

```python
def resolve_alias_conflict(alias: str, existing_aliases: list) -> str:
    """
    解决别名冲突
    """
    if alias not in existing_aliases:
        return alias
    
    # 策略1: 添加数字后缀
    for i in range(2, 100):
        new_alias = f"{alias}-{i}"
        if new_alias not in existing_aliases:
            return new_alias
    
    # 策略2: 添加日期
    from datetime import datetime
    date_suffix = datetime.now().strftime("%y%m")
    return f"{alias}-{date_suffix}"

# 示例
# react-tutorial 已存在
# → react-tutorial-2
# → react-tutorial-3
# → react-tutorial-2404 (带日期)
```

### 6.2 相似别名检测

```python
def find_similar_aliases(alias: str, existing_aliases: list, threshold=0.8) -> list:
    """
    查找相似的别名
    """
    from difflib import SequenceMatcher
    
    similar = []
    for existing in existing_aliases:
        ratio = SequenceMatcher(None, alias, existing).ratio()
        if ratio >= threshold:
            similar.append({
                'alias': existing,
                'similarity': ratio
            })
    
    return similar

# 示例
# 新别名: react-tut
# 相似: react-tutorial (0.85), react-tutorials (0.82)
```

---

## 7. 命名审核清单

### 7.1 别名审核

```markdown
□ 长度在 5-40 字符之间
□ 只包含小写字母、数字和短横线
□ 不以短横线开头或结尾
□ 没有连续的短横线
□ 不包含停用词（的、了、是等）
□ 与现有别名不重复
□ 能清晰表达书签内容
□ 易于输入和记忆
```

### 7.2 标题审核

```markdown
□ 移除了平台和来源标识
□ 移除了推荐、热门等前缀
□ 没有无意义的序号
□ 长度适中（20-100字符）
□ 保留了核心信息
□ 语法正确
```

### 7.3 标签审核

```markdown
□ 包含至少一个技术栈标签
□ 包含内容类型标签
□ 标签数量在 3-8 个之间
□ 使用小写和短横线格式
□ 标签之间无重复含义
□ 没有过于宽泛的标签
```

---

## 8. 自动化命名工具

### 8.1 完整命名流水线

```python
class NamingPipeline:
    """
    命名流水线：从原始数据生成规范命名
    """
    
    def __init__(self):
        self.title_cleaner = TitleCleaner()
        self.alias_generator = AliasGenerator()
        self.tag_recommender = TagRecommender()
        self.categorizer = Categorizer()
    
    def process(self, bookmark: dict) -> dict:
        """
        处理书签，生成规范命名
        """
        result = bookmark.copy()
        
        # 1. 清洗标题
        result['title'] = self.title_cleaner.clean(
            bookmark['title']
        )
        
        # 2. 标准化 URL
        result['url'] = normalize_url(bookmark['url'])
        
        # 3. 生成分类
        if not bookmark.get('category'):
            result['category'] = self.categorizer.categorize(
                result['title'], 
                result['url']
            )
        
        # 4. 推荐标签
        if not bookmark.get('tags'):
            result['tags'] = self.tag_recommender.recommend(
                result['title'],
                result['url'],
                result['category']
            )
        
        # 5. 生成别名
        if not bookmark.get('alias'):
            alias_suggestions = self.alias_generator.generate(result)
            if alias_suggestions:
                result['alias'] = alias_suggestions[0]['alias']
                result['alias_suggestions'] = alias_suggestions
        
        return result
```

### 8.2 使用示例

```python
# 原始数据
raw_bookmark = {
    "title": "【强烈推荐】React 18 新特性详解 - 掘金",
    "url": "https://juejin.cn/post/123456?utm_source=bookmark",
    "category": "前端",
    "tags": ["react", "前端"]
}

# 处理后
pipeline = NamingPipeline()
clean_bookmark = pipeline.process(raw_bookmark)

# 结果
{
    "title": "React 18 新特性详解",
    "url": "https://juejin.cn/post/123456",
    "category": "前端开发",
    "tags": ["react", "javascript", "tutorial", "frontend"],
    "alias": "react-18-features",
    "alias_suggestions": [
        {"alias": "react-18-features", "score": 0.95},
        {"alias": "juejin-react-18", "score": 0.85},
        {"alias": "react-new-features", "score": 0.80}
    ]
}
```

---

## 9. 快速参考卡片

### 别名生成速查

```
技术文档 → {tech}-docs
教程指南 → {tech}-tutorial
GitHub项目 → gh-{owner}-{repo}
博客文章 → {author}-{topic}
工具站点 → {name}-tool
速查表 → {tech}-cheatsheet
官方站点 → {tech}-official
```

### 标签速查

```
必需: 技术栈 (react, python, docker)
推荐: 内容类型 (tutorial, docs, tool)
可选: 难度级别 (beginner, advanced)
可选: 状态标记 (favorite, todo, done)
```

### 分类速查

```
技术/前端开发/React
技术/后端开发/Python
技术/数据库/PostgreSQL
技术/基础设施/Docker
资源/工具集合
资源/技术博客
```

---

## 10. 总结

好的命名 = 清晰的结构 + 一致的规范 + 智能的生成

1. **别名**：简洁、有意义、易输入
2. **标题**：清晰、无噪音、保留核心
3. **标签**：分层、适量、标准化
4. **分类**：层次清晰、易于导航
5. **URL**：标准化、去跟踪参数

---

需要我将这些规范实现为具体的代码模块吗？
