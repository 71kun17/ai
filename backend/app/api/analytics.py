from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.database import get_db
from app.models.conversation import Conversation
from app.models.knowledge import Knowledge

router = APIRouter(prefix="/api/analytics", tags=["数据分析"])

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    total_convs = db.query(func.count(Conversation.id)).scalar() or 0
    total_sessions = db.query(func.count(func.distinct(Conversation.session_id))).scalar() or 0
    week_sessions = db.query(func.count(func.distinct(Conversation.session_id))).filter(
        func.date(Conversation.created_at) >= week_ago
    ).scalar() or 0
    handoff_count = db.query(func.count(Conversation.id)).filter(
        Conversation.message.contains("转接")
    ).scalar() or 0
    positive_feedback = db.query(func.count(Conversation.id)).filter(
        Conversation.feedback == "helpful"
    ).scalar() or 0
    negative_feedback = db.query(func.count(Conversation.id)).filter(
        Conversation.feedback == "not_helpful"
    ).scalar() or 0
    kb_count = db.query(func.count(Knowledge.id)).scalar() or 0

    return {
        "total_conversations": total_convs,
        "total_sessions": total_sessions,
        "week_sessions": week_sessions,
        "handoff_count": handoff_count,
        "handoff_rate": round(handoff_count / total_convs * 100, 1) if total_convs else 0,
        "positive_feedback": positive_feedback,
        "negative_feedback": negative_feedback,
        "satisfaction_rate": round(positive_feedback / (positive_feedback + negative_feedback) * 100, 1) if (positive_feedback + negative_feedback) else 0,
        "knowledge_count": kb_count
    }

@router.get("/intents/distribution")
def intent_distribution(db: Session = Depends(get_db)):
    results = db.query(
        Conversation.intent, func.count(Conversation.id)
    ).filter(Conversation.intent.isnot(None)).group_by(Conversation.intent).all()
    return [{"intent": r[0], "count": r[1]} for r in results]

@router.get("/trends/daily")
def daily_trends(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    since = datetime.utcnow().date() - timedelta(days=days)
    results = db.query(
        func.date(Conversation.created_at).label("date"),
        func.count(Conversation.id)
    ).filter(func.date(Conversation.created_at) >= since).group_by("date").order_by("date").all()
    return [{"date": str(r[0]), "count": r[1]} for r in results]

@router.get("/hot/questions")
def hot_questions(limit: int = Query(10, ge=5, le=50), db: Session = Depends(get_db)):
    user_msgs = db.query(Conversation.message).filter(Conversation.role == "user").all()
    word_count = {}
    for (msg,) in user_msgs:
        for word in msg[:50]:
            word_count[word] = word_count.get(word, 0) + 1
    words = [(w, c) for w, c in word_count.items() if len(w) >= 2]
    words.sort(key=lambda x: -x[1])
    return [{"word": w, "count": c} for w, c in words[:limit]]

@router.get("/sessions/recent")
def recent_sessions(limit: int = Query(20, ge=5, le=100), db: Session = Depends(get_db)):
    sessions = db.query(
        Conversation.session_id,
        func.min(Conversation.created_at).label("started"),
        func.count(Conversation.id).label("msg_count")
    ).group_by(Conversation.session_id).order_by(func.min(Conversation.created_at).desc()).limit(limit).all()
    return [{"session_id": s[0], "started": s[1].isoformat(), "msg_count": s[2]} for s in sessions]
