# 书签别名系统与命名建议

> 别名是书签的"快捷方式"，用于快速搜索和访问

---

## 1. 别名系统设计

### 1.1 什么是别名

```
书签标题："Thinking in React – React"
别名："react-tutorial"
别名："react思维"
别名："react官方教程"

使用场景：
- 搜索时输入 "react" 快速找到
- 命令行快速打开 bookmark open react-tutorial
- 生成短链接时作为 slug
```

### 1.2 别名生成策略

```python
# 别名生成器主类
class AliasGenerator:
    """
    多策略别名生成器
    """
    
    def __init__(self):
        self.strategies = [
            DomainStrategy(),           # 域名提取
            TitleKeywordStrategy(),     # 标题关键词
            AbbreviationStrategy(),     # 缩写生成
            PinyinStrategy(),           # 中文拼音
            CategoryTagStrategy(),      # 分类标签组合
            SemanticStrategy(),         # 语义理解
        ]
    
    def generate(self, bookmark: dict, max_suggestions: int = 3) -> list:
        """
        生成别名建议列表
        
        Returns:
            [
                {
                    "alias": "react-tutorial",
                    "score": 0.95,
                    "strategy": "domain_keyword",
                    "reason": "基于域名+关键词组合"
                },
                ...
            ]
        """
        candidates = []
        
        for strategy in self.strategies:
            result = strategy.generate(bookmark)
            if result:
                candidates.extend(result)
        
        # 去重、排序、返回最佳建议
        return self._rank_and_deduplicate(candidates, max_suggestions)
```

---

## 2. 具体生成策略

### 2.1 域名提取策略

```python
class DomainStrategy:
    """
    从URL域名生成别名
    
    示例：
    - github.com/facebook/react → "github-react"
    - docs.python.org → "python-docs"
    - zhihu.com/question/123 → "zhihu-q123"
    """
    
    def generate(self, bookmark: dict) -> list:
        url = bookmark['url']
        title = bookmark['title']
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.strip('/').split('/')
        
        candidates = []
        
        # 规则1: 主域名 + 一级路径
        if len(path) >= 1 and path[0]:
            alias = f"{domain.split('.')[0]}-{path[0]}"
            candidates.append({
                "alias": self._sanitize(alias),
                "score": 0.90,
                "strategy": "domain_path",
                "reason": f"域名+路径: {domain}/{path[0]}"
            })
        
        # 规则2: 二级域名作为前缀
        parts = domain.split('.')
        if len(parts) > 2 and parts[0] not in ['www', 'm', 'mobile']:
            alias = f"{parts[0]}-{path[0] if path else 'home'}"
            candidates.append({
                "alias": self._sanitize(alias),
                "score": 0.85,
                "strategy": "subdomain",
                "reason": f"子域名: {parts[0]}"
            })
        
        # 规则3: GitHub 特殊处理
        if 'github.com' in domain and len(path) >= 2:
            alias = f"github-{path[0]}-{path[1]}"
            candidates.append({
                "alias": self._sanitize(alias),
                "score": 0.95,
                "strategy": "github_repo",
                "reason": f"GitHub仓库: {path[0]}/{path[1]}"
            })
        
        # 规则4: 文档站点
        docs_keywords = ['docs', 'documentation', 'wiki', 'guide']
        if any(kw in domain or kw in path[0] for kw in docs_keywords):
            main_domain = parts[-2] if len(parts) >= 2 else parts[0]
            alias = f"{main_domain}-docs"
            candidates.append({
                "alias": self._sanitize(alias),
                "score": 0.88,
                "strategy": "docs_site",
                "reason": "文档站点"
            })
        
        return candidates
    
    def _sanitize(self, alias: str) -> str:
        """清理别名"""
        # 转小写，替换特殊字符
        alias = alias.lower()
        alias = re.sub(r'[^\w\-]', '-', alias)
        alias = re.sub(r'-+', '-', alias)
        return alias.strip('-')[:50]
```

### 2.2 标题关键词策略

