#!/bin/bash
# ============================================
# 云服务器安装 Codex CLI + DeepSeek API 配置
# 用法: 
#   ssh root@<服务器IP> "bash -s" < deploy/setup-codex.sh
#   或: bash deploy/setup-codex.sh <你的DeepSeek_API_Key>
# ============================================
set -e

DEEPSEEK_API_KEY="${1}"
DEEPSEEK_MODEL="${2:-deepseek-chat}"

echo "========================================"
echo "  安装 Codex CLI + DeepSeek 配置"
echo "========================================"

# --- 1. 检查 Node.js ---
echo "[1/5] 检查 Node.js..."
if ! command -v node &>/dev/null; then
    echo "  Node.js 未安装，正在安装 Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi
echo "  Node: $(node --version)"
echo "  npm:  $(npm --version)"

# --- 2. 安装 Codex CLI ---
echo "[2/5] 安装 Codex CLI (全局)..."
npm install -g @openai/codex

echo "  Codex CLI 版本:"
codex --version 2>/dev/null || echo "  (安装完成)"

# --- 3. 创建配置目录 ---
echo "[3/5] 创建配置目录..."
mkdir -p ~/.codex

# --- 4. 写入 Codex 配置 (DeepSeek) ---
echo "[4/5] 配置 Codex 使用 DeepSeek API..."

cat > ~/.codex/config.toml << 'TOMLEOF'
model_provider = "deepseek"
model = "deepseek-chat"
model_reasoning_effort = "xhigh"

[model_providers.deepseek]
name = "DeepSeek"
wire_api = "responses"
requires_openai_auth = true
base_url = "https://api.deepseek.com/v1"

[windows]
sandbox = "elevated"
TOMLEOF

# 替换模型名（如果指定了不同模型）
if [ -n "$DEEPSEEK_MODEL" ] && [ "$DEEPSEEK_MODEL" != "deepseek-chat" ]; then
    sed -i "s/model = \"deepseek-chat\"/model = \"$DEEPSEEK_MODEL\"/" ~/.codex/config.toml
fi

echo "  config.toml 已创建 → base_url: https://api.deepseek.com/v1"

# --- 5. 写入 API Key ---
if [ -n "$DEEPSEEK_API_KEY" ]; then
    echo "[5/5] 写入 API Key..."
    cat > ~/.codex/auth.json << AUTHEOF
{
  "OPENAI_API_KEY": "$DEEPSEEK_API_KEY"
}
AUTHEOF
    chmod 600 ~/.codex/auth.json
    echo "  auth.json 已创建"
else
    echo "[5/5] 跳过 API Key (未提供)"
    echo "  → 请稍后手动创建 ~/.codex/auth.json 或运行 codex 配置"
fi

echo ""
echo "========================================"
echo "  Codex CLI + DeepSeek 配置完成!"
echo "========================================"
echo ""
echo "已配置:"
echo "  模型: $DEEPSEEK_MODEL"
echo "  API:  https://api.deepseek.com/v1"
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "  Key:  ⚠ 未设置，请手动创建 ~/.codex/auth.json"
    echo ""
    echo "  手动配置 API Key:"
    echo '    echo '"'"'{"OPENAI_API_KEY": "你的Key"}'"'"' > ~/.codex/auth.json'
    echo '    chmod 600 ~/.codex/auth.json'
fi
echo ""
echo "使用方法："
echo "  SSH 登录后运行:  codex"
echo ""