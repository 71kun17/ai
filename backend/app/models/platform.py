"""多平台数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from app.models.database import Base


class PlatformConfig(Base):
    """平台API配置"""
    __tablename__ = 'platform_configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_name = Column(String(50), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    api_key = Column(String(500), nullable=False)
    api_secret = Column(String(500), nullable=False)
    access_token = Column(String(1000), default='')
    refresh_token = Column(String(1000), default='')
    token_expires_at = Column(DateTime, nullable=True)
    shop_id = Column(String(100), default='')
    extra_config = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    poll_interval = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlatformMessage(Base):
    """平台消息记录"""
    __tablename__ = 'platform_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False, index=True)
    conversation_id = Column(String(100), nullable=False, index=True)
    message_id = Column(String(100), nullable=False, unique=True)
    sender = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    buyer_name = Column(String(100), default='')
    order_id = Column(String(100), default='')
    raw_data = Column(JSON, default={})
    status = Column(String(30), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)


class AutoReplyLog(Base):
    """自动回复日志"""
    __tablename__ = 'auto_reply_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False)
    conversation_id = Column(String(100), nullable=False)
    message_id = Column(String(100), nullable=False)
    buyer_message = Column(Text, default='')
    reply_content = Column(Text, default='')
    kb_score = Column(Float, default=0.0)
    intent_score = Column(Float, default=0.0)
    final_confidence = Column(Float, default=0.0)
    action = Column(String(30), default='auto_replied')
    handoff = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)