#!/bin/bash
set -e
cd /opt/customer-service

echo "0. fix data directory permissions"
mkdir -p backend/data
chown -R www-data:www-data backend/data 2>/dev/null || true
chmod -R 755 backend/data 2>/dev/null || true
chmod 644 backend/data/customer_service.db 2>/dev/null || true

echo "[$(date)] Deploy started" >> /var/log/customer-service-deploy.log

echo "1. git pull"
git pull origin main 2>&1 | tee -a /var/log/customer-service-deploy.log

echo "2. build frontend"
cd frontend
npm install --silent 2>&1 | tee -a /var/log/customer-service-deploy.log
npm run build 2>&1 | tee -a /var/log/customer-service-deploy.log
cd ..

echo "3. restart backend"
systemctl restart customer-service

echo "[$(date)] Deploy done" >> /var/log/customer-service-deploy.log