```python
class TitleKeywordStrategy:
    """
    从标题提取关键词生成别名
    
    示例：
    - "React 官方文档 Tutorial" → "react-tutorial"
    - "2024年最新 Python 入门指南" → "python-guide-2024"
    - "【推荐】超详细 Vue3 源码解析" → "vue3-source-analysis"
    """
    
    # 停用词
    STOP_WORDS = {
        '的', '了', '和', '是', '在', '有', '我', '他', '她', '它',
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        '【', '】', '★', '☆', '◆', '◇', '▲', '▼', '●', '○',
        '推荐', '最新', '超详细', '全网最全', '必看', '收藏'
    }
    
    # 技术关键词优先级
    TECH_KEYWORDS = {
        'tutorial': 10, 'guide': 10, 'docs': 10, 'documentation': 10,
        '入门': 9, '教程': 9, '指南': 9, '文档': 9,
        'advanced': 8, '进阶': 8, '深入': 8,
        'source': 7, '源码': 7, '原理': 7,
        'best-practices': 7, '最佳实践': 7, '实战': 7,
        'cheatsheet': 6, '速查': 6, '备忘': 6,
        'course': 5, '课程': 5, '学习': 5,
    }
    
    def generate(self, bookmark: dict) -> list:
        title = bookmark['title']
        category = bookmark.get('category', '')
        
        candidates = []
        
        # 提取关键词
        keywords = self._extract_keywords(title)
        
        if len(keywords) >= 2:
            # 组合前2-3个关键词
            alias = '-'.join(keywords[:3])
            candidates.append({
                "alias": alias,
                "score": 0.85,
                "strategy": "title_keywords",
                "reason": f"标题关键词: {', '.join(keywords[:3])}"
            })
        
        # 提取年份（如果有）
        year_match = re.search(r'(20\d{2})', title)
        if year_match and keywords:
            alias = f"{keywords[0]}-{year_match.group(1)}"
            candidates.append({
                "alias": alias,
                "score": 0.80,
                "strategy": "keyword_year",
                "reason": f"关键词+年份"
            })
        
        # 分类 + 关键词
        if category and keywords:
            alias = f"{category}-{keywords[0]}"
            candidates.append({
                "alias": self._transliterate(alias),
                "score": 0.75,
                "strategy": "category_keyword",
                "reason": f"分类+关键词: {category}"
            })
        
        return candidates
    
    def _extract_keywords(self, title: str) -> list:
        """提取关键词，按优先级排序"""
        # 清理标题
        title = re.sub(r'[【\[\(（].*?[】\]\)）]', '', title)
        words = re.findall(r'[\w\u4e00-\u9fa5]+', title.lower())
        
        keywords = []
        for word in words:
            if word in self.STOP_WORDS:
                continue
            
            # 计算优先级
            priority = self.TECH_KEYWORDS.get(word, 5)
            
            # 技术栈名称提高优先级
            if word in ['react', 'vue', 'angular', 'python', 'java', 'go', 'rust']:
                priority += 10
            
            keywords.append((word, priority))
        
        # 按优先级排序
        keywords.sort(key=lambda x: x[1], reverse=True)
        return [k[0] for k in keywords]
    
    def _transliterate(self, text: str) -> str:
        """中文转拼音/英文"""
        # 简化的拼音映射（实际使用 pypinyin 库）
        result = []
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                # 这里应该调用拼音转换
                result.append(char)  # 简化处理
            else:
                result.append(char)
        return ''.join(result)
```

### 2.3 缩写生成策略

