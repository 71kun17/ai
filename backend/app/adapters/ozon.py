"""Ozon Seller API 平台适配器"""
import time
from datetime import datetime
from typing import List
import httpx
from app.services.platform_adapter import BasePlatformAdapter, PlatformMessage

OZON_API_BASE = "https://api-seller.ozon.ru"


class OzonAdapter(BasePlatformAdapter):
    """Ozon Seller API Chat 适配器"""

    @property
    def platform_name(self) -> str:
        return "ozon"

    def __init__(self, config: dict):
        super().__init__(config)
        self.client_id = config.get("api_key", "")
        self.api_key = config.get("api_secret", "")
        self.shop_id = config.get("shop_id", "")

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
        if data.get("error"):
            raise Exception(f"Ozon API error: {data.get('error')}")
        return data

    async def fetch_new_messages(self) -> List[PlatformMessage]:
        """拉取未读聊天消息"""
        try:
            resp = await self._post("/v1/chat/list", {
                "filter": {"unread_only": True},
                "limit": 50
            })

            messages = []
            chats = resp.get("result", {}).get("chats", [])
            for chat in chats:
                chat_id = chat.get("chat_id", "")
                if not chat_id:
                    continue

                buyer_name = chat.get("user", {}).get("name", "")
                order_id = chat.get("order", {}).get("order_id", "")

                msg_resp = await self._post(f"/v1/chat/{chat_id}/messages", {
                    "limit": 20,
                    "offset": 0
                })

                for msg in msg_resp.get("result", {}).get("messages", []):
                    if msg.get("direction") != "client_to_seller":
                        continue
                    text = msg.get("text", "")
                    if not text:
                        continue

                    messages.append(PlatformMessage(
                        platform="ozon",
                        conversation_id=str(chat_id),
                        message_id=str(msg.get("id", "")),
                        sender="buyer",
                        content=text,
                        timestamp=datetime.fromisoformat(
                            msg.get("created_at", datetime.utcnow().isoformat())
                            .replace("Z", "+00:00")
                        ),
                        buyer_name=buyer_name,
                        order_id=str(order_id) if order_id else None,
                        raw_data=msg
                    ))

            return messages
        except Exception as e:
            print(f"[OzonAdapter] fetch_new_messages error: {e}")
            return []

    async def send_message(self, conversation_id: str, message: str) -> bool:
        """发送回复"""
        try:
            resp = await self._post(f"/v1/chat/{conversation_id}/message", {
                "text": message
            })
            return resp.get("result", {}).get("id") is not None
        except Exception as e:
            print(f"[OzonAdapter] send_message error: {e}")
            return False

    async def mark_read(self, conversation_id: str) -> bool:
        """Ozon 拉取后自动标记已读，无需额外调用"""
        return True

    async def refresh_access_token(self) -> bool:
        """Ozon API Key 长期有效，无需刷新"""
        return True

    def is_token_expired(self) -> bool:
        return False