#!/bin/bash
# ============================================
# 服务器初始化脚本 - 只在服务器上跑一次
# 用法: bash setup-server.sh <Gitee仓库地址> [webhook密钥] [DeepSeek_API_Key]
# 示例: bash setup-server.sh https://gitee.com/zhangsan/customer-service.git my-secret sk-xxxx
# ============================================
set -e

REPO_URL="${1}"   # Gitee 仓库地址
WEBHOOK_SECRET="${2:-my-secret-key-2024}"
DEEPSEEK_KEY="${3}"

if [ -z "$REPO_URL" ]; then
    echo "用法: bash setup-server.sh <Gitee仓库地址> [webhook密钥] [DeepSeek_API_Key]"
    echo "示例: bash setup-server.sh https://gitee.com/zhangsan/customer-service.git my-secret sk-xxxx"
    exit 1
fi

echo "========================================"
echo "  AI智能客服 - 服务器初始化"
echo "========================================"

# --- 1. 系统更新 ---
echo "[1/9] 更新系统..."
apt update && apt upgrade -y

# --- 2. 安装依赖 ---
echo "[2/9] 安装 Python3 / Node.js / Nginx / Git..."
apt install -y python3 python3-pip python3-venv nginx git

# Node.js 20.x
if ! command -v node &>/dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

echo "  Node: $(node --version)"
echo "  Python: $(python3 --version)"

# --- 3. 克隆代码 ---
echo "[3/9] 克隆仓库..."
mkdir -p /opt/customer-service
cd /opt
rm -rf customer-service

git clone "$REPO_URL" customer-service
cd customer-service

# --- 4. 创建 .env ---
echo "[4/9] 创建环境配置..."
cat > backend/.env << 'ENVEOF'
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
ENVEOF

# 如果提供了 DeepSeek Key，同步写入后端 .env
if [ -n "$DEEPSEEK_KEY" ]; then
    sed -i "s/LLM_API_KEY=/LLM_API_KEY=$DEEPSEEK_KEY/" backend/.env
    echo "  → 后端 .env 已写入 DeepSeek Key"
else
    echo "  → 请之后手动编辑 backend/.env 填入实际API Key"
fi

# --- 5. 安装 Python 依赖 ---
echo "[5/9] 安装 Python 依赖..."
cd /opt/customer-service/backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# --- 6. 构建前端 ---
echo "[6/9] 构建前端..."
cd /opt/customer-service/frontend
npm install
npm run build

# --- 7. 注册服务 ---
echo "[7/9] 注册 systemd 服务..."

# 后端守护
cp /opt/customer-service/deploy/customer-service.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable customer-service
systemctl start customer-service

# Webhook 守护
cat > /etc/systemd/system/webhook-server.service << 'UNITEOF'
[Unit]
Description=Git Webhook Receiver
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/customer-service
ExecStart=/opt/customer-service/backend/venv/bin/python deploy/webhook-server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNITEOF

# 注入 webhook 密钥
sed -i "s/CHANGE_THIS_TO_RANDOM_STRING/$WEBHOOK_SECRET/" /opt/customer-service/deploy/webhook-server.py

systemctl daemon-reload
systemctl enable webhook-server
systemctl start webhook-server

# --- 8. 配置 Nginx ---
echo "[8/9] 配置 Nginx..."
cp /opt/customer-service/deploy/nginx.conf /etc/nginx/conf.d/customer-service.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# --- 防火墙 ---
echo "配置防火墙..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 9000/tcp
ufw --force enable

# --- 9. 安装 Codex CLI ---
echo "[9/9] 安装 Codex CLI + DeepSeek..."
bash /opt/customer-service/deploy/setup-codex.sh "$DEEPSEEK_KEY" 2>&1 | tee -a /var/log/codex-setup.log || echo "  Codex 安装失败，可稍后手动运行 bash deploy/setup-codex.sh <Key>"

echo ""
echo "========================================"
echo "  初始化完成!"
echo "========================================"
echo ""
echo "访问地址: http://$(curl -s ifconfig.me)"
echo ""
echo "后续操作："
echo "1. 重启后端: systemctl restart customer-service"
echo "2. 在云服务器安全组中放通 80, 9000 端口"
echo "3. SSH 登录后运行 codex 开始编程"
echo ""
echo "Webhook 地址（填到 Gitee）:"
echo "  http://$(curl -s ifconfig.me):9000/deploy"
echo "  密钥: $WEBHOOK_SECRET"
echo ""