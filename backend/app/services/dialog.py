import httpx
from functools import lru_cache
from app.config import settings
from app.services.vector_store import vector_store
from app.services.nlp import recognize_intent
from app.models.database import SessionLocal
from app.models.knowledge import Knowledge
from app.models.store_profile import StoreProfile

RAG_PROMPTS = {
    "zh": """{store_context}
你是一个专业的电商客服助手。请严格基于以下【参考资料】回答用户问题。

【参考资料】
{context}

【对话规则】
1. 仅基于参考资料回答，不要编造信息
2. 如果参考资料不足以回答，诚实告知并建议转人工
3. 保持友好、专业的语气
4. 回答简洁，不要过度展开

【用户问题】
{question}

【回复】""",
    "en": """{store_context}
You are a professional e-commerce customer service assistant. Answer strictly based on the following reference materials.

[Reference Materials]
{context}

[Rules]
1. Only answer based on the reference materials, do not fabricate information
2. If the materials are insufficient, honestly state so and suggest human support
3. Maintain a friendly, professional tone
4. Keep answers concise

[User Question]
{question}

[Response]""",
    "ja": """{store_context}
あなたはプロのECカスタマーサービスアシスタントです。以下の参考資料に厳密に基づいて回答してください。

【参考資料】
{context}

【ルール】
1. 参考資料のみに基づいて回答し、情報をでっち上げないでください
2. 資料が不十分な場合は正直に伝え、有人対応を提案してください
3. 親しみやすくプロフェッショナルな口調を保ってください
4. 簡潔に回答してください

【ユーザー質問】
{question}

【回答】""",
    "ko": """{store_context}
당신은 전문 전자상거래 고객 서비스 어시스턴트입니다. 다음 참고 자료에 기반하여 답변하세요.

[참고 자료]
{context}

[규칙]
1. 참고 자료에만 기반하여 답변하고 정보를 조작하지 마세요
2. 자료가 불충분하면 솔직히 알리고 상담원 연결을 제안하세요
3. 친절하고 전문적인 어조를 유지하세요
4. 간결하게 답변하세요

[사용자 질문]
{question}

[답변]""",
    "fr": """{store_context}
Vous êtes un assistant professionnel du service client e-commerce. Répondez strictement sur la base des documents de référence.

[Documents de référence]
{context}

[Règles]
1. Répondez uniquement sur la base des documents, n'inventez pas d'informations
2. Si les documents sont insuffisants, indiquez-le honnêtement et suggérez une assistance humaine
3. Gardez un ton amical et professionnel
4. Soyez concis

[Question de l'utilisateur]
{question}

[Réponse]""",
    "es": """{store_context}
Eres un asistente profesional de atención al cliente de e-commerce. Responde estrictamente basándote en los materiales de referencia.

[Materiales de referencia]
{context}

[Reglas]
1. Responde solo basándote en los materiales, no inventes información
2. Si los materiales son insuficientes, indícalo honestamente y sugiere asistencia humana
3. Mantén un tono amable y profesional
4. Sé conciso

[Pregunta del usuario]
{question}

[Respuesta]""",
    "de": """{store_context}
Du bist ein professioneller E-Commerce-Kundendienst-Assistent. Antworte ausschließlich auf Basis der Referenzmaterialien.

[Referenzmaterialien]
{context}

[Regeln]
1. Antworte nur basierend auf den Materialien, erfinde keine Informationen
2. Wenn die Materialien nicht ausreichen, gib dies ehrlich zu und schlage menschliche Hilfe vor
3. Bewahre einen freundlichen, professionellen Ton
4. Halte die Antworten knapp

[Benutzerfrage]
{question}

[Antwort]""",
}

RAG_PROMPT = """{store_context}
你是一个专业的电商客服助手。请严格基于以下【参考资料】回答用户问题。

【参考资料】
{context}

【对话规则】
1. 仅基于参考资料回答，不要编造信息
2. 如果参考资料不足以回答，诚实告知并建议转人工
3. 保持友好、专业的语气
4. 回答简洁，不要过度展开

【用户问题】
{question}

【回复】"""

HANDOFF_KEYWORDS = ["投诉", "退款纠纷", "举报", "欺诈", "诈骗", "赔偿", "法律", "起诉"]

async def should_handoff(user_message: str, failed_attempts: int = 0) -> bool:
    if failed_attempts >= 3:
        return True
    for kw in HANDOFF_KEYWORDS:
        if kw in user_message:
            return True
    return False

