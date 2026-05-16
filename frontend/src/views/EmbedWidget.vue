<template>
  <div class="embed-root">
    <div class="embed-header">
      <span>🤖 {{ t.header }}</span>
      <el-select v-model="lang" size="small" style="width:100px">
        <el-option v-for="l in languages" :key="l.value" :label="l.label" :value="l.value" />
      </el-select>
    </div>
    <div class="embed-messages" ref="msgList">
      <div v-if="messages.length === 0" class="embed-welcome">
        <p>{{ t.welcome }}</p>
        <p style="font-size:13px;color:#909399">{{ t.welcomeSub }}</p>
        <div class="embed-quick">
          <span v-for="q in quickQuestions" :key="q" @click="send(q)" class="embed-quick-tag">{{ q }}</span>
        </div>
      </div>
      <div v-for="(msg, i) in messages" :key="i" :class="['embed-msg', msg.role]">
        <div class="embed-bubble" v-html="renderMarkdown(msg.content)" />
      </div>
      <div v-if="loading" class="embed-msg assistant">
        <div class="embed-bubble typing">{{ t.typing }}</div>
      </div>
    </div>
    <div class="embed-input">
      <input v-model="input" :placeholder="t.placeholder" @keyup.enter="send()" :disabled="loading" class="embed-input-field" />
      <button @click="send()" :disabled="loading" class="embed-send-btn">{{ t.send }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, computed } from 'vue'
import { chatApi } from '@/api'
import { useRoute, useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ breaks: true })

const messages = ref<{role:string;content:string;sources?:any[]}[]>([])
const input = ref('')
const loading = ref(false)
const msgList = ref<HTMLElement>()

const translations: Record<string, Record<string, string>> = {
  zh: { header:'智能客服', welcome:'👋 您好！', welcomeSub:'有什么可以帮助您的？', placeholder:'输入问题...', send:'发送', typing:'输入中...', handoffMsg:'🔔 已转接人工客服' },
  en: { header:'AI Support', welcome:'👋 Hello!', welcomeSub:'How can I help?', placeholder:'Type here...', send:'Send', typing:'Typing...', handoffMsg:'🔔 Transferring to agent' },
  ja: { header:'AIサポート', welcome:'👋 こんにちは', welcomeSub:'ご用件は？', placeholder:'質問を入力...', send:'送信', typing:'入力中...', handoffMsg:'🔔 オペレーター転送中' },
  ko: { header:'AI 지원', welcome:'👋 안녕하세요', welcomeSub:'무엇을 도와드릴까요?', placeholder:'질문 입력...', send:'전송', typing:'입력 중...', handoffMsg:'🔔 상담원 연결 중' },
  fr: { header:'Support IA', welcome:'👋 Bonjour', welcomeSub:'Comment vous aider?', placeholder:'Votre question...', send:'Envoyer', typing:'En cours...', handoffMsg:'🔔 Transfert en cours' },
  es: { header:'Soporte IA', welcome:'👋 Hola', welcomeSub:'¿Cómo ayudar?', placeholder:'Escribe aquí...', send:'Enviar', typing:'Escribiendo...', handoffMsg:'🔔 Transfiriendo' },
  de: { header:'KI-Support', welcome:'👋 Hallo', welcomeSub:'Wie kann ich helfen?', placeholder:'Frage eingeben...', send:'Senden', typing:'Wird geschrieben...', handoffMsg:'🔔 Wird verbunden' },
}

const quickQuestionsMap: Record<string, string[]> = {
  zh: ['我的快递到哪了？','如何退换货？','支持哪些支付方式？'],
  en: ['Where is my order?','How to return?','Payment methods?'],
  ja: ['注文状況は？','返品方法は？','支払い方法は？'],
  ko: ['주문 현황은?','반품 방법은?','결제 수단은?'],
  fr: ['Où est ma commande?','Comment retourner?','Moyens de paiement?'],
  es: ['¿Dónde está mi pedido?','¿Cómo devolver?','¿Métodos de pago?'],
  de: ['Wo ist meine Bestellung?','Wie retournieren?','Zahlungsarten?'],
}

