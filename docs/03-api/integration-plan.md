# Bookmark Manager 前后端 API 对接方案

> 版本: v1.0  
> 日期: 2026-04-01  
> 状态: 待评审

---

## 1. 现状分析

### 1.1 前端现状
- **框架**: React + TypeScript + TanStack Query
- **API 客户端**: 自定义 fetch 封装，基于 RESTful 设计
- **期望端点**: `/api/*` (可通过环境变量配置)
- **核心依赖接口**: 25+ 个（包含 AI、隐私、质量监控等高级功能）

### 1.2 后端现状
- **框架**: Flask (Python)
- **API 前缀**: `/v1/*`
- **已有接口**: 18 个（基础 CRUD + 脚本管理 + 批量操作）
- **存储**: JSON 文件（无数据库）

### 1.3 核心差距

| 维度 | 前端期望 | 后端实际 | 差距 |
|------|----------|----------|------|
| **接口数量** | 32 个 | 18 个 | -14 个 |
| **数据模型** | Bookmark + Folder + Vault + AI建议 | 仅 Bookmark | 缺失 3 个实体 |
| **认证授权** | JWT Token (隐私空间) | 无 | 需新增 |
| **API 风格** | RESTful (PUT/DELETE/PATCH) | POST 为主 | 需适配 |
| **路径前缀** | `/api/v1/*` | `/v1/*` | 需对齐 |

---

## 2. 对接方案选型

### 方案对比

| 方案 | 描述 | 工作量 | 风险 | 推荐度 |
|------|------|--------|------|--------|
| **A. 纯适配层** | 前端增加 API 适配映射 | 低 | 部分功能不可用 | ⭐⭐⭐ |
| **B. RESTful改造** | 后端接口统一为 RESTful 风格 | 中 | 需回归测试 | ⭐⭐⭐⭐ |
| **C. 增量开发** | 后端补齐缺失接口 | 高 | 开发周期长 | ⭐⭐⭐⭐⭐ |
| **D. 混合方案** | B + C 结合，分阶段实施 | 中-高 | 可控 | ⭐⭐⭐⭐⭐ **推荐** |

### 最终推荐: 混合方案（分三期）

```
┌─────────────────────────────────────────────────────────────┐
│  第一期（1-2天）：基础适配 + 核心功能打通                      │
│  ├── 后端增加 /api 前缀支持（或反向代理）                      │
│  ├── RESTful 路由映射（兼容现有 POST 方式）                    │
│  ├── 前端配置 baseURL 指向后端                                 │
│  └── MSW 接管缺失的高级功能                                    │
├─────────────────────────────────────────────────────────────┤
│  第二期（3-5天）：接口标准化改造                               │
│  ├── 后端新增 RESTful 路由（保持向后兼容）                     │
│  ├── Bookmark ID 字段支持（当前以 URL 为主键）                 │
│  └── 数据模型扩展（Folder 基础支持）                           │
├─────────────────────────────────────────────────────────────┤
│  第三期（1-2周）：高级功能实现                                 │
│  ├── AI 建议系统（可接入外部 LLM API）                         │
│  ├── 隐私空间（客户端加密 + 服务端存储）                       │
│  ├── 质量监控（定时任务 + 链接检测）                           │
│  └── Chrome 同步（浏览器扩展集成）                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 详细接口映射表

### 3.1 第一期：基础对接（高优先级）

#### 路由适配

| 前端调用 | 后端现有 | 适配方式 | 状态 |
|----------|----------|----------|------|
| `GET /api/bookmarks` | `GET /v1/bookmarks` | 直接转发 | ✅ |
| `POST /api/bookmarks` | `POST /v1/bookmark` | 路径映射 | ✅ |
| `PUT /api/bookmarks/:id` | `POST /v1/bookmark/update` | **需改造** | ⚠️ |
| `DELETE /api/bookmarks/:id` | `POST /v1/bookmark/delete` | **需改造** | ⚠️ |
| `POST /api/import/html` | `POST /v1/bookmark/upload` | 路径映射 | ✅ |
| `GET /api/bookmarks/stats` | `GET /v1/bookmarks/stats` | 直接转发 | ✅ |

#### 关键改造点

**1. ID 字段问题**
```javascript
// 前端期望
GET /api/bookmarks/bookmark-123

// 后端实际（以 URL 为主键）
POST /v1/bookmark/update
Body: { url: "https://example.com", title: "..." }
```

**解决方案**: 后端在返回书签时增加 `id` 字段（可用 URL hash 或自增索引）

```python
# 后端序列化时增加 id
{
    "id": hashlib.md5(bookmark.url.encode()).hexdigest()[:12],  # URL 的短 hash
    "url": bookmark.url,
    "title": bookmark.title,
    ...
}
```

**2. 更新/删除接口改造**

新增 RESTful 路由（同时保留旧接口兼容）：

```python
# bookmark-manager-admin/app/api/api_app.py

