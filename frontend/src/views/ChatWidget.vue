<template>
  <div class="chat-container">
    <div class="chat-header">
      <span>{{ isHandoff ? '🎧' : '🤖' }} {{ isHandoff ? t.handoffTitle : t.header }}</span>
      <el-select v-model="lang" size="small" style="width:110px">
        <el-option v-for="l in languages" :key="l.value" :label="l.label" :value="l.value" />
      </el-select>
    </div>
    <div class="chat-messages" ref="msgList">
      <div v-if="messages.length === 0" class="welcome">
        <h3>{{ t.welcome }}</h3>
        <p>{{ t.welcomeSub }}</p>
        <div class="quick-questions">
          <el-tag v-for="q in quickQuestions" :key="q" @click="send(q)" class="quick-tag">{{ q }}</el-tag>
        </div>
      </div>
      <div v-for="(msg, i) in messages" :key="i" :class="['msg-row', msg.role]">
        <div class="avatar">{{ msg.role === 'user' ? '👤' : msg.role === 'admin' ? '🎧' : '🤖' }}</div>
        <div class="msg-content">
          <div class="bubble" v-html="renderMarkdown(msg.content)" />
        </div>
      </div>
      <div v-if="loading" class="msg-row assistant">
        <div class="avatar">🤖</div>
        <div class="msg-content"><div class="bubble typing">{{ t.typing }}</div></div>
      </div>
    </div>
    <div class="chat-input">
      <el-input v-model="input" :placeholder="isHandoff ? t.handoffPlaceholder : t.placeholder" @keyup.enter="send()" :disabled="loading" size="large">
        <template #append>
          <el-button @click="send()" :disabled="loading" type="primary">{{ t.send }}</el-button>
        </template>
      </el-input>
      <div style="margin-top:6px;text-align:right">
        <el-button v-if="!isHandoff" size="small" type="warning" plain @click="requestHandoff">{{ t.handoff }}</el-button>
        <el-tag v-else type="success" size="small">{{ t.handoffActive }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onUnmounted } from 'vue'
import { chatApi } from '@/api'
import { useRoute, useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ breaks: true })

interface Message {
  role: string
  content: string
  sources?: { id: number; similarity: number }[]
}

const messages = ref<Message[]>([])
const input = ref('')
const loading = ref(false)
const isHandoff = ref(false)
const msgList = ref<HTMLElement>()
const lastPollId = ref(0)
let pollTimer: ReturnType<typeof setInterval> | null = null

