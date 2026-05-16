#!/bin/bash
# ============================================
# 云服务器安装 Codex CLI + DeepSeek 代理
# 用法: bash deploy/setup-codex.sh <DeepSeek_API_Key>
# ============================================
set -e

DEEPSEEK_API_KEY="${1}"
DEEPSEEK_MODEL="${2:-deepseek-chat}"

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "用法: bash setup-codex.sh <DeepSeek_API_Key> [模型名]"
    echo "示例: bash setup-codex.sh sk-xxxx deepseek-chat"
    exit 1
fi

echo "========================================"
echo "  安装 Codex CLI + DeepSeek 代理"
echo "========================================"

# --- 1. 检查 Node.js ---
echo "[1/6] 检查 Node.js..."
if ! command -v node &>/dev/null; then
    echo "  Node.js 未安装，正在安装 Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi
echo "  Node: $(node --version)"

# --- 2. 安装 Codex CLI ---
echo "[2/6] 安装 Codex CLI..."
npm install -g @openai/codex 2>/dev/null || sudo npm install -g @openai/codex
echo "  Codex: $(codex --version 2>/dev/null || echo 'done')"

# --- 3. 注册 DeepSeek 代理服务 ---
echo "[3/6] 注册 DeepSeek 代理服务..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo tee /etc/systemd/system/deepseek-proxy.service > /dev/null << UNITEOF
[Unit]
Description=DeepSeek API Proxy for Codex
After=network.target

[Service]
Type=simple
ExecStart=/opt/customer-service/backend/venv/bin/python /opt/customer-service/deploy/deepseek-proxy.py 3000
Restart=always
RestartSec=3
Environment="DEEPSEEK_KEY=${DEEPSEEK_API_KEY}"

[Install]
WantedBy=multi-user.target
UNITEOF

sudo systemctl daemon-reload
sudo systemctl enable deepseek-proxy
sudo systemctl start deepseek-proxy
echo "  代理已启动"

# --- 4. 写入 Codex 配置 ---
echo "[4/6] 配置 Codex..."
mkdir -p ~/.codex

cat > ~/.codex/config.toml << TOMLEOF
model_provider = "deepseek"
model = "${DEEPSEEK_MODEL}"
model_reasoning_effort = "xhigh"

[model_providers.deepseek]
name = "DeepSeek"
wire_api = "responses"
requires_openai_auth = true
base_url = "http://127.0.0.1:3000/v1"
TOMLEOF

# --- 5. 写入 API Key ---
echo "[5/6] 写入 API Key..."
cat > ~/.codex/auth.json << AUTHEOF
{
  "OPENAI_API_KEY": "${DEEPSEEK_API_KEY}"
}
AUTHEOF
chmod 600 ~/.codex/auth.json

# --- 6. 完成 ---
echo "[6/6] 完成!"
echo ""
echo "========================================"
echo "  Codex CLI + DeepSeek 就绪"
echo "========================================"
echo ""
echo "架构: codex → localhost:3000 (代理) → api.deepseek.com"
echo "模型: ${DEEPSEEK_MODEL}"
echo ""
echo "运行: codex"
echo ""