# 书签数据模型设计

> 清洗后的数据结构，支持当前功能并预留未来扩展

---

## 1. 核心设计理念

### 设计原则
1. **向前兼容**：预留字段支持未来功能（AI、隐私、质量监控）
2. **可追溯性**：保留原始数据，方便回滚和审计
3. **灵活性**：支持多维度标签、多级分类、自定义元数据
4. **性能友好**：避免深层嵌套，常用字段扁平化

### 数据层次
```
清洗报告 (CleaningReport)
    ├── 批次元数据（本次导入的整体信息）
    └── 书签列表 List<Bookmark>
            ├── 核心字段（必需）
            ├── 扩展字段（可选）
            ├── 元数据（自动提取）
            ├── AI建议（预留）
            ├── 质量状态（预留）
            └── 隐私设置（预留）
```

---

## 2. 清洗后的数据结构

### 2.1 顶层：清洗报告

```json
{
  "report_meta": {
    "report_id": "clean_abc123",
    "version": "1.0",
    "created_at": "2026-04-01T10:00:00Z",
    "expires_at": "2026-04-01T10:15:00Z",
    
    "source": {
      "type": "chrome_html",
      "filename": "bookmarks_2026_04_01.html",
      "size_bytes": 256000,
      "checksum": "sha256:abc..."
    },
    
    "summary": {
      "original_count": 150,
      "after_cleaning": 138,
      "exact_duplicates_removed": 5,
      "similar_groups_pending": 3,
      "invalid_urls_found": 2,
      "suggestions_generated": 45,
      "processing_time_ms": 9250
    },
    
    "options_used": {
      "auto_dedup": true,
      "check_urls": true,
      "similar_threshold": 0.85,
      "auto_classify": true
    }
  },
  
  "cleaning_actions": [
    {
      "action_id": "act_001",
      "type": "exact_dedup",
      "description": "合并完全重复的书签",
      "affected_count": 5,
      "details": [...]
    },
    {
      "action_id": "act_002", 
      "type": "url_normalize",
      "description": "标准化URL",
      "affected_count": 23,
      "details": [...]
    }
  ],
  
  "bookmarks": [
    // Bookmark 对象列表
  ],
  
  "similar_groups": [...],
  "invalid_urls": [...],
  "suggestions": [...]
}
```

### 2.2 核心：书签对象

