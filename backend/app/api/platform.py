"""多平台管理API"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.models.database import get_db
from app.models.platform import PlatformConfig, PlatformMessage, AutoReplyLog

router = APIRouter(prefix="/api/platforms", tags=["平台管理"])


# ── Pydantic schemas ──

class PlatformConfigIn(BaseModel):
    platform_name: str
    display_name: str
    api_key: str
    api_secret: str
    shop_id: str = ""
    extra_config: dict = {}
    poll_interval: int = 30


class PlatformConfigOut(BaseModel):
    id: int
    platform_name: str
    display_name: str
    is_active: bool
    poll_interval: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewMessageOut(BaseModel):
    id: int
    platform: str
    conversation_id: str
    buyer_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewAction(BaseModel):
    reply_text: str = ""


class PlatformStats(BaseModel):
    platform: str
    total_messages: int
    auto_replied: int
    pending_review: int
    rejected: int


# ── 平台配置 ──

@router.get("")
def list_platforms(db: Session = Depends(get_db)):
    """获取所有已接入平台"""
    configs = db.query(PlatformConfig).all()
    return [
        {
            "id": c.id,
            "platform_name": c.platform_name,
            "display_name": c.display_name,
            "is_active": c.is_active,
            "poll_interval": c.poll_interval,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in configs
    ]


@router.post("/{platform}/config")
def save_platform_config(platform: str, data: PlatformConfigIn, db: Session = Depends(get_db)):
    """保存或更新平台配置"""
    existing = db.query(PlatformConfig).filter(
        PlatformConfig.platform_name == platform
    ).first()

    if existing:
        existing.api_key = data.api_key
        existing.api_secret = data.api_secret
        existing.shop_id = data.shop_id
        existing.extra_config = data.extra_config
        existing.poll_interval = data.poll_interval
        existing.updated_at = datetime.utcnow()
    else:
        config = PlatformConfig(
            platform_name=platform,
            display_name=data.display_name,
            api_key=data.api_key,
            api_secret=data.api_secret,
            shop_id=data.shop_id,
            extra_config=data.extra_config,
            poll_interval=data.poll_interval
        )
        db.add(config)

    db.commit()
    return {"ok": True}


@router.delete("/{platform}/config")
def delete_platform_config(platform: str, db: Session = Depends(get_db)):
    """删除平台配置"""
    db.query(PlatformConfig).filter(
        PlatformConfig.platform_name == platform
    ).delete()
    db.commit()
    return {"ok": True}


# ── 审核队列 ──

@router.get("/review")
def get_review_queue(
    platform: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取待审核消息列表"""
    query = db.query(PlatformMessage).filter(
        PlatformMessage.status == "pending_review"
    )
    if platform:
        query = query.filter(PlatformMessage.platform == platform)

    messages = query.order_by(PlatformMessage.created_at.desc()).limit(limit).all()
    return [
        {
            "id": m.id,
            "platform": m.platform,
            "conversation_id": m.conversation_id,
            "buyer_name": m.buyer_name,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in messages
    ]


@router.post("/review/{message_id}/approve")
def approve_review(message_id: int, data: ReviewAction, db: Session = Depends(get_db)):
    """审核通过并发送回复"""
    msg = db.query(PlatformMessage).filter(PlatformMessage.id == message_id).first()
    if not msg:
        raise HTTPException(404, "消息不存在")

    msg.status = "auto_replied"

    log = AutoReplyLog(
        platform=msg.platform,
        conversation_id=msg.conversation_id,
        message_id=msg.message_id,
        buyer_message=msg.content,
        reply_content=data.reply_text,
        action="manual_approved"
    )
    db.add(log)
    db.commit()

    return {"ok": True, "reply": data.reply_text}


@router.post("/review/{message_id}/reject")
def reject_review(message_id: int, db: Session = Depends(get_db)):
    """拒绝审核（转人工标签）"""
    msg = db.query(PlatformMessage).filter(PlatformMessage.id == message_id).first()
    if not msg:
        raise HTTPException(404, "消息不存在")

    msg.status = "rejected"

    log = AutoReplyLog(
        platform=msg.platform,
        conversation_id=msg.conversation_id,
        message_id=msg.message_id,
        buyer_message=msg.content,
        action="rejected"
    )
    db.add(log)
    db.commit()

    return {"ok": True}



# ── Ozon 聊天查看 ──

@router.get("/ozon/chats")
async def ozon_chat_list(limit: int = 50):
    """从Ozon拉取聊天列表"""
    from app.models.database import SessionLocal
    db = SessionLocal()
    try:
        config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_name == "ozon",
            PlatformConfig.is_active == True
        ).first()
        if not config:
            return {"chats": [], "error": "Ozon not configured"}

        from app.adapters.ozon import OzonAdapter
        adapter = OzonAdapter({
            "api_key": config.api_key,
            "api_secret": config.api_secret
        })

        resp = await adapter._post("/v3/chat/list", {
            "filter": {"chat_status": "OPENED"},
            "limit": limit
        })
        await adapter.close()

        chats = []
        for ch in resp.get("chats", []):
            c = ch.get("chat", {})
            chats.append({
                "chat_id": c.get("chat_id"),
                "chat_type": c.get("chat_type"),
                "chat_status": c.get("chat_status"),
                "created_at": c.get("created_at"),
                "unread_count": ch.get("unread_count", 0),
                "last_message_id": ch.get("last_message_id"),
            })

        return {
            "chats": chats,
            "total_unread_count": resp.get("total_unread_count", 0),
            "has_next": resp.get("has_next", False)
        }
    finally:
        db.close()


