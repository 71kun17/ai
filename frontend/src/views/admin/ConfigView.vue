<template>
  <div style="max-width:700px">
    <h2 style="margin-bottom:16px">{{ ts.title }}</h2>
    <el-alert type="info" :closable="false" style="margin-bottom:20px">
      {{ ts.tip }}
    </el-alert>

    <el-card style="margin-bottom:16px">
      <template #header>
        <span>{{ ts.presets }}</span>
      </template>
      <el-radio-group v-model="preset" @change="applyPreset" size="small">
        <el-radio-button v-for="p in presets" :key="p.name" :value="p.name">{{ p.label }}</el-radio-button>
      </el-radio-group>
    </el-card>

    <el-card>
      <template #header><span>{{ ts.custom }}</span></template>
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item :label="ts.key">
          <el-input v-model="form.llm_api_key" type="password" show-password placeholder="sk-..." />
        </el-form-item>
        <el-form-item :label="ts.url">
          <el-input v-model="form.llm_base_url" placeholder="https://api.deepseek.com/v1" />
        </el-form-item>
        <el-form-item :label="ts.model">
          <el-input v-model="form.llm_model" placeholder="deepseek-chat" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="save" :loading="saving">{{ ts.save }}</el-button>
          <el-button @click="load">{{ ts.reset }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <template #header><span>{{ ts.status }}</span></template>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item :label="ts.currentKey">
          <el-tag :type="hasKey ? 'success' : 'danger'">{{ hasKey ? ts.configured : ts.notConfigured }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="ts.currentUrl">{{ form.llm_base_url }}</el-descriptions-item>
        <el-descriptions-item :label="ts.currentModel">{{ form.llm_model }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive, onMounted, computed } from 'vue'
import { configApi } from '@/api'
import { ElMessage } from 'element-plus'

const i18n: Record<string, Record<string, string>> = {
  zh: {
    title: 'API 配置', tip: '切换大模型API后，重启后端生效。不改代码即可接入 OpenAI / DeepSeek / 通义千问 等。',
    presets: '快速切换', custom: '自定义配置',
    key: 'API Key', url: '接口地址', model: '模型名称',
    save: '保存配置', reset: '重置',
    status: '当前状态', currentKey: 'Key状态', currentUrl: '接口地址', currentModel: '模型',
    configured: '已配置', notConfigured: '未配置',
  },
  en: {
    title: 'API Configuration', tip: 'After switching, restart backend to apply. Supports OpenAI / DeepSeek / Qwen etc.',
    presets: 'Quick Switch', custom: 'Custom',
    key: 'API Key', url: 'Base URL', model: 'Model',
    save: 'Save', reset: 'Reset',
    status: 'Status', currentKey: 'Key', currentUrl: 'Base URL', currentModel: 'Model',
    configured: 'Configured', notConfigured: 'Not configured',
  },
  ja: { title: 'API設定', tip: '切り替え後、バックエンドを再起動してください', presets: 'クイック切替', custom: 'カスタム', key: 'APIキー', url: 'ベースURL', model: 'モデル', save: '保存', reset: 'リセット', status: 'ステータス', currentKey: 'キー', currentUrl: 'URL', currentModel: 'モデル', configured: '設定済', notConfigured: '未設定' },
  ko: { title: 'API 설정', tip: '전환 후 백엔드를 재시작하세요', presets: '빠른 전환', custom: '사용자 정의', key: 'API 키', url: '기본 URL', model: '모델', save: '저장', reset: '초기화', status: '상태', currentKey: '키', currentUrl: 'URL', currentModel: '모델', configured: '설정됨', notConfigured: '미설정' },
  fr: { title: 'Configuration API', tip: 'Redémarrez le backend après changement', presets: 'Rapide', custom: 'Personnalisé', key: 'Clé API', url: 'URL de base', model: 'Modèle', save: 'Enregistrer', reset: 'Réinitialiser', status: 'Statut', currentKey: 'Clé', currentUrl: 'URL', currentModel: 'Modèle', configured: 'Configuré', notConfigured: 'Non configuré' },
  es: { title: 'Configuración API', tip: 'Reinicie el backend tras cambiar', presets: 'Rápido', custom: 'Personalizado', key: 'Clave API', url: 'URL base', model: 'Modelo', save: 'Guardar', reset: 'Restablecer', status: 'Estado', currentKey: 'Clave', currentUrl: 'URL', currentModel: 'Modelo', configured: 'Configurado', notConfigured: 'No configurado' },
  de: { title: 'API-Konfiguration', tip: 'Backend nach Änderung neu starten', presets: 'Schnellwechsel', custom: 'Benutzerdefiniert', key: 'API-Schlüssel', url: 'Basis-URL', model: 'Modell', save: 'Speichern', reset: 'Zurücksetzen', status: 'Status', currentKey: 'Schlüssel', currentUrl: 'URL', currentModel: 'Modell', configured: 'Konfiguriert', notConfigured: 'Nicht konfiguriert' },
}

const lang = ref('zh')
const ts = reactive(i18n['zh'])
watch(lang, (v) => { Object.assign(ts, i18n[v]) })

const form = reactive({ llm_api_key: '', llm_base_url: '', llm_model: '' })
const saving = ref(false)
const preset = ref('')
const hasKey = computed(() => form.llm_api_key.length > 5)

const presets = [
  { name: 'deepseek', label: 'DeepSeek', url: 'https://api.deepseek.com/v1', model: 'deepseek-chat' },
  { name: 'qwen', label: '通义千问', url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-plus' },
  { name: 'openai', label: 'OpenAI', url: 'https://api.openai.com/v1', model: 'gpt-4o' },
  { name: 'zhipu', label: '智谱GLM', url: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4' },
  { name: 'moonshot', label: 'Moonshot', url: 'https://api.moonshot.cn/v1', model: 'moonshot-v1-8k' },
]

const applyPreset = (name: string) => {
  const p = presets.find(x => x.name === name)
  if (p) { form.llm_base_url = p.url; form.llm_model = p.model }
}

const load = async () => {
  try {
    const r = (await configApi.getLLM()).data
    Object.assign(form, r)
  } catch { ElMessage.error('加载失败') }
}

const save = async () => {
  saving.value = true
  try {
    await configApi.updateLLM({ ...form })
    ElMessage.success('已保存，重启后端后生效')
  } catch { ElMessage.error('保存失败') }
  saving.value = false
}

onMounted(load)

</script>
