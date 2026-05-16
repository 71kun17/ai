const API_BASE = 'http://127.0.0.1:8000/api';

const toggle = document.getElementById('toggle');
const langSelect = document.getElementById('lang');
const statusEl = document.getElementById('status');

// 加载状态
chrome.storage.local.get(['enabled', 'lang'], (data) => {
  toggle.checked = data.enabled !== false;
  if (data.lang) langSelect.value = data.lang;
});

// 切换开关
toggle.addEventListener('change', () => {
  chrome.storage.local.set({ enabled: toggle.checked });
});

// 切换语言
langSelect.addEventListener('change', () => {
  chrome.storage.local.set({ lang: langSelect.value });
});

// 检查后端连通性
async function checkBackend() {
  try {
    const resp = await fetch(`${API_BASE}/health`);
    if (resp.ok) {
      statusEl.textContent = '✅ 后端已连接';
      statusEl.className = 'status ok';
    } else {
      throw new Error();
    }
  } catch {
    statusEl.textContent = '❌ 后端未启动 (127.0.0.1:8000)';
    statusEl.className = 'status err';
  }
}

checkBackend();
setInterval(checkBackend, 5000);