# 🚀 Cafe24 배포 가이드

## 📋 사전 준비사항

### 도메인
- **도메인:** `kfire.kbcosmos.com`

### 서버 접속 정보 (사용자가 제공)
다음 정보를 서버에서 확인해주세요:

```bash
# 1. OS 확인
cat /etc/os-release

# 2. Python 버전 확인
python3 --version

# 3. nginx 설치 여부
nginx -v

# 4. 포트 확인
sudo ss -tlnp | grep -E ':(80|443|3000)'

# 5. 방화벽 상태
sudo ufw status || sudo iptables -L -n | head -20
```

---

## 🔧 수동 배포 절차

### 1. 서버 접속

```bash
ssh root@cafe24-server-ip
# 또는
ssh user@cafe24-server-ip
```

### 2. 시스템 업데이트

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 3. 필요 패키지 설치

```bash
sudo apt-get install -y python3-venv python3-pip nginx git curl
```

### 4. 프로젝트 클론

```bash
cd /var/www
sudo mkdir -p kfire.kbcosmos.com
cd kfire.kbcosmos.com

# GitHub에서 클론
sudo git clone https://github.com/choikb/fire-investigation-ai.git .
```

### 5. 가상환경 설정

```bash
cd web-service
sudo python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 6. 환경변수 설정

```bash
cd /var/www/kfire.kbcosmos.com
sudo cp .env.example .env
sudo nano .env
```

`.env` 파일 내용:
```
OPENAI_API_KEY=sk-proj-your_actual_key_here
HOST=0.0.0.0
PORT=3000
DEBUG=false
```

### 7. 서비스 실행 (임시)

```bash
cd /var/www/kfire.kbcosmos.com/web-service
source venv/bin/activate
python main.py
```

브라우저에서 `http://서버IP:3000` 접속 테스트

---

## 🔒 SSL 인증서 발급 (Let's Encrypt)

### 1. Certbot 설치

```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

### 2. nginx 설정 먼저 적용

```bash
sudo cp /var/www/kfire.kbcosmos.com/deploy/nginx/kfire.kbcosmos.com.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/kfire.kbcosmos.com.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 3. SSL 인증서 발급

```bash
sudo certbot --nginx -d kfire.kbcosmos.com
```

- 이메일 입력
- 약관 동의 (Y)
- 뉴스레터 (N)
- 리다이렉트 선택 (2: 모든 HTTP를 HTTPS로)

### 4. 인증서 자동 갱신 확인

```bash
sudo certbot renew --dry-run
```

---

## 🔄 systemd 서비스 등록 (권장)

### 1. 서비스 파일 생성

```bash
sudo cp /var/www/kfire.kbcosmos.com/deploy/systemd/fire-ai.service /etc/systemd/system/
```

### 2. 서비스 활성화 및 시작

```bash
sudo systemctl daemon-reload
sudo systemctl enable fire-ai
sudo systemctl start fire-ai
```

### 3. 상태 확인

```bash
sudo systemctl status fire-ai
sudo journalctl -u fire-ai -f
```

---

## 🐳 Docker 배포 (선택)

### Docker 설치

```bash
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
```

### 실행

```bash
cd /var/www/kfire.kbcosmos.com
docker-compose up -d
```

---

## 🌐 최종 접속

- **HTTP:** http://kfire.kbcosmos.com
- **HTTPS:** https://kfire.kbcosmos.com

---

## 🚨 문제 해결

### 1. 서비스 시작 실패

```bash
# 로그 확인
sudo journalctl -u fire-ai -n 50

# 포트 확인
sudo netstat -tlnp | grep 3000
```

### 2. nginx 오류

```bash
sudo nginx -t
sudo systemctl status nginx
```

### 3. 권한 문제

```bash
sudo chown -R www-data:www-data /var/www/kfire.kbcosmos.com
```

### 4. 방화벽 설정

```bash
# Ubuntu UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

---

## 📁 배포 파일 구조

```
/var/www/kfire.kbcosmos.com/
├── web-service/
│   ├── main.py
│   ├── static/
│   ├── templates/
│   └── venv/
├── .env
├── requirements.txt
└── deploy/
    ├── systemd/
    └── nginx/
```
