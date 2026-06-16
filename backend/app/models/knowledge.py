from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
import enum
from app.models.database import Base

class KnowledgeType(str, enum.Enum):
    FAQ = 'faq'
    DOCUMENT = 'document'
    API_RESPONSE = 'api_response'

class KnowledgeStatus(str, enum.Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'

class Knowledge(Base):
    __tablename__ = 'knowledge'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), default='通用')
    tags = Column(String(500), default='')
    keywords = Column(String(500), default='')
    knowledge_type = Column(String(20), default='faq')
    status = Column(String(20), default='published')
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
