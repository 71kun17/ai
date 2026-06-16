import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from app.models.database import get_db
from app.models.store_profile import StoreProfile

router = APIRouter(prefix="/api/store", tags=["店铺画像"])

class StoreProfileUpdate(BaseModel):
    store_name: Optional[str] = None
    store_logo: Optional[str] = None
    store_description: Optional[str] = None
    main_products: Optional[str] = None
    product_categories: Optional[str] = None
    communication_style: Optional[str] = None
    tone: Optional[str] = None
    greeting_template: Optional[str] = None
    closing_template: Optional[str] = None
    business_hours: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    shipping_policy: Optional[str] = None
    return_policy: Optional[str] = None
    custom_info: Optional[str] = None
    is_active: Optional[int] = None

def _get_or_create_profile(db: Session) -> StoreProfile:
    profile = db.query(StoreProfile).first()
    if not profile:
        profile = StoreProfile()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db)
    return {
        "id": profile.id,
        "store_name": profile.store_name,
        "store_logo": profile.store_logo,
        "store_description": profile.store_description,
        "main_products": profile.main_products,
        "product_categories": profile.product_categories,
        "communication_style": profile.communication_style,
        "tone": profile.tone,
        "greeting_template": profile.greeting_template,
        "closing_template": profile.closing_template,
        "business_hours": profile.business_hours,
        "contact_phone": profile.contact_phone,
        "contact_email": profile.contact_email,
        "shipping_policy": profile.shipping_policy,
        "return_policy": profile.return_policy,
        "custom_info": profile.custom_info,
        "is_active": profile.is_active,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }

@router.put("/profile")
def update_profile(data: StoreProfileUpdate, db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    from app.services.dialog import build_store_context
    build_store_context.cache_clear()
    return {"ok": True, "message": "店铺画像已更新"}
