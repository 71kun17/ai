from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import app.models.knowledge
    import app.models.conversation
    import app.models.store_profile
    import app.models.platform
    Base.metadata.create_all(bind=engine)
    from app.services.vector_store import vector_store
    from app.models.knowledge import Knowledge
    db = SessionLocal()
    try:
        items = db.query(Knowledge).filter(Knowledge.status == 'published').all()
        if items:
            vector_store.rebuild_from_db(items)
    finally:
        db.close()