def _db_keyword_search(query: str, top_k: int = 3) -> list:
    db = SessionLocal()
    try:
        items = db.query(Knowledge).filter(Knowledge.status == 'published').all()
        results = []
        for item in items:
            score = 0
            for kw in query:
                if kw in item.question or kw in item.keywords:
                    score += 1
            if score > 0:
                results.append({
                    "id": item.id,
                    "document": f"Q: {item.question}\nA: {item.answer}",
                    "similarity": min(score / max(len(query), 1), 1.0)
                })
        results.sort(key=lambda x: -x["similarity"])
        return results[:top_k]
    finally:
        db.close()

@lru_cache(maxsize=1)
def build_store_context() -> str:
    """从数据库读取店铺画像，构建注入prompt的上下文"""
    db = SessionLocal()
    try:
        profile = db.query(StoreProfile).first()
        if not profile or not profile.is_active:
            return ""

        parts = []
        parts.append("【店铺身份信息】")
        if profile.store_name:
            parts.append(f"- 店铺名称: {profile.store_name}")
        if profile.store_description:
            parts.append(f"- 店铺简介: {profile.store_description}")
        if profile.main_products:
            parts.append(f"- 主营产品: {profile.main_products}")
        if profile.product_categories:
            parts.append(f"- 产品分类: {profile.product_categories}")
        if profile.business_hours:
            parts.append(f"- 营业时间: {profile.business_hours}")
        if profile.contact_phone or profile.contact_email:
            contact = []
            if profile.contact_phone:
                contact.append(f"电话 {profile.contact_phone}")
            if profile.contact_email:
                contact.append(f"邮箱 {profile.contact_email}")
            parts.append(f"- 联系方式: {', '.join(contact)}")

        parts.append("")
        parts.append("【沟通风格要求】")
        if profile.communication_style:
            parts.append(f"- 整体风格: {profile.communication_style}")
        if profile.tone:
            parts.append(f"- 语气: {profile.tone}")
        if profile.greeting_template:
            parts.append(f"- 开场白参考: {profile.greeting_template}")
        if profile.closing_template:
            parts.append(f"- 结束语参考: {profile.closing_template}")

        if profile.shipping_policy or profile.return_policy:
            parts.append("")
            parts.append("【业务政策】")
            if profile.shipping_policy:
                parts.append(f"- 物流配送: {profile.shipping_policy}")
            if profile.return_policy:
                parts.append(f"- 退换货: {profile.return_policy}")

        if profile.custom_info:
            parts.append("")
            parts.append("【其他信息】")
            parts.append(profile.custom_info)

        return "\n".join(parts)
    finally:
        db.close()

async def generate_answer(user_message: str, intent: dict, history: list = None, lang: str = "zh") -> dict:
    kb_results = vector_store.search(user_message, top_k=3)
    if not kb_results:
        kb_results = _db_keyword_search(user_message, top_k=3)

    context_parts = []
    for r in kb_results:
        context_parts.append(f"【{r['id']}】{r['document']}")
    context = "\n\n".join(context_parts) if context_parts else "暂无相关参考资料"

    store_context = build_store_context()

    if not settings.LLM_API_KEY:
        if kb_results:
            doc = kb_results[0]['document']
            answer = doc.split('\nA: ')[-1] if '\nA: ' in doc else doc
        else:
            answer = "抱歉，我暂时无法回答这个问题。正在为您转接人工客服..."
    else:
        system_prompt = RAG_PROMPTS.get(lang, RAG_PROMPTS['zh']).format(
            store_context=store_context,
            context=context,
            question=user_message
        )
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages = [messages[0]] + history[-6:] + [{"role": "user", "content": user_message}]
        else:
            messages.append({"role": "user", "content": user_message})
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{settings.LLM_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                    json={"model": settings.LLM_MODEL, "messages": messages, "temperature": 0.3}
                )
                resp.raise_for_status()
                answer = resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"LLM generation error: {e}")
            if kb_results:
                doc = kb_results[0]['document']
                answer = doc.split('\nA: ')[-1] if '\nA: ' in doc else doc
            else:
                answer = "抱歉，服务暂时不可用，请稍后再试。"

    return {
        "answer": answer,
        "intent": intent,
        "sources": [{"id": r["id"], "similarity": r["similarity"]} for r in kb_results],
        "kb_matched": len(kb_results) > 0
    }
