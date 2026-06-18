# Bookmark Manager - AI Coding Agent Guide

> This file contains project-specific information for AI coding agents working on the Bookmark Manager project. The project contains both a frontend web application and a backend API service.

## Project Overview

Bookmark Manager is a full-stack web application for managing browser bookmarks with AI-powered organization features. The project consists of two main components:

1. **bookmark-manager-web**: React-based frontend web application
2. **bookmark-manager-admin**: Flask-based backend API service

### Key Features
- Bookmark management with multiple view modes (list, card, tree)
- Chrome browser bookmark synchronization
- AI-powered bookmark organization and optimization
- Auto-tagging and auto-classification based on content
- HTML bookmark file import from browsers
- Tag cloud visualization and analytics
- Quality monitoring for bookmark health
- Private vault for encrypted bookmarks
- Task manager for batch operations
- Reader mode for bookmarked articles

---

## Technology Stack

### Frontend (bookmark-manager-web)

| Category | Technology | Version |
|----------|------------|---------|
| Framework | React | 18.3.1 |
| Language | TypeScript | 5.x |
| Build Tool | Vite | 6.3.5 |
| Styling | Tailwind CSS | 4.1.12 |
| UI Components | Radix UI + shadcn/ui patterns | - |
| Animation | Motion (Framer Motion successor) | 12.x |
| Icons | Lucide React | - |
| Charts | Recharts | 2.x |
| State Management | React Context + Hooks | - |
| Data Fetching | TanStack React Query | 5.x |
| Internationalization | react-i18next + i18next | 26.x / 17.x |
| Mocking | MSW (Mock Service Worker) | 2.x |
| Forms | react-hook-form | 7.x |
| Hooks Library | ahooks | 3.x |
| Themes | next-themes | 0.4.x |
| Testing | Jest + React Testing Library | 30.x |
| Package Manager | pnpm | - |
| Routing | React Router DOM | 7.x |

### Backend (bookmark-manager-admin)

| Category | Technology | Version |
|----------|------------|---------|
| Language | Python | 3.9+ |
| Web Framework | Flask | 2.3.2 |
| HTML Parsing | BeautifulSoup4 | 4.12.2 |
| Data Storage | JSON file | - |
| CORS | flask-cors | 4.0+ |
| Rate Limiting | flask-limiter | 3.0+ |

---

## Project Structure