const languages = [
  { label:'🇨🇳 中文',value:'zh'},{ label:'🇺🇸 EN',value:'en'},{ label:'🇯🇵 日本語',value:'ja'},
  { label:'🇰🇷 한국어',value:'ko'},{ label:'🇫🇷 FR',value:'fr'},{ label:'🇪🇸 ES',value:'es'},{ label:'🇩🇪 DE',value:'de'},
]

const route = useRoute()
const router = useRouter()
const supported = ['zh','en','ja','ko','fr','es','de']

const lang = computed({
  get: () => {
    const p = route.params.lang as string
    return (p && supported.includes(p)) ? p : 'zh'
  },
  set: (v: string) => {
    router.replace({ params: { lang: v } })
  }
})
const t = computed(() => translations[lang.value])
const quickQuestions = computed(() => quickQuestionsMap[lang.value])
let sessionId = ''



const send = async (text?: string) => {
  const msg = text || input.value.trim()
  if (!msg || loading.value) return
  messages.value.push({ role:'user', content:msg })
  input.value = ''; loading.value = true
  await nextTick(); scrollBottom()
  try {
    const res = (await chatApi.send({ session_id:sessionId, message:msg, lang:lang.value })).data
    sessionId = res.session_id
    messages.value.push({ role:'assistant', content:res.answer })
    if (res.handoff) messages.value.push({ role:'system', content:t.value.handoffMsg })
  } catch { messages.value.push({ role:'assistant', content:'抱歉，服务暂时不可用' }) }
  loading.value = false
  await nextTick(); scrollBottom()
}

const renderMarkdown = (text:string) => md.render(text)
const scrollBottom = () => { if (msgList.value) msgList.value.scrollTop = msgList.value.scrollHeight }
</script>

<style scoped>
.embed-root { display:flex; flex-direction:column; height:100vh; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
.embed-header { background:linear-gradient(135deg,#409eff,#337ecc); color:#fff; padding:12px 16px; font-size:15px; font-weight:600; display:flex; justify-content:space-between; align-items:center; flex-shrink:0; }
.embed-messages { flex:1; overflow-y:auto; padding:12px; background:#f5f7fa; }
.embed-welcome { text-align:center; padding:30px 16px; }
.embed-welcome p { margin:4px 0; }
.embed-quick { margin-top:12px; display:flex; flex-wrap:wrap; gap:6px; justify-content:center; }
.embed-quick-tag { cursor:pointer; background:#ecf5ff; color:#409eff; padding:4px 10px; border-radius:12px; font-size:12px; }
.embed-quick-tag:hover { background:#409eff; color:#fff; }
.embed-msg { margin-bottom:12px; }
.embed-msg.user { text-align:right; }
.embed-msg.user .embed-bubble { background:#409eff; color:#fff; display:inline-block; border-radius:12px 4px 12px 12px; }
.embed-msg.assistant .embed-bubble { background:#fff; display:inline-block; border-radius:4px 12px 12px 12px; }
.embed-msg.system .embed-bubble { background:#fdf6ec; color:#e6a23c; display:inline-block; border-radius:8px; font-size:12px; }
.embed-bubble { padding:8px 12px; max-width:85%; word-break:break-word; font-size:13px; line-height:1.5; }
.typing { color:#909399; font-style:italic; }
.embed-input { display:flex; padding:10px 12px; background:#fff; border-top:1px solid #e4e7ed; gap:8px; flex-shrink:0; }
.embed-input-field { flex:1; border:1px solid #dcdfe6; border-radius:6px; padding:8px 12px; font-size:13px; outline:none; }
.embed-input-field:focus { border-color:#409eff; }
.embed-send-btn { background:#409eff; color:#fff; border:none; border-radius:6px; padding:8px 16px; font-size:13px; cursor:pointer; }
.embed-send-btn:disabled { opacity:0.5; cursor:default; }
</style>