```python
class AbbreviationStrategy:
    """
    生成缩写别名
    
    示例：
    - "JavaScript Object Notation" → "json"
    - "Create Read Update Delete" → "crud"
    - "Model View Controller" → "mvc"
    - "HyperText Transfer Protocol" → "http"
    """
    
    # 常见缩写词表
    COMMON_ABBREVS = {
        'javascript': 'js',
        'typescript': 'ts',
        'python': 'py',
        'database': 'db',
        'application': 'app',
        'document': 'doc',
        'image': 'img',
        'configuration': 'config',
        'library': 'lib',
        'package': 'pkg',
        'reference': 'ref',
        'source': 'src',
        'utility': 'util',
        'temporary': 'tmp',
        'example': 'ex',
        'alternative': 'alt',
        'original': 'orig',
        'version': 'v',
        'development': 'dev',
        'production': 'prod',
        'environment': 'env',
    }
    
    def generate(self, bookmark: dict) -> list:
        title = bookmark['title'].lower()
        candidates = []
        
        # 规则1: 首字母缩写
        words = re.findall(r'\b\w+\b', title)
        if len(words) >= 3:
            abbrev = ''.join(w[0] for w in words[:5])
            if len(abbrev) >= 3:
                candidates.append({
                    "alias": abbrev,
                    "score": 0.70,
                    "strategy": "initialism",
                    "reason": f"首字母缩写: {abbrev.upper()}"
                })
        
        # 规则2: 常见缩写替换
        for full, abbrev in self.COMMON_ABBREVS.items():
            if full in title:
                alias = title.replace(full, abbrev)
                alias = re.sub(r'\s+', '-', alias)
                alias = re.sub(r'-+', '-', alias).strip('-')
                if len(alias) <= 30:
                    candidates.append({
                        "alias": alias[:50],
                        "score": 0.75,
                        "strategy": "common_abbrev",
                        "reason": f"{full} → {abbrev}"
                    })
        
        # 规则3: 骆驼命名转短横线
        camel_words = re.findall(r'[A-Z][a-z]+', bookmark['title'])
        if len(camel_words) >= 2:
            alias = '-'.join(w.lower() for w in camel_words[:4])
            candidates.append({
                "alias": alias,
                "score": 0.72,
                "strategy": "camel_case",
                "reason": "骆驼命名转换"
            })
        
        return candidates
```

### 2.4 中文拼音策略

```python
class PinyinStrategy:
    """
    为中文标题生成拼音别名
    
    示例：
    - "React 官方文档" → "react-guanfang-wendang"
    - "JavaScript 高级程序设计" → "js-gaoji-chengxu-sheji"
    - "深入理解计算机系统" → "shenru-shejie-jisuanji-xitong"
    """
    
    def __init__(self):
        try:
            from pypinyin import pinyin, Style
            self.pinyin = pinyin
            self.style = Style
            self.available = True
        except ImportError:
            self.available = False
    
    def generate(self, bookmark: dict) -> list:
        if not self.available:
            return []
        
        title = bookmark['title']
        
        # 检查是否包含中文
        if not re.search(r'[\u4e00-\u9fff]', title):
            return []
        
        candidates = []
        
        # 全拼
        try:
            pinyin_list = self.pinyin(title, style=self.style.NORMAL)
            full_pinyin = ''.join([p[0] for p in pinyin_list])
            
            # 首字母
            initials = ''.join([p[0][0] for p in pinyin_list])
            
            # 混合：英文保留，中文转拼音
            mixed = self._mixed_convert(title)
            
            candidates.extend([
                {
                    "alias": mixed[:50],
                    "score": 0.88,
                    "strategy": "pinyin_mixed",
                    "reason": "中英文混合拼音"
                },
                {
                    "alias": full_pinyin[:50],
                    "score": 0.75,
                    "strategy": "pinyin_full",
                    "reason": "完整拼音"
                },
                {
                    "alias": initials[:10],
                    "score": 0.65,
                    "strategy": "pinyin_initials",
                    "reason": f"拼音首字母: {initials.upper()}"
                }
            ])
        except Exception:
            pass
        
        return candidates
    
    def _mixed_convert(self, text: str) -> str:
        """混合转换：英文保留，中文转拼音"""
        result = []
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                try:
                    py = self.pinyin(char, style=self.style.NORMAL)[0][0]
                    result.append(py)
                except:
                    result.append(char)
            elif char.isalnum():
                result.append(char.lower())
            else:
                result.append('-')
        
        return re.sub(r'-+', '-', ''.join(result)).strip('-')
```

### 2.5 语义理解策略

