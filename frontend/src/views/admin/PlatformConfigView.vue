<template>
  <div>
    <h2 style="margin-bottom:20px">平台管理</h2>

    <el-card>
      <template #header>虾皮 (Shopee) API 配置</template>
      <el-form :model="form" label-width="140px" @submit.prevent="save">
        <el-form-item label="Partner ID">
          <el-input v-model="form.api_key" placeholder="虾皮开放平台 Partner ID" />
        </el-form-item>
        <el-form-item label="Partner Key">
          <el-input v-model="form.api_secret" type="password" placeholder="虾皮开放平台 Partner Key" show-password />
        </el-form-item>
        <el-form-item label="Shop ID">
          <el-input v-model="form.shop_id" placeholder="店铺 ID" />
        </el-form-item>
        <el-form-item label="轮询间隔(秒)">
          <el-input-number v-model="form.poll_interval" :min="10" :max="300" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="save" :loading="saving">保存配置</el-button>
          <el-button @click="load">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:20px">
      <template #header>Ozon Seller API 配置</template>
      <el-form :model="ozonForm" label-width="140px" @submit.prevent="saveOzon">
        <el-form-item label="Client-Id">
          <el-input v-model="ozonForm.api_key" placeholder="Ozon API Client-Id" />
        </el-form-item>
        <el-form-item label="Api-Key">
          <el-input v-model="ozonForm.api_secret" type="password" placeholder="Ozon API Key" show-password />
        </el-form-item>
        <el-form-item label="轮询间隔(秒)">
          <el-input-number v-model="ozonForm.poll_interval" :min="10" :max="300" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveOzon" :loading="saving">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:20px">
      <template #header>已接入平台</template>
      <el-table :data="platforms" stripe>
        <el-table-column prop="platform_name" label="平台标识" />
        <el-table-column prop="display_name" label="显示名称" />
        <el-table-column prop="poll_interval" label="轮询间隔(s)" />
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '运行中' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { configApi } from '@/api'
import { ElMessage } from 'element-plus'

const form = ref({ api_key: '', api_secret: '', shop_id: '', poll_interval: 30 })
const ozonForm = ref({ api_key: '', api_secret: '', poll_interval: 30 })
const platforms = ref<any[]>([])
const saving = ref(false)

const load = async () => {
  try {
    const res = await fetch('/api/platforms')
    platforms.value = await res.json()
  } catch {}
}

const save = async () => {
  saving.value = true
  try {
    await fetch('/api/platforms/shopee/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platform_name: 'shopee',
        display_name: '虾皮',
        api_key: form.value.api_key,
        api_secret: form.value.api_secret,
        shop_id: form.value.shop_id,
        poll_interval: form.value.poll_interval
      })
    })
    ElMessage.success('保存成功，重启后端后生效')
    await load()
  } catch {
    ElMessage.error('保存失败')
  }
  saving.value = false
}

const saveOzon = async () => {
  saving.value = true
  try {
    await fetch('/api/platforms/ozon/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platform_name: 'ozon',
        display_name: 'Ozon',
        api_key: ozonForm.value.api_key,
        api_secret: ozonForm.value.api_secret,
        shop_id: '',
        poll_interval: ozonForm.value.poll_interval
      })
    })
    ElMessage.success('保存成功，重启后端后生效')
    await load()
  } catch {
    ElMessage.error('保存失败')
  }
  saving.value = false
}

onMounted(load)
</script>