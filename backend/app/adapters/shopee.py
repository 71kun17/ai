"""虾皮 (Shopee) 平台适配器"""
import hashlib
import hmac
import time
from datetime import datetime
from typing import List
import httpx
from app.services.platform_adapter import BasePlatformAdapter, PlatformMessage


SHOPEE_API_BASE = "https://partner.shopeemobile.com/api/v2"


class ShopeeAdapter(BasePlatformAdapter):
    """虾皮 Open API v2 Chat 接口适配器"""

    @property
    def platform_name(self) -> str:
        return "shopee"

    def __init__(self, config: dict):
        super().__init__(config)
        self.partner_id = config.get("api_key", "")
        self.partner_key = config.get("api_secret", "")
        self.shop_id = int(config.get("shop_id", 0))
        self.access_token = config.get("access_token", "")
        self.refresh_token = config.get("refresh_token", "")
        self.token_expires_at = config.get("token_expires_at")

    def _sign(self, timestamp: int) -> str:
        base = f"{self.partner_id}{timestamp}{self.access_token}"
        return hmac.new(
            self.partner_key.encode(),
            base.encode(),
            hashlib.sha256
        ).hexdigest()

    def _make_url(self, path: str) -> str:
        timestamp = int(time.time())
        sign = self._sign(timestamp)
        return (
            f"{SHOPEE_API_BASE}{path}"
            f"?partner_id={self.partner_id}"
            f"&timestamp={timestamp}"
            f"&access_token={self.access_token}"
            f"&sign={sign}"
        )

    async def _post(self, path: str, body: dict) -> dict:
        url = self._make_url(path)
        client = await self.get_client()
        resp = await client.post(url, json=body)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise Exception(f"Shopee API error: {data["error"]}")
        return data

    async def fetch_new_messages(self) -> List[PlatformMessage]:
        try:
            body = {
                "shop_id": self.shop_id,
                "page_size": 50,
                "direction": "latest"
            }
            resp = await self._post("/sellerchat/get_message_list", body)

            messages = []
            conversations = resp.get("response", {}).get("conversation_list", [])
            for conv in conversations:
                conversation_id = str(conv.get("conversation_id", ""))
                buyer_name = conv.get("buyer_name", "")
                order_sn = conv.get("order_sn", "")
                for msg in conv.get("message_list", []):
                    if msg.get("message_type") == "image":
                        continue
                    content = msg.get("content", {}).get("text", "")
                    if not content:
                        continue
                    if msg.get("from") != "buyer":
                        continue
                    messages.append(PlatformMessage(
                        platform="shopee",
                        conversation_id=conversation_id,
                        message_id=str(msg.get("message_id", "")),
                        sender="buyer",
                        content=content,
                        timestamp=datetime.fromtimestamp(msg.get("created_timestamp", 0)),
                        buyer_name=buyer_name,
                        order_id=order_sn,
                        raw_data=msg
                    ))
            return messages
        except Exception as e:
            print(f"[ShopeeAdapter] fetch_new_messages error: {e}")
            return []

    async def send_message(self, conversation_id: str, message: str) -> bool:
        try:
            body = {
                "shop_id": self.shop_id,
                "conversation_id": int(conversation_id),
                "message_type": "text",
                "content": {"text": message}
            }
            resp = await self._post("/sellerchat/send_message", body)
            return resp.get("response", {}).get("message_id") is not None
        except Exception as e:
            print(f"[ShopeeAdapter] send_message error: {e}")
            return False

    async def mark_read(self, conversation_id: str) -> bool:
        try:
            body = {
                "shop_id": self.shop_id,
                "conversation_id": int(conversation_id)
            }
            await self._post("/sellerchat/read_conversation", body)
            return True
        except Exception as e:
            print(f"[ShopeeAdapter] mark_read error: {e}")
            return False

    async def refresh_access_token(self) -> bool:
        try:
            body = {
                "refresh_token": self.refresh_token,
                "shop_id": self.shop_id,
                "merchant_id": self.shop_id
            }
            resp = await self._post("/auth/access_token/get", body)
            token_data = resp.get("response", {})
            self.access_token = token_data.get("access_token", self.access_token)
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            expire_in = token_data.get("expire_in", 14400)
            self.token_expires_at = datetime.fromtimestamp(time.time() + expire_in)
            return True
        except Exception as e:
            print(f"[ShopeeAdapter] refresh_token error: {e}")
            return False

    def is_token_expired(self) -> bool:
        if not self.token_expires_at:
            return False
        return time.time() > (self.token_expires_at.timestamp() - 300)