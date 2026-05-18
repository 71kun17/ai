from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.config import settings
from app.models.database import init_db, SessionLocal
from app.models.platform import PlatformConfig
from app.services.auto_reply import AutoReplyEngine
from app.adapters.shopee import ShopeeAdapter
from app.adapters.ozon import OzonAdapter
from app.api import knowledge, chat, analytics, config_api, store_api, amazon, platform

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
app.include_router(amazon.router)
app.include_router(platform.router)

polling_tasks: list = []


async def poll_platform(config_id: int):
    db = SessionLocal()
    try:
        config = db.query(PlatformConfig).filter(PlatformConfig.id == config_id).first()
        if not config or not config.is_active:
            return
        if config.platform_name == 'ozon':
            adapter = OzonAdapter({
                'api_key': config.api_key,
                'api_secret': config.api_secret,
                'shop_id': config.shop_id
            })
        else:
            adapter = ShopeeAdapter({
            "api_key": config.api_key,
            "api_secret": config.api_secret,
            "shop_id": config.shop_id,
            "access_token": config.access_token,
            "refresh_token": config.refresh_token,
            "token_expires_at": config.token_expires_at
        })
        engine = AutoReplyEngine()
        print(f"[Poller] {config.platform_name} started (interval={config.poll_interval}s)")
        while True:
            try:
                msgs = await adapter.fetch_new_messages()
                for msg in msgs:
                    await engine.process_message(msg, adapter)
            except Exception as e:
                print(f"[Poller] {config.platform_name} error: {e}")
            await asyncio.sleep(config.poll_interval)
    finally:
        db.close()


@app.on_event("startup")
async def start_pollers():
    db = SessionLocal()
    try:
        configs = db.query(PlatformConfig).filter(PlatformConfig.is_active == True).all()
        for c in configs:
            task = asyncio.create_task(poll_platform(c.id))
            polling_tasks.append(task)
        print(f"[Poller] {len(polling_tasks)} platform poller(s) started")
    finally:
        db.close()


@app.on_event("shutdown")
async def stop_pollers():
    for task in polling_tasks:
        task.cancel()
    print("[Poller] all pollers stopped")


@app.get("/health")
def health():
    return {"status": "ok"}