const translations: Record<string, Record<string, string>> = {
  zh: {
    header: '智能客服助手',
    handoffTitle: '人工客服',
    welcome: '👋 您好！我是智能客服小助手',
    welcomeSub: '有什么可以帮助您的？',
    placeholder: '请输入您的问题...',
    handoffPlaceholder: '输入消息，与人工客服沟通...',
    send: '发送',
    handoff: '转人工客服',
    handoffActive: '人工客服已接入',
    typing: '正在输入...',
    handoffMsg: '🔔 已为您转接人工客服，请稍候...',
    handoffConnected: '🔔 人工客服已接入，请直接发送您的问题',
    errorMsg: '抱歉，服务暂时不可用，请稍后再试。',
    sessionEnded: '🔔 会话已结束，感谢您的咨询。如需帮助请重新发起对话。',
  },
  en: {
    header: 'AI Customer Service',
    handoffTitle: 'Human Agent',
    welcome: '👋 Hello! I am your AI assistant',
    welcomeSub: 'How can I help you today?',
    placeholder: 'Type your question...',
    handoffPlaceholder: 'Type message to human agent...',
    send: 'Send',
    handoff: 'Transfer to Human',
    handoffActive: 'Agent Connected',
    typing: 'Typing...',
    handoffMsg: '🔔 Transferring to a human agent, please wait...',
    handoffConnected: '🔔 A human agent has joined. Please send your question directly.',
    errorMsg: 'Sorry, service is temporarily unavailable. Please try again later.',
    sessionEnded: '🔔 Session ended. Thank you. Start a new chat if you need help.',
  },
  ja: {
    header: 'AIカスタマーサービス',
    handoffTitle: '有人対応',
    welcome: '👋 こんにちは！AIアシスタントです',
    welcomeSub: 'どのようなご用件でしょうか？',
    placeholder: '質問を入力してください...',
    handoffPlaceholder: 'オペレーターにメッセージを入力...',
    send: '送信',
    handoff: 'オペレーターに転送',
    handoffActive: 'オペレーター接続中',
    typing: '入力中...',
    handoffMsg: '🔔 オペレーターにお繋ぎしますので、少々お待ちください...',
    handoffConnected: '🔔 オペレーターが接続しました。直接ご質問をお送りください',
    errorMsg: '申し訳ございません。一時的にサービスがご利用いただけません。',
    sessionEnded: '🔔 セッションが終了しました。新しいチャットを開始してください。',
  },
  ko: {
    header: 'AI 고객 서비스',
    handoffTitle: '상담원 연결',
    welcome: '👋 안녕하세요! AI 어시스턴트입니다',
    welcomeSub: '무엇을 도와드릴까요?',
    placeholder: '질문을 입력하세요...',
    handoffPlaceholder: '상담원에게 메시지 입력...',
    send: '전송',
    handoff: '상담원 연결',
    handoffActive: '상담원 연결됨',
    typing: '입력 중...',
    handoffMsg: '🔔 상담원에게 연결 중입니다. 잠시만 기다려주세요...',
    handoffConnected: '🔔 상담원이 연결되었습니다. 직접 질문을 보내주세요',
    errorMsg: '죄송합니다. 서비스를 일시적으로 사용할 수 없습니다.',
    sessionEnded: '🔔 세션이 종료되었습니다. 새로운 채팅을 시작하세요.',
  },
  fr: {
    header: 'Service Client IA',
    handoffTitle: 'Agent Humain',
    welcome: '👋 Bonjour ! Je suis votre assistant IA',
    welcomeSub: 'Comment puis-je vous aider ?',
    placeholder: 'Saisissez votre question...',
    handoffPlaceholder: "Écrivez à l'agent...",
    send: 'Envoyer',
    handoff: 'Transférer à un humain',
    handoffActive: 'Agent connecté',
    typing: 'En cours...',
    handoffMsg: '🔔 Transfert vers un agent en cours, veuillez patienter...',
    handoffConnected: '🔔 Un agent a rejoint la conversation. Posez directement votre question.',
    errorMsg: 'Désolé, le service est temporairement indisponible.',
    sessionEnded: '🔔 Session terminée. Merci. Démarrez un nouveau chat si besoin.',
  },
  es: {
    header: 'Atención al Cliente IA',
    handoffTitle: 'Agente Humano',
    welcome: '👋 ¡Hola! Soy tu asistente IA',
    welcomeSub: '¿En qué puedo ayudarte?',
    placeholder: 'Escribe tu pregunta...',
    handoffPlaceholder: 'Escribe al agente...',
    send: 'Enviar',
    handoff: 'Transferir a humano',
    handoffActive: 'Agente conectado',
    typing: 'Escribiendo...',
    handoffMsg: '🔔 Transfiriendo a un agente, por favor espera...',
    handoffConnected: '🔔 Un agente se ha unido. Envía tu pregunta directamente.',
    errorMsg: 'Lo sentimos, el servicio no está disponible temporalmente.',
    sessionEnded: '🔔 Sesión finalizada. Gracias. Inicia un nuevo chat si necesitas ayuda.',
  },
  de: {
    header: 'KI-Kundenservice',
    handoffTitle: 'Mitarbeiter',
    welcome: '👋 Hallo! Ich bin Ihr KI-Assistent',
    welcomeSub: 'Wie kann ich Ihnen helfen?',
    placeholder: 'Geben Sie Ihre Frage ein...',
    handoffPlaceholder: 'Nachricht an Mitarbeiter...',
    send: 'Senden',
    handoff: 'Mitarbeiter sprechen',
    handoffActive: 'Mitarbeiter verbunden',
    typing: 'Eingabe...',
    handoffMsg: '🔔 Sie werden mit einem Mitarbeiter verbunden, bitte warten...',
    handoffConnected: '🔔 Ein Mitarbeiter ist der Konversation beigetreten. Stellen Sie Ihre Frage direkt.',
    errorMsg: 'Entschuldigung, der Dienst ist vorübergehend nicht verfügbar.',
    sessionEnded: '🔔 Sitzung beendet. Danke. Starten Sie einen neuen Chat, falls nötig.',
  },
}

const quickQuestionsMap: Record<string, string[]> = {
  zh: ['我的快递到哪了？', '如何申请退换货？', '这款商品有优惠吗？', '订单多久能到？', '支持哪些支付方式？'],
  en: ['Where is my package?', 'How do I return an item?', 'Any discounts available?', 'How long for delivery?', 'What payment methods?'],
  ja: ['私の荷物はどこですか？', '返品方法を教えてください', '割引はありますか？', '配送にはどのくらいかかりますか？', '支払い方法は？'],
  ko: ['내 배송은 어디에 있나요?', '반품은 어떻게 하나요?', '할인이 있나요?', '배송에 얼마나 걸리나요?', '결제 방법은?'],
  fr: ['Où est mon colis ?', 'Comment retourner un article ?', 'Des réductions disponibles ?', 'Délai de livraison ?', 'Moyens de paiement ?'],
  es: ['¿Dónde está mi paquete?', '¿Cómo devuelvo un artículo?', '¿Hay descuentos?', '¿Cuánto tarda el envío?', '¿Métodos de pago?'],
  de: ['Wo ist mein Paket?', 'Wie kann ich zurücksenden?', 'Gibt es Rabatte?', 'Wie lange dauert die Lieferung?', 'Welche Zahlungsarten?'],
}