```python
class SemanticStrategy:
    """
    基于语义理解的智能别名生成
    
    示例：
    - "2024 React Conf 大会演讲合集" → "react-conf-2024"
    - "阮一峰的网络日志" → "ruanyf-blog"
    - "MDN Web Docs" → "mdn-reference"
    """
    
    # 知名站点识别
    FAMOUS_SITES = {
        'github.com': ('github', 'repo'),
        'stackoverflow.com': ('stackoverflow', 'qa'),
        'zhihu.com': ('zhihu', 'qa'),
        'juejin.cn': ('juejin', 'article'),
        'csdn.net': ('csdn', 'blog'),
        'ruanyifeng.com': ('ruanyf', 'blog'),
        'mdn.mozilla.org': ('mdn', 'docs'),
        'developer.mozilla.org': ('mdn', 'docs'),
    }
    
    # 内容类型识别
    CONTENT_TYPES = {
        r'(blog|博客|日志)': 'blog',
        r'(github|gitlab)': 'repo',
        r'(doc|文档|docs)': 'docs',
        r'(tutorial|教程)': 'tutorial',
        r'(tool|工具)': 'tool',
        r'(course|课程)': 'course',
        r'(video|视频)': 'video',
    }
    
    def generate(self, bookmark: dict) -> list:
        url = bookmark['url']
        title = bookmark['title']
        domain = urlparse(url).netloc.lower()
        
        candidates = []
        
        # 知名站点处理
        for site, (prefix, ctype) in self.FAMOUS_SITES.items():
            if site in domain:
                # 提取路径中的标识
                path_id = self._extract_path_id(url)
                if path_id:
                    alias = f"{prefix}-{path_id}"
                else:
                    alias = f"{prefix}-{ctype}"
                
                candidates.append({
                    "alias": alias[:50],
                    "score": 0.95,
                    "strategy": "famous_site",
                    "reason": f"知名站点: {site}"
                })
        
        # 内容类型识别
        title_lower = title.lower()
        for pattern, ctype in self.CONTENT_TYPES.items():
            if re.search(pattern, title_lower):
                # 提取技术栈名称
                tech = self._extract_tech_name(title)
                if tech:
                    alias = f"{tech}-{ctype}"
                    candidates.append({
                        "alias": alias[:50],
                        "score": 0.85,
                        "strategy": "content_type",
                        "reason": f"{tech} {ctype}"
                    })
        
        return candidates
    
    def _extract_path_id(self, url: str) -> str:
        """从URL路径提取标识"""
        path = urlparse(url).path.strip('/').split('/')
        if len(path) >= 2:
            return f"{path[0]}-{path[1]}"
        elif len(path) == 1:
            return path[0]
        return ""
    
    def _extract_tech_name(self, title: str) -> str:
        """提取技术栈名称"""
        tech_keywords = [
            'react', 'vue', 'angular', 'svelte',
            'python', 'javascript', 'typescript', 'go', 'rust', 'java',
            'node', 'deno', 'bun',
            'docker', 'kubernetes', 'k8s',
            'aws', 'azure', 'gcp',
            'mysql', 'postgresql', 'mongo', 'redis',
        ]
        
        title_lower = title.lower()
        for tech in tech_keywords:
            if tech in title_lower:
                return tech
        return ""
```

---

## 3. 别名质量评估

### 3.1 评分维度

