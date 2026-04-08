"""
API v1 라우터 설정
"""
from fastapi import APIRouter

from app.api.v1.endpoints import investigations, auth, search, dashboard

api_router = APIRouter()

# 인증
api_router.include_router(auth.router, prefix="/auth", tags=["인증"])

# 화재 조사
api_router.include_router(
    investigations.router, 
    prefix="/investigations", 
    tags=["화재 조사"]
)

# 검색/분석
api_router.include_router(
    search.router, 
    prefix="/search", 
    tags=["검색 및 분석"]
)

# 대시보드
api_router.include_router(
    dashboard.router, 
    prefix="/dashboard", 
    tags=["대시보드"]
)
