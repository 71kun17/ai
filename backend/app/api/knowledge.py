from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from app.models.database import get_db
from app.models.knowledge import Knowledge

router = APIRouter(prefix="/api/knowledge", tags=["知识库"])

class KnowledgeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    category: str = "通用"
    tags: str = ""
    keywords: str = ""

class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    keywords: Optional[str] = None
    status: Optional[str] = None

@router.get("/")
def list_knowledge(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None, status: Optional[str] = None,
    search: Optional[str] = None, db: Session = Depends(get_db)
):
    q = db.query(Knowledge)
    if category:
        q = q.filter(Knowledge.category == category)
    if status:
        q = q.filter(Knowledge.status == status)
    if search:
        q = q.filter(Knowledge.question.contains(search) | Knowledge.title.contains(search))
    total = q.count()
    items = q.order_by(Knowledge.updated_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}

@router.post("/")
def create_knowledge(data: KnowledgeCreate, db: Session = Depends(get_db)):
    item = Knowledge(**data.model_dump(), status="published")
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{knowledge_id}")
def get_knowledge(knowledge_id: int, db: Session = Depends(get_db)):
    item = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    if not item:
        raise HTTPException(404, "知识条目不存在")
    return item

@router.put("/{knowledge_id}")
def update_knowledge(knowledge_id: int, data: KnowledgeUpdate, db: Session = Depends(get_db)):
    item = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    if not item:
        raise HTTPException(404, "知识条目不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{knowledge_id}")
def delete_knowledge(knowledge_id: int, db: Session = Depends(get_db)):
    item = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    if not item:
        raise HTTPException(404, "知识条目不存在")
    db.delete(item)
    db.commit()
    return {"deleted": True}

@router.get("/categories/list")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Knowledge.category).distinct().all()
    return [c[0] for c in cats if c[0]]
