# 🚀 배포 가이드

## Cafe24 서버 배포 절차

### 1. Git 저장소 연결

```bash
# 로컬에서 원격 저장소 추가
git remote add origin https://github.com/your-org/fire-investigation-ai.git
git push -u origin main
```

### 2. Cafe24 서버 접속

```bash
# SSH로 서버 접속
ssh cafe24-user@your-server.cafe24.com

# 프로젝트 디렉토리 생성
mkdir -p ~/fire-ai
cd ~/fire-ai

# Git 클론
git clone https://github.com/your-org/fire-investigation-ai.git .
```

### 3. Python 환경 설정

```bash
cd web-service

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 4. 서비스 실행 (기본)

```bash
# 포트 3000으로 실행
python main.py 3000
```

### 5. systemd 서비스 등록 (권장)

```bash
sudo nano /etc/systemd/system/fire-ai.service
```

```ini
[Unit]
Description=Fire Investigation AI Service
After=network.target

[Service]
Type=simple
User=cafe24-user
WorkingDirectory=/home/cafe24-user/fire-ai/web-service
Environment=PATH=/home/cafe24-user/fire-ai/web-service/venv/bin
ExecStart=/home/cafe24-user/fire-ai/web-service/venv/bin/python main.py 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable fire-ai
sudo systemctl start fire-ai

# 상태 확인
sudo systemctl status fire-ai
sudo journalctl -u fire-ai -f
```

### 6. nginx 리버스 프록시 (선택)

```bash
sudo nano /etc/nginx/conf.d/fire-ai.conf
```

```nginx
server {
    listen 80;
    server_name fire-ai.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 환경 변수 설정

`.env` 파일 생성:

```bash
cd web-service
nano .env
```

```env
# 서버 설정
HOST=0.0.0.0
PORT=8080
DEBUG=false

# OpenAI API (실제 배포 시)
OPENAI_API_KEY=your-api-key-here

# 데이터베이스 (향후 연동)
# DATABASE_URL=postgresql://user:pass@localhost/fireai
```

---

## 업데이트 절차

```bash
cd ~/fire-ai
git pull origin main

# 가상환경 활성화
source web-service/venv/bin/activate

# 의존성 업데이트 (필요 시)
pip install -r web-service/requirements.txt --upgrade

# 서비스 재시작
sudo systemctl restart fire-ai
```

---

## 트러블슈팅

### 1. 포트 충돌

```bash
# 포트 사용 현황 확인
netstat -tlnp | grep 8080

# 프로세스 종료
kill -9 <PID>
```

### 2. 권한 문제

```bash
# 소유권 변경
sudo chown -R cafe24-user:cafe24-user ~/fire-ai

# 실행 권한 확인
chmod +x web-service/main.py
```

### 3. 로그 확인

```bash
# 실시간 로그
sudo journalctl -u fire-ai -f

# 최근 100줄
sudo journalctl -u fire-ai -n 100
```

---

## 백업 및 복구

### 백업

```bash
# 소스 코드 백업
cd ~
tar -czvf fire-ai-backup-$(date +%Y%m%d).tar.gz fire-ai/

# 데이터베이스 백업 (연동 시)
# pg_dump fireai > backup.sql
```

### 복구

```bash
# 압축 해제
tar -xzvf fire-ai-backup-20240406.tar.gz

# 서비스 재시작
sudo systemctl restart fire-ai
```
