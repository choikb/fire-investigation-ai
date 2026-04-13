#!/bin/bash
# KFireAI 서버 설정 스크립트
# 서버에서 실행: bash setup_server.sh

set -e

echo "========================================"
echo "🔥 KFireAI 서버 설정 시작"
echo "========================================"

# 1. 디렉토리 확인
echo "📁 디렉토리 확인..."
cd /opt/kfireai
pwd
ls -la

# 2. deploy 디렉토리 생성
echo "📁 deploy 디렉토리 생성..."
mkdir -p deploy/nginx deploy/systemd

# 3. Nginx 설정 파일 생성
echo "🌐 Nginx 설정 생성..."
cat > deploy/nginx/kfireai.conf << 'NGINX_EOF'
upstream kfireai_backend {
    server 127.0.0.1:8003;
    keepalive 32;
}

server {
    listen 80;
    server_name kfireai.kbcosmos.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name kfireai.kbcosmos.com;
    
    ssl_certificate /etc/letsencrypt/live/kfireai.kbcosmos.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kfireai.kbcosmos.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    access_log /var/log/nginx/kfireai-access.log;
    error_log /var/log/nginx/kfireai-error.log;
    
    location /static/ {
        alias /opt/kfireai/static/;
        expires 1y;
        access_log off;
    }
    
    location / {
        proxy_pass http://kfireai_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINX_EOF

# 4. Systemd 서비스 파일 생성
echo "⚙️ Systemd 설정 생성..."
cat > deploy/systemd/kfireai.service << 'SYSTEMD_EOF'
[Unit]
Description=KFireAI - Fire Investigation AI Service
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/kfireai
Environment="PATH=/opt/kfireai/venv/bin"
Environment="PYTHONPATH=/opt/kfireai"
Environment="PORT=8003"

ExecStart=/opt/kfireai/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8003 --workers 2
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

# 5. Nginx 설정 복사
echo "🌐 Nginx 설정 적용..."
cp deploy/nginx/kfireai.conf /etc/nginx/sites-available/kfireai
rm -f /etc/nginx/sites-enabled/kfireai
ln -s /etc/nginx/sites-available/kfireai /etc/nginx/sites-enabled/

# 6. Systemd 설정 복사
echo "⚙️ Systemd 설정 적용..."
cp deploy/systemd/kfireai.service /etc/systemd/system/
systemctl daemon-reload

# 7. Nginx 설정 테스트
echo "🧪 Nginx 설정 테스트..."
nginx -t

echo ""
echo "========================================"
echo "✅ 기본 설정 완료!"
echo "========================================"
echo ""
echo "다음 단계 실행:"
echo "1. SSL 발급: certbot --nginx -d kfireai.kbcosmos.com"
echo "2. 서비스 시작: systemctl start kfireai"
echo "3. Nginx 재시작: systemctl reload nginx"
echo ""
