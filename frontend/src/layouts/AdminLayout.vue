<template>
  <el-container style="height:100vh">
    <el-aside width="220px" style="background:#304156;overflow-y:auto">
      <div style="color:#fff;padding:20px 16px;font-size:18px;font-weight:600;text-align:center;border-bottom:1px solid #4a5568">
        🛒 {{ ts.header }}
      </div>
      <el-menu :default-active="route.path" background-color="#304156" text-color="#bfcbd9" active-text-color="#409eff" router>
        <el-menu-item index="/admin">
          <el-icon><DataAnalysis /></el-icon>
          <span>{{ ts.dashboard }}</span>
        </el-menu-item>
        <el-menu-item index="/admin/knowledge">
          <el-icon><Collection /></el-icon>
          <span>{{ ts.knowledge }}</span>
        </el-menu-item>
        <el-menu-item index="/admin/conversations">
          <el-icon><ChatDotRound /></el-icon>
          <span>{{ ts.conversations }}</span>
        </el-menu-item>
        <el-menu-item index="/admin/store-profile">
          <el-icon><Shop /></el-icon>
          <span>{{ ts.storeProfile }}</span>
        </el-menu-item>
        <el-menu-item index="/admin/config">
          <el-icon><Setting /></el-icon>
          <span>{{ ts.config }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background:#fff;border-bottom:1px solid #e4e7ed;display:flex;align-items:center;justify-content:space-between;padding:0 20px">
        <span style="font-size:16px;font-weight:600">{{ pageTitle }}</span>
        <div style="display:flex;gap:10px;align-items:center">
          <el-select v-model="lang" size="small" style="width:110px">
            <el-option v-for="l in langs" :key="l.value" :label="l.label" :value="l.value" />
          </el-select>
          <el-button @click="$router.push('/')" size="small">{{ ts.back }}</el-button>
        </div>
      </el-header>
      <el-main style="background:#f5f7fa">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, watch, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const langMessages: Record<string, Record<string, string>> = {
  zh: { header: '客服管理后台', storeProfile: '店铺画像', dashboard: '数据看板', knowledge: '知识库管理', conversations: '对话记录', config: 'API配置', back: '返回聊天' },
  en: { header: 'Admin Panel', storeProfile: 'Store Profile', dashboard: 'Dashboard', knowledge: 'Knowledge Base', conversations: 'Conversations', config: 'API Config', back: 'Back to Chat' },
  ja: { header: '管理パネル', dashboard: 'ダッシュボード', knowledge: 'ナレッジベース', conversations: '会話記録', config: 'API設定', back: 'チャットに戻る' },
  ko: { header: '관리자 패널', dashboard: '대시보드', knowledge: '지식 베이스', conversations: '대화 기록', config: 'API 설정', back: '채팅으로 돌아가기' },
  fr: { header: 'Panneau Admin', dashboard: 'Tableau de bord', knowledge: 'Base de connaissances', conversations: 'Conversations', config: 'API Config', back: 'Retour au chat' },
  es: { header: 'Panel Admin', dashboard: 'Panel', knowledge: 'Base de conocimiento', conversations: 'Conversaciones', config: 'Configuración API', back: 'Volver al chat' },
  de: { header: 'Admin-Panel', dashboard: 'Dashboard', knowledge: 'Wissensdatenbank', conversations: 'Gespräche', config: 'API-Konfig', back: 'Zurück zum Chat' },
}

const titleMap: Record<string, Record<string, string>> = {
  '/admin': { zh: '数据看板', en: 'Dashboard', ja: 'ダッシュボード', ko: '대시보드', fr: 'Tableau de bord', es: 'Panel', de: 'Dashboard' },
  '/admin/knowledge': { zh: '知识库管理', en: 'Knowledge Base', ja: 'ナレッジベース', ko: '지식 베이스', fr: 'Base de connaissances', es: 'Base de conocimiento', de: 'Wissensdatenbank' },
  '/admin/conversations': { zh: '对话记录', en: 'Conversations', ja: '会話記録', ko: '대화 기록', fr: 'Conversations', es: 'Conversaciones', de: 'Gespräche' },
}

const langs = [
  { label: '🇨🇳 中文', value: 'zh' }, { label: '🇺🇸 English', value: 'en' },
  { label: '🇯🇵 日本語', value: 'ja' }, { label: '🇰🇷 한국어', value: 'ko' },
  { label: '🇫🇷 Français', value: 'fr' }, { label: '🇪🇸 Español', value: 'es' }, { label: '🇩🇪 Deutsch', value: 'de' },
]

const lang = ref('zh')
const ts = reactive(langMessages['zh'])
const pageTitle = computed(() => (titleMap[route.path] || {})[lang.value] || titleMap[route.path]?.zh || '')

watch(lang, (v) => { Object.assign(ts, langMessages[v]) })

</script>





