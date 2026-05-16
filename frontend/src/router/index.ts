import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/embed/:lang?', component: () => import('@/views/EmbedWidget.vue') },
    {
      path: '/amazon',
      component: () => import('@/views/AmazonAssistant.vue'),
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      children: [
        { path: '', component: () => import('@/views/admin/Dashboard.vue') },
        { path: 'knowledge', component: () => import('@/views/admin/KnowledgeList.vue') },
        { path: 'knowledge/new', component: () => import('@/views/admin/KnowledgeEdit.vue') },
        { path: 'knowledge/:id', component: () => import('@/views/admin/KnowledgeEdit.vue') },
        { path: 'conversations', component: () => import('@/views/admin/Conversations.vue') },
        { path: 'store-profile', component: () => import('@/views/admin/StoreProfileView.vue') },
        { path: 'config', component: () => import('@/views/admin/ConfigView.vue') },
        { path: 'platforms/config', component: () => import('@/views/admin/PlatformConfigView.vue') },
        { path: 'platforms/review', component: () => import('@/views/admin/PlatformReviewView.vue') },
        { path: 'platforms/stats', component: () => import('@/views/admin/PlatformStatsView.vue') },
      ]
    },
    { path: '/:lang?', component: () => import('@/views/ChatWidget.vue') },
  ]
})
export default router
