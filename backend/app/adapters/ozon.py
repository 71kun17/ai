"""Ozon Seller API 适配器

文档: https://docs.ozon.ru/api/seller/
认证: Client-Id + Api-Key  header
Base: https://api-seller.ozon.ru

已验证端点:
  POST /v3/product/info/list     - 商品列表
  POST /v2/posting/fbo/list      - FBO订单
  POST /v1/report/info           - 报表
  POST /v1/warehouse/list        - 仓库
  POST /v1/review/list           - 评价

消息/聊天 API: Ozon 暂未开放 (所有 chat/message 端点返回404)
"""
import time
from datetime import datetime
from typing import List
import httpx
from app.services.platform_adapter import BasePlatformAdapter, PlatformMessage

OZON_API_BASE = "https://api-seller.ozon.ru"


class OzonAdapter(BasePlatformAdapter):
    """Ozon Seller API 适配器"""

    @property
    def platform_name(self) -> str:
        return "ozon"

    def __init__(self, config: dict):
        super().__init__(config)
        self.client_id = config.get("api_key", "")
        self.api_key = config.get("api_secret", "")

    def _headers(self) -> dict:
        return {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def _post(self, path: str, body: dict = None) -> dict:
        client = await self.get_client()
        resp = await client.post(
            f"{OZON_API_BASE}{path}",
            json=body or {},
            headers=self._headers()
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "error" in data:
            raise Exception(f"Ozon API error: {data.get("message", data["error"])}")
        return data

    # ── 评价管理 ──

    async def get_reviews(self, limit: int = 50) -> list:
        """获取买家评价列表"""
        try:
            resp = await self._post("/v1/review/list", {"limit": limit})
            return resp.get("result", {}).get("reviews", [])
        except Exception as e:
            print(f"[OzonAdapter] get_reviews error: {e}")
            return []

    async def reply_to_review(self, review_id: str, text: str) -> bool:
        """回复买家评价"""
        try:
            await self._post("/v1/review/comment/create", {
                "review_id": review_id,
                "text": text
            })
            return True
        except Exception as e:
            print(f"[OzonAdapter] reply_to_review error: {e}")
            return False

    # ── 消息轮询(暂不可用) ──

    async def fetch_new_messages(self) -> List[PlatformMessage]:
        # Ozon 没有卖家-买家聊天API，用评价代替
        try:
            reviews = await self.get_reviews(20)
            messages = []
            for rv in reviews:
                if not rv.get("text"):
                    continue
                messages.append(PlatformMessage(
                    platform="ozon",
                    conversation_id=rv.get("id", ""),
                    message_id=f"review_{rv.get('id')}",
                    sender="buyer",
                    content=f"[评价{rv.get('rating')}星] {rv.get('text', '')}",
                    timestamp=datetime.fromisoformat(
                        rv.get("created_at", datetime.utcnow().isoformat())
                        .replace("Z", "+00:00")
                    ),
                    buyer_name=rv.get("author", {}).get("name", ""),
                    order_id=str(rv.get("order_id", "")),
                    raw_data=rv
                ))
            return messages
        except Exception as e:
            print(f"[OzonAdapter] fetch_new_messages error: {e}")
            return []

    async def send_message(self, conversation_id: str, message: str) -> bool:
        # 评价回复
        return await self.reply_to_review(conversation_id, message)

    async def mark_read(self, conversation_id: str) -> bool:
        return True

    async def refresh_access_token(self) -> bool:
        return True

    def is_token_expired(self) -> bool:
        return False