@router.get("/ozon/chats/{chat_id}/messages")
async def ozon_chat_messages(chat_id: str, limit: int = 100):
    """从Ozon拉取指定聊天的消息历史"""
    from app.models.database import SessionLocal
    db = SessionLocal()
    try:
        config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_name == "ozon",
            PlatformConfig.is_active == True
        ).first()
        if not config:
            return {"messages": [], "error": "Ozon not configured"}

        from app.adapters.ozon import OzonAdapter
        adapter = OzonAdapter({
            "api_key": config.api_key,
            "api_secret": config.api_secret
        })

        resp = await adapter._post("/v3/chat/history", {
            "chat_id": chat_id,
            "direction": "Backward",
            "limit": limit
        })
        await adapter.close()

        messages = []
        for m in resp.get("messages", []):
            user = m.get("user", {})
            data_parts = m.get("data", [])
            content = " ".join(str(d) for d in data_parts if isinstance(d, str))
            messages.append({
                "message_id": str(m.get("message_id", "")),
                "user_type": user.get("type", "unknown"),
                "user_id": str(user.get("id", "")),
                "content": content,
                "is_read": m.get("is_read", False),
                "created_at": m.get("created_at"),
                "is_image": m.get("is_image", False),
                "order_number": m.get("context", {}).get("order_number", ""),
            })

        return {
            "messages": messages,
            "has_next": resp.get("has_next", False)
        }
    finally:
        db.close()


@router.post("/ozon/chats/{chat_id}/read")
async def ozon_chat_read(chat_id: str):
    """标记Ozon聊天为已读，消除红点"""
    from app.models.database import SessionLocal
    db = SessionLocal()
    try:
        config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_name == "ozon",
            PlatformConfig.is_active == True
        ).first()
        if not config:
            return {"ok": False, "error": "Ozon not configured"}

        from app.adapters.ozon import OzonAdapter
        adapter = OzonAdapter({
            "api_key": config.api_key,
            "api_secret": config.api_secret
        })

        resp = await adapter._post("/v2/chat/read", {"chat_id": chat_id})
        await adapter.close()

        return {"ok": True, "unread_count": resp.get("unread_count", 0)}
    finally:
        db.close()

# ── 统计 ──

@router.get("/stats")
def get_platform_stats(db: Session = Depends(get_db)):
    """获取各平台自动回复统计"""
    logs = db.query(AutoReplyLog).all()
    stats = {}
    for log in logs:
        if log.platform not in stats:
            stats[log.platform] = {
                "platform": log.platform,
                "total_messages": 0,
                "auto_replied": 0,
                "pending_review": 0,
                "rejected": 0
            }
        stats[log.platform]["total_messages"] += 1
        if log.action == "auto_replied":
            stats[log.platform]["auto_replied"] += 1
        elif log.action == "manual_approved":
            stats[log.platform]["auto_replied"] += 1
        elif log.action == "rejected":
            stats[log.platform]["rejected"] += 1

    pending = db.query(PlatformMessage).filter(
        PlatformMessage.status == "pending_review"
    ).all()
    for m in pending:
        if m.platform in stats:
            stats[m.platform]["pending_review"] += 1

    return list(stats.values())

