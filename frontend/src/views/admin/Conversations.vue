<template>
  <div>
    <h2 style="margin-bottom:16px">对话记录</h2>
    <el-table :data="sessions" stripe v-loading="loading" @row-click="showDetail" style="cursor:pointer">
      <el-table-column prop="session_id" label="会话ID" width="280" show-overflow-tooltip />
      <el-table-column prop="started" label="开始时间" width="180">
        <template #default="{ row }">{{ row.started?.slice(0, 16) }}</template>
      </el-table-column>
      <el-table-column prop="msg_count" label="消息数" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" @click.stop="showDetail(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="对话详情" width="700px">
      <div class="detail-chat">
        <div v-for="(msg, i) in detailMsgs" :key="i" :class="['d-msg', msg.role]">
          <strong>{{ msg.role === 'user' ? '👤 用户' : '🤖 客服' }}</strong>
          <span style="color:#909399;font-size:12px;margin-left:8px">{{ msg.time?.slice(11, 16) }}</span>
          <div class="d-bubble">{{ msg.message }}</div>
        </div>
        <div v-if="detailMsgs.length === 0" style="text-align:center;color:#909399;padding:20px">暂无对话记录</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { analyticsApi, chatApi } from '@/api'

const sessions = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const detailMsgs = ref<any[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const res = (await analyticsApi.recentSessions()).data
    sessions.value = res
  } catch { /* */ }
  loading.value = false
})

const showDetail = async (row: any) => {
  dialogVisible.value = true
  try {
    const res = (await chatApi.history(row.session_id)).data
    detailMsgs.value = res
  } catch { detailMsgs.value = [] }
}
</script>

<style scoped>
.detail-chat { max-height: 400px; overflow-y: auto; }
.d-msg { margin-bottom: 14px; }
.d-msg.user .d-bubble { background: #ecf5ff; border-left: 3px solid #409eff; }
.d-msg.assistant .d-bubble { background: #f0f9eb; border-left: 3px solid #67c23a; }
.d-bubble { padding: 8px 12px; margin-top: 4px; border-radius: 4px; font-size: 14px; }
</style>
