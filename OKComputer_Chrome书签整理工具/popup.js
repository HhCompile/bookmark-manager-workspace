// popup.js - 弹窗交互逻辑
const $ = (id) => document.getElementById(id);

async function loadConfig() {
  const { apiBase, authToken } = await chrome.storage.local.get(['apiBase', 'authToken']);
  $('apiBase').value = apiBase || 'http://localhost:9001/v1';
  $('authToken').value = authToken || '';
}

async function saveConfig() {
  const apiBase = $('apiBase').value.trim();
  const authToken = $('authToken').value.trim();
  await chrome.runtime.sendMessage({ type: 'set-config', apiBase, authToken });
  setStatus('✅ 配置已保存');
}

async function syncAll() {
  $('syncAll').disabled = true;
  setStatus('🔄 正在全量同步...');
  const resp = await chrome.runtime.sendMessage({ type: 'sync-all' });
  if (resp.ok) {
    const { total, added, skipped, errors } = resp.result;
    setStatus(`✅ 同步完成\n总计 ${total} · 新增 ${added} · 跳过 ${skipped} · 失败 ${errors}`);
  } else {
    setStatus(`❌ 失败：${resp.error}`);
  }
  $('syncAll').disabled = false;
}

async function syncCurrent() {
  $('syncCurrent').disabled = true;
  setStatus('📌 正在同步当前页...');
  const resp = await chrome.runtime.sendMessage({ type: 'sync-current-tab' });
  if (resp.ok) {
    setStatus('✅ 当前页已同步');
  } else {
    setStatus(`❌ 失败：${resp.error}`);
  }
  $('syncCurrent').disabled = false;
}

function setStatus(msg) {
  $('status').textContent = msg;
}

document.addEventListener('DOMContentLoaded', async () => {
  await loadConfig();
  $('saveConfig').addEventListener('click', saveConfig);
  $('syncAll').addEventListener('click', syncAll);
  $('syncCurrent').addEventListener('click', syncCurrent);
});