const languages = [
  { label: '🇨🇳 中文', value: 'zh' },
  { label: '🇺🇸 English', value: 'en' },
  { label: '🇯🇵 日本語', value: 'ja' },
  { label: '🇰🇷 한국어', value: 'ko' },
  { label: '🇫🇷 Français', value: 'fr' },
  { label: '🇪🇸 Español', value: 'es' },
  { label: '🇩🇪 Deutsch', value: 'de' },
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

const startPolling = () => {
  if (pollTimer) return
  pollTimer = setInterval(async () => {
    if (!sessionId) return
    try {
      const r = await fetch(`/api/chat/handoff/${sessionId}/poll?after_id=${lastPollId.value}`)
      const newMsgs = await r.json()
      for (const m of newMsgs) {
        lastPollId.value = m.id
        if (m.role === 'admin') {
          messages.value.push({ role: 'admin', content: m.content })
        } else if (m.role === 'system' && m.content.includes('接入')) {
          messages.value.push({ role: 'system', content: t.value.handoffConnected })
        } else if (m.role === 'system' && m.content.includes('结束')) {
          messages.value.push({ role: 'system', content: t.value.sessionEnded })
        }
      }
      if (newMsgs.length > 0) {
        await nextTick()
        scrollBottom()
      }
    } catch {}
  }, 2000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const sendHandoffMessage = async (text: string) => {
  try {
    await fetch(`/api/chat/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: text, lang: lang.value })
    })
  } catch {}
}

const send = async (text?: string) => {
  const msg = text || input.value.trim()
  if (!msg || loading.value) return
  messages.value.push({ role: 'user', content: msg })
  input.value = ''
  loading.value = true
  await nextTick()
  scrollBottom()
  try {
    if (isHandoff.value) {
      await sendHandoffMessage(msg)
    } else {
      const res = (await chatApi.send({ session_id: sessionId, message: msg, lang: lang.value })).data
      sessionId = res.session_id
      messages.value.push({ role: 'assistant', content: res.answer, sources: res.sources })
      if (res.handoff) {
        isHandoff.value = true
        messages.value.push({ role: 'system', content: t.value.handoffMsg })
        startPolling()
      }
    }
  } catch {
    if (!isHandoff.value) {
      messages.value.push({ role: 'assistant', content: t.value.errorMsg })
    }
  }
  loading.value = false
  await nextTick()
  scrollBottom()
}

const requestHandoff = () => {
  const texts: Record<string, string> = {
    zh: '转人工客服', en: 'Transfer to human', ja: 'オペレーター転送',
    ko: '상담원 연결', fr: 'Parler à un humain', es: 'Hablar con un humano', de: 'Mitarbeiter sprechen'
  }
  send(texts[lang.value] || '转人工客服')
}

const renderMarkdown = (text: string) => md.render(text)
const scrollBottom = () => {
  if (msgList.value) msgList.value.scrollTop = msgList.value.scrollHeight
}

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.chat-container {
  max-width: 560px; margin: 30px auto; border: 1px solid #e4e7ed;
  border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; height: 650px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.chat-header {
  background: linear-gradient(135deg, #409eff, #337ecc); color: #fff;
  padding: 14px 20px; font-size: 17px; font-weight: 600;
  display: flex; justify-content: space-between; align-items: center;
}
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; background: #f5f7fa; }
.welcome { text-align: center; padding: 40px 20px; color: #606266; }
.welcome h3 { margin-bottom: 8px; }
.quick-questions { margin-top: 18px; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.quick-tag { cursor: pointer; padding: 6px 14px; font-size: 13px; }
.msg-row { display: flex; margin-bottom: 16px; gap: 10px; }
.msg-row.user { flex-direction: row-reverse; }
.avatar { width: 36px; height: 36px; border-radius: 50%; background: #e4e7ed; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.msg-content { max-width: 75%; }
.msg-row.user .bubble { background: #409eff; color: #fff; border-radius: 14px 4px 14px 14px; }
.msg-row.assistant .bubble { background: #fff; border-radius: 4px 14px 14px 14px; }
.msg-row.admin .bubble { background: #f0f9eb; border: 1px solid #c6e2c0; border-radius: 4px 14px 14px 14px; }
.msg-row.system .bubble { background: #fdf6ec; color: #e6a23c; border-radius: 8px; font-size: 13px; text-align: center; }
.bubble { padding: 10px 16px; word-break: break-word; font-size: 14px; line-height: 1.6; }
.typing { color: #909399; font-style: italic; }
.chat-input { padding: 14px 16px; background: #fff; border-top: 1px solid #e4e7ed; }
</style>


