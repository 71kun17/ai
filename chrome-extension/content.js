// AI客服助手 Content Script - Shopee/Ozon/Amazon
const API_BASE = 'http://124.221.93.157:8000/api';
let config = { enabled: true, platform: 'shopee', lang: 'zh' };
let processedMessages = new Set();
let observer = null;

chrome.storage.local.get(['enabled', 'platform', 'lang'], (data) => {
  config = { ...config, ...data };
  if (config.enabled) startWatching();
});

chrome.storage.onChanged.addListener((changes) => {
  if (changes.enabled) config.enabled = changes.enabled.newValue;
  if (changes.lang) config.lang = changes.lang.newValue;
  if (config.enabled && !observer) startWatching();
  if (!config.enabled && observer) stopWatching();
});

function startWatching() {
  const host = location.hostname;
  console.log('[AI客服] 开始监听 ' + host + ' ...');
  
  observer = new MutationObserver((mutations) => {
    for (const m of mutations) {
      for (const node of m.addedNodes) {
        if (node.nodeType !== 1) continue;
        const messages = findBuyerMessages(node);
        for (const msg of messages) handleNewMessage(msg);
      }
    }
  });

  observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  scanExisting();
}

function stopWatching() {
  if (observer) { observer.disconnect(); observer = null; }
}

function findBuyerMessages(root) {
  const results = [];
  const host = location.hostname;
  let selectors = [];

  if (host.includes('ozon')) {
    // Ozon seller chat selectors
    selectors = [
      '[class*="message"]:not([class*="self"]):not([class*="mine"]):not([class*="own"])',
      'div[class*="bubble"]:not([class*="self"]):not([class*="mine"])',
      'div[class*="Message"][class*="incoming"]',
      'div[class*="chat-message"]:not([class*="outgoing"])'
    ];
  } else {
    // Shopee/Amazon selectors
    selectors = [
      '[class*="message"][class*="buyer"]',
      '[class*="msg"][class*="left"]',
      '[class*="chat-bubble"]:not([class*="self"])',
      '[data-sender="buyer"]',
      'div[class*="bubble"]:not([class*="mine"]):not([class*="self"])'
    ];
  }
  
  for (const sel of selectors) {
    try {
      const els = root.querySelectorAll ? root.querySelectorAll(sel) : [];
      for (const el of els) results.push(el);
      if (root.matches && root.matches(sel)) results.push(root);
    } catch {}
  }
  
  return results;
}

let processingQueue = Promise.resolve();

function handleNewMessage(el) {
  const text = el.textContent && el.textContent.trim();
  if (!text || text.length < 2 || text.length > 2000) return;
  
  const hash = simpleHash(text);
  if (processedMessages.has(hash)) return;
  processedMessages.add(hash);
  
  if (processedMessages.size > 500) {
    const arr = [...processedMessages];
    processedMessages = new Set(arr.slice(-300));
  }

  console.log('[AI客服] 买家消息:', text.slice(0, 60));
  processingQueue = processingQueue.then(() => processMessage(text, el));
}

async function processMessage(text, el) {
  try {
    const resp = await fetch(API_BASE + '/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        lang: config.lang,
        session_id: 'ext_' + Date.now()
      })
    });
    
    const data = await resp.json();
    if (data.answer) {
      console.log('[AI客服] AI回复:', data.answer.slice(0, 60));
      fillReply(data.answer);
    }
  } catch (err) {
    console.error('[AI客服] API调用失败:', err.message);
  }
}

function fillReply(text) {
  const host = location.hostname;
  let inputSelectors, sendSelectors;

  if (host.includes('ozon')) {
    inputSelectors = [
      'div[contenteditable="true"]',
      'textarea',
      '[class*="ChatInput"] textarea',
      '[class*="chat-input"]',
      '[class*="editor"]'
    ];
    sendSelectors = [
      'button[class*="send"]',
      'button[class*="Send"]',
      'svg[class*="send"]',
      'button:has(svg)'
    ];
  } else {
    inputSelectors = [
      'textarea',
      '[contenteditable="true"]',
      '[class*="input"]',
      '[class*="editor"]',
      '[role="textbox"]',
      'input[type="text"]'
    ];
    sendSelectors = [
      'button[class*="send"]',
      'button[class*="submit"]',
      '[class*="send-btn"]',
      'button:has(svg)'
    ];
  }

  let input = null;
  for (const sel of inputSelectors) {
    const el = document.querySelector(sel);
    if (el && el.offsetParent !== null) { input = el; break; }
  }

  if (!input) {
    console.log('[AI客服] 未找到输入框');
    return;
  }

  if (input.tagName === 'TEXTAREA' || input.tagName === 'INPUT') {
    input.value = text;
    input.dispatchEvent(new Event('input', { bubbles: true }));
  } else {
    input.textContent = text;
    input.dispatchEvent(new Event('input', { bubbles: true }));
  }

  setTimeout(() => {
    for (const sel of sendSelectors) {
      const btn = document.querySelector(sel);
      if (btn && btn.offsetParent !== null) {
        btn.click();
        console.log('[AI客服] 已发送回复');
        return;
      }
    }
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    console.log('[AI客服] 尝试回车发送');
  }, 500);
}

function scanExisting() {
  const all = findBuyerMessages(document.body);
  for (const el of all) handleNewMessage(el);
}

function simpleHash(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  }
  return h.toString(36);
}

console.log('[AI客服] Content Script 已加载 (' + location.hostname + ')');