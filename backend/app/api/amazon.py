import json
from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from app.config import settings

router = APIRouter(prefix="/api/amazon", tags=["亚马逊辅助"])

AMAZON_SYSTEM_PROMPT = """你是一个亚马逊电商客服专家。你会收到员工粘贴的亚马逊买家消息页面文本。

请完成以下任务：
1. 从文本中提取买家的问题、诉求和情绪
2. 判断买家的意图（商品咨询/物流查询/退换货/投诉/议价/售后/其他）
3. 判断买家情绪（积极/中性/焦虑/愤怒）
4. 生成3-5条中文回复建议，每条标注风格（专业礼貌/温和安抚/简洁高效/促销引导），供员工选择后直接粘贴回复

严格按以下JSON格式返回，不要包含其他内容：
{
  "buyer_name": "买家名称（如果能识别）",
  "summary": "一句话概括买家诉求",
  "intent": "意图分类",
  "sentiment": "情绪",
  "key_points": ["关键信息点1", "关键信息点2"],
  "responses": [
    {"style": "风格标签", "text": "回复内容", "note": "使用建议"}
  ]
}"""

class AmazonAnalyzeRequest(BaseModel):
    text: str

class AmazonAnalyzeResponse(BaseModel):
    buyer_name: str = ""
    summary: str = ""
    intent: str = ""
    sentiment: str = ""
    key_points: list = []
    responses: list = []

@router.post("/analyze")
async def analyze_conversation(req: AmazonAnalyzeRequest):
    """分析粘贴的亚马逊对话文本，生成回复建议"""
    if not req.text.strip():
        return {
            "buyer_name": "",
            "summary": "未检测到对话内容",
            "intent": "未知",
            "sentiment": "未知",
            "key_points": [],
            "responses": [{"style": "提示", "text": "请粘贴亚马逊买家消息页面的文本内容。", "note": ""}]
        }

    if not settings.LLM_API_KEY:
        return _fallback_analyze(req.text)

    messages = [
        {"role": "system", "content": AMAZON_SYSTEM_PROMPT},
        {"role": "user", "content": f"以下是亚马逊买家消息页面的文本内容，请分析：\n\n{req.text}"}
    ]

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.LLM_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                json={
                    "model": settings.LLM_MODEL,
                    "messages": messages,
                    "temperature": 0.5,
                    "response_format": {"type": "json_object"}
                }
            )
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"]
            parsed = json.loads(result)
            return {
                "buyer_name": parsed.get("buyer_name", ""),
                "summary": parsed.get("summary", ""),
                "intent": parsed.get("intent", ""),
                "sentiment": parsed.get("sentiment", ""),
                "key_points": parsed.get("key_points", []),
                "responses": parsed.get("responses", [])
            }
    except Exception as e:
        print(f"Amazon analyze error: {e}")
        return _fallback_analyze(req.text)

def _fallback_analyze(text: str) -> dict:
    """无LLM时的本地回退分析"""
    text_lower = text.lower()

    # 简单意图判断
    if any(kw in text for kw in ["退款", "退货", "换货", "return", "refund"]):
        intent = "退换货"
    elif any(kw in text for kw in ["快递", "物流", "发货", "shipping", "delivery", "track"]):
        intent = "物流查询"
    elif any(kw in text for kw in ["投诉", "差评", "complaint"]):
        intent = "投诉"
    elif any(kw in text for kw in ["价格", "便宜", "discount", "price"]):
        intent = "议价"
    elif any(kw in text for kw in ["质量", "坏了", "破损", "damaged", "broken"]):
        intent = "售后"
    else:
        intent = "商品咨询"

    # 简单情绪判断
    if any(kw in text for kw in ["生气", "愤怒", "投诉", "差评", "骗子", "awful", "terrible"]):
        sentiment = "愤怒"
    elif any(kw in text for kw in ["着急", "快点", "多久", "urgent", "hurry"]):
        sentiment = "焦虑"
    elif any(kw in text for kw in ["谢谢", "好的", "great", "love", "完美"]):
        sentiment = "积极"
    else:
        sentiment = "中性"

    return {
        "buyer_name": "",
        "summary": f"买家似乎在进行{intent}相关的咨询",
        "intent": intent,
        "sentiment": sentiment,
        "key_points": ["已粘贴的对话内容"],
        "responses": [
            {"style": "专业礼貌", "text": "感谢您的来信！我已收到您的消息，正在为您核实相关信息，会尽快给您回复。", "note": "适合需要时间核实时使用"},
            {"style": "温和安抚", "text": "非常抱歉给您带来了不便，我完全理解您的心情。我会立即为您处理此事，请稍等片刻。", "note": "适合买家情绪不佳时使用"},
            {"style": "简洁高效", "text": "您好，已收到您的反馈，正在处理中，稍后回复您。", "note": "适合简单问题快速响应"},
            {"style": "促销引导", "text": "感谢您的关注！关于您咨询的商品，我们目前还有限时优惠活动，如需了解更多详情请告诉我。", "note": "适合咨询类问题，可引导销售"}
        ]
    }