```json
{
  "bookmark": {
    // ==================== 核心字段（必需）====================
    "id": "bm_7f8a9b2c",
    "url": "https://react.dev/learn/thinking-in-react",
    "title": "Thinking in React – React",
    
    // ==================== 基础属性 ====================
    "description": "A JavaScript library for building user interfaces",
    "category": "前端开发",
    "tags": ["React", "教程", "JavaScript"],
    
    // ==================== 文件夹系统（预留）====================
    "folder": {
      "id": "fd_001",              // 文件夹ID（后续支持）
      "name": "前端框架",
      "path": ["技术", "前端", "前端框架"],
      "depth": 3,
      "parent_id": "fd_parent_001"
    },
    "original_folder": {           // 原始导入时的文件夹
      "name": "temp",
      "path": ["temp"],
      "is_deprecated": true        // 是否废弃分类
    },
    
    // ==================== 时间戳 ====================
    "timestamps": {
      "added_at": "2026-04-01T10:00:00Z",
      "modified_at": "2026-04-01T10:00:00Z",
      "accessed_at": null,          // 上次访问时间（预留）
      "last_checked_at": "2026-04-01T10:05:00Z"  // 链接检查时间
    },
    
    // ==================== URL元数据 ====================
    "url_meta": {
      "normalized": "https://react.dev/learn/thinking-in-react",
      "original": "http://react.dev/learn/thinking-in-react?utm_source=bookmark",
      "domain": "react.dev",
      "protocol": "https",
      "path": "/learn/thinking-in-react",
      "query": {},                   // 清理后的query参数
      "hash": "",
      "favicon_url": "https://react.dev/favicon.ico",
      "is_available": true,
      "status_code": 200,
      "redirect_chain": [],          // 重定向链
      "final_url": null              // 最终URL（有重定向时）
    },
    
    // ==================== 内容摘要（预留）====================
    "content": {
      "summary": null,               // AI生成的摘要（后续）
      "full_text": null,             // 网页全文（后续归档功能）
      "screenshot_url": null,        // 截图（后续）
      "reading_time_minutes": 15     // 预计阅读时间
    },
    
    // ==================== AI建议（预留）====================
    "ai_suggestions": {
      "category": {
        "suggested": "前端开发",
        "confidence": 0.95,
        "alternatives": ["JavaScript", "UI框架"],
        "reason": "基于URL路径和内容分析"
      },
      "tags": {
        "suggested": ["React", "教程", "组件化"],
        "confidence": 0.88,
        "to_add": ["组件化"],
        "to_remove": []
      },
      "alias": {
        "suggested": "React思维",
        "confidence": 0.82
      },
      "priority": {
        "suggested": "high",         // AI建议的阅读优先级
        "reason": "官方文档，基础教程"
      }
    },
    
    // ==================== 质量监控（预留）====================
    "quality": {
      "score": 95,                   // 质量分数 0-100
      "status": "healthy",           // healthy | warning | dead
      "checks": {
        "url_accessible": true,
        "has_duplicate": false,
        "title_valid": true,
        "has_description": true,
        "has_tags": true,
        "is_outdated": false          // 内容是否过时
      },
      "issues": [],                  // 发现的问题列表
      "last_check": "2026-04-01T10:05:00Z"
    },
    
    // ==================== 隐私空间（预留）====================
    "privacy": {
      "is_private": false,           // 是否为隐私书签
      "encrypted": false,            // 是否加密
      "encryption_version": null,    // 加密版本
      "access_control": {            // 访问控制
        "password_protected": false,
        "allowed_users": []
      }
    },
    
    // ==================== 社交/分享（预留）====================
    "social": {
      "note": "",                    // 用户备注
      "rating": 5,                   // 用户评分 1-5
      "is_favorite": true,
      "is_read": false,
      "read_progress": 0,            // 阅读进度 %
      "share_count": 0,
      "shared_with": []
    },
    
    // ==================== 来源追溯 ====================
    "provenance": {
      "import_batch_id": "clean_abc123",
      "original_index": 42,          // 在原始HTML中的顺序
      "source_type": "chrome_export",
      "import_date": "2026-04-01T10:00:00Z",
      "imported_by": "user_123",
      "cleaning_actions": [          // 对本书签执行的清洗操作
        "url_normalize",
        "title_clean"
      ],
      "original_data": {             // 原始数据快照
        "title": "【推荐】Thinking in React – React",
        "url": "http://react.dev/learn/thinking-in-react?utm_source=bookmark",
        "folder": ["temp"]
      }
    },
    
    // ==================== 统计（预留）====================
    "stats": {
      "click_count": 0,              // 点击次数
      "last_clicked_at": null,
      "copy_count": 0,               // 复制URL次数
      "share_count": 0               // 分享次数
    },
    
    // ==================== 扩展字段 ====================
    "extras": {
      "custom_fields": {},           // 用户自定义字段
      "third_party_ids": {           // 第三方系统ID
        "notion": null,
        "raindrop": null
      }
    }
  }
}
```

---

## 3. 关键设计说明

### 3.1 ID 生成策略

```python
# 书签ID：URL的短哈希（保证唯一性）
import hashlib

def generate_bookmark_id(url: str) -> str:
    """基于URL生成唯一ID"""
    return "bm_" + hashlib.md5(url.encode()).hexdigest()[:8]

# 文件夹ID：随机字符串
def generate_folder_id() -> str:
    import uuid
    return "fd_" + uuid.uuid4().hex[:8]

# 批次ID：时间戳+随机
def generate_batch_id() -> str:
    import time
    return f"clean_{int(time.time())}_{uuid.uuid4().hex[:4]}"
```

### 3.2 字段可空性

| 字段组 | 必需字段 | 可选字段 | 说明 |
|--------|----------|----------|------|
| 核心 | id, url, title | - | 最基本的书签信息 |
| 基础 | category, tags | description | 组织管理 |
| 时间 | added_at | accessed_at, modified_at | 访问时间可空 |
| AI | - | 全部 | 未分析时全为空 |
| 质量 | status, score | checks | 未检查时简化 |
| 隐私 | is_private | 其他 | 默认为false |

