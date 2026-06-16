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
    import app.models.handoff
    Base.metadata.create_all(bind=engine)

    # Migration: add lang column to handoff_sessions if not exists
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            cols = [row[1] for row in conn.execute(text("PRAGMA table_info(handoff_sessions)")).fetchall()]
            if 'lang' not in cols:
                conn.execute(text("ALTER TABLE handoff_sessions ADD COLUMN lang VARCHAR(10) DEFAULT 'zh'"))
                conn.commit()
    except Exception:
        pass
    from app.services.vector_store import vector_store
    from app.models.knowledge import Knowledge
    db = SessionLocal()
    try:
        items = db.query(Knowledge).filter(Knowledge.status == 'published').all()
        if items:
            vector_store.rebuild_from_db(items)
    finally:
        db.close()

