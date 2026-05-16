<template>
  <div style="max-width:900px">
    <h2 style="margin-bottom:8px">{{ ts.title }}</h2>
    <p style="color:#909399;margin-bottom:20px">{{ ts.tip }}</p>

    <el-card>
      <template #header><span style="font-weight:600">{{ ts.basic }}</span></template>
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item :label="ts.storeName">
          <el-input v-model="form.store_name" :placeholder="ts.storeNamePlaceholder" />
        </el-form-item>
        <el-form-item :label="ts.storeLogo">
          <el-input v-model="form.store_logo" :placeholder="ts.storeLogoPlaceholder" />
        </el-form-item>
        <el-form-item :label="ts.storeDesc">
          <el-input v-model="form.store_description" type="textarea" :rows="2" :placeholder="ts.storeDescPlaceholder" />
        </el-form-item>
        <el-form-item :label="ts.mainProducts">
          <el-input v-model="form.main_products" :placeholder="ts.mainProductsPlaceholder" />
        </el-form-item>
        <el-form-item :label="ts.productCats">
          <el-input v-model="form.product_categories" :placeholder="ts.productCatsPlaceholder" />
        </el-form-item>
        <el-form-item :label="ts.bizHours">
          <el-input v-model="form.business_hours" :placeholder="ts.bizHoursPlaceholder" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="ts.phone">
              <el-input v-model="form.contact_phone" :placeholder="ts.phonePlaceholder" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="ts.email">
              <el-input v-model="form.contact_email" :placeholder="ts.emailPlaceholder" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <template #header><span style="font-weight:600">{{ ts.commStyle }}</span></template>
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item :label="ts.commDesc">
          <el-input v-model="form.communication_style" type="textarea" :rows="2" :placeholder="ts.commDescPlaceholder" />
        </el-form-item>
        <el-form-item :label="ts.tone">
          <el-radio-group v-model="form.tone">
            <el-radio-button value="亲切">{{ ts.toneWarm }}</el-radio-button>
            <el-radio-button value="正式">{{ ts.toneFormal }}</el-radio-button>
            <el-radio-button value="活泼">{{ ts.toneLively }}</el-radio-button>
            <el-radio-button value="简洁">{{ ts.toneConcise }}</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="ts.greeting">
          <el-input v-model="form.greeting_template" type="textarea" :rows="2" :placeholder="ts.greetingPlaceholder" />
        </el-form-item>
        <el-form-item :label="ts.closing">
          <el-input v-model="form.closing_template" type="textarea" :rows="2" :placeholder="ts.closingPlaceholder" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <template #header><span style="font-weight:600">{{ ts.policy }}</span></template>
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item :label="ts.shipping">
          <el-input v-model="form.shipping_policy" type="textarea" :rows="3" :placeholder="ts.shippingPlaceholder" />
        </el-form-item>
        <el-form-item :label="ts.returnPolicy">
          <el-input v-model="form.return_policy" type="textarea" :rows="3" :placeholder="ts.returnPlaceholder" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <template #header><span style="font-weight:600">{{ ts.custom }}</span></template>
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item :label="ts.customInfo">
          <el-input v-model="form.custom_info" type="textarea" :rows="3" :placeholder="ts.customPlaceholder" />
        </el-form-item>
        <el-form-item :label="ts.active">
          <el-switch v-model="form.is_active" :active-value="1" :inactive-value="0" />
          <span style="margin-left:8px;color:#909399;font-size:12px">{{ form.is_active ? ts.enabled : ts.disabled }}</span>
        </el-form-item>
      </el-form>
    </el-card>

    <div style="margin-top:20px;display:flex;gap:10px">
      <el-button type="primary" @click="save" :loading="saving">{{ ts.save }}</el-button>
      <el-button @click="load">{{ ts.reset }}</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { storeApi } from '@/api'
import { ElMessage } from 'element-plus'