### 3.3 向后兼容策略

```json
{
  "version": "1.0",                  // 数据模型版本
  "bookmark": {
    // 当前版本字段
    
    "_reserved": {                   // 预留字段区域
      "for_ai": ["summary", "embedding"],
      "for_vault": ["encrypted_content"],
      "for_sync": ["sync_id", "sync_version"]
    }
  }
}
```

---

## 4. 不同场景的数据视图

### 4.1 列表视图（轻量）

```json
{
  "id": "bm_7f8a9b2c",
  "url": "https://react.dev/learn/thinking-in-react",
  "title": "Thinking in React – React",
  "category": "前端开发",
  "tags": ["React", "教程"],
  "folder": {
    "name": "前端框架",
    "path": ["技术", "前端", "前端框架"]
  },
  "timestamps": {
    "added_at": "2026-04-01T10:00:00Z"
  },
  "url_meta": {
    "domain": "react.dev",
    "favicon_url": "https://react.dev/favicon.ico"
  },
  "quality": {
    "status": "healthy",
    "score": 95
  }
}
```

### 4.2 详情视图（完整）

包含上面定义的所有字段。

### 4.3 导入视图（清洗中）

```json
{
  "id": "bm_7f8a9b2c",
  "url": "https://react.dev/...",
  "title": "Thinking in React",
  "original_data": {
    "title": "【推荐】Thinking in React",
    "url": "http://react.dev/...",
    "folder": ["temp"]
  },
  "cleaning_actions": [
    {
      "type": "title_clean",
      "from": "【推荐】Thinking in React",
      "to": "Thinking in React"
    },
    {
      "type": "url_normalize",
      "from": "http://react.dev/...",
      "to": "https://react.dev/..."
    }
  ],
  "suggestions": [
    {
      "type": "category_change",
      "field": "category",
      "from": "temp",
      "to": "前端开发",
      "confidence": 0.95
    }
  ],
  "user_decision": null  // 等待用户决策
}
```

---

## 5. 数据库存储映射

### 5.1 JSON文件存储（当前方案）

```json
// bookmarks.json
{
  "version": "1.0",
  "last_updated": "2026-04-01T10:00:00Z",
  
  "folders": [
    {
      "id": "fd_001",
      "name": "前端框架",
      "parent_id": "fd_002",
      "path": ["技术", "前端", "前端框架"],
      "created_at": "2026-04-01T10:00:00Z"
    }
  ],
  
  "bookmarks": [
    {
      "id": "bm_001",
      "url": "...",
      "title": "...",
      "category": "前端开发",
      "tags": ["React"],
      "folder_id": "fd_001",
      "added_at": "2026-04-01T10:00:00Z",
      // ... 其他字段
    }
  ],
  
  "import_history": [
    {
      "batch_id": "clean_abc123",
      "imported_at": "2026-04-01T10:00:00Z",
      "count": 138,
      "source": "chrome_html"
    }
  ]
}
```

### 5.2 未来数据库迁移（PostgreSQL）

```sql
-- 书签表
CREATE TABLE bookmarks (
    id VARCHAR(20) PRIMARY KEY,
    url TEXT NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    tags TEXT[],
    folder_id VARCHAR(20) REFERENCES folders(id),
    
    -- 时间戳
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accessed_at TIMESTAMP WITH TIME ZONE,
    
    -- URL元数据
    domain VARCHAR(200),
    favicon_url TEXT,
    is_available BOOLEAN DEFAULT true,
    status_code INTEGER,
    
    -- AI建议（JSONB）
    ai_suggestions JSONB,
    
    -- 质量监控
    quality_score INTEGER DEFAULT 100,
    quality_status VARCHAR(20) DEFAULT 'healthy',
    quality_checks JSONB,
    
    -- 隐私
    is_private BOOLEAN DEFAULT false,
    is_encrypted BOOLEAN DEFAULT false,
    
    -- 社交
    is_favorite BOOLEAN DEFAULT false,
    is_read BOOLEAN DEFAULT false,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    
    -- 来源
    import_batch_id VARCHAR(50),
    original_data JSONB,
    
    -- 扩展
    extras JSONB DEFAULT '{}'::jsonb
);

-- 文件夹表
CREATE TABLE folders (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    parent_id VARCHAR(20) REFERENCES folders(id),
    path TEXT[],
    depth INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 导入历史表
CREATE TABLE import_batches (
    id VARCHAR(50) PRIMARY KEY,
    source_type VARCHAR(50),
    filename VARCHAR(500),
    count INTEGER,
    imported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    imported_by VARCHAR(50),
    cleaning_report JSONB
);
```

