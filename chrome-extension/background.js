// ── AI客服助手 Background Service Worker ──

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    enabled: true,
    platform: 'shopee',
    lang: 'zh'
  });
  console.log('[AI客服] 扩展已安装');
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'getStatus') {
    chrome.storage.local.get(['enabled', 'platform', 'lang'], (data) => {
      sendResponse(data);
    });
    return true;
  }
  
  if (msg.type === 'toggle') {
    chrome.storage.local.get(['enabled'], (data) => {
      chrome.storage.local.set({ enabled: !data.enabled });
      sendResponse({ enabled: !data.enabled });
    });
    return true;
  }

  if (msg.type === 'setLang') {
    chrome.storage.local.set({ lang: msg.lang });
    sendResponse({ ok: true });
    return true;
  }
});