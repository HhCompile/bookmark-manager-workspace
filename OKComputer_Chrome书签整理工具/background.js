// background.js - Bookmark Manager Sync
// Chrome Extension Service Worker
//
// 职责：
// 1. 监听浏览器书签变化（新增/修改/删除）→ 推送到 admin
// 2. 提供全量同步入口（一次性把整棵书签树推送）
// 3. 失败重试 + 队列管理

// ============================================================================
// 配置
// ============================================================================

const DEFAULT_API_BASE = 'http://localhost:9001/v1';
const SYNC_ALARM_NAME = 'bookmark-sync-periodic';
const SYNC_PERIOD_MIN = 30; // 30 分钟
const RETRY_DELAY_MS = 60_000; // 失败后 1 分钟重试
const MAX_BATCH_SIZE = 50;

// ============================================================================
// 工具
// ============================================================================

async function getApiBase() {
  const { apiBase } = await chrome.storage.local.get('apiBase');
  return apiBase || DEFAULT_API_BASE;
}

async function getAuthToken() {
  const { authToken } = await chrome.storage.local.get('authToken');
  return authToken || '';
}

function canonicalizeUrl(url) {
  if (!url) return url;
  try {
    const u = new URL(url);
    // 强制 https
    if (u.protocol === 'http:') u.protocol = 'https:';
    // 去 utm_*
    const TRACKING = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                      'fbclid', 'gclid', 'mc_cid', 'mc_eid', '_ga'];
    TRACKING.forEach(p => u.searchParams.delete(p));
    // 去末尾 /
    let pathname = u.pathname;
    if (pathname.endsWith('/') && pathname.length > 1) {
      pathname = pathname.slice(0, -1);
    }
    u.pathname = pathname;
    // 去 fragment
    u.hash = '';
    return u.toString();
  } catch (e) {
    return url;
  }
}

function flattenBookmarks(nodes, folderPath = '') {
  // 把书签树扁平化为数组
  const result = [];
  for (const node of nodes) {
    const currentPath = folderPath
      ? (node.title ? `${folderPath}/${node.title}` : folderPath)
      : (node.title || '');

    if (node.url) {
      // 叶子节点（书签）
      result.push({
        url: node.url,
        title: node.title || node.url,
        folder_path: currentPath,
        date_added: node.dateAdded,
      });
    } else if (node.children) {
      // 文件夹 → 递归
      result.push(...flattenBookmarks(node.children, currentPath));
    }
  }
  return result;
}

function chunk(arr, size) {
  const chunks = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

async function callApi(path, method = 'POST', body = null) {
  const apiBase = await getApiBase();
  const token = await getAuthToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const resp = await fetch(`${apiBase}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`API ${resp.status}: ${text}`);
  }
  return resp.json();
}

// ============================================================================
// 核心同步
// ============================================================================

async function syncOne(bookmark) {
  const body = {
    url: bookmark.url,
    title: bookmark.title,
    description: bookmark.description || '',
    folder_path: bookmark.folder_path || '',
  };
  try {
    return await callApi('/bookmark/sync-from-extension', 'POST', body);
  } catch (e) {
    console.error('[bookmark-sync] syncOne failed:', e.message);
    return { status: 'error', error: e.message };
  }
}

async function syncBatch(bookmarks) {
  try {
    return await callApi('/bookmarks/sync-batch', 'POST', { bookmarks });
  } catch (e) {
    console.error('[bookmark-sync] syncBatch failed:', e.message);
    return { status: 'error', error: e.message };
  }
}

async function syncAll() {
  console.log('[bookmark-sync] 开始全量同步...');
  const tree = await chrome.bookmarks.getTree();
  const all = flattenBookmarks(tree);

  let totalAdded = 0, totalSkipped = 0, totalErrors = 0;

  // 分批推送（每批 50 条）
  const batches = chunk(all, MAX_BATCH_SIZE);
  for (const batch of batches) {
    const result = await syncBatch(batch);
    if (result.status === 'success') {
      totalAdded += result.stats.added;
      totalSkipped += result.stats.skipped;
      totalErrors += result.stats.errors;
    } else {
      totalErrors += batch.length;
    }
  }

  const summary = { total: all.length, added: totalAdded, skipped: totalSkipped, errors: totalErrors };
  console.log('[bookmark-sync] 同步完成:', summary);
  await chrome.storage.local.set({ lastSyncResult: summary, lastSyncAt: new Date().toISOString() });
  return summary;
}

// ============================================================================
// 事件监听
// ============================================================================

// 新增书签
chrome.bookmarks.onCreated.addListener(async (id, bookmark) => {
  if (!bookmark.url) return;
  const result = await syncOne({
    url: bookmark.url,
    title: bookmark.title,
    folder_path: bookmark.path || '',
  });
  if (result.status === 'success') {
    console.log('[bookmark-sync] 新增已同步:', bookmark.title);
  }
});

// 修改书签
chrome.bookmarks.onChanged.addListener(async (id, changeInfo) => {
  if (!changeInfo.url) return;
  await syncOne({
    url: changeInfo.url,
    title: changeInfo.title,
  });
});

// 定期全量同步
chrome.alarms.create(SYNC_ALARM_NAME, { periodInMinutes: SYNC_PERIOD_MIN });
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === SYNC_ALARM_NAME) {
    await syncAll();
  }
});

// 安装时立即同步
chrome.runtime.onInstalled.addListener(async () => {
  console.log('[bookmark-sync] 扩展已安装，启动首次同步');
  await syncAll();
});

// ============================================================================
// 消息接口（popup 调用）
// ============================================================================

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    try {
      if (msg.type === 'sync-all') {
        const result = await syncAll();
        sendResponse({ ok: true, result });
      } else if (msg.type === 'sync-current-tab') {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab || !tab.url) {
          sendResponse({ ok: false, error: '没有活动 tab' });
          return;
        }
        const result = await syncOne({
          url: tab.url,
          title: tab.title,
        });
        sendResponse({ ok: result.status === 'success', result });
      } else if (msg.type === 'get-status') {
        const { lastSyncResult, lastSyncAt } = await chrome.storage.local.get(['lastSyncResult', 'lastSyncAt']);
        sendResponse({ ok: true, lastSyncResult, lastSyncAt });
      } else if (msg.type === 'set-config') {
        await chrome.storage.local.set({ apiBase: msg.apiBase, authToken: msg.authToken || '' });
        sendResponse({ ok: true });
      } else {
        sendResponse({ ok: false, error: '未知消息' });
      }
    } catch (e) {
      sendResponse({ ok: false, error: e.message });
    }
  })();
  return true; // 异步响应
});