---

## 6. 与现有系统的兼容

### 6.1 向后兼容（旧数据 → 新模型）

```python
def migrate_old_bookmark(old_bookmark: dict) -> dict:
    """将旧格式书签迁移到新格式"""
    return {
        "id": old_bookmark.get('id') or generate_id(old_bookmark['url']),
        "url": old_bookmark['url'],
        "title": old_bookmark['title'],
        "description": old_bookmark.get('description', ''),
        "category": old_bookmark.get('category', '未分类'),
        "tags": old_bookmark.get('tags', []),
        
        # 新增字段默认值
        "folder": {
            "id": None,
            "name": old_bookmark.get('category', '未分类'),
            "path": [old_bookmark.get('category', '未分类')],
            "depth": 1
        },
        "timestamps": {
            "added_at": old_bookmark.get('date', datetime.now().isoformat()),
            "modified_at": datetime.now().isoformat(),
            "accessed_at": None
        },
        "url_meta": {
            "normalized": old_bookmark['url'],
            "original": old_bookmark['url'],
            "domain": extract_domain(old_bookmark['url']),
            "is_available": True
        },
        "quality": {
            "score": 100,
            "status": "healthy",
            "checks": {},
            "issues": []
        },
        "privacy": {
            "is_private": False,
            "encrypted": False
        },
        "ai_suggestions": {},
        "social": {
            "is_favorite": False,
            "is_read": False,
            "rating": 0
        },
        "provenance": {
            "import_batch_id": "migration_2026_04",
            "original_data": old_bookmark
        }
    }
```

### 6.2 向前兼容（新数据 → 旧API）

```python
def to_legacy_format(bookmark: dict) -> dict:
    """转换为旧格式（供旧API使用）"""
    return {
        "url": bookmark['url'],
        "title": bookmark['title'],
        "category": bookmark['category'],
        "tags": bookmark['tags']
    }
```

---

## 7. 使用示例

### 7.1 清洗后数据使用流程

```python
# 1. 解析并清洗
report = cleaning_pipeline.process("bookmarks.html")

# 2. 获取书签列表
bookmarks = report['bookmarks']

# 3. 按分类分组
by_category = {}
for bm in bookmarks:
    cat = bm['category']
    by_category.setdefault(cat, []).append(bm)

# 4. 筛选高质量书签
healthy_bookmarks = [
    bm for bm in bookmarks 
    if bm['quality']['status'] == 'healthy'
]

# 5. 获取AI建议
suggestions = [
    bm for bm in bookmarks
    if bm['ai_suggestions'].get('category', {}).get('confidence', 0) > 0.8
]
```

### 7.2 前端使用示例

```typescript
// 展示书签卡片
interface BookmarkCardProps {
  bookmark: Bookmark;
}

const BookmarkCard: React.FC<BookmarkCardProps> = ({ bookmark }) => {
  return (
    <div className={`bookmark-card status-${bookmark.quality.status}`}>
      <img src={bookmark.url_meta.favicon_url} alt="" />
      <h3>{bookmark.title}</h3>
      <p>{bookmark.url_meta.domain}</p>
      <span className="category">{bookmark.category}</span>
      {bookmark.tags.map(tag => (
        <span key={tag} className="tag">{tag}</span>
      ))}
      {bookmark.quality.score < 80 && (
        <WarningIcon title={`质量分: ${bookmark.quality.score}`} />
      )}
    </div>
  );
};
```

---

## 8. 总结

这个数据模型的核心优势：

1. **完整性**：涵盖当前所有需求和未来扩展
2. **可追溯性**：original_data 保留一切原始信息
3. **分层设计**：provenance、quality、ai_suggestions 等独立模块
4. **性能友好**：列表视图可精简字段
5. **兼容性强**：支持新旧格式互转

需要我详细展开某个部分，比如具体的数据库 Schema 或者前端 TypeScript 类型定义吗？
