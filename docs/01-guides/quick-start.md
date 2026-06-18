# MVP 快速开始指南

## 1. 启动服务

### 启动后端 (端口 9001)
```bash
cd bookmark-manager-admin
source venv/bin/activate
python3 run.py
```

### 启动前端 (端口 3000)
```bash
cd bookmark-manager-web
pnpm dev
```

---

## 2. API 快速参考

### 健康检查
```bash
curl http://localhost:9001/v1/health
```

### 书签操作

#### 获取书签列表
```bash
# 基础列表
curl "http://localhost:9001/v1/bookmarks?page=1&limit=20"

# 按分类筛选
curl "http://localhost:9001/v1/bookmarks?category=技术"

# 按标签筛选
curl "http://localhost:9001/v1/bookmarks?tag=python"
```

#### 创建书签
```bash
curl -X POST http://localhost:9001/v1/bookmark \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com",
    "title": "GitHub",
    "tags": ["代码", "开源"],
    "category": "开发工具"
  }'
```

#### 批量创建书签
```bash
curl -X POST http://localhost:9001/v1/bookmarks/batch \
  -H "Content-Type: application/json" \
  -d '{
    "bookmarks": [
      {"url": "https://example1.com", "title": "示例1"},
      {"url": "https://example2.com", "title": "示例2"}
    ]
  }'
```

#### 更新书签
```bash
curl -X POST http://localhost:9001/v1/bookmark/update \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com",
    "title": "GitHub - 新版标题",
    "tags": ["git", "版本控制"]
  }'
```

#### 删除书签
```bash
curl -X POST http://localhost:9001/v1/bookmark/delete \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

#### 上传 HTML 书签文件
```bash
curl -X POST http://localhost:9001/v1/bookmark/upload \
  -F "file=@bookmarks.html"
```

### 文件夹操作

#### 获取文件夹列表
```bash
curl http://localhost:9001/v1/folders
```

#### 创建文件夹
```bash
curl -X POST http://localhost:9001/v1/folders \
  -H "Content-Type: application/json" \
  -d '{
    "name": "开发资源",
    "parentId": "1"
  }'
```

#### 更新文件夹
```bash
curl -X POST http://localhost:9001/v1/folders/update \
  -H "Content-Type: application/json" \
  -d '{
    "id": "a1b2c3d4",
    "name": "新的文件夹名称"
  }'
```

#### 删除文件夹
```bash
curl -X POST http://localhost:9001/v1/folders/delete \
  -H "Content-Type: application/json" \
  -d '{"id": "a1b2c3d4"}'
```

### 数据统计

#### 书签统计
```bash
curl http://localhost:9001/v1/bookmarks/stats
```

---

## 3. 前端 Hook 使用示例

### 获取书签列表
```typescript
import { useBookmarksQuery } from '@/api';

function BookmarkList() {
  const { data, isLoading, error } = useBookmarksQuery({
    page: 1,
    limit: 20,
    category: '技术'
  });

  if (isLoading) return <div>加载中...</div>;
  if (error) return <div>错误: {error.message}</div>;

  return (
    <ul>
      {data?.data.bookmarks.map(bookmark => (
        <li key={bookmark.url}>{bookmark.title}</li>
      ))}
    </ul>
  );
}
```

### 创建书签
```typescript
import { useCreateBookmark } from '@/api';

function CreateBookmarkForm() {
  const mutation = useCreateBookmark();

  const handleSubmit = (data) => {
    mutation.mutate({
      url: data.url,
      title: data.title,
      tags: data.tags,
      category: data.category
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* 表单字段 */}
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? '创建中...' : '创建'}
      </button>
    </form>
  );
}
```

### 获取文件夹列表
```typescript
import { useFoldersQuery } from '@/api';

function FolderTree() {
  const { data: folders, isLoading } = useFoldersQuery();

  if (isLoading) return <div>加载中...</div>;

  return (
    <ul>
      {folders?.data.map(folder => (
        <li key={folder.id}>{folder.name}</li>
      ))}
    </ul>
  );
}
```

---

## 4. 测试运行

### 后端测试
```bash
cd bookmark-manager-admin
source venv/bin/activate
pytest

# 带覆盖率
pytest --cov=app --cov-report=html
```

### 前端测试
```bash
cd bookmark-manager-web
pnpm test

# 带覆盖率
pnpm test --coverage
```

---

## 5. 常见问题

### Q: 前端无法连接到后端？
A: 检查 `bookmark-manager-web/.env.development` 中的 `VITE_APP_API_BASE_URL` 是否为 `http://localhost:3001/api`，并确保后端服务在 9001 端口运行。

### Q: 如何查看 API 文档？
A: 后端提供 OpenAPI 规范文件 `bookmark-manager-admin/openapi.yaml`，可以导入到 Swagger UI 或 Postman 中查看。

### Q: 如何重置数据？
A: 删除 `bookmark-manager-admin/bookmarks.json` 和 `bookmark-manager-admin/folders.json` 文件，重启后端服务即可。

---

## 6. 下一步

1. 尝试使用上面的 curl 命令测试 API
2. 在浏览器中打开前端页面 `http://localhost:3000`
3. 阅读 `API_ALIGNMENT.md` 了解完整的 API 对齐情况
4. 查看 `MVP_COMPLETION_REPORT.md` 了解详细的完成报告
