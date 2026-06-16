from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from app.models.database import Base

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(100), default='anonymous')
    role = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    intent = Column(String(100))
    entities = Column(Text)
    confidence = Column(Float)
    feedback = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalyticsLog(Base):
    __tablename__ = 'analytics_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False)
    event_type = Column(String(50), nullable=False)
    detail = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
