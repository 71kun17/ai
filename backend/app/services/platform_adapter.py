"""多平台适配器抽象基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import httpx


@dataclass
class PlatformMessage:
    """统一的消息数据结构"""
    platform: str
    conversation_id: str
    message_id: str
    sender: str  # buyer / seller
    content: str
    timestamp: datetime
    buyer_name: str = ""
    order_id: Optional[str] = None
    raw_data: dict = field(default_factory=dict)


@dataclass
class ReplyResult:
    """回复结果"""
    message_id: str
    answer: str
    kb_score: float
    intent_score: float
    final_confidence: float
    sources: list = field(default_factory=list)
    handoff: bool = False


class BasePlatformAdapter(ABC):
    """
    平台适配器抽象基类。
    每个平台（虾皮、亚马逊等）需实现此类。
    """

    def __init__(self, config: dict):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """返回平台标识，如 'shopee', 'amazon'"""
        ...

    async def get_client(self) -> httpx.AsyncClient:
        """获取或创建 HTTP 客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30)
        return self._client

    @abstractmethod
    async def fetch_new_messages(self) -> List[PlatformMessage]:
        """拉取新消息"""
        ...

    @abstractmethod
    async def send_message(self, conversation_id: str, message: str) -> bool:
        """发送消息到指定会话"""
        ...

    @abstractmethod
    async def mark_read(self, conversation_id: str) -> bool:
        """标记会话为已读"""
        ...

    async def close(self):
        """关闭HTTP客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()