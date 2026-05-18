<template>
  <el-container class="admin-root">
    <el-aside :width="collapsed ? '64px' : '220px'" class="admin-sidebar">
      <div class="sidebar-brand" @click="collapsed = !collapsed">
        <el-icon :size="22"><Service /></el-icon>
        <span v-show="!collapsed" class="brand-text">{{ ts.header }}</span>
      </div>

      <el-menu
        :default-active="route.path"
        :collapse="collapsed"
        :collapse-transition="false"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/admin">
          <el-icon><DataAnalysis /></el-icon>
          <span>{{ ts.dashboard }}</span>
        </el-menu-item>
        <el-menu-item index="/admin/knowledge">
          <el-icon><Collection /></el-icon>
          <span>{{ ts.knowledge }}</span>
        </el-menu-item>
        <el-menu-item index="/admin/handoff">
          <el-icon><Headset /></el-icon>
          <span>{{ ts.handoff }}</span>
        </el-menu-item>
        <el-menu-item index="/admin/conversations">
          <el-icon><ChatDotRound /></el-icon>
          <span>{{ ts.conversations }}</span>
        </el-menu-item>
        <el-menu-item index="/admin/store-profile">
          <el-icon><Shop /></el-icon>
          <span>{{ ts.storeProfile }}</span>
        </el-menu-item>
        <el-sub-menu index="platforms">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>{{ ts.platforms }}</span>
          </template>
          <el-menu-item index="/admin/ozon-chats">
            <el-icon><ChatDotSquare /></el-icon>
            <span>Ozon</span>
          </el-menu-item>
          <el-menu-item index="/admin/platforms/config">
            <span>{{ ts.platConfig }}</span>
          </el-menu-item>
          <el-menu-item index="/admin/platforms/review">
            <span>{{ ts.platReview }}</span>
            <el-badge v-if="pendingCount" :value="pendingCount" class="menu-badge" />
          </el-menu-item>
          <el-menu-item index="/admin/platforms/stats">
            <span>{{ ts.platStats }}</span>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/admin/config">
          <el-icon><Setting /></el-icon>
          <span>{{ ts.config }}</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer" v-show="!collapsed">
        <el-select v-model="lang" size="small" class="lang-select">
          <el-option v-for="l in langs" :key="l.value" :label="l.label" :value="l.value" />
        </el-select>
        <el-button size="small" text @click="$router.push('/')">
          <el-icon><Promotion /></el-icon>{{ ts.back }}
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header class="admin-header">
        <span class="header-title">{{ pageTitle }}</span>
      </el-header>
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, watch, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { Promotion } from '@element-plus/icons-vue'

const route = useRoute()
const collapsed = ref(false)

const pendingCount = ref(0)
const fetchPending = async () => {
  try { const r = await fetch('/api/platforms/review?limit=1'); const d = await r.json(); pendingCount.value = d.length } catch {}
}
fetchPending()
setInterval(fetchPending, 30000)

const langMessages: Record<string, Record<string, string>> = {
  zh: { header: '客服管理后台', handoff: '人工客服', storeProfile: '店铺画像', dashboard: '数据看板',
    knowledge: '知识库管理', conversations: '对话记录', config: 'API配置', platforms: '平台管理',
    platConfig: '凭证配置', platReview: '待审核消息', platStats: '自动回复统计', back: '返回聊天' },
  en: { header: 'Admin Panel', handoff: 'Live Chat', storeProfile: 'Store Profile', dashboard: 'Dashboard',
    knowledge: 'Knowledge Base', conversations: 'Conversations', config: 'API Config', platforms: 'Platforms',
    platConfig: 'API Credentials', platReview: 'Review Queue', platStats: 'Reply Stats', back: 'Back to Chat' },
  ja: { header: '管理パネル', handoff: 'ライブチャット', dashboard: 'ダッシュボード',
    knowledge: 'ナレッジベース', conversations: '会話記録', config: 'API設定', platforms: 'プラットフォーム',
    platConfig: 'API認証', platReview: 'レビュー', platStats: '自動返信統計', back: 'チャットに戻る' },
  ko: { header: '관리자 패널', handoff: '실시간 채팅', dashboard: '대시보드',
    knowledge: '지식 베이스', conversations: '대화 기록', config: 'API 설정', platforms: '플랫폼',
    platConfig: 'API 인증', platReview: '검토 대기', platStats: '자동 응답 통계', back: '채팅으로' },
  fr: { header: 'Panneau Admin', handoff: 'Chat en direct', dashboard: 'Tableau de bord',
    knowledge: 'Base de connaissances', conversations: 'Conversations', config: 'API Config', platforms: 'Plateformes',
    platConfig: 'Accréditations', platReview: 'Queue de revue', platStats: 'Stats', back: 'Retour' },
  es: { header: 'Panel Admin', handoff: 'Chat en vivo', dashboard: 'Panel',
    knowledge: 'Base de conocimiento', conversations: 'Conversaciones', config: 'Configuración', platforms: 'Plataformas',
    platConfig: 'Credenciales', platReview: 'Revisión', platStats: 'Estadísticas', back: 'Volver' },
  de: { header: 'Admin-Panel', handoff: 'Live-Chat', dashboard: 'Dashboard',
    knowledge: 'Wissensdatenbank', conversations: 'Gespräche', config: 'API-Konfig', platforms: 'Plattformen',
    platConfig: 'Zugangsdaten', platReview: 'Prüfung', platStats: 'Auto-Antwort', back: 'Zurück' },
}

