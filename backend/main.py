"""
소방 AI 화재조사 시스템 - FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작
    logger.info("🚀 소방 AI 화재조사 시스템 시작 중...")
    logger.info(f"   환경: {'개발' if settings.DEBUG else '운영'}")
    logger.info(f"   API 버전: {settings.VERSION}")
    
    # 데이터베이스 초기화
    try:
        init_db()
        logger.info("✅ 데이터베이스 초기화 완료")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}")
    
    yield
    
    # 종료
    logger.info("🛑 소방 AI 화재조사 시스템 종료 중...")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# 미들웨어 설정
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://fire-investigation.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 신뢰할 수 있는 호스트
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["fire-investigation.app", "*.fire-investigation.app"]
)


# 요청 처리 시간 로깅 미들웨어
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 느린 요청 로깅 (1초 이상)
    if process_time > 1.0:
        logger.warning(f"느린 요청: {request.method} {request.url.path} - {process_time:.3f}s")
    
    return response


# 글로벌 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "남부 서버 오류가 발생했습니다. 관리자에게 문의하세요.",
            "error_code": "INTERNAL_ERROR"
        }
    )


# 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)


# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    """시스템 헬스체크"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": time.time()
    }


# 루트 엔드포인트
@app.get("/")
async def root():
    """API 루트"""
    return {
        "message": "소방 AI 화재조사 시스템 API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
