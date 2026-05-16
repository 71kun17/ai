#!/bin/bash
set -e
cd /opt/customer-service

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
