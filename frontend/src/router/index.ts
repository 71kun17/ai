import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('@/views/ChatWidget.vue') },
    { path: '/embed', component: () => import('@/views/EmbedWidget.vue') },
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
      ]
    }
  ]
})
export default router