```
bookmark-manager/
├── .env                       # Environment variables (DEEPSEEK_API_KEY, etc.)
├── start.sh                   # One-click startup script (macOS/Linux)
├── start.py                   # One-click startup script (cross-platform)
├── start.bat                  # One-click startup script (Windows)
├── docs/                      # Structured documentation (guides, conventions, API)
├── ui-design-agent/           # AI-powered UI design assistant (MCP-based)
├── bookmark-manager-web/           # Frontend React Application
│   ├── src/
│   │   ├── App.tsx                 # Main app component with routing
│   │   ├── main.tsx                # Application entry point (MSW, React Query, i18n, SW)
│   │   ├── Layout/                 # Layout components (Header, Sidebar)
│   │   ├── router/                 # React Router configuration (index.tsx)
│   │   ├── api/                    # API client functions (client.ts, bookmarks.ts, tags.ts, etc.)
│   │   ├── components/             # React components
│   │   │   ├── ui/                 # 40+ reusable UI components
│   │   │   ├── home/               # Homepage feature sections
│   │   │   ├── auth/               # ProtectedRoute authentication wrapper
│   │   │   ├── ai/                 # AI-related components
│   │   │   ├── bookmark/           # Bookmark-specific components
│   │   │   ├── tags/               # Tag management components
│   │   │   ├── upload/             # File upload components
│   │   │   ├── views/              # Bookmark view modes (card/list/tree)
│   │   │   └── fallback/           # Error and loading fallbacks
│   │   ├── common/                 # Shared feature components
│   │   ├── contexts/               # React Context providers (AuthContext, BookmarkContext)
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── pages/                  # Page components
│   │   │   ├── home/               # HomePage
│   │   │   ├── auth/               # LoginPage, RegisterPage
│   │   │   ├── bookmark/           # BookmarkView, PrivateVault
│   │   │   └── tags/               # TagManagementPage
│   │   ├── types/                  # TypeScript type definitions
│   │   ├── utils/                  # Utility functions (analytics, format, serviceWorker)
│   │   ├── locales/                # i18n translations (en, zh)
│   │   ├── mocks/                  # MSW mock data and handlers
│   │   └── styles/                 # CSS stylesheets (tailwind.css, theme.css)
│   ├── index.html                  # HTML entry
│   ├── manifest.json               # Chrome extension manifest (MV3)
│   ├── index.html                  # HTML entry
│   ├── manifest.json               # Chrome extension manifest (MV3)
│   ├── package.json                # Dependencies and scripts
│   ├── vite.config.ts              # Vite configuration
│   ├── tsconfig.json               # TypeScript configuration
│   ├── tailwind.config.ts          # Tailwind CSS configuration
│   ├── eslint.config.js            # ESLint flat config (v9+)
│   ├── prettier.config.mjs         # Prettier formatting config
│   ├── jest.config.js              # Jest test configuration
│   └── .env.{development,production} # Environment variables
│
└── bookmark-manager-admin/         # Backend Flask Application
    ├── app/                        # Main application directory
    │   ├── api/                    # API layer - HTTP request handlers
    │   │   └── api_app.py          # Flask app instance and all API routes
    │   ├── controllers/            # Controller layer - business logic
    │   │   ├── bookmark_controller.py  # Bookmark CRUD operations
    │   │   ├── folder_controller.py    # Folder tree management
    │   │   └── metadata_controller.py  # Bookmark metadata (alias, notes, favorites)
    │   ├── models/                 # Model layer - data structures
    │   │   ├── bookmark.py             # Core bookmark model
    │   │   ├── bookmark_metadata.py    # Metadata model (alias, notes, visits, favorites)
    │   │   ├── folder.py               # Folder tree model
    │   │   └── tag.py                  # Tag model with hierarchy, color, usage stats
    │   ├── scripts/                # Script module - specific functions
    │   │   ├── interface.py        # Script interface definition
    │   │   ├── bookmark_analyzer.py
    │   │   ├── bookmark_parser.py
    │   │   └── controller.py
    │   ├── services/               # Service layer - core business logic
    │   │   ├── classifier_service.py   # Auto-tagging and classification
    │   │   ├── storage_service.py      # JSON persistence with atomic writes
    │   │   └── tag_manager.py          # Tag CRUD, merge, search, hierarchy
    │   ├── utils/                  # Utilities - shared functions
    │   │   ├── script_manager.py
    │   │   ├── serializers.py
    │   │   ├── cache.py
    │   │   ├── i18n.py
    │   │   └── auth.py
    │   └── config.py               # Application configuration
    ├── docs/                       # Documentation directory
    ├── uploads/                    # Upload file directory
    ├── bookmarks.json              # Bookmark data file (JSON storage)
    ├── folders.json                # Folder tree data file (JSON storage)
    ├── metadata.json               # Bookmark metadata file (JSON storage)
    ├── openapi.yaml                # OpenAPI 3.0 API documentation
    ├── requirements.txt            # Python dependencies
    ├── run.py                      # Application entry point
    ├── main.py                     # Demo/CLI entry (for testing)
    ├── backup.py                   # Data backup utility
    └── .env.example                # Environment variables template
```

---

## Build and Development Commands

### Frontend (bookmark-manager-web)

```bash
# Navigate to frontend directory
cd bookmark-manager-web

# Install dependencies
pnpm install

# Start development server (port 3000)
pnpm dev

# Build for production
pnpm build

# Run linting
pnpm lint

# Run type checking
pnpm typecheck

# Run tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run tests with coverage
pnpm test:coverage
```

### Backend (bookmark-manager-admin)

```bash
# Navigate to backend directory
cd bookmark-manager-admin

# Create virtual environment (recommended)
python3 -m venv venv_new

# Activate virtual environment (Linux/macOS)
source venv_new/bin/activate

# Activate virtual environment (Windows)
venv_new\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server (port 9001)
python3 run.py

# Production deployment with Gunicorn
gunicorn -w 4 -b 0.0.0.0:9001 run:app
```

### One-Click Startup (root directory)

```bash
# Start both frontend and backend services simultaneously

# Option 1: shell script (macOS/Linux)
./start.sh

# Option 2: Python script (cross-platform)
python3 start.py

# Option 3: batch script (Windows)
start.bat
```
Frontend starts on port **3000**, backend on port **9001**. Press Ctrl+C to stop all services.

---

## Code Style Guidelines

### Frontend (TypeScript/React)

