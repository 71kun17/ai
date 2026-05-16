<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>知识库管理</h2>
      <el-button type="primary" @click="$router.push('/admin/knowledge/new')">+ 新增条目</el-button>
    </div>

    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="8">
        <el-input v-model="searchText" placeholder="搜索问题或标题..." clearable @clear="fetchData" @keyup.enter="fetchData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </el-col>
      <el-col :span="4">
        <el-select v-model="filterCategory" placeholder="分类筛选" clearable @change="fetchData" style="width:100%">
          <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-button @click="fetchData">查询</el-button>
      </el-col>
    </el-row>

    <el-table :data="items" stripe border style="width:100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" width="160" />
      <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">{{ row.status === 'published' ? '已发布' : '草稿' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="170">
        <template #default="{ row }">{{ row.updated_at?.slice(0, 16) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/admin/knowledge/${row.id}`)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page" :page-size="pageSize" :total="total"
      layout="total, prev, pager, next" @current-change="fetchData"
      style="margin-top:16px;justify-content:flex-end"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { knowledgeApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const items = ref([])
const categories = ref<string[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const searchText = ref('')
const filterCategory = ref('')

const fetchData = async () => {
  loading.value = true
  try {
    const res = (await knowledgeApi.list({ page: page.value, page_size: pageSize, search: searchText.value || undefined, category: filterCategory.value || undefined })).data
    items.value = res.items
    total.value = res.total
    const cats = (await knowledgeApi.categories()).data
    categories.value = cats
  } catch { ElMessage.error('加载失败') }
  loading.value = false
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除「${row.title}」？`, '确认删除', { type: 'warning' })
    await knowledgeApi.delete(row.id)
    ElMessage.success('已删除')
    fetchData()
  } catch { /* canceled */ }
}

onMounted(fetchData)
</script>
