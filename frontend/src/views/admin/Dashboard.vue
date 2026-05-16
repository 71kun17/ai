<template>
  <div>
    <h2 style="margin-bottom:20px">数据看板</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card shadow="hover">
          <el-statistic :title="card.label" :value="card.value" :suffix="card.suffix">
            <template #prefix><el-icon :size="20"><component :is="card.icon" /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card header="意图分布"><div ref="intentChart" style="height:320px" /></el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="每日对话趋势"><div ref="trendChart" style="height:320px" /></el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { analyticsApi } from '@/api'
import { ChatDotSquare, Warning, Star, Reading } from '@element-plus/icons-vue'

const cards = ref([
  { label: '总会话数', value: 0, suffix: '', icon: ChatDotSquare },
  { label: '转人工率', value: 0, suffix: '%', icon: Warning },
  { label: '满意度', value: 0, suffix: '%', icon: Star },
  { label: '知识条目', value: 0, suffix: '', icon: Reading },
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
  } catch { /* empty state */ }

  try {
    const intents = (await analyticsApi.intents()).data
    const pieData = intents.length > 0 ? intents.map((i: any) => ({ name: i.intent || '未知', value: i.count })) : [{ name: '暂无数据', value: 1 }]
    echarts.init(intentChart.value!).setOption({
      tooltip: { trigger: 'item' },
      series: [{ type: 'pie', radius: ['45%', '72%'], data: pieData, label: { formatter: '{b}\n{d}%' } }]
    })
  } catch { /* */ }

  try {
    const trends = (await analyticsApi.trends(7)).data
    const dates = trends.map((t: any) => t.date.slice(5))
    const counts = trends.map((t: any) => t.count)
    echarts.init(trendChart.value!).setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: dates.length > 0 ? dates : ['暂无'] },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{ type: 'line', data: counts.length > 0 ? counts : [0], smooth: true, areaStyle: { opacity: 0.15 }, itemStyle: { color: '#409eff' } }]
    })
  } catch { /* */ }
})
</script>
