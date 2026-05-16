<template>
  <div style="max-width:800px">
    <h2>{{ isEdit ? '编辑知识条目' : '新增知识条目' }}</h2>
    <el-form :model="form" label-width="80px" style="margin-top:20px">
      <el-form-item label="标题">
        <el-input v-model="form.title" placeholder="如：物流查询FAQ" />
      </el-form-item>
      <el-form-item label="问题">
        <el-input v-model="form.question" type="textarea" :rows="2" placeholder="用户可能问的问题..." />
      </el-form-item>
      <el-form-item label="回答">
        <el-input v-model="form.answer" type="textarea" :rows="5" placeholder="标准回答内容...（支持Markdown）" />
      </el-form-item>
      <el-form-item label="分类">
        <el-input v-model="form.category" placeholder="如：物流、售后、支付" />
      </el-form-item>
      <el-form-item label="标签">
        <el-input v-model="form.tags" placeholder="逗号分隔，如：快递,发货,配送" />
      </el-form-item>
      <el-form-item label="关键词">
        <el-input v-model="form.keywords" placeholder="逗号分隔，如：查询,进度,物流" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submit" :loading="saving">{{ isEdit ? '更新' : '创建' }}</el-button>
        <el-button @click="$router.back()">返回</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { knowledgeApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)

const form = ref({ title: '', question: '', answer: '', category: '通用', tags: '', keywords: '' })

onMounted(async () => {
  if (isEdit.value) {
    try {
      const res = (await knowledgeApi.get(Number(route.params.id))).data
      form.value = { title: res.title, question: res.question, answer: res.answer, category: res.category, tags: res.tags || '', keywords: res.keywords || '' }
    } catch { ElMessage.error('加载失败'); router.back() }
  }
})

const submit = async () => {
  if (!form.value.question || !form.value.answer) { ElMessage.warning('问题和回答不能为空'); return }
  saving.value = true
  try {
    if (isEdit.value) {
      await knowledgeApi.update(Number(route.params.id), form.value)
      ElMessage.success('已更新')
    } else {
      await knowledgeApi.create(form.value)
      ElMessage.success('已创建')
    }
    router.push('/admin/knowledge')
  } catch { ElMessage.error('保存失败') }
  saving.value = false
}
</script>
