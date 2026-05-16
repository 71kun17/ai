from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.models.database import Base

class StoreProfile(Base):
    __tablename__ = 'store_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_name = Column(String(200), default='我的店铺', comment='店铺名称')
    store_logo = Column(String(500), default='', comment='店铺Logo URL')
    store_description = Column(Text, default='', comment='店铺简介')
    main_products = Column(Text, default='', comment='主营产品，逗号分隔')
    product_categories = Column(Text, default='', comment='产品分类，逗号分隔')
    communication_style = Column(String(500), default='友好、专业', comment='沟通风格描述')
    tone = Column(String(50), default='亲切', comment='语气：亲切/正式/活泼/简洁')
    greeting_template = Column(Text, default='', comment='开场白模板')
    closing_template = Column(Text, default='', comment='结束语模板')
    business_hours = Column(String(200), default='工作日 9:00-18:00', comment='营业时间')
    contact_phone = Column(String(50), default='', comment='联系电话')
    contact_email = Column(String(100), default='', comment='联系邮箱')
    shipping_policy = Column(Text, default='', comment='物流配送说明')
    return_policy = Column(Text, default='', comment='退换货政策')
    custom_info = Column(Text, default='', comment='其他自定义信息（JSON格式）')
    is_active = Column(Integer, default=1, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