```python
class AliasScorer:
    """
    别名质量评分器
    """
    
    def score(self, alias: str, bookmark: dict) -> dict:
        """
        多维度评分
        """
        scores = {
            'length': self._score_length(alias),
            'readability': self._score_readability(alias),
            'uniqueness': self._score_uniqueness(alias),
            'relevance': self._score_relevance(alias, bookmark),
            'memorability': self._score_memorability(alias),
        }
        
        # 加权总分
        weights = {
            'length': 0.15,
            'readability': 0.20,
            'uniqueness': 0.25,
            'relevance': 0.30,
            'memorability': 0.10,
        }
        
        total = sum(scores[k] * weights[k] for k in scores)
        
        return {
            'total': round(total, 2),
            'breakdown': scores,
            'grade': self._grade(total)
        }
    
    def _score_length(self, alias: str) -> float:
        """长度评分：10-30字符最佳"""
        length = len(alias)
        if 10 <= length <= 30:
            return 1.0
        elif 5 <= length < 10:
            return 0.8
        elif 30 < length <= 50:
            return 0.7
        else:
            return 0.5
    
    def _score_readability(self, alias: str) -> float:
        """可读性评分"""
        # 避免连续多个短横线
        if '--' in alias:
            return 0.6
        
        # 避免纯数字
        if alias.isdigit():
            return 0.4
        
        # 单词数量适中
        parts = alias.split('-')
        if 2 <= len(parts) <= 4:
            return 1.0
        elif len(parts) == 1:
            return 0.8
        else:
            return 0.7
    
    def _score_uniqueness(self, alias: str) -> float:
        """唯一性评分（检查是否已存在）"""
        # 查询数据库
        existing = check_alias_exists(alias)
        if existing:
            return 0.3
        
        # 检查相似别名
        similar = find_similar_aliases(alias)
        if similar:
            return 0.7
        
        return 1.0
    
    def _score_relevance(self, alias: str, bookmark: dict) -> float:
        """相关性评分"""
        score = 0.5
        
        # 是否包含技术关键词
        tech_words = ['react', 'vue', 'python', 'js', 'api']
        if any(w in alias for w in tech_words):
            score += 0.2
        
        # 是否包含在标题中
        title_words = bookmark['title'].lower().split()
        alias_words = alias.split('-')
        matches = sum(1 for w in alias_words if w in title_words)
        score += matches * 0.1
        
        return min(score, 1.0)
    
    def _score_memorability(self, alias: str) -> float:
        """易记性评分"""
        # 押韵或重复模式
        parts = alias.split('-')
        if len(parts) >= 2 and parts[0] == parts[-1]:
            return 0.9
        
        # 全字母或全数字较差
        if alias.isalpha() or alias.isdigit():
            return 0.6
        
        return 0.8
    
    def _grade(self, score: float) -> str:
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        else:
            return "D"
```

---

## 4. 别名使用场景

### 4.1 快速搜索

```
输入 "react" → 匹配包含 react 的书签和别名
输入 "gh-react" → 匹配 github 相关的 react 书签
输入 "tutorial" → 匹配教程类型的书签
```

### 4.2 命令行快捷访问

```bash
# 假设有命令行工具
bookmark open react-tutorial      # 打开 React 教程
bookmark open mdn-js              # 打开 MDN JavaScript 文档
bookmark list --alias "github-*"  # 列出所有 GitHub 相关的书签
```

### 4.3 短链接生成

```
原始URL：https://github.com/facebook/react/blob/main/README.md
短链接：bm.app/r/gh-react-readme
```

---

## 5. 其他推荐建议

### 5.1 命名规范建议

| 类型 | 推荐格式 | 示例 |
|------|----------|------|
| 技术教程 | `{tech}-tutorial` | `react-tutorial`, `python-guide` |
| 官方文档 | `{tech}-docs` | `vue-docs`, `django-docs` |
| GitHub仓库 | `gh-{user}-{repo}` | `gh-facebook-react` |
| 个人博客 | `{author}-blog` | `ruanyf-blog`, `dan-abramov` |
| 工具站点 | `{tool}-tool` | `regex-tool`, `json-formatter` |
| 课程视频 | `{topic}-course` | `ml-course`, `react-mosh` |

### 5.2 标签策略建议

```python
# 三层标签体系
TAG_STRATEGY = {
    # 技术栈（必需）
    'tech_stack': [
        'react', 'vue', 'angular',
        'python', 'go', 'rust',
        'docker', 'k8s'
    ],
    
    # 内容类型（推荐）
    'content_type': [
        'tutorial', 'docs', 'blog',
        'video', 'tool', 'course',
        'source', 'cheatsheet'
    ],
    
    # 难度级别（可选）
    'difficulty': [
        'beginner', 'intermediate', 'advanced'
    ],
    
    # 状态标记（可选）
    'status': [
        'toread', 'reading', 'done', 'favorite'
    ]
}
```

### 5.3 文件夹组织建议

```
书签根目录
├── 技术/
│   ├── 前端/
│   │   ├── React/
│   │   ├── Vue/
│   │   └── 工程化/
│   ├── 后端/
│   │   ├── Python/
│   │   ├── Go/
│   │   └── 数据库/
│   └── 基础设施/
│       ├── Docker/
│       ├── K8s/
│       └── CI_CD/
├── 产品/
│   ├── 设计/
│   ├── 运营/
│   └── 数据/
├── 资源/
│   ├── 工具/
│   ├── 文档/
│   └── 博客/
└── 待整理/          # 临时存放，定期清理
```

