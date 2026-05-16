<template>
  <div>
    <h2 style="margin-bottom:20px">待审核消息</h2>

    <el-table :data="messages" stripe v-loading="loading" empty-text="暂无待审核消息">
      <el-table-column prop="platform" label="平台" width="80" />
      <el-table-column prop="buyer_name" label="买家" width="120" />
      <el-table-column prop="content" label="消息内容" min-width="300" show-overflow-tooltip />
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="success" size="small" @click="approve(row)">批准</el-button>
          <el-button type="danger" size="small" @click="reject(row)">拒绝</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="审核回复" width="500px">
      <el-input v-model="replyText" type="textarea" :rows="4" placeholder="输入要发送的回复..." />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmApprove" :loading="submitting">确认发送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const messages = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const replyText = ref('')
const currentRow = ref<any>(null)
const submitting = ref(false)

const load = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/platforms/review?limit=50')
    messages.value = await res.json()
  } catch {}
  loading.value = false
}

const approve = (row: any) => {
  currentRow.value = row
  replyText.value = ''
  dialogVisible.value = true
}

const confirmApprove = async () => {
  submitting.value = true
  try {
    await fetch(`/api/platforms/review/${currentRow.value.id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reply_text: replyText.value })
    })
    ElMessage.success('已批准')
    dialogVisible.value = false
    await load()
  } catch {
    ElMessage.error('操作失败')
  }
  submitting.value = false
}

const reject = async (row: any) => {
  await ElMessageBox.confirm('确定拒绝此消息？将标记为转人工处理。', '确认', { type: 'warning' })
  try {
    await fetch(`/api/platforms/review/${row.id}/reject`, { method: 'POST' })
    ElMessage.success('已拒绝')
    await load()
  } catch {
    ElMessage.error('操作失败')
  }
}

const formatTime = (t: string) => {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(load)
</script>