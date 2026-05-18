<template>
  <div class="ozon-container">
    <div class="ozon-sidebar">
      <div style="padding:12px;border-bottom:1px solid #e4e7ed;display:flex;justify-content:space-between;align-items:center">
        <h3 style="margin:0;font-size:15px">💬 Ozon 聊天</h3>
        <el-button size="small" @click="loadChats" :loading="loading">刷新</el-button>
      </div>
      <div style="padding:8px 12px;font-size:12px;color:#909399">
        {{ chats.length }} 个对话，{{ totalUnread }} 未读
      </div>
      <div v-if="chats.length === 0 && !loading" style="text-align:center;color:#909399;padding:30px">暂无聊天</div>
      <div
        v-for="chat in chats"
        :key="chat.chat_id"
        :class="['chat-item', { active: selectedChat === chat.chat_id }]"
        @click="selectChat(chat)"
      >
        <div style="display:flex;justify-content:space-between;align-items:center">
          <el-tag size="small" :type="chat.chat_type === 'SELLER_SUPPORT' ? 'primary' : 'info'">
            {{ chat.chat_type || '未知' }}
          </el-tag>
          <el-badge v-if="chat.unread_count" :value="chat.unread_count" type="danger" />
        </div>
        <div style="font-size:12px;color:#909399;margin-top:4px">{{ chat.chat_id?.slice(0, 16) }}...</div>
        <div style="font-size:12px;color:#c0c4cc">{{ chat.created_at?.slice(0, 16)?.replace('T', ' ') }}</div>
      </div>
    </div>

    <div class="ozon-main">
      <template v-if="!selectedChat">
        <div style="display:flex;align-items:center;justify-content:center;height:100%;color:#909399">
          从左侧选择聊天查看消息
        </div>
      </template>
      <template v-else>
        <div class="ozon-header">
          <span>{{ selectedChat }}</span>
          <el-tag size="small">{{ messages.length }} 条消息</el-tag>
        </div>
        <div class="ozon-messages" ref="msgBox">
          <div v-for="m in messages" :key="m.message_id" :class="['msg', m.user_type === 'Customer' ? 'buyer' : m.user_type === 'Seller' ? 'seller' : 'system']">
            <div class="msg-meta">
              <span class="msg-user">{{ m.user_type === 'Customer' ? '👤 买家' : m.user_type === 'Seller' ? '🏪 卖家' : '🔔 系统' }}</span>
              <span class="msg-time">{{ m.created_at?.slice(0, 19)?.replace('T', ' ') }}</span>
            </div>
            <div class="msg-body" v-html="renderContent(m.content)" />
            <div v-if="m.order_number" class="msg-order">📦 订单: {{ m.order_number }}</div>
            <div v-if="m.is_image" class="msg-image">📷 包含图片</div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'

interface Chat {
  chat_id: string
  chat_type: string
  chat_status: string
  created_at: string
  unread_count: number
  last_message_id: string
}

interface Msg {
  message_id: string
  user_type: string
  user_id: string
  content: string
  is_read: boolean
  created_at: string
  is_image: boolean
  order_number: string
}

const chats = ref<Chat[]>([])
const messages = ref<Msg[]>([])
const selectedChat = ref('')
const totalUnread = ref(0)
const loading = ref(false)
const msgBox = ref<HTMLElement>()

const loadChats = async () => {
  loading.value = true
  try {
    const r = await fetch('/api/platforms/ozon/chats')
    const data = await r.json()
    chats.value = data.chats || []
    totalUnread.value = data.total_unread_count || 0
  } catch {}
  loading.value = false
}

const selectChat = async (chat: Chat) => {
  selectedChat.value = chat.chat_id
  loading.value = true
  try {
    const r = await fetch(`/api/platforms/ozon/chats/${chat.chat_id}/messages`)
    const data = await r.json()
    messages.value = (data.messages || []).reverse()
    await nextTick()
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  } catch {}
  loading.value = false
}

const renderContent = (text: string) => {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
}

onMounted(loadChats)
</script>

<style scoped>
.ozon-container { display: flex; height: calc(100vh - 120px); }
.ozon-sidebar {
  width: 280px; background: #fff; border-right: 1px solid #e4e7ed;
  overflow-y: auto; flex-shrink: 0;
}
.chat-item {
  padding: 10px 12px; border-bottom: 1px solid #f0f0f0;
  cursor: pointer; transition: background 0.2s;
}
.chat-item:hover { background: #f5f7fa; }
.chat-item.active { background: #ecf5ff; border-left: 3px solid #409eff; }
.ozon-main { flex: 1; display: flex; flex-direction: column; background: #fff; }
.ozon-header {
  padding: 10px 16px; border-bottom: 1px solid #e4e7ed;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 13px; font-family: monospace;
}
.ozon-messages {
  flex: 1; overflow-y: auto; padding: 12px 16px; background: #f5f7fa;
}
.msg {
  margin-bottom: 14px; padding: 10px 14px; border-radius: 8px;
  background: #fff; border: 1px solid #ebeef5;
}
.msg.buyer { border-left: 3px solid #409eff; background: #ecf5ff; }
.msg.seller { border-left: 3px solid #67c23a; background: #f0f9eb; }
.msg.system { border-left: 3px solid #e6a23c; background: #fdf6ec; }
.msg-meta { display: flex; justify-content: space-between; margin-bottom: 6px; }
.msg-user { font-size: 12px; font-weight: 600; }
.msg-time { font-size: 11px; color: #909399; }
.msg-body { font-size: 13px; line-height: 1.6; word-break: break-word; }
.msg-order { font-size: 11px; color: #409eff; margin-top: 4px; }
.msg-image { font-size: 11px; color: #e6a23c; margin-top: 4px; }
</style>