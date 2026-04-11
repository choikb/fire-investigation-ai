#!/bin/bash
# 소방 AI 화재조사 시스템 배포 스크립트
# Usage: ./deploy.sh

set -e

# 설정
DOMAIN="kfire.kbcosmos.com"
DEPLOY_DIR="/var/www/$DOMAIN"
SERVICE_NAME="fire-ai"
NGINX_CONF="/etc/nginx/sites-available/$DOMAIN.conf"

echo "========================================"
echo "🔥 Fire Investigation AI 배포 시작"
echo "========================================"

# 1. 시스템 패키지 업데이트
echo "📦 시스템 패키지 업데이트..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip nginx certbot python3-certbot-nginx

# 2. 디렉토리 생성
echo "📁 디렉토리 생성..."
sudo mkdir -p $DEPLOY_DIR
sudo mkdir -p /var/log/nginx
sudo mkdir -p /var/www/certbot

# 3. 파일 복사
echo "📂 파일 복사..."
sudo cp -r ../web-service/* $DEPLOY_DIR/
sudo chown -R www-data:www-data $DEPLOY_DIR

# 4. 가상환경 설정
echo "🐍 가상환경 설정..."
cd $DEPLOY_DIR
sudo python3 -m venv venv
sudo venv/bin/pip install --upgrade pip
sudo venv/bin/pip install -r requirements.txt

# 5. 환경변수 설정 확인
echo "⚙️ 환경변수 설정 확인..."
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    echo "⚠️ .env 파일이 없습니다. .env.example을 복사해서 설정하세요."
    sudo cp $DEPLOY_DIR/.env.example $DEPLOY_DIR/.env
    sudo nano $DEPLOY_DIR/.env
fi

# 6. systemd 서비스 등록
echo "🔧 systemd 서비스 등록..."
sudo cp systemd/fire-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fire-ai

# 7. nginx 설정
echo "🌐 nginx 설정..."
sudo cp nginx/$DOMAIN.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/$DOMAIN.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 8. 서비스 시작
echo "🚀 서비스 시작..."
sudo systemctl restart fire-ai

# 9. SSL 인증서 발급
echo "🔒 SSL 인증서 발급..."
echo "certbot을 실행하여 SSL 인증서를 발급받으세요:"
echo "  sudo certbot --nginx -d $DOMAIN"

echo ""
echo "========================================"
echo "✅ 배포 완료!"
echo "========================================"
echo ""
echo "🔍 상태 확인:"
echo "  서비스 상태: sudo systemctl status fire-ai"
echo "  로그 확인: sudo journalctl -u fire-ai -f"
echo "  nginx 상태: sudo systemctl status nginx"
echo ""
echo "🌐 접속 주소:"
echo "  https://$DOMAIN"
echo ""
echo "⚠️ SSL 인증서 발급 필요:"
echo "  sudo certbot --nginx -d $DOMAIN"
echo ""
