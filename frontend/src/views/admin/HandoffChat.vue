<template>
  <div class="handoff-container">
    <div class="queue-panel">
      <h3 style="margin:0 0 12px 0;font-size:15px">
        <el-icon style="margin-right:4px"><UserFilled /></el-icon> 等待列表
        <el-badge v-if="queue.length" :value="queue.length" style="margin-left:4px" />
      </h3>
      <div v-if="queue.length === 0" style="text-align:center;color:#909399;padding:30px 0">
        暂无等待会话
      </div>
      <div
        v-for="item in queue"
        :key="item.session_id"
        :class="['queue-item', { active: selectedSession === item.session_id }]"
        @click="selectSession(item)"
      >
        <div class="queue-item-top">
          <el-tag :type="item.status === 'waiting' ? 'warning' : 'success'" size="small">
            {{ item.status === 'waiting' ? '等待中' : '对话中' }}
          </el-tag>
          <span style="font-size:12px;color:#909399">{{ item.session_id.slice(0, 8) }}</span>
        </div>
        <div style="font-size:11px;color:#909399;margin-bottom:2px">{{ langLabel(item.lang) }}</div>
        <div class="queue-item-msg">{{ item.last_message || '(暂无消息)' }}</div>
        <div style="font-size:11px;color:#c0c4cc">{{ item.updated_at?.slice(11, 19) }}</div>
      </div>
    </div>

    <div class="chat-panel">
      <template v-if="!selectedSession">
        <div style="display:flex;align-items:center;justify-content:center;height:100%;color:#909399;font-size:15px">
          请从左侧选择一个会话开始聊天
        </div>
      </template>
      <template v-else>
        <div class="chat-panel-header">
          <span>{{ selectedSession.slice(0, 12) }}... <span style="color:#909399;font-size:12px">| {{ currentStatus === 'waiting' ? '等待接入' : currentStatus === 'active' ? '对话中' : '已结束' }} | {{ currentLang ? langLabel(currentLang) : '' }}</span></span>
          <div style="display:flex;gap:8px">
            <el-button v-if="currentStatus === 'waiting'" type="primary" size="small" @click="takeover">接入</el-button>
            <el-button v-if="currentStatus === 'active'" type="warning" size="small" @click="resolve">结束会话</el-button>
          </div>
        </div>
        <div class="chat-panel-msgs" ref="msgContainer">
          <div v-for="(msg, i) in messages" :key="i" :class="['h-msg', msg.role]">
            <template v-if="msg.role === 'system'">
              <div class="h-system">{{ msg.content }}</div>
            </template>
            <template v-else>
              <div class="h-avatar">
                <el-icon v-if="msg.role === 'user'" :size="16"><User /></el-icon>
                <el-icon v-else :size="16"><Headset /></el-icon>
              </div>
              <div class="h-bubble">{{ msg.content }}</div>
            </template>
          </div>
        </div>
        <div class="chat-panel-input" v-if="currentStatus === 'waiting' || currentStatus === 'active'">
          <el-input
            v-model="replyText"
            placeholder="输入回复..."
            @keyup.enter="sendReply"
            :disabled="currentStatus === 'waiting'"
          >
            <template #append>
              <el-button @click="sendReply" :disabled="currentStatus === 'waiting' || !replyText.trim()" type="primary">发送</el-button>
            </template>
          </el-input>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

interface QueueItem {
  session_id: string
  status: string
  admin_name: string
  lang: string
  created_at: string
  updated_at: string
  last_message: string
  last_role: string
}

interface HandoffMsg {
  role: string
  content: string
  time: string
}

const queue = ref<QueueItem[]>([])
const selectedSession = ref('')
const currentStatus = ref('')
const currentLang = ref('')
const messages = ref<HandoffMsg[]>([])
const replyText = ref('')
const msgContainer = ref<HTMLElement>()
let pollTimer: ReturnType<typeof setInterval> | null = null
let msgPollTimer: ReturnType<typeof setInterval> | null = null

const fetchQueue = async () => {
  try {
    const r = await fetch('/api/chat/handoff/queue')
    queue.value = await r.json()
  } catch {}
}

const fetchMessages = async () => {
  if (!selectedSession.value) return
  try {
    const r = await fetch(`/api/chat/handoff/${selectedSession.value}/messages`)
    messages.value = await r.json()
    await nextTick()
    scrollBottom()
  } catch {}
}

const selectSession = async (item: QueueItem) => {
  selectedSession.value = item.session_id
  currentStatus.value = item.status
  currentLang.value = item.lang || 'zh'
  await fetchMessages()
}

const takeover = async () => {
  try {
    await fetch('/api/chat/handoff/takeover', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: selectedSession.value, admin_name: '客服' })
    })
    currentStatus.value = 'active'
    await fetchQueue()
    await fetchMessages()
  } catch {}
}

const sendReply = async () => {
  const text = replyText.value.trim()
  if (!text || currentStatus.value !== 'active') return
  replyText.value = ''
  try {
    await fetch('/api/chat/handoff/reply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: selectedSession.value, message: text, admin_name: '客服' })
    })
    await fetchMessages()
  } catch {}
}

const resolve = async () => {
  try {
    await fetch('/api/chat/handoff/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: selectedSession.value, admin_name: '客服' })
    })
    currentStatus.value = 'resolved'
    await fetchQueue()
    await fetchMessages()
  } catch {}
}

const langLabels: Record<string, string> = {
  zh: '🇨🇳 中文', en: '🇺🇸 English', ja: '🇯🇵 日本語',
  ko: '🇰🇷 한국어', fr: '🇫🇷 Français', es: '🇪🇸 Español', de: '🇩🇪 Deutsch'
}
const langLabel = (lang: string) => langLabels[lang] || '🇨🇳 中文'

const scrollBottom = () => {
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  }
}

onMounted(() => {
  fetchQueue()
  pollTimer = setInterval(fetchQueue, 5000)
  msgPollTimer = setInterval(() => {
    if (selectedSession.value) fetchMessages()
  }, 3000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (msgPollTimer) clearInterval(msgPollTimer)
})
</script>

<style scoped>
.handoff-container {
  display: flex;
  height: calc(100vh - 120px);
  gap: 0;
}
.queue-panel {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  padding: 12px;
  overflow-y: auto;
  flex-shrink: 0;
}
.queue-item {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 4px;
  transition: background 0.2s;
}
.queue-item:hover { background: #f5f7fa; }
.queue-item.active { background: #ecf5ff; border-left: 3px solid #409eff; }
.queue-item-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.queue-item-msg {
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}
.chat-panel-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
}
.chat-panel-msgs {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
}
.h-msg {
  margin-bottom: 14px;
  display: flex;
  gap: 8px;
}
.h-msg.user {
  flex-direction: row-reverse;
}
.h-msg.admin {
  flex-direction: row;
}
.h-system {
  text-align: center;
  color: #909399;
  font-size: 12px;
  width: 100%;
  padding: 4px 0;
}
.h-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}
.h-bubble {
  max-width: 70%;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}
.h-msg.user .h-bubble {
  background: #409eff;
  color: #fff;
  border-radius: 14px 4px 14px 14px;
}
.h-msg.admin .h-bubble {
  background: #fff;
  border-radius: 4px 14px 14px 14px;
  border: 1px solid #e4e7ed;
}
.chat-panel-input {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
}
</style>