### 5.4 智能分类规则

```python
AUTO_CLASSIFICATION_RULES = {
    '前端开发': {
        'domains': ['react.dev', 'vuejs.org', 'angular.io'],
        'keywords': ['react', 'vue', 'angular', 'webpack', 'babel'],
        'paths': ['/docs', '/guide', '/tutorial']
    },
    '后端开发': {
        'domains': ['docs.python.org', 'golang.org', 'spring.io'],
        'keywords': ['python', 'go', 'java', 'spring', 'django'],
    },
    'AI/ML': {
        'domains': ['pytorch.org', 'tensorflow.org', 'huggingface.co'],
        'keywords': ['machine-learning', 'deep-learning', 'nlp', 'llm'],
    },
    'DevOps': {
        'domains': ['docker.com', 'kubernetes.io', 'jenkins.io'],
        'keywords': ['docker', 'kubernetes', 'ci/cd', 'devops'],
    }
}
```

### 5.5 质量监控指标

```python
QUALITY_METRICS = {
    # 健康度评分
    'health_score': {
        'url_accessible': 30,      # 链接可访问
        'has_description': 20,     # 有描述
        'has_tags': 20,            # 有标签
        'proper_category': 20,     # 分类正确
        'has_alias': 10,           # 有别名
    },
    
    # 问题检测
    'issues': {
        'duplicate_url': '重复URL',
        'dead_link': '失效链接',
        'empty_title': '空标题',
        'no_category': '未分类',
        'too_many_tags': '标签过多(>10)',
        'suspicious_domain': '可疑域名',
    }
}
```

---

## 6. 完整代码示例

### 6.1 使用示例

```python
# 初始化
from alias_generator import AliasGenerator

generator = AliasGenerator()

# 示例书签
bookmark = {
    "title": "React 官方文档 - Thinking in React",
    "url": "https://react.dev/learn/thinking-in-react",
    "category": "前端开发",
    "tags": ["React", "教程"]
}

# 生成别名建议
suggestions = generator.generate(bookmark, max_suggestions=5)

# 输出结果
for s in suggestions:
    print(f"[{s['score']:.2f}] {s['alias']}")
    print(f"      策略: {s['strategy']} - {s['reason']}")
    print()

# 预期输出:
# [0.95] react-thinking
#       策略: domain_keyword - 基于域名+关键词组合
#
# [0.90] react-tutorial
#       策略: title_keywords - 标题关键词: react, tutorial
#
# [0.88] react-guanfang-wendang
#       策略: pinyin_mixed - 中英文混合拼音
#
# [0.85] frontend-react-thinking
#       策略: category_keyword - 分类+关键词
#
# [0.80] react-learn-thinking
#       策略: domain_path - 域名+路径
```

### 6.2 批量生成

```python
# 为所有书签生成别名
for bookmark in bookmarks:
    if not bookmark.get('alias'):
        suggestions = generator.generate(bookmark)
        if suggestions:
            # 自动应用最高分建议
            bookmark['alias'] = suggestions[0]['alias']
            bookmark['alias_confidence'] = suggestions[0]['score']
```

---

## 7. 总结

### 别名最佳实践

1. **简洁**：10-30字符最佳
2. **有意义**：包含技术关键词
3. **唯一性**：避免与现有别名重复
4. **可读性**：使用短横线分隔，避免连续横线
5. **多语言**：中文内容使用拼音或英文

### 推荐优先级

| 优先级 | 策略 | 适用场景 |
|--------|------|----------|
| 1 | 域名+关键词 | 大多数技术文档 |
| 2 | 标题关键词 | 中文博客文章 |
| 3 | 知名站点识别 | GitHub、MDN等 |
| 4 | 拼音转换 | 纯中文内容 |
| 5 | 缩写生成 | 长标题简化 |

---

需要我详细展开某个策略的实现，或者提供前端展示别名建议的UI组件设计吗？
