<template>
  <div>
    <h2 class="page-title">数据看板</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card shadow="never" class="stat-card card-hover">
          <el-skeleton :loading="loading" animated>
            <template #template>
              <div style="padding:8px 0">
                <el-skeleton-item variant="text" style="width:60%;height:14px" />
                <el-skeleton-item variant="text" style="width:40%;height:28px;margin-top:8px" />
              </div>
            </template>
            <template #default>
              <el-statistic :title="card.label" :value="card.value" :suffix="card.suffix">
                <template #prefix>
                  <el-icon :size="20" :color="card.color"><component :is="card.icon" /></el-icon>
                </template>
              </el-statistic>
            </template>
          </el-skeleton>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card shadow="never" header="意图分布" class="chart-card">
          <div style="height:320px;position:relative">
            <div v-if="loading" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:#fff">
              <el-icon class="is-loading" :size="32" color="#c0c4cc"><Loading /></el-icon>
            </div>
            <div ref="intentChart" style="height:320px" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" header="每日对话趋势" class="chart-card">
          <div style="height:320px;position:relative">
            <div v-if="loading" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:#fff">
              <el-icon class="is-loading" :size="32" color="#c0c4cc"><Loading /></el-icon>
            </div>
            <div ref="trendChart" style="height:320px" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { analyticsApi } from '@/api'
import { ChatDotSquare, Warning, Star, Reading, Loading } from '@element-plus/icons-vue'

const loading = ref(true)

const cards = ref([
  { label: '总会话数', value: 0, suffix: '', icon: ChatDotSquare, color: '#1a73e8' },
  { label: '转人工率', value: 0, suffix: '%', icon: Warning, color: '#fbbc04' },
  { label: '满意度', value: 0, suffix: '%', icon: Star, color: '#34a853' },
  { label: '知识条目', value: 0, suffix: '', icon: Reading, color: '#ea4335' },
])

const intentChart = ref<HTMLElement>()
const trendChart = ref<HTMLElement>()

onMounted(async () => {
  try {
    const overview = (await analyticsApi.overview()).data
    cards.value[0].value = overview.total_sessions
    cards.value[1].value = overview.handoff_rate
    cards.value[2].value = overview.satisfaction_rate
    cards.value[3].value = overview.knowledge_count
  } catch { /* */ }

  loading.value = false
  await nextTick()

  try {
    const intents = (await analyticsApi.intents()).data
    const pieData = intents.length > 0
      ? intents.map((i: any) => ({ name: i.intent || '未知', value: i.count }))
      : [{ name: '暂无数据', value: 1, itemStyle: { color: '#e0e0e0' } }]
    if (intentChart.value) {
      echarts.init(intentChart.value).setOption({
        color: ['#1a73e8', '#34a853', '#fbbc04', '#ea4335', '#a142f4', '#00bcd4', '#ff6d00'],
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', radius: ['45%', '72%'], data: pieData, label: { formatter: '{b}\n{d}%' } }]
      })
    }
  } catch { /* */ }

  try {
    const trends = (await analyticsApi.trends(7)).data
    const dates = trends.map((t: any) => t.date.slice(5))
    const counts = trends.map((t: any) => t.count)
    if (trendChart.value) {
      echarts.init(trendChart.value).setOption({
        color: ['#1a73e8'],
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: dates.length > 0 ? dates : ['暂无'] },
        yAxis: { type: 'value', minInterval: 1 },
        series: [{
          type: 'line', data: counts.length > 0 ? counts : [0], smooth: true,
          areaStyle: { opacity: 0.12, color: '#1a73e8' },
          itemStyle: { color: '#1a73e8' },
          lineStyle: { color: '#1a73e8', width: 2 }
        }]
      })
    }
  } catch { /* */ }
})
</script>

<style scoped>
.page-title { margin: 0 0 20px 0; font-size: 20px; font-weight: 700; color: var(--c-text); }

.stat-card {
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
}
.stat-card :deep(.el-card__body) { padding: 20px; }

.chart-card {
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
}
.chart-card :deep(.el-card__header) {
  font-weight: 600;
  font-size: 15px;
  border-bottom: 1px solid var(--c-border);
}
</style>