#### ESLint Configuration
- Uses ESLint v9+ flat config format
- TypeScript parser with strict rules
- React hooks rules enforced
- No explicit `any` allowed (`@typescript-eslint/no-explicit-any: error`)
- Console warnings in development (`no-console: warn`)
- Debugger statements forbidden (`no-debugger: error`)

#### Prettier Configuration
- 2-space indentation (no tabs)
- Single quotes
- Semicolons required
- Trailing commas (ES5 style)
- 80 character line width
- LF line endings

#### Naming Conventions
- Components: PascalCase (e.g., `BookmarkView.tsx`)
- Hooks: camelCase starting with `use` (e.g., `useChromeBookmarks.ts`)
- Utilities: camelCase (e.g., `analytics.ts`)
- CSS classes: Tailwind utility-first approach

#### Import Organization
```typescript
// 1. React/Third-party imports
import { useState, useCallback } from 'react';
import * as Tooltip from '@radix-ui/react-tooltip';

// 2. Absolute imports from @/
import Header from '@/layout/Header';
import { useBookmarks } from '@/contexts/BookmarkContext';

// 3. Relative imports (only when necessary)
import './styles.css';
```

### Backend (Python)

#### File Naming Convention
- Use **snake_case** for all file names
- Module files use singular form (e.g., `bookmark.py` not `bookmarks.py`)
- Utility files end with `_utils.py`
- Configuration files use `config.py` or specific prefix

#### Code Style
- Use 4-space indentation
- File header must include encoding declaration: `# -*- coding: utf-8 -*-`
- Use Chinese docstrings for classes and methods
- Import order: Standard library → Third-party → Local modules

