# 🚀 KFireAI 서버 설정 명령어

> **도메인:** kfireai.kbcosmos.com  
> **포트:** 8003 (기존 8002와 충돌 방지)  
> **디렉토리:** /opt/kfireai

---

## 1️⃣ 서버 접속 및 기본 설정

```bash
# 서버 접속
ssh root@kbcosmos.com

# 시스템 업데이트
apt-get update
apt-get install -y python3-venv python3-pip nginx git curl
```

---

## 2️⃣ 디렉토리 생성

```bash
# 애플리케이션 디렉토리
mkdir -p /opt/kfireai
mkdir -p /opt/kfireai/models
mkdir -p /opt/kfireai/static
mkdir -p /opt/kfireai/templates
mkdir -p /var/log/kfireai

# 권한 설정
chown -R root:root /opt/kfireai
chmod -R 755 /opt/kfireai
```

---

## 3️⃣ 포트 확인

```bash
# 8003 포트 사용 가능 여부 확인
ss -tln | grep ':8003 ' || echo '✅ 8003 포트 사용 가능'

# 현재 사용 중인 포트 확인
ss -tln | grep -E ':(8002|8003|80|443)'
```

---

## 4️⃣ Nginx 설정

```bash
# 설정 파일 생성
cat > /etc/nginx/sites-available/kfireai << 'EOF'
upstream kfireai_backend {
    server 127.0.0.1:8003;
    keepalive 32;
}

# HTTP → HTTPS 리다이렉트
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

# HTTPS 서버
server {
    listen 443 ssl http2;
    server_name kfireai.kbcosmos.com;
    
    # SSL 인증서 (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/kfireai.kbcosmos.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kfireai.kbcosmos.com/privkey.pem;
    
    # SSL 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # 보안 헤더
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # 로깅
    access_log /var/log/nginx/kfireai-access.log;
    error_log /var/log/nginx/kfireai-error.log;
    
    # 정적 파일
    location /static/ {
        alias /opt/kfireai/static/;
        expires 1y;
        access_log off;
    }
    
    # FastAPI/Uvicorn 프록시
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
EOF

# 심볼릭 링크 생성
ln -sf /etc/nginx/sites-available/kfireai /etc/nginx/sites-enabled/

# Nginx 설정 테스트
nginx -t
```

---

## 5️⃣ Systemd 서비스 설정

```bash
# 서비스 파일 생성
cat > /etc/systemd/system/kfireai.service << 'EOF'
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

ExecStart=/opt/kfireai/venv/bin/uvicorn main:app \
    --host 127.0.0.1 \
    --port 8003 \
    --workers 2 \
    --access-logfile /var/log/kfireai/access.log \
    --error-logfile /var/log/kfireai/error.log

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# systemd 재로드
systemctl daemon-reload
systemctl enable kfireai
```

---

## 6️⃣ SSL 인증서 발급

```bash
# Certbot으로 SSL 발급
certbot --nginx -d kfireai.kbcosmos.com

# 자동 발급 (비대화형)
# certbot --nginx -d kfireai.kbcosmos.com --non-interactive --agree-tos --email your-email@example.com
```

---

## 7️⃣ 방화벽 설정 (필요시)

```bash
# UFW 사용 시
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8003/tcp

# iptables 사용 시
iptables -I INPUT -p tcp --dport 80 -j ACCEPT
iptables -I INPUT -p tcp --dport 443 -j ACCEPT
iptables -I INPUT -p tcp --dport 8003 -j ACCEPT
```

---

## 8️⃣ 서비스 시작

```bash
# KFireAI 서비스 시작
systemctl start kfireai

# Nginx 재시작
systemctl reload nginx

# 상태 확인
systemctl status kfireai
systemctl status nginx

# 로그 확인
tail -f /var/log/kfireai/error.log
tail -f /var/log/nginx/kfireai-error.log
```

---

## 🔍 상태 확인 명령어

```bash
# 서비스 상태
curl http://127.0.0.1:8003/api/health

# 외부 접속 테스트
curl https://kfireai.kbcosmos.com/api/health

# 프로세스 확인
ps aux | grep kfireai

# 포트 사용 확인
ss -tln | grep 8003
```

---

## 🚨 문제 해결

### 서비스 시작 실패
```bash
# 로그 확인
journalctl -u kfireai -n 50

# 권한 확인
ls -la /opt/kfireai/
```

### Nginx 오류
```bash
# 설정 테스트
nginx -t

# 에러 로그
tail -f /var/log/nginx/kfireai-error.log
```

### SSL 오류
```bash
# 인증서 확인
ls -la /etc/letsencrypt/live/kfireai.kbcosmos.com/

# 재발급
certbot renew --force-renewal -d kfireai.kbcosmos.com
```
