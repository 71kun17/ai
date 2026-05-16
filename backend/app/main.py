from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.database import init_db
from app.api import knowledge, chat, analytics, config_api, store_api

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(config_api.router)
app.include_router(store_api.router)

@app.get("/health")
def health():
    return {"status": "ok"}
