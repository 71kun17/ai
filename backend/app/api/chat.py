import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.models.conversation import Conversation
from app.models.handoff import HandoffSession, HandoffMessage
from app.services.dialog import generate_answer, should_handoff
from app.services.nlp import recognize_intent

router = APIRouter(prefix="/api/chat", tags=["对话"])

sessions = {}

class ChatRequest(BaseModel):
    session_id: str = None
    message: str
    lang: str = 'zh'

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    intent: dict = None
    handoff: bool = False
    sources: list = []

class HandoffReplyRequest(BaseModel):
    session_id: str
    message: str
    admin_name: str = '客服'

class HandoffTakeoverRequest(BaseModel):
    session_id: str
    admin_name: str = '客服'

@router.post("/send")
async def send_message(req: ChatRequest, db: Session = Depends(get_db)):
    session_id = req.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = {"history": [], "failed_count": 0}

    session = sessions[session_id]
    history = session["history"]

    # Check if this session is in handoff mode (active)
    handoff = db.query(HandoffSession).filter(
        HandoffSession.session_id == session_id,
        HandoffSession.status.in_(["active"])
    ).first()

    if handoff:
        # In handoff mode: just save user message, don't use AI
        db.add(Conversation(session_id=session_id, role="user", message=req.message))
        db.add(HandoffMessage(session_id=session_id, role="user", content=req.message))
        handoff.updated_at = datetime.now(timezone.utc)
        db.commit()
        return ChatResponse(
            session_id=session_id,
            answer="",
            intent={},
            handoff=True,
            sources=[]
        )

    db.add(Conversation(session_id=session_id, role="user", message=req.message))
    db.commit()

    intent = await recognize_intent(req.message, history, req.lang)

    should = await should_handoff(req.message, session["failed_count"])
    if should:
        answer = "您的问题需要人工客服协助处理，正在为您转接，请稍候..."
        session["history"].append({"role": "user", "content": req.message})
        session["history"].append({"role": "assistant", "content": answer})

        # Create handoff session
        existing = db.query(HandoffSession).filter(
            HandoffSession.session_id == session_id
        ).first()
        if not existing:
            db.add(HandoffSession(session_id=session_id, status="waiting"))
            db.add(HandoffMessage(session_id=session_id, role="system", content="用户请求转人工客服"))
            db.commit()

        return ChatResponse(session_id=session_id, answer=answer, intent=intent, handoff=True)

    result = await generate_answer(req.message, intent, history, req.lang)

    if not result["kb_matched"]:
        session["failed_count"] += 1
    else:
        session["failed_count"] = 0

    db.add(Conversation(
        session_id=session_id, role="assistant",
        message=result["answer"], intent=intent.get("intent"),
        entities=str(intent.get("entities")), confidence=intent.get("confidence")
    ))
    db.commit()

    session["history"].append({"role": "user", "content": req.message})
    session["history"].append({"role": "assistant", "content": result["answer"]})

    return ChatResponse(
        session_id=session_id, answer=result["answer"],
        intent=intent, handoff=False, sources=result["sources"]
    )

@router.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    msgs = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).order_by(Conversation.created_at).all()
    return [{"role": m.role, "message": m.message, "time": m.created_at.isoformat()} for m in msgs]

# ---------- Handoff API ----------

@router.get("/handoff/queue")
def handoff_queue(db: Session = Depends(get_db)):
    """获取等待人工的会话列表"""
    items = db.query(HandoffSession).filter(
        HandoffSession.status.in_(["waiting", "active"])
    ).order_by(HandoffSession.updated_at.desc()).all()
    result = []
    for h in items:
        last_msg = db.query(HandoffMessage).filter(
            HandoffMessage.session_id == h.session_id
        ).order_by(HandoffMessage.created_at.desc()).first()
        result.append({
            "session_id": h.session_id,
            "status": h.status,
            "admin_name": h.admin_name,
            "created_at": h.created_at.isoformat(),
            "updated_at": h.updated_at.isoformat(),
            "last_message": last_msg.content if last_msg else "",
            "last_role": last_msg.role if last_msg else "",
        })
    return result

@router.post("/handoff/takeover")
def handoff_takeover(req: HandoffTakeoverRequest, db: Session = Depends(get_db)):
    """管理员接管会话"""
    handoff = db.query(HandoffSession).filter(
        HandoffSession.session_id == req.session_id
    ).first()
    if not handoff:
        return {"ok": False, "error": "会话不存在"}
    handoff.status = "active"
    handoff.admin_name = req.admin_name
    handoff.updated_at = datetime.now(timezone.utc)
    db.add(HandoffMessage(
        session_id=req.session_id,
        role="system",
        content=f"客服 {req.admin_name} 已接入"
    ))
    db.commit()
    return {"ok": True}

@router.post("/handoff/reply")
def handoff_reply(req: HandoffReplyRequest, db: Session = Depends(get_db)):
    """管理员回复用户"""
    handoff = db.query(HandoffSession).filter(
        HandoffSession.session_id == req.session_id
    ).first()
    if not handoff:
        return {"ok": False, "error": "会话不存在"}
    handoff.updated_at = datetime.now(timezone.utc)
    db.add(Conversation(session_id=req.session_id, role="assistant", message=req.message))
    db.add(HandoffMessage(session_id=req.session_id, role="admin", content=req.message))
    db.commit()
    return {"ok": True}

@router.post("/handoff/resolve")
def handoff_resolve(req: HandoffTakeoverRequest, db: Session = Depends(get_db)):
    """管理员结束会话"""
    handoff = db.query(HandoffSession).filter(
        HandoffSession.session_id == req.session_id
    ).first()
    if not handoff:
        return {"ok": False, "error": "会话不存在"}
    handoff.status = "resolved"
    handoff.updated_at = datetime.now(timezone.utc)
    db.add(HandoffMessage(
        session_id=req.session_id,
        role="system",
        content="会话已结束"
    ))
    db.commit()
    return {"ok": True}

@router.get("/handoff/{session_id}/messages")
def handoff_messages(session_id: str, db: Session = Depends(get_db)):
    """获取转人工会话的所有消息"""
    msgs = db.query(HandoffMessage).filter(
        HandoffMessage.session_id == session_id
    ).order_by(HandoffMessage.created_at).all()
    return [{
        "role": m.role,
        "content": m.content,
        "time": m.created_at.isoformat()
    } for m in msgs]

@router.get("/handoff/{session_id}/poll")
def handoff_poll(
    session_id: str,
    after_id: int = Query(0),
    db: Session = Depends(get_db)
):
    """用户端轮询：获取after_id之后的新消息"""
    msgs = db.query(HandoffMessage).filter(
        HandoffMessage.session_id == session_id,
        HandoffMessage.id > after_id
    ).order_by(HandoffMessage.created_at).all()
    return [{
        "id": m.id,
        "role": m.role,
        "content": m.content,
        "time": m.created_at.isoformat()
    } for m in msgs]

@router.get("/handoff/{session_id}/status")
def handoff_status(session_id: str, db: Session = Depends(get_db)):
    """查询handoff会话状态"""
    handoff = db.query(HandoffSession).filter(
        HandoffSession.session_id == session_id
    ).first()
    if not handoff:
        return {"status": "none"}
    return {
        "status": handoff.status,
        "admin_name": handoff.admin_name,
    }

