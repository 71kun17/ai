import os
from fastapi import APIRouter
from pydantic import BaseModel
from app.config import BASE_DIR

router = APIRouter(prefix="/api/config", tags=["配置"])

ENV_PATH = os.path.join(BASE_DIR, '.env')

class LLMConfig(BaseModel):
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_model: str = "deepseek-chat"

def _read_env():
    config = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    config[k.strip().lower()] = v.strip()
    return config

def _write_env(config):
    lines = []
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    updated = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if '=' in stripped and not stripped.startswith('#'):
            k = stripped.split('=', 1)[0].strip().lower()
            if k in config:
                new_lines.append(k.upper() + "=" + config[k] + "\n")
                updated.add(k)
                continue
        new_lines.append(line)
    for k, v in config.items():
        if k not in updated:
            new_lines.append(k.upper() + "=" + v + "\n")
    with open(ENV_PATH, 'w', encoding='utf-8', newline='') as f:
        f.writelines(new_lines)

@router.get("/llm")
def get_llm_config():
    cfg = _read_env()
    return {
        "llm_api_key": cfg.get("llm_api_key", ""),
        "llm_base_url": cfg.get("llm_base_url", "https://api.deepseek.com/v1"),
        "llm_model": cfg.get("llm_model", "deepseek-chat"),
    }

@router.put("/llm")
def update_llm_config(data: LLMConfig):
    _write_env({
        "llm_api_key": data.llm_api_key,
        "llm_base_url": data.llm_base_url,
        "llm_model": data.llm_model,
    })
    from app.config import settings
    settings.LLM_API_KEY = data.llm_api_key
    settings.LLM_BASE_URL = data.llm_base_url
    settings.LLM_MODEL = data.llm_model
    return {"ok": True, "message": "配置已更新，下次对话生效"}
