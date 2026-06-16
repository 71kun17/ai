<template>
  <div>
    <h2 style="margin-bottom:20px">自动回复统计</h2>

    <el-row :gutter="20">
      <el-col :span="6" v-for="s in stats" :key="s.platform">
        <el-card>
          <template #header>{{ s.platform }}</template>
          <el-statistic title="总消息" :value="s.total_messages" />
          <el-divider />
          <el-row>
            <el-col :span="8">
              <el-statistic title="自动回复" :value="s.auto_replied">
                <template #suffix>
                  <el-tag type="success" size="small">{{ percent(s.auto_replied, s.total_messages) }}</el-tag>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic title="待审核" :value="s.pending_review">
                <template #suffix>
                  <el-tag type="warning" size="small">{{ percent(s.pending_review, s.total_messages) }}</el-tag>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic title="已拒绝" :value="s.rejected">
                <template #suffix>
                  <el-tag type="danger" size="small">{{ percent(s.rejected, s.total_messages) }}</el-tag>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="stats.length === 0" description="暂无数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const stats = ref<any[]>([])

const load = async () => {
  try {
    const res = await fetch('/api/platforms/stats')
    stats.value = await res.json()
  } catch {}
}

const percent = (val: number, total: number) => {
  if (!total) return '0%'
  return Math.round(val / total * 100) + '%'
}

onMounted(load)
</script>