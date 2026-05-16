#!/bin/bash
# deploy.sh - 一键部署到云服务器
# 用法: ./deploy.sh 你的服务器IP

SERVER="${1}"
if [ -z "$SERVER" ]; then
    echo "用法: ./deploy.sh <服务器IP>"
    exit 1
fi

REMOTE_DIR="/opt/customer-service"

echo "=== 1. 构建前端 ==="
cd frontend && npm run build && cd ..

echo "=== 2. 同步后端代码 ==="
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' --exclude 'data/' --exclude '.env' backend/ root@${SERVER}:${REMOTE_DIR}/backend/

echo "=== 3. 同步前端构建产物 ==="
rsync -avz frontend/dist/ root@${SERVER}:${REMOTE_DIR}/frontend/dist/

echo "=== 4. 上传nginx配置并重载 ==="
scp deploy/nginx.conf root@${SERVER}:/etc/nginx/conf.d/customer-service.conf
ssh root@${SERVER} "nginx -t && nginx -s reload"

echo "=== 5. 重启后端 ==="
ssh root@${SERVER} "systemctl restart customer-service"

echo "=== 部署完成 ==="