@app.route(f'{API_PREFIX}/bookmarks/<id>', methods=['PUT'])
def update_bookmark_by_id(id):
    """RESTful 风格更新书签"""
    # 1. 通过 id 查找 URL（需建立 id->url 映射）
    # 2. 调用现有 update_bookmark 逻辑
    pass

@app.route(f'{API_PREFIX}/bookmarks/<id>', methods=['DELETE'])
def delete_bookmark_by_id(id):
    """RESTful 风格删除书签"""
    # 1. 通过 id 查找 URL
    # 2. 调用现有 delete_bookmark 逻辑
    pass
```

---

### 3.2 第二期：接口标准化（中优先级）

#### 需新增的接口

| 接口 | 方法 | 描述 | 后端工作量 |
|------|------|------|------------|
| `/api/folders` | GET/POST | 文件夹列表/创建 | 2h |
| `/api/folders/:id` | PUT/DELETE | 文件夹更新/删除 | 2h |
| `/api/analytics/tags` | GET | 标签统计 | 1h |
| `/api/analytics/categories` | GET | 分类统计 | 1h |
| `/api/analytics/trends` | GET | 趋势数据 | 2h |

#### 数据模型扩展

**Folder 模型（新增）**
```python
# app/models/folder.py
class Folder:
    """文件夹模型"""
    def __init__(self, id: str, name: str, parent_id: str = None, 
                 created_at: str = None, updated_at: str = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.parent_id = parent_id
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
```

**Bookmark 模型扩展**
```python
# 在 Bookmark 类中增加
self.id = hashlib.md5(url.encode()).hexdigest()[:12]
self.folder_id = folder_id  # 新增
self.added_date = added_date or datetime.now().isoformat()  # 新增
```

---

### 3.3 第三期：高级功能（低优先级，可 Mock）

#### AI 建议系统

| 接口 | 方法 | 描述 | 实现方案 |
|------|------|------|----------|
| `/api/ai/suggestions` | GET | 获取 AI 建议 | 接入 OpenAI/Claude API |
| `/api/ai/analyze` | POST | 分析书签 | 调用 LLM 生成标签/分类 |
| `/api/ai/suggestions/:id/accept` | POST | 接受建议 | 更新书签数据 |
| `/api/ai/suggestions/:id/reject` | POST | 拒绝建议 | 标记建议状态 |

**最小可行实现（MVP）**:
```python
# app/services/ai_service.py
class AIService:
    """AI 建议服务（简化版）"""
    
    def generate_suggestions(self, bookmark):
        """基于规则的简单建议（不调用 LLM）"""
        suggestions = []
        
        # 基于 URL 域名推荐分类
        domain_categories = {
            'github.com': '开发',
            'stackoverflow.com': '开发',
            'youtube.com': '视频',
            'bilibili.com': '视频',
            'zhihu.com': '知识',
        }
        
        domain = urlparse(bookmark.url).netloc
        if domain in domain_categories:
            if bookmark.category != domain_categories[domain]:
                suggestions.append({
                    'id': str(uuid.uuid4()),
                    'bookmark_id': bookmark.id,
                    'bookmark_title': bookmark.title,
                    'original_category': bookmark.category,
                    'suggested_category': domain_categories[domain],
                    'confidence': 'high',
                    'reason': f'基于域名 {domain} 推荐'
                })
        
        return suggestions
```

#### 隐私空间

| 接口 | 方法 | 描述 | 安全要求 |
|------|------|------|----------|
| `/api/vault/bookmarks` | GET | 获取隐私书签 | JWT Token |
| `/api/vault/unlock` | POST | 解锁 | 密码验证 |
| `/api/vault/lock` | POST | 锁定 | Token 过期 |
| `/api/vault/bookmarks` | POST | 创建隐私书签 | 客户端加密 |

**安全设计**:
```
客户端加密流程:
1. 用户输入密码
2. 前端派生加密密钥 (PBKDF2)
3. 书签内容 AES-GCM 加密
4. 发送密文到后端存储
5. 后端仅存储加密数据，无法解密
```

#### 质量监控

| 接口 | 方法 | 描述 | 实现复杂度 |
|------|------|------|------------|
| `/api/quality/report` | GET | 质量报告 | 低 |
| `/api/quality/duplicates` | GET | 重复书签 | 低（已有去重逻辑）|
| `/api/quality/dead-links` | GET | 失效链接 | 高（需定时检测）|
| `/api/quality/check` | POST | 运行检查 | 中 |

---

## 4. 数据模型对齐

### 4.1 Bookmark 统一模型

```typescript
// 前端期望
interface Bookmark {
  id: string;              // 必需（后端新增）
  url: string;             // 必需
  title: string;           // 必需
  tags: string[];          // 必需
  category: string;        // 必需
  folderId?: string;       // 可选（二期支持）
  addedDate: string;       // ISO 格式（后端新增）
  updatedDate?: string;    // 可选
}
```

```python
# 后端实现
class Bookmark:
    def __init__(self, url: str, title: str = "", 
                 tags: list = None, category: str = None,
                 folder_id: str = None, added_date: str = None):
        self.id = hashlib.md5(url.encode()).hexdigest()[:12]  # 自动生成
        self.url = url
        self.title = title
        self.tags = tags or []
        self.category = category
        self.folder_id = folder_id
        self.added_date = added_date or datetime.now().isoformat()
        self.updated_date = datetime.now().isoformat()
```

### 4.2 API 响应格式统一

**当前后端格式**:
```json
{
  "bookmarks": [...],
  "pagination": {...}
}
```

**前端期望格式**:
```json
{
  "data": [...],
  "success": true,
  "message": "...",
  "timestamp": "2026-04-01T12:00:00Z"
}
```

**适配方案**: 后端增加统一响应包装

```python
# app/utils/response.py
from functools import wraps
from flask import jsonify
from datetime import datetime

def api_response(f):
    """API 响应统一包装器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        result = f(*args, **kwargs)
        
        # 如果已经是 tuple (data, status_code)
        if isinstance(result, tuple):
            data, status_code = result
        else:
            data, status_code = result, 200
        
        # 如果已经是标准格式，直接返回
        if isinstance(data, dict) and 'success' in data:
            return jsonify(data), status_code
        
        # 包装为标准格式
        response = {
            'success': status_code < 400,
            'data': data,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if not response['success'] and 'error' in data:
            response['message'] = data['error']
            del response['data']
        
        return jsonify(response), status_code
    
    return decorated

# 使用示例
@app.route(f'{API_PREFIX}/bookmarks')
@api_response
def get_bookmarks():
    bookmarks = manager.get_bookmarks()
    return {'bookmarks': bookmarks_to_dict_list(bookmarks)}
```

---

## 5. 实施计划

### 5.1 任务分解

```
Week 1: 基础对接
├── Day 1-2: 后端改造
│   ├── 添加 id 字段到 Bookmark
│   ├── 新增 PUT/DELETE 路由
│   └── 统一响应格式
├── Day 3: 联调测试
│   ├── 书签 CRUD 测试
│   └── 导入功能测试
└── Day 4-5: 问题修复

Week 2: 标准化
├── 文件夹功能实现
├── 统计接口实现
└── 前端 Folder 模块联调

Week 3: 高级功能（可选）
├── AI 建议（规则版）
├── 隐私空间（基础版）
└── 质量监控报告
```

### 5.2 环境配置

**前端环境变量** (`.env.development`):
```bash
# 对接后端
VITE_API_BASE_URL=http://localhost:9001/v1

# 或使用代理（推荐，避免 CORS）
VITE_API_BASE_URL=/api
```

**开发代理配置** (`vite.config.ts`):
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/v1'),
      },
    },
  },
})
```

---

## 6. 风险与应对

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| URL 主键改造成本高 | 高 | 中 | 保留 URL 主键，id 作为派生字段 |
| JSON 文件并发问题 | 中 | 低 | 加强文件锁，或迁移到 SQLite |
| AI 功能开发周期长 | 中 | 高 | 先用规则引擎，再接入 LLM |
| 隐私空间安全审计 | 高 | 中 | 先做客户端加密，后请安全 review |
| 前端代码大量修改 | 高 | 低 | 通过适配层减少前端改动 |

---

## 7. 附录

### A. 后端新增文件清单

```
app/
├── models/
│   └── folder.py              # 新增
├── services/
│   ├── ai_service.py          # 新增（简化版）
│   └── vault_service.py       # 新增
├── utils/
│   └── response.py            # 新增（响应包装器）
└── api/
    └── routes/                # 可选：路由拆分
        ├── bookmarks.py
        ├── folders.py
        ├── ai.py
        └── vault.py
```

### B. 前端修改清单

```
src/
├── api/
│   ├── client.ts              # 修改 baseURL
│   └── index.ts               # 可能需要路径映射
└── mocks/
    └── handlers.ts            # 保留高级功能 Mock
```

### C. 接口测试用例

```bash
# 基础 CRUD 测试
curl -X GET http://localhost:9001/v1/bookmarks
curl -X POST http://localhost:9001/v1/bookmark \
  -H "Content-Type: application/json" \
  -d '{"url":"https://test.com","title":"Test"}'
curl -X PUT http://localhost:9001/v1/bookmarks/<id> \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated"}'

# 统计接口
curl -X GET http://localhost:9001/v1/bookmarks/stats

# 导入测试
curl -X POST http://localhost:9001/v1/bookmark/upload \
  -F "file=@bookmarks.html"
```

---

## 8. 决策记录

| 日期 | 决策 | 原因 | 决策人 |
|------|------|------|--------|
| 2026-04-01 | 采用混合方案 | 平衡工作量与功能完整性 | - |
| - | ID 使用 URL Hash | 避免数据迁移 | - |
| - | 保留 POST 旧接口 | 向后兼容 | - |
| - | AI 先用规则引擎 | 快速验证需求 | - |

---

*文档维护：定期更新进度，标记已完成项*
