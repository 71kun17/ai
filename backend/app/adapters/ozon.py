"""Ozon Seller API 聊天适配器

真实端点 (基于官方文档):
  POST /v3/chat/list          - 聊天清单
  POST /v3/chat/history       - 聊天历史
  POST /v1/chat/send/message  - 发送消息 (需Premium订阅)
  POST /v1/chat/start         - 创建新聊天
  POST /v2/chat/read          - 标记已读

认证: Client-Id + Api-Key header
"""
from datetime import datetime
from typing import List
import httpx
from app.services.platform_adapter import BasePlatformAdapter, PlatformMessage

OZON_API_BASE = "https://api-seller.ozon.ru"


class OzonAdapter(BasePlatformAdapter):
    """Ozon Seller API 聊天适配器"""

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
            raise Exception(f"Ozon error: {data.get("message", data.get("error"))}")
        return data

    async def fetch_new_messages(self) -> List[PlatformMessage]:
        """拉取未读聊天消息"""
        try:
            # Step 1: 获取未读聊天列表
            resp = await self._post("/v3/chat/list", {
                "filter": {
                    "chat_status": "OPENED",
                    "unread_only": True
                },
                "limit": 50
            })

            chats = resp.get("chats", [])
            if not chats:
                return []

            messages = []
            for ch in chats:
                chat = ch.get("chat", {})
                chat_id = chat.get("chat_id", "")
                if not chat_id:
                    continue

                # Step 2: 获取聊天历史
                try:
                    hist = await self._post("/v3/chat/history", {
                        "chat_id": chat_id,
                        "direction": "Backward",
                        "limit": 20
                    })
                except Exception:
                    continue

                for msg in hist.get("messages", []):
                    user = msg.get("user", {})
                    # 只处理买家消息
                    if user.get("type") not in ("Customer", "customer"):
                        continue

                    data_parts = msg.get("data", [])
                    if not data_parts:
                        continue

                    content = " ".join(str(d) for d in data_parts if isinstance(d, str))
                    if not content.strip():
                        continue

                    messages.append(PlatformMessage(
                        platform="ozon",
                        conversation_id=chat_id,
                        message_id=str(msg.get("message_id", "")),
                        sender="buyer",
                        content=content,
                        timestamp=datetime.fromisoformat(
                            msg.get("created_at", "")
                                .replace("Z", "+00:00")
                        ) if msg.get("created_at") else datetime.utcnow(),
                        buyer_name=user.get("id", ""),
                        order_id=msg.get("context", {}).get("order_number", ""),
                        raw_data=msg
                    ))

            print(f"[OzonAdapter] Fetched {len(messages)} new buyer messages")
            return messages

        except Exception as e:
            print(f"[OzonAdapter] fetch_new_messages error: {e}")
            return []

    async def send_message(self, conversation_id: str, message: str) -> bool:
        """发送消息到买家 (需要Premium Plus/Pro订阅)"""
        try:
            await self._post("/v1/chat/send/message", {
                "chat_id": conversation_id,
                "text": message
            })
            return True
        except Exception as e:
            print(f"[OzonAdapter] send_message error: {e}")
            return False

    async def mark_read(self, conversation_id: str) -> bool:
        """标记已读"""
        try:
            await self._post("/v2/chat/read", {
                "chat_id": conversation_id
            })
            return True
        except Exception as e:
            print(f"[OzonAdapter] mark_read error: {e}")
            return False

    async def refresh_access_token(self) -> bool:
        return True

    def is_token_expired(self) -> bool:
        return False