#### File Header Template
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块功能说明
"""

import os
import sys
from flask import Flask
from app.models.bookmark import Bookmark


class BookmarkManager:
    """
    书签管理器核心逻辑
    """
    
    def add_bookmark(self, bookmark):
        """添加书签"""
        pass
```

---

## Testing Strategy

### Frontend
- Framework: Jest 30.x with jsdom environment
- React Testing Library for component tests
- ts-jest for TypeScript transformation
- Coverage reporting with lcov
- Test files: No existing tests (Jest configured but empty)
- Path mapping `@/*` mapped to `src/*`

### Backend
- No formal test framework configured yet
- Manual testing via API endpoints recommended
- Postman or curl can be used for testing
- Health check endpoint: `GET /v1/health`

#### Example API Test
```bash
# Health check
curl http://127.0.0.1:9001/v1/health

# Get all bookmarks
curl http://127.0.0.1:9001/v1/bookmarks

# Add a bookmark
curl -X POST http://127.0.0.1:9001/v1/bookmark \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "title": "Example"}'
```

---

## Architecture

### Frontend Architecture

#### Application Entry Point
The app initializes in `main.tsx`:
1. **MSW (Mock Service Worker)** starts in development mode to intercept API calls
2. **TanStack React Query** `QueryClientProvider` wraps the app with 5-min stale time and offline retry logic
3. **i18n** is initialized from `locales/` (Chinese + English)
4. **Service Worker** is registered in production for offline support
5. **ErrorBoundary** wraps the entire render tree
6. Finally, `App.tsx` renders inside `AuthProvider` → `BookmarkProvider` → `Tooltip.Provider`

#### Routing
Two routing systems coexist:
- **App.tsx**: Uses `<BrowserRouter>` + `<Routes>` directly, defines layouts (HomeLayout vs MainLayout), auth guards, and nested `/app/*` routes
- **router/index.tsx**: A `createBrowserRouter`-based configuration with the same structure (older pattern, may be consolidated)

Routes:
- `/` — HomePage (no sidebar, public)
- `/login`, `/register` — Auth pages (public, minimal layout)
- `/app/bookmarks` — BookmarkView (sidebar, requires auth)
- `/app/analytics` — TagCloudVisualization
- `/app/quality` — QualityMonitor
- `/app/private` — PrivateVault
- `/app/ai` — AIConfirmationPanel
- `/app/tags` — TagManagementPage

#### State Management
- **React Context**: `BookmarkContext` manages bookmarks, folders, view mode, search — accessed via `useBookmarks()` hook
- **AuthContext**: Handles user authentication state (login, register, logout)
- **TanStack React Query**: Server state caching for API data, with automatic background refetching
- **Component state**: Local `useState` for UI state (panels, modals)

#### Data Fetching
- `src/api/client.ts` — Axios/fetch-based API client with base URL configuration
- `src/api/bookmarks.ts` — Bookmark CRUD operations
- `src/api/tags.ts` — Tag management endpoints
- `src/api/ai.ts` — AI optimization endpoints
- `src/api/vault.ts` — Private vault operations
- `src/api/analytics.ts` — Analytics data
- `src/api/quality.ts` — Quality monitoring

#### Offline Support
- Service worker (`utils/serviceWorker.ts`) registers in production
- React Query retry logic respects `navigator.onLine`
- `onOffline`/`onOnline` callbacks for UI adaptation

#### Component Patterns
All UI components follow the shadcn/ui pattern using:
- `class-variance-authority` for variant management
- `cn()` utility for class name merging
- Radix UI primitives for accessibility
- CSS variables from `theme.css`

#### Lazy Loading
Major page components are lazy-loaded for performance:
```typescript
const BookmarkView = lazy(() => import('./pages/bookmark/BookmarkView'));
```

### Backend Architecture

#### Layered Architecture

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| API Layer | `app/api/` | Handle HTTP requests/responses, define all routes |
| Controller Layer | `app/controllers/` | Business logic control, coordinate services |
| Service Layer | `app/services/` | Core business logic implementation |
| Model Layer | `app/models/` | Data structures and entity definitions |
| Script Layer | `app/scripts/` | Independent functional scripts |
| Utility Layer | `app/utils/` | Common utility functions |

#### Core Classes

**Bookmark** (`app/models/bookmark.py`)
- Data model with url, title, tags, category properties
- Implements `__eq__` and `__hash__` based on URL

**BookmarkMetadata** (`app/models/bookmark_metadata.py`)
- Extended metadata: alias, notes, folder_id, custom_tags, is_favorite
- Tracks visit_count and last_visited timestamp
- Linked to bookmarks via URL hash

**Folder** (`app/models/folder.py`)
- Tree structure with id, name, parent_id, children list
- UUID-based ID generation, `to_dict()` serialization

**Tag** (`app/models/tag.py`)
- Supports hierarchy (parent_id), color from predefined palette
- Tracks usage_count, created_at timestamps
- `to_dict()` and `from_dict()` serialization

**BookmarkManager** (`app/controllers/bookmark_controller.py`)
- Controller class for bookmark CRUD operations
- Supports query by category and tag

**FolderManager** (`app/controllers/folder_controller.py`)
- Creates and manages folder tree with default folders ("书签栏", "其他书签")
- Supports add, update, delete, move operations

**MetadataManager** (`app/controllers/metadata_controller.py`)
- Manages per-bookmark metadata (alias, notes, favorites, custom_tags)
- URL-hash based lookup for consistency

**Classifier** (`app/services/classifier_service.py`)
- Auto-tagging and auto-classification based on keywords
- Configurable rules via JSON

**TagManager** (`app/services/tag_manager.py`)
- Tag CRUD with merge, search/suggestions, hierarchy management
- Usage statistics tracking, parent-child relationships
- Custom exceptions: TagExistsError, TagNotFoundError

**Storage** (`app/services/storage_service.py`)
- JSON file persistence with atomic writes (write to temp, rename)
- Backup mechanism with rotation
- Thread-safe with file locking
- Three independent stores: `bookmarks.json`, `folders.json`, `metadata.json`

---

## API Specification

### Base URL
- Development: `http://127.0.0.1:9001/v1`
- All endpoints use `/v1` version prefix

### Authentication
- **Frontend**: Has full auth UI (LoginPage, RegisterPage, AuthContext, ProtectedRoute)
- **Backend API**: Currently no authentication enforcement (development mode); API Key authentication planned for production
- Protected frontend routes (`/app/*`) require login via `ProtectedRoute` component

### Main Endpoints

#### Bookmark Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/health` | Health check with system metrics |
| GET | `/v1/bookmarks` | Get all bookmarks (paginated) |
| POST | `/v1/bookmark` | Add single bookmark |
| POST | `/v1/bookmarks/batch` | Batch add bookmarks (max 1000) |
| GET | `/v1/bookmarks/category/{category}` | Get by category |
| GET | `/v1/bookmarks/tag/{tag}` | Get by tag |
| POST | `/v1/bookmark/update` | Update bookmark |
| POST | `/v1/bookmark/delete` | Delete bookmark |
| POST | `/v1/bookmark/upload` | Upload HTML bookmark file |

#### Data Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/bookmarks/export` | Export bookmarks (JSON/CSV/HTML) |
| POST | `/v1/bookmarks/batch-update` | Batch update bookmarks |
| POST | `/v1/bookmarks/batch-delete` | Batch delete bookmarks |
| POST | `/v1/bookmarks/deduplicate` | Remove duplicates by URL |
| GET | `/v1/bookmarks/stats` | Get statistics |

#### Script Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/scripts` | List registered scripts |
| POST | `/v1/scripts/parse` | Parse HTML to JSON |
| POST | `/v1/scripts/analyze` | Analyze bookmarks |
| POST | `/v1/scripts/process` | Parse and analyze |

#### Tags Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/tags` | Get tag list (paginated, searchable, sortable) |
| POST | `/v1/tags` | Create new tag (name, color, description, parent_id) |
| GET | `/v1/tags/{id}` | Get tag detail with bookmark count and related tags |
| PUT | `/v1/tags/{id}` | Update tag properties |
| DELETE | `/v1/tags/{id}` | Delete tag (optional migrate_to) |
| POST | `/v1/tags/{id}/merge` | Merge tag into another, update all bookmark references |
| GET | `/v1/tags/suggestions` | Tag autocomplete suggestions (`?q=`) |
| GET | `/v1/tags/stats` | Tag usage statistics (total, distribution) |

#### Metadata Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/bookmark/{url}/metadata` | Get metadata for a bookmark (alias, notes, folder, favorites) |
| PUT | `/v1/bookmark/{url}/metadata` | Update metadata fields |
| DELETE | `/v1/bookmark/{url}/metadata` | Delete metadata for a bookmark |
| POST | `/v1/bookmark/{url}/visit` | Record a visit (increments visit_count, updates last_visited) |
| GET | `/v1/metadata/by-folder/{folder_id}` | Get all metadata for bookmarks in a folder |
| GET | `/v1/metadata/favorites` | Get all favorited bookmark metadata |

#### Folder Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/folders` | List all folders (tree structure) |
| POST | `/v1/folders` | Create new folder |
| PUT | `/v1/folders/{id}` | Update folder name or parent |
| DELETE | `/v1/folders/{id}` | Delete folder |

### Query Parameters
- `/v1/bookmarks` supports: `page`, `limit`, `category`, `tag`
- Default page size: 20, Maximum: 100

### Request/Response Headers
- `X-Request-ID`: Request tracking ID (auto-generated or provided)
- `Content-Type: application/json` for JSON endpoints

Complete API documentation: `bookmark-manager-admin/openapi.yaml`

---

## Environment Variables

### Frontend
Variables must be prefixed with `VITE_` to be exposed to client:

| Variable | Development | Production |
|----------|-------------|------------|
| `VITE_APP_NAME` | Bookmark Manager | Bookmark Manager |
| `VITE_APP_ENV` | development | production |
| `VITE_APP_API_BASE_URL` | http://localhost:3001/api | https://api.bookmark-manager.com/api |
| `VITE_APP_DEBUG` | true | false |
| `VITE_APP_VERSION` | 1.0.0 | 1.0.0 |

### Backend
See `bookmark-manager-admin/.env.example`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | True | Debug mode |
| `HOST` | 0.0.0.0 | Server bind address |
| `PORT` | 9001 | Server port |
| `SECRET_KEY` | dev-secret-key | Flask secret key |
| `DATA_FILE` | bookmarks.json | Data storage file |
| `MAX_BACKUP_COUNT` | 5 | Max backup files |
| `UPLOAD_FOLDER` | uploads | Upload directory |
| `MAX_CONTENT_LENGTH` | 16777216 | Max upload size (16MB) |
| `LOG_LEVEL` | INFO | Logging level |
| `LOG_FILE` | None | Log file path |
| `CORS_ORIGINS` | * | Allowed CORS origins |
| `MAX_BOOKMARKS_PER_BATCH` | 1000 | Batch size limit |

---

## Security Considerations

### Frontend
1. **Authentication**: Frontend has LoginPage/RegisterPage with ProtectedRoute guarding `/app/*` routes; AuthContext manages session state
2. **XSS Prevention**: React's built-in escaping + no `dangerouslySetInnerHTML`
3. **Content Security**: Configure CSP headers in production
4. **Chrome Extension**: Only requests necessary `bookmarks` permission
5. **Private Vault**: Client-side encryption for sensitive bookmarks
6. **Environment**: API keys and secrets should NEVER be in client-side env vars

### Backend
1. **No Authentication on API**: All endpoints are currently unauthenticated (dev only)
2. **File Upload Limits**: Max 16MB, HTML files only
3. **File Path Security**: Uses `werkzeug.utils.secure_filename`
4. **Input Validation**: URL format validation and string sanitization
5. **Rate Limiting**: 1000/hour, 100/minute per IP
6. **CORS**: Configurable allowed origins
7. **Path Traversal Protection**: Script registration validates file paths

---

## Chrome Extension Integration

The frontend app is designed to work as a Chrome extension:

### Manifest V3
- Permission: `bookmarks`
- Default popup: `index.html`
- Background service worker ready

### Chrome Bookmarks Hook
`useChromeBookmarks()` hook provides:
- `refreshBookmarks()` - Sync with Chrome bookmarks
- `createBookmark()`, `updateBookmark()`, `removeBookmark()` - CRUD operations
- Only works in Chrome extension environment (graceful fallback)

---

## Development Workflow

### Adding a New Feature

1. **Backend First**:
   - Add model changes to `app/models/`
   - Add business logic to `app/services/` or `app/controllers/`
   - Add API endpoint to `app/api/api_app.py`
   - Update `openapi.yaml` documentation

2. **Frontend**:
   - Add API client function in `src/api/`
   - Add types to `src/types/`
   - Create/update components in `src/components/`
   - Add page in `src/pages/` if needed
   - Update routing in `src/App.tsx`

3. **Testing**:
   - Test API with curl/Postman
   - Test frontend integration
   - Verify Chrome extension compatibility

### Git Workflow
- Both projects have separate `.git` directories (can be unified if needed)
- Commit to appropriate project directory
- Update relevant AGENTS.md if conventions change

---

## Deployment

### Frontend Production Build
```bash
cd bookmark-manager-web
pnpm build
```
Output goes to `dist/` directory.

### Backend Production Deployment
```bash
cd bookmark-manager-admin
gunicorn -w 4 -b 0.0.0.0:9001 run:app
```

### Chrome Extension
1. Build the frontend project
2. Load `dist/` as unpacked extension in Chrome
3. Or pack for Chrome Web Store submission

---

## Documentation References

### Frontend
- `bookmark-manager-web/README.md` - Basic setup
- `bookmark-manager-web/AGENTS.md` - Detailed frontend guide
- `bookmark-manager-web/设计系统指南.md` - Design system (Chinese)
- `bookmark-manager-web/技能功能与使用方法文档.md` - Feature docs (Chinese)

### Backend
- `bookmark-manager-admin/README.md` - Project overview and quick start
- `bookmark-manager-admin/AGENTS.md` - Detailed backend guide (Chinese)
- `bookmark-manager-admin/docs/DOCUMENTATION.md` - Documentation index
- `bookmark-manager-admin/docs/PROJECT_STRUCTURE.md` - Architecture details
- `bookmark-manager-admin/docs/INTEGRATION_GUIDE.md` - Adding new features
- `bookmark-manager-admin/openapi.yaml` - API specification (OpenAPI 3.0)

### Root
- `docs/` - Structured project documentation (guides, conventions, API, architecture)
  - `00-index/` - Documentation navigation and overview
  - `05-conventions/` - Naming conventions and alias guides
- `ui-design-agent/` - AI-powered UI design assistant (MCP-based) with its own docs

---

## Troubleshooting

### Frontend Issues

**Chrome API not available**
- App gracefully degrades when not in Chrome extension context
- Check `isChromeExtension()` before calling Chrome APIs

**Tailwind classes not working**
- Ensure `@import 'tailwindcss'` is in `tailwind.css`
- Run dev server to regenerate styles

**Import path issues**
- Use `@/` prefix for src imports
- Check `tsconfig.json` paths configuration

### Backend Issues

**Port already in use**
- Change `PORT` in environment variables
- Or kill existing process: `lsof -ti:9001 | xargs kill -9`

**Permission denied on uploads/** 
- Ensure directory exists: `mkdir -p uploads`
- Check write permissions

**Module import errors**
- Ensure virtual environment is activated
- Check `sys.path` includes project root

---

## Language Notes

- **Frontend**: UI text is primarily in Chinese, code in English
- **Backend**: Comments and docstrings are in Chinese, code in English
- **API**: Error messages support i18n (English/Chinese)
- **Documentation**: Mixed English and Chinese, matching project conventions

---

*Last updated: 2026-04-13*