const titleMap: Record<string, Record<string, string>> = {
  '/admin': { zh: '数据看板', en: 'Dashboard', ja: 'ダッシュボード', ko: '대시보드', fr: 'Tableau de bord', es: 'Panel', de: 'Dashboard' },
  '/admin/knowledge': { zh: '知识库管理', en: 'Knowledge Base', ja: 'ナレッジベース', ko: '지식 베이스', fr: 'Base de connaissances', es: 'Base de conocimiento', de: 'Wissensdatenbank' },
  '/admin/handoff': { zh: '人工客服', en: 'Live Chat', ja: 'ライブチャット', ko: '실시간 채팅', fr: 'Chat en direct', es: 'Chat en vivo', de: 'Live-Chat' },
  '/admin/conversations': { zh: '对话记录', en: 'Conversations', ja: '会話記録', ko: '대화 기록', fr: 'Conversations', es: 'Conversaciones', de: 'Gespräche' },
  '/admin/store-profile': { zh: '店铺画像', en: 'Store Profile', ja: 'ショップ情報', ko: '스토어 프로필', fr: 'Profil boutique', es: 'Perfil tienda', de: 'Shop-Profil' },
  '/admin/config': { zh: 'API配置', en: 'API Config', ja: 'API設定', ko: 'API 설정', fr: 'Config API', es: 'Config API', de: 'API-Konfig' },
  '/admin/ozon-chats': { zh: 'Ozon聊天', en: 'Ozon Chats', ja: 'Ozonチャット', ko: 'Ozon 채팅', fr: 'Chats Ozon', es: 'Chats Ozon', de: 'Ozon-Chats' },
  '/admin/platforms/config': { zh: '平台凭证', en: 'Credentials', ja: '認証情報', ko: '인증 정보', fr: 'Accréditations', es: 'Credenciales', de: 'Zugangsdaten' },
  '/admin/platforms/review': { zh: '待审核', en: 'Review Queue', ja: 'レビュー待ち', ko: '검토 대기', fr: "File dattente", es: 'Cola revisión', de: 'Überprüfung' },
  '/admin/platforms/stats': { zh: '回复统计', en: 'Reply Stats', ja: '返信統計', ko: '응답 통계', fr: 'Statistiques', es: 'Estadísticas', de: 'Statistik' },
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

<style scoped>
.admin-root { height: 100vh; }

.admin-sidebar {
  background: var(--c-sidebar);
  border-right: 1px solid var(--c-border);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  overflow: hidden;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 16px;
  color: var(--c-primary);
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
  border-bottom: 1px solid var(--c-border);
  user-select: none;
}
.brand-text {
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  background: transparent;
}
.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  color: var(--c-text);
  transition: all var(--transition-fast);
}
.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background: #e8eaed;
  color: var(--c-text);
}
.sidebar-menu .el-menu-item.is-active {
  background: var(--c-primary-light);
  color: var(--c-primary);
  font-weight: 600;
}

.menu-badge { margin-left: 6px; }

.sidebar-footer {
  border-top: 1px solid var(--c-border);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.lang-select { width: 100%; }

.admin-header {
  background: var(--c-card);
  border-bottom: 1px solid var(--c-border);
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 52px;
  flex-shrink: 0;
}
.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
}

.admin-main {
  background: var(--c-bg);
  padding: 20px 24px;
  overflow-y: auto;
}
</style>