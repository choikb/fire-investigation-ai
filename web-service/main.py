"""
소방 AI 화재조사 시스템 - 웹 서비스
FastAPI + 정적 파일 서빙
"""
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from typing import Optional
from datetime import datetime
import base64
from io import BytesIO

app = FastAPI(
    title="소방 AI 화재조사 시스템",
    description="Circle-to-Search 증거 식별 + ChatGPT 원인 분석",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "service": "Fire Investigation AI",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    center_x: Optional[float] = Form(None),
    center_y: Optional[float] = Form(None),
    radius: Optional[float] = Form(None)
):
    """
    이미지 분석 API
    - 이미지 업로드
    - Circle-to-Search 영역 정보
    - 증거물 식별 결과 반환
    """
    try:
        # 파일 읽기
        contents = await file.read()
        
        # TODO: 실제 YOLO 모델 연동
        # 현재는 Mock 데이터 반환
        
        result = {
            "status": "success",
            "filename": file.filename,
            "selected_area": {
                "center_x": center_x,
                "center_y": center_y,
                "radius": radius
            } if center_x else None,
            "objects": [
                {
                    "type": "전열기",
                    "shape": "원통형 가열 장치",
                    "material": "금속 + 세라믹",
                    "purpose": "액체 가열용",
                    "confidence": 0.92
                },
                {
                    "type": "전원 케이블",
                    "shape": "코일 형태",
                    "material": "구리 + PVC 절연체",
                    "purpose": "전력 공급",
                    "confidence": 0.88
                },
                {
                    "type": "연소 흔적",
                    "shape": "불규칙한 탄화 패턴",
                    "material": "탄화 물질",
                    "purpose": "화재 확산 증거",
                    "confidence": 0.95
                }
            ]
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/api/ai-analysis")
async def ai_analysis(request: dict):
    """
    AI 화재 원인 분석 API
    - ChatGPT API 연동 (Mock)
    """
    try:
        evidence = request.get("evidence", {})
        selected_area = request.get("selected_area")
        
        # TODO: 실제 ChatGPT API 연동
        # 현재는 Mock 분석 결과 반환
        
        analysis_html = """
        <h4>🔍 분석 개요</h4>
        <p>제공된 현장 사진과 증거물 식별 결과를 바탕으로 <strong>전기적 요인</strong>에 의한 화재로 추정됩니다.</p>
        
        <h4>📊 감지된 주요 증거</h4>
        <ul>
            <li>전열기 (신뢰도: 92%) - 과열 흔적 관찰</li>
            <li>전원 케이블 (신뢰도: 88%) - 절연체 손상</li>
            <li>연소 흔적 (신뢰도: 95%) - V자형 연소 패턴</li>
        </ul>
        
        <h4>🔥 발화지점 추정</h4>
        <p>전열기 본체와 전원 케이블 연결 부위 근처로 추정됩니다.</p>
        
        <h4>⚠️ 화재 원인 분석</h4>
        <p>AI 분석 결과, 다음과 같은 원인이 가능성이 높습니다:</p>
        <ul>
            <li><strong>전열기 과부하</strong>: 정격 용량 이상의 과부하 사용</li>
            <li><strong>전원 케이블 단선</strong>: 반복적 구부림으로 인한 단선</li>
            <li><strong>열전달</strong>: 주변 가연물과의 접촉으로 인한 점화</li>
        </ul>
        
        <h4>📝 권장 사항</h4>
        <ul>
            <li>전열기 정격 전압 및 용량 확인</li>
            <li>케이블 및 플러그 교체 권장</li>
            <li>주변 가연물 정리 및 안전거리 확보</li>
        </ul>
        
        <p style="color: #666; font-size: 12px; margin-top: 20px;">
            * 본 분석은 ChatGPT AI 기반 추론 결과이며, 최종 판단은 담당 조사관이 수행해야 합니다.
        </p>
        """
        
        return JSONResponse(content={
            "status": "success",
            "analysis": analysis_html
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/api/report")
async def generate_report(request: dict):
    """
    조사보고서 생성 API
    """
    try:
        evidence = request.get("evidence", {})
        analysis = request.get("analysis", "")
        
        # TODO: 실제 보고서 생성 로직
        # 현재는 Mock 보고서 반환
        
        report = """화재조사 보고서

■ 사건 개요
- 사걸번호: FIRE-2024-001A
- 발생일시: 2024년 4월 6일
- 발생장소: 아파트 주방
- 조사관: 화재조사관

■ 현장 상황
싱크대 인근에서 화재가 발생하였으며, 주변 전열기 및 전원 케이블에서 
심각한 전기적 손상이 관찰되었습니다.

■ 증거 수집
1. 현장 사진 (3장) - 연소 흔적 및 증거물 촬영
2. 증거물 식별 결과:
   - 전열기 (형상: 원통형, 재질: 금속+세라믹)
   - 전원 케이블 (재질: 구리+PVC, 손상 상태)
   - 연소 흔적 (V자형 패턴)

■ AI 분석 결과
Circle-to-Search 기반 증거 분석 및 ChatGPT AI 원인 추론 결과,
전기적 요인에 의한 화재로 추정됩니다.

주요 원인:
1. 전열기 과부하 또는 과열
2. 전원 케이블 단선
3. 주변 가연물과의 접촉

■ 결론
본 화재는 전기적 요인으로 인한 발화로 추정되며, 
전열기 및 전원 케이블의 정상적인 사용 관리가 필요합니다.

■ 조치 사항
1. 전열기 정격 확인 및 교체
2. 전원 케이블 교체
3. 주변 가연물 정리

작성일: 2024년 4월 6일
AI 분석 시스템 v1.0 / 담당 조사관"""
        
        return JSONResponse(content={
            "status": "success",
            "report": report
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    uvicorn.run(app, host="0.0.0.0", port=port)
