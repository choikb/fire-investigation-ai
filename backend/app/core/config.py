"""
소방 AI 화재조사 시스템 설정
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    PROJECT_NAME: str = "Fire Investigation AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI 기반 화재조사 지원 시스템"
    
    # 서버 설정
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # 보안 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24시간
    
    # 데이터베이스 설정 - SQLite로 변경 (데모용)
    DATABASE_URL: str = "sqlite:///./fire_investigation.db"
    
    # Redis 설정 (데모용으로 비활성화)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # MinIO/S3 설정 (데모용으로 로컬 스토리지 사용)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "fire-evidence"
    MINIO_SECURE: bool = False
    
    # AI 모델 설정
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "models/yolov5s-fire.pt")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    
    # OpenAI 설정
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")
    
    # 파일 업로드 설정
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "mp4", "mov"}
    
    # 오프라인 설정
    OFFLINE_MODE_ENABLED: bool = True
    SYNC_INTERVAL_SECONDS: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
