"""Ozon Seller API 平台适配器 (待验证)

Ozon Seller API 文档: https://docs.ozon.ru/api/seller/

TODO: Ozon 的公开 API 暂时未确认是否包含消息/客服模块。
当前适配器为占位实现，需要根据实际 API 文档调整端点。

常用已验证端点:
  - POST /v1/product/list         获取商品列表
  - POST /v1/posting/fbs/list     获取FBS订单
  - POST /v2/posting/fbo/list     获取FBO订单
"""
import time
from datetime import datetime
from typing import List
import httpx
from app.services.platform_adapter import BasePlatformAdapter, PlatformMessage

OZON_API_BASE = "https://api-seller.ozon.ru"


class OzonAdapter(BasePlatformAdapter):
    """Ozon Seller API 适配器 (消息模块待验证)"""

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
        if "error" in data:
            raise Exception(f"Ozon API error: {data["error"]}")
        return data

    async def fetch_new_messages(self) -> List[PlatformMessage]:
        # TODO: Ozon 消息API端点待确认，当前返回空列表
        # 需要根据 https://docs.ozon.ru/api/seller/ 找到实际的聊天端点
        print("[OzonAdapter] fetch_new_messages: Ozon chat API not yet configured")
        return []

    async def send_message(self, conversation_id: str, message: str) -> bool:
        # TODO: Ozon 发送消息API端点待确认
        print(f"[OzonAdapter] send_message: Ozon chat API not yet configured")
        return False

    async def mark_read(self, conversation_id: str) -> bool:
        return True

    async def refresh_access_token(self) -> bool:
        return True

    def is_token_expired(self) -> bool:
        return False