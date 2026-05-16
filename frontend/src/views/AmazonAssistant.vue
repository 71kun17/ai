<template>
  <div class="amazon-container">
    <!-- 顶部导航 -->
    <div class="top-bar">
      <div class="top-left">
        <el-button text @click="$router.push('/')">
          <el-icon><ArrowLeft /></el-icon> 返回客服
        </el-button>
        <span class="title">📦 亚马逊消息辅助</span>
      </div>
      <el-button size="small" text @click="$router.push('/admin')">管理后台</el-button>
    </div>

    <div class="main-area">
      <!-- 左侧：粘贴区 -->
      <div class="panel paste-panel">
        <div class="panel-header">
          <span>📋 粘贴亚马逊对话</span>
          <el-button size="small" type="primary" @click="analyze" :loading="loading" :disabled="!inputText.trim()">
            🔍 分析对话
          </el-button>
        </div>
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="18"
          placeholder="从亚马逊买家消息页面复制对话文本粘贴到这里...

示例：
Buyer: Hi, I received the item but it's damaged. I want a refund.
Seller: Sorry to hear that. Could you send photos?
Buyer: Yes, here they are. I'm very upset about this."
          resize="none"
          clearable
        />
        <div class="paste-hint">
          <el-icon><InfoFilled /></el-icon>
          提示：在亚马逊买家消息页面选中对话内容，Ctrl+C 复制后在此处 Ctrl+V 粘贴，然后点击「分析对话」
        </div>
      </div>

      <!-- 右侧：分析结果 -->
      <div class="panel result-panel">
        <div class="panel-header">
          <span>💡 分析结果</span>
          <el-button v-if="result" size="small" text @click="reset">清空</el-button>
        </div>

        <!-- 空状态 -->
        <div v-if="!result" class="empty-state">
          <div class="empty-icon">🤖</div>
          <p>粘贴对话文本后点击「分析对话」</p>
          <p class="empty-sub">AI 将自动识别买家意图并生成回复建议</p>
        </div>

        <!-- 分析结果 -->
        <div v-if="result" class="result-content">
          <!-- 概览卡片 -->
          <div class="overview-cards">
            <div class="oc-item">
              <div class="oc-label">买家意图</div>
              <el-tag :type="intentTagType" size="large">{{ result.intent }}</el-tag>
            </div>
            <div class="oc-item">
              <div class="oc-label">情绪状态</div>
              <el-tag :type="sentimentTagType" size="large">{{ result.sentiment }}</el-tag>
            </div>
            <div class="oc-item" v-if="result.buyer_name">
              <div class="oc-label">买家</div>
              <span class="buyer-name">{{ result.buyer_name }}</span>
            </div>
          </div>

          <!-- 摘要 -->
          <div class="summary-box">
            <div class="section-title">📝 诉求摘要</div>
            <p>{{ result.summary }}</p>
          </div>

          <!-- 关键信息 -->
          <div v-if="result.key_points?.length" class="key-points-box">
            <div class="section-title">🔑 关键信息</div>
            <ul>
              <li v-for="(kp, i) in result.key_points" :key="i">{{ kp }}</li>
            </ul>
          </div>

          <!-- 回复选项 -->
          <div class="responses-box">
            <div class="section-title">✍️ 回复建议（点击复制）</div>
            <div
              v-for="(resp, i) in result.responses"
              :key="i"
              class="response-card"
              :class="{ copied: copiedIndex === i }"
              @click="copyResponse(resp.text, i)"
            >
              <div class="resp-header">
                <el-tag size="small" effect="dark" :type="respStyleType(resp.style)">{{ resp.style }}</el-tag>
                <span class="copy-icon">{{ copiedIndex === i ? '✅ 已复制' : '📋 点击复制' }}</span>
              </div>
              <div class="resp-text">{{ resp.text }}</div>
              <div v-if="resp.note" class="resp-note">💬 {{ resp.note }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { amazonApi } from '@/api'
import { ElMessage } from 'element-plus'

interface ResponseItem {
  style: string
  text: string
  note: string
}

interface AnalyzeResult {
  buyer_name: string
  summary: string
  intent: string
  sentiment: string
  key_points: string[]
  responses: ResponseItem[]
}

const inputText = ref('')
const loading = ref(false)
const result = ref<AnalyzeResult | null>(null)
const copiedIndex = ref(-1)

const analyze = async () => {
  if (!inputText.value.trim()) return
  loading.value = true
  result.value = null
  try {
    const res = (await amazonApi.analyze({ text: inputText.value })).data
    result.value = res
  } catch {
    ElMessage.error('分析失败，请检查后端服务是否启动')
  }
  loading.value = false
}

const copyResponse = async (text: string, index: number) => {
  try {
    await navigator.clipboard.writeText(text)
    copiedIndex.value = index
    ElMessage.success('已复制到剪贴板，可直接粘贴到亚马逊回复框')
    setTimeout(() => { copiedIndex.value = -1 }, 2000)
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

const reset = () => {
  result.value = null
  copiedIndex.value = -1
}

const intentTagType = (intent: string) => {
  const map: Record<string, string> = { '投诉': 'danger', '退换货': 'warning', '售后': 'warning', '议价': 'info', '物流查询': '', '商品咨询': 'success' }
  return map[intent] || ''
}

const sentimentTagType = (sentiment: string) => {
  const map: Record<string, string> = { '愤怒': 'danger', '焦虑': 'warning', '中性': 'info', '积极': 'success' }
  return map[sentiment] || 'info'
}

const respStyleType = (style: string) => {
  if (style.includes('专业')) return ''
  if (style.includes('温和') || style.includes('安抚')) return 'success'
  if (style.includes('简洁') || style.includes('高效')) return 'info'
  if (style.includes('促销')) return 'warning'
  return ''
}
</script>

<style scoped>
.amazon-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.top-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.main-area {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 16px 24px;
  overflow: hidden;
}

.panel {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.paste-panel {
  flex: 1;
  min-width: 0;
}
.paste-panel :deep(.el-textarea__inner) {
  border: none;
  border-radius: 0;
  font-size: 14px;
  line-height: 1.7;
  flex: 1;
}
.paste-panel :deep(.el-textarea) {
  flex: 1;
  display: flex;
}
.paste-panel :deep(.el-textarea__inner:focus) {
  box-shadow: none;
}
.paste-hint {
  padding: 10px 20px;
  font-size: 12px;
  color: #909399;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  gap: 4px;
}

.result-panel {
  flex: 1;
  min-width: 0;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}
.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}
.empty-sub {
  font-size: 13px;
  margin-top: 4px;
}

.result-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overview-cards {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.oc-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.oc-label {
  font-size: 12px;
  color: #909399;
}
.buyer-name {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.summary-box, .key-points-box, .responses-box {
  background: #fafafa;
  border-radius: 8px;
  padding: 14px 16px;
}
.section-title {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
}
.summary-box p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}
.key-points-box ul {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.response-card {
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.response-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64,158,255,0.15);
  transform: translateY(-1px);
}
.response-card.copied {
  border-color: #67c23a;
  background: #f0f9eb;
}
.resp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.copy-icon {
  font-size: 12px;
  color: #909399;
}
.resp-text {
  font-size: 14px;
  line-height: 1.7;
  color: #303133;
}
.resp-note {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  font-style: italic;
}
</style>
