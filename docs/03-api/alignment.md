# MVP 版本 API 对齐文档

## 概述
本文档记录了 Bookmark Manager MVP 版本中前后端 API 的对齐情况。

**后端 API 基础 URL**: `http://localhost:9001/v1`  
**前端 API 基础 URL**: `/api/v1` (通过 Vite 代理配置)

---

## API 端点对照表

### 书签管理 (Bookmarks)

| 功能 | 前端 Hook | 后端端点 | 方法 | 状态 |
|------|-----------|----------|------|------|
| 获取书签列表 | `useBookmarksQuery` | `/bookmarks` | GET | ✅ 对齐 |
| 按分类获取 | `useBookmarksByCategoryQuery` | `/bookmarks/category/<category>` | GET | ✅ 对齐 |
| 按标签获取 | `useBookmarksByTagQuery` | `/bookmarks/tag/<tag>` | GET | ✅ 对齐 |
| 创建书签 | `useCreateBookmark` | `/bookmark` | POST | ✅ 对齐 |
| 批量创建 | `useCreateBookmarksBatch` | `/bookmarks/batch` | POST | ✅ 对齐 |
| 更新书签 | `useUpdateBookmark` | `/bookmark/update` | POST | ✅ 对齐 |
| 删除书签 | `useDeleteBookmark` | `/bookmark/delete` | POST | ✅ 对齐 |
| 上传 HTML | `useUploadBookmarkFile` | `/bookmark/upload` | POST | ✅ 对齐 |
| 批量更新 | `useBatchUpdateBookmarks` | `/bookmarks/batch-update` | POST | ✅ 对齐 |
| 批量删除 | `useBatchDeleteBookmarks` | `/bookmarks/batch-delete` | POST | ✅ 对齐 |
| 导出书签 | `useExportBookmarks` | `/bookmarks/export` | POST | ✅ 对齐 |
| 书签去重 | - | `/bookmarks/deduplicate` | POST | ⚠️ 后端有，前端未使用 |
| 书签统计 | `useBookmarksStatsQuery` | `/bookmarks/stats` | GET | ✅ 对齐 |

### 文件夹管理 (Folders)

| 功能 | 前端 Hook | 后端端点 | 方法 | 状态 |
|------|-----------|----------|------|------|
| 获取文件夹列表 | `useFoldersQuery` | `/folders` | GET | ✅ 对齐 |
| 创建文件夹 | `useCreateFolder` | `/folders` | POST | ✅ 对齐 |
| 更新文件夹 | `useUpdateFolder` | `/folders/update` | POST | ✅ 对齐 |
| 删除文件夹 | `useDeleteFolder` | `/folders/delete` | POST | ✅ 对齐 |

### 脚本工具 (Scripts)

| 功能 | 前端 Hook | 后端端点 | 方法 | 状态 |
|------|-----------|----------|------|------|
| 获取脚本列表 | `useScriptsQuery` | `/scripts` | GET | ✅ 对齐 |
| 解析 HTML | `useParseBookmarks` | `/scripts/parse` | POST | ✅ 对齐 |
| 分析书签 | `useAnalyzeBookmarks` | `/scripts/analyze` | POST | ✅ 对齐 |
| 处理书签 | `useProcessBookmarks` | `/scripts/process` | POST | ✅ 对齐 |

### 系统接口

| 功能 | 后端端点 | 方法 | 状态 |
|------|----------|------|------|
| 健康检查 | `/health` | GET | ✅ 可用 |

---

## 请求/响应示例

### 获取书签列表

**请求:**
```http
GET /v1/bookmarks?page=1&limit=20&category=技术
```

**响应:**
```json
{
  "bookmarks": [
    {
      "url": "https://example.com",
      "title": "示例网站",
      "tags": ["示例", "教程"],
      "category": "技术"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

### 创建书签

**请求:**
```http
POST /v1/bookmark
Content-Type: application/json

{
  "url": "https://github.com",
  "title": "GitHub",
  "tags": ["代码", "开源"],
  "category": "开发工具"
}
```

**响应:**
```json
{
  "url": "https://github.com",
  "title": "GitHub",
  "tags": ["代码", "开源", "git"],
  "category": "开发工具"
}
```

### 创建文件夹

**请求:**
```http
POST /v1/folders
Content-Type: application/json

{
  "name": "开发资源",
  "parentId": "1"
}
```

**响应:**
```json
{
  "message": "Folder created successfully",
  "folder": {
    "id": "a1b2c3d4",
    "name": "开发资源",
    "parentId": "1",
    "children": []
  }
}
```

---

## 未实现功能 (后续版本)

以下功能在 MVP 版本中未实现，将在后续版本添加：

### AI 功能
- `GET /ai/suggestions` - 获取 AI 建议
- `POST /ai/analyze` - 分析书签
- `POST /ai/suggestions/:id/accept` - 接受建议
- `POST /ai/suggestions/:id/reject` - 拒绝建议

### 质量监控
- `GET /quality/duplicates` - 获取重复书签
- `GET /quality/dead-links` - 获取失效链接
- `GET /quality/report` - 获取质量报告
- `POST /quality/check` - 运行质量检查

### 隐私空间
- `GET /vault/bookmarks` - 获取隐私书签
- `POST /vault/unlock` - 解锁隐私空间
- `POST /vault/lock` - 锁定隐私空间

### 数据分析
- `GET /analytics/tags` - 标签统计
- `GET /analytics/categories` - 分类统计
- `GET /analytics/trends` - 趋势数据

---

## 开发注意事项

1. **URL 编码**: 当使用分类或标签作为路径参数时，确保进行 URL 编码
   ```typescript
   const encodedCategory = encodeURIComponent('技术');
   const url = `/bookmarks/category/${encodedCategory}`;
   ```

2. **错误处理**: 后端返回的错误格式统一为:
   ```json
   { "error": "错误消息" }
   ```

3. **分页参数**: 
   - `page`: 页码，从 1 开始
   - `limit`: 每页数量，默认 20，最大 100

4. **文件上传**: 上传 HTML 书签文件时使用 `multipart/form-data`:
   ```typescript
   const formData = new FormData();
   formData.append('file', file);
   ```

---

## 最后更新

- 更新日期: 2026-04-03
- 版本: MVP v1.0
- 对齐状态: ✅ 22/22 个基础 API 已对齐
