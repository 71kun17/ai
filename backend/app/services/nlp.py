import json
import httpx
from app.config import settings

INTENT_LABELS = [
    "商品咨询", "物流查询", "订单查询", "退换货", "投诉建议",
    "价格咨询", "支付问题", "账户问题", "售后维修", "闲聊"
]

ENTITY_TYPES = ["商品名", "订单号", "日期", "金额", "手机号", "地址", "快递公司"]

LANG_PROMPTS = {
    "zh": """你是一个电商智能客服的意图识别引擎。分析用户输入，严格按JSON格式返回：

{"intent": "商品咨询/物流查询/订单查询/退换货/投诉建议/价格咨询/支付问题/账户问题/售后维修/闲聊", "entities": [{"type": "实体类型", "value": "实体值"}], "confidence": 0.0-1.0, "summary": "一句话概括用户需求"}

实体类型包括: 商品名, 订单号, 日期, 金额, 手机号, 地址, 快递公司""",
    "en": """You are an intent recognition engine for an e-commerce customer service. Analyze user input and return strictly in JSON format:

{"intent": "Product Inquiry/Logistics Query/Order Query/Returns & Exchanges/Complaints/Price Inquiry/Payment Issue/Account Issue/After-sales/Chat", "entities": [{"type": "entity type", "value": "entity value"}], "confidence": 0.0-1.0, "summary": "one sentence summary"}

Entity types: product name, order number, date, amount, phone, address, courier""",
    "ja": """あなたはECカスタマーサービスの意図認識エンジンです。ユーザー入力を分析し、厳密にJSON形式で返してください：

{"intent": "商品相談/物流照会/注文照会/返品交換/苦情/価格照会/支払い問題/アカウント問題/アフターサービス/雑談", "entities": [{"type": "エンティティタイプ", "value": "値"}], "confidence": 0.0-1.0, "summary": "一言で要約"}""",
    "ko": """당신은 전자상거래 고객 서비스의 의도 인식 엔진입니다. 사용자 입력을 분석하고 JSON 형식으로 반환하세요:

{"intent": "상품문의/물류조회/주문조회/반품교환/불만/가격문의/결제문제/계정문제/A/S/잡담", "entities": [{"type": "엔티티 유형", "value": "값"}], "confidence": 0.0-1.0, "summary": "한 문장 요약"}""",
    "fr": """Vous êtes un moteur de reconnaissance d'intention pour le service client e-commerce. Analysez et retournez en JSON:

{"intent": "Consultation produit/Suivi logistique/Suivi commande/Retours échanges/Réclamations/Prix/Paiement/Compte/SAV/Discussion", "entities": [{"type": "type", "value": "valeur"}], "confidence": 0.0-1.0, "summary": "résumé"}""",
    "es": """Eres un motor de reconocimiento de intención para atención al cliente de e-commerce. Analiza y devuelve en JSON:

{"intent": "Consulta producto/Logística/Pedido/Devoluciones/Reclamaciones/Precio/Pago/Cuenta/Postventa/Charla", "entities": [{"type": "tipo", "value": "valor"}], "confidence": 0.0-1.0, "summary": "resumen"}""",
    "de": """Du bist eine Intent-Erkennungs-Engine für den E-Commerce-Kundenservice. Analysiere und gib JSON zurück:

{"intent": "Produktanfrage/Logistik/Bestellung/Rückgabe/Beschwerde/Preis/Zahlung/Konto/After-Sales/Plauderei", "entities": [{"type": "Typ", "value": "Wert"}], "confidence": 0.0-1.0, "summary": "Zusammenfassung"}""",
}

SYSTEM_PROMPT = f"""你是一个电商智能客服的意图识别引擎。分析用户输入，严格按JSON格式返回：

{{
  "intent": "{'/'.join(INTENT_LABELS)} 中的一个",
  "entities": [{{"type": "实体类型", "value": "实体值"}}],
  "confidence": 0.0-1.0,
  "summary": "一句话概括用户需求"
}}

实体类型包括: {', '.join(ENTITY_TYPES)}"""

async def recognize_intent(user_message: str, history: list = None, lang: str = "zh") -> dict:
    """调用LLM进行意图识别和实体抽取"""
    if not settings.LLM_API_KEY:
        return _fallback_intent(user_message)

    prompt = LANG_PROMPTS.get(lang, LANG_PROMPTS["zh"])
    messages = [{"role": "system", "content": prompt}]
    if history:
        messages.extend(history[-4:])
    messages.append({"role": "user", "content": user_message})

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.LLM_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                json={
                    "model": settings.LLM_MODEL,
                    "messages": messages,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }
            )
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"]
            return json.loads(result)
    except Exception as e:
        print(f"Intent recognition error: {e}")
        return _fallback_intent(user_message)

def _fallback_intent(text: str) -> dict:
    """基于关键词的本地意图识别回退方案"""
    keyword_map = {
        "物流查询": ["快递", "物流", "发货", "到哪", "配送", "运输"],
        "退换货": ["退货", "换货", "退款", "退钱"],
        "订单查询": ["订单", "下单", "买了"],
        "价格咨询": ["多少钱", "价格", "便宜", "贵", "优惠", "打折"],
        "支付问题": ["支付", "付款", "微信", "支付宝", "花呗"],
        "商品咨询": ["怎么", "什么", "哪个", "好不好", "质量"],
        "投诉建议": ["投诉", "差评", "举报"],
        "账户问题": ["账号", "密码", "登录", "注册", "会员"],
        "闲聊": ["你好", "谢谢", "天气"],
    }
    entities = []
    for word in ["JD", "DD", "TB"]:
        import re
        match = re.search(rf'{word}\d{{8,}}', text)
        if match:
            entities.append({"type": "订单号", "value": match.group()})

    for intent, keywords in keyword_map.items():
        if any(kw in text for kw in keywords):
            return {"intent": intent, "entities": entities, "confidence": 0.7, "summary": text[:30]}
    return {"intent": "商品咨询", "entities": entities, "confidence": 0.5, "summary": text[:30]}
