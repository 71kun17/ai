import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.models.conversation import Conversation
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

@router.post("/send")
async def send_message(req: ChatRequest, db: Session = Depends(get_db)):
    session_id = req.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = {"history": [], "failed_count": 0}

    session = sessions[session_id]
    history = session["history"]

    db.add(Conversation(session_id=session_id, role="user", message=req.message))
    db.commit()

    intent = await recognize_intent(req.message, history, req.lang)

    if await should_handoff(req.message, session["failed_count"]):
        answer = "您的问题需要人工客服协助处理，正在为您转接，请稍候..."
        session["history"].append({"role": "user", "content": req.message})
        session["history"].append({"role": "assistant", "content": answer})
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