const i18n: Record<string, Record<string, string>> = {
  zh: {
    title: '店铺画像设置',
    tip: '设置店铺的基础信息、沟通风格和政策。AI客服会在对话中自动参考这些信息，确保回答准确、贴合店铺实际情况。',
    basic: '基础信息', storeName: '店铺名称', storeNamePlaceholder: '例如：XX数码旗舰店',
    storeLogo: 'Logo URL', storeLogoPlaceholder: 'https://...',
    storeDesc: '店铺简介', storeDescPlaceholder: '一句话介绍你的店铺...',
    mainProducts: '主营产品', mainProductsPlaceholder: '例如：智能手机、笔记本电脑、平板（逗号分隔）',
    productCats: '产品分类', productCatsPlaceholder: '例如：3C数码、家用电器、服装鞋帽',
    bizHours: '营业时间', bizHoursPlaceholder: '例如：工作日 9:00-18:00',
    phone: '联系电话', phonePlaceholder: '400-xxx-xxxx',
    email: '联系邮箱', emailPlaceholder: 'service@example.com',
    commStyle: '沟通风格',
    commDesc: '整体风格', commDescPlaceholder: '例如：友好、专业、善于推荐适合客户的产品。回答简洁明了，不使用过于技术化的词汇。',
    tone: '语气', toneWarm: '亲切', toneFormal: '正式', toneLively: '活泼', toneConcise: '简洁',
    greeting: '开场白', greetingPlaceholder: '例如：您好，欢迎光临XX旗舰店！我是智能客服小助手，很高兴为您服务~',
    closing: '结束语', closingPlaceholder: '例如：感谢您的咨询，如果有其他问题随时找我哦！祝您购物愉快~',
    policy: '业务政策',
    shipping: '物流配送', shippingPlaceholder: '例如：全场满99包邮，默认发中通/圆通。顺丰需补差价。下单后24小时内发货。',
    returnPolicy: '退换货政策', returnPlaceholder: '例如：支持7天无理由退换（需保持商品完好）。质量问题30天内免费换新。退回运费本店承担。',
    custom: '其他设置', customInfo: '自定义信息', customPlaceholder: '可以写任何额外信息，例如：本店所有商品均为正品国行、支持以旧换新、企业采购可开发票等...',
    active: '启用店铺画像', enabled: '已启用 - AI会参考以上信息', disabled: '已禁用 - AI不会参考以上信息',
    save: '保存设置', reset: '重置',
  },
  en: {
    title: 'Store Profile Settings',
    tip: 'Configure store info, communication style and policies. The AI will automatically reference these to provide accurate responses.',
    basic: 'Basic Info', storeName: 'Store Name', storeNamePlaceholder: 'e.g. XX Digital Flagship',
    storeLogo: 'Logo URL', storeLogoPlaceholder: 'https://...',
    storeDesc: 'Description', storeDescPlaceholder: 'Brief description of your store...',
    mainProducts: 'Main Products', mainProductsPlaceholder: 'e.g. Smartphones, Laptops, Tablets',
    productCats: 'Categories', productCatsPlaceholder: 'e.g. Electronics, Home Appliances',
    bizHours: 'Business Hours', bizHoursPlaceholder: 'e.g. Mon-Fri 9:00-18:00',
    phone: 'Phone', phonePlaceholder: '400-xxx-xxxx',
    email: 'Email', emailPlaceholder: 'service@example.com',
    commStyle: 'Communication Style',
    commDesc: 'Overall Style', commDescPlaceholder: 'e.g. Friendly, professional, good at recommending products...',
    tone: 'Tone', toneWarm: 'Warm', toneFormal: 'Formal', toneLively: 'Lively', toneConcise: 'Concise',
    greeting: 'Greeting', greetingPlaceholder: 'e.g. Hello, welcome to our store! How can I help you today?',
    closing: 'Closing', closingPlaceholder: 'e.g. Thank you for visiting! Have a great day!',
    policy: 'Policies',
    shipping: 'Shipping', shippingPlaceholder: 'e.g. Free shipping over $50. Ships within 24 hours.',
    returnPolicy: 'Returns', returnPlaceholder: 'e.g. 7-day return policy. Free returns for defective items.',
    custom: 'Other', customInfo: 'Custom Info', customPlaceholder: 'Any additional information...',
    active: 'Enable Store Profile', enabled: 'Enabled', disabled: 'Disabled',
    save: 'Save', reset: 'Reset',
  },
  ja: {
    title: 'ショッププロフィール設定', tip: '店舗情報やコミュニケーションスタイルを設定します',
    basic: '基本情報', storeName: '店舗名', storeNamePlaceholder: '例：XXデジタル旗艦店',
    storeLogo: 'ロゴURL', storeLogoPlaceholder: 'https://...',
    storeDesc: '紹介文', storeDescPlaceholder: '店舗の簡単な紹介...',
    mainProducts: '主力商品', mainProductsPlaceholder: '例：スマートフォン、ノートパソコン',
    productCats: 'カテゴリ', productCatsPlaceholder: '例：電子機器、家電',
    bizHours: '営業時間', bizHoursPlaceholder: '例：平日 9:00-18:00',
    phone: '電話', phonePlaceholder: '400-xxx-xxxx',
    email: 'メール', emailPlaceholder: 'service@example.com',
    commStyle: 'コミュニケーションスタイル',
    commDesc: '全体的なスタイル', commDescPlaceholder: '例：親しみやすく、プロフェッショナル...',
    tone: 'トーン', toneWarm: '親しみやすい', toneFormal: 'フォーマル', toneLively: '活発', toneConcise: '簡潔',
    greeting: '挨拶', greetingPlaceholder: '例：こんにちは、XX店へようこそ！',
    closing: '締めの言葉', closingPlaceholder: '例：ありがとうございました！',
    policy: 'ポリシー',
    shipping: '配送', shippingPlaceholder: '例：5,000円以上で送料無料。24時間以内に出荷。',
    returnPolicy: '返品', returnPlaceholder: '例：7日間の返品ポリシー。不良品は無料返品。',
    custom: 'その他', customInfo: 'カスタム情報', customPlaceholder: '追加情報...',
    active: 'プロフィール有効', enabled: '有効', disabled: '無効',
    save: '保存', reset: 'リセット',
  },
}

const lang = ref('zh')
const ts = reactive(i18n['zh'])
watch(lang, (v) => { Object.assign(ts, i18n[v]) })

const form = reactive({
  store_name: '', store_logo: '', store_description: '',
  main_products: '', product_categories: '',
  communication_style: '', tone: '亲切',
  greeting_template: '', closing_template: '',
  business_hours: '', contact_phone: '', contact_email: '',
  shipping_policy: '', return_policy: '',
  custom_info: '', is_active: 1,
})
const saving = ref(false)

const load = async () => {
  try {
    const r = (await storeApi.getProfile()).data
    Object.keys(form).forEach(k => { if (r[k] !== undefined) (form as any)[k] = r[k] })
  } catch { ElMessage.error('加载失败') }
}

const save = async () => {
  saving.value = true
  try {
    await storeApi.updateProfile({ ...form })
    ElMessage.success('店铺画像已保存，AI客服下次对话将自动生效')
  } catch { ElMessage.error('保存失败') }
  saving.value = false
}

onMounted(load)
</script>
