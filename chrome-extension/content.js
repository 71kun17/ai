// AI客服助手 - Ozon按钮模式 (始终显示)
const API_BASE = 'http://124.221.93.157/api';
let config = { enabled: true, lang: 'zh' };

chrome.storage.local.get(['enabled', 'lang'], (data) => {
  config = { ...config, ...data };
  if (config.enabled) createButton();
});

function createButton() {
  if (document.getElementById('ai-reply-btn')) return;
  const host = location.hostname;
  if (!host.includes('ozon')) return;

  const btn = document.createElement('div');
  btn.id = 'ai-reply-btn';
  btn.innerHTML = '🤖';
  btn.title = 'AI自动回复';
  btn.style.cssText = 'position:fixed;bottom:100px;right:20px;z-index:999999;width:48px;height:48px;background:#409eff;color:#fff;border:none;border-radius:50%;font-size:22px;cursor:pointer;box-shadow:0 3px 12px rgba(64,158,255,0.4);display:flex;align-items:center;justify-content:center;transition:transform 0.2s';
  btn.onmouseenter = () => btn.style.transform = 'scale(1.15)';
  btn.onmouseleave = () => btn.style.transform = 'scale(1)';
  btn.onclick = async () => {
    btn.style.background = '#909399';
    btn.innerHTML = '<span style=font-size:12px>...</span>';
    
    // 尽可能抓取页面上看起来像消息的文本
    const texts = [];
    document.querySelectorAll('div,p,span').forEach(el => {
      const t = el.textContent?.trim();
      if (t && t.length > 8 && t.length < 2000 && el.children.length === 0 && el.offsetParent) {
        texts.push(t);
      }
    });
    const context = [...new Set(texts)].slice(-6).join('\n');
    
    try {
      const resp = await fetch(API_BASE + '/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: '请根据以下对话上下文，生成一条简短专业的客服回复：\n' + context,
          lang: config.lang,
          session_id: 'ozon_' + Date.now()
        })
      });
      const data = await resp.json();
      if (data.answer) {
        await navigator.clipboard.writeText(data.answer);
        btn.innerHTML = '✅';
        btn.style.background = '#67c23a';
        // 尝试填入输入框
        setTimeout(() => tryFillInput(data.answer), 100);
      } else {
        btn.innerHTML = '❌';
        btn.style.background = '#f56c6c';
      }
    } catch {
      btn.innerHTML = '❌';
      btn.style.background = '#f56c6c';
    }
    setTimeout(() => { btn.innerHTML = '🤖'; btn.style.background = '#409eff'; }, 2500);
  };
  document.body.appendChild(btn);
  console.log('[AI客服] 按钮已创建');
}

function tryFillInput(text) {
  // 尝试所有可能的输入元素
  const candidates = [
    ...document.querySelectorAll('div[contenteditable="true"]'),
    ...document.querySelectorAll('textarea'),
    ...document.querySelectorAll('[role="textbox"]'),
    ...document.querySelectorAll('[data-test-id*="input" i]'),
    ...document.querySelectorAll('[data-test-id*="chat" i]'),
    document.activeElement
  ].filter(Boolean);
  
  for (const el of candidates) {
    if (!el.offsetParent) continue;
    try {
      if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
        el.value = text;
      } else {
        el.textContent = text;
        el.innerHTML = text;
      }
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.focus();
      console.log('[AI客服] 已填入:', el.tagName, el.className?.slice(0,20));
      return;
    } catch {}
  }
  console.log('[AI客服] 未找到输入框，已复制到剪贴板');
}

// 页面变化时重新尝试
let attempts = 0;
const retry = setInterval(() => {
  if (document.getElementById('ai-reply-btn')) {
    if (attempts > 5) { clearInterval(retry); return; }
    attempts++;
    return;
  }
  if (document.body) createButton();
}, 1000);

console.log('[AI客服] Ozon按钮模式已加载');