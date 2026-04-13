"""
소방 AI 화재조사 시스템 - 웹 서비스
FastAPI + OpenAI GPT-4 + YOLOv8 연동
"""
import os
import json
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

# YOLO 모델 임포트
try:
    from yolo_model import get_model, FireDetectionModel
    YOLO_AVAILABLE = True
    print("✅ YOLO 모듈 로드 성공")
except ImportError as e:
    YOLO_AVAILABLE = False
    print(f"⚠️ YOLO 모듈 로드 실패: {e}")

# 환경변수 로드
load_dotenv()

app = FastAPI(
    title="소방 AI 화재조사 시스템",
    description="Circle-to-Search 증거 식별 + ChatGPT 원인 분석",
    version="1.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI 클라이언트 초기화
openai_client = None
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    try:
        openai_client = OpenAI(api_key=api_key)
        print("✅ OpenAI 클라이언트 초기화 완료")
    except Exception as e:
        print(f"⚠️ OpenAI 초기화 오류: {e}")
else:
    print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않음")

# YOLO 모델 초기화
yolo_model = None
try:
    if YOLO_AVAILABLE:
        yolo_model = get_model()
        print("✅ YOLO 모델 초기화 완료")
    else:
        print("⚠️ YOLO 모듈 없음 - Mock 모드로 실행")
except Exception as e:
    print(f"⚠️ YOLO 모델 초기화 오류: {e}")

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
        "version": "1.1.0",
        "openai_connected": openai_client is not None,
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
    이미지 분석 API - YOLOv8 + Mock 하이브리드
    Fire/Smoke는 YOLO, 기타 장비는 Mock 데이터
    """
    try:
        contents = await file.read()
        
        # YOLO 모델로 객체 감지
        detected_objects = []
        hazard_analysis = {}
        
        if yolo_model:
            # YOLO 추론
            detections = yolo_model.detect(contents, conf_threshold=0.4)
            
            # 감지 결과 변환
            for det in detections:
                obj = {
                    "id": det["id"],
                    "type": det["class_ko"],
                    "type_en": det["class"],
                    "category": det["type"],
                    "shape": "감지된 객체",
                    "material": det["material"],
                    "purpose": det["purpose"],
                    "risk": det["risk"],
                    "confidence": det["confidence"],
                    "bbox": det["bbox"]
                }
                detected_objects.append(obj)
            
            # 화재 위험 분석
            hazard_analysis = yolo_model.analyze_fire_hazard(detections)
        
        # 감지된 객체에 source 표시
        for obj in detected_objects:
            obj["source"] = "yolo"
        
        # YOLO로 감지되지 않았으면 Mock 데이터 추가 (데모용)
        if len(detected_objects) == 0:
            detected_objects = [
                {
                    "id": 0,
                    "type": "전열기",
                    "type_en": "heater",
                    "category": "electrical",
                    "shape": "원통형 가열 장치",
                    "material": "금속 + 세라믹",
                    "purpose": "액체 가열용",
                    "risk": "과열",
                    "confidence": 0.92,
                    "source": "mock"
                },
                {
                    "id": 1,
                    "type": "전원 케이블",
                    "type_en": "cable",
                    "category": "electrical",
                    "shape": "코일 형태",
                    "material": "구리 + PVC 절연체",
                    "purpose": "전력 공급",
                    "risk": "단선",
                    "confidence": 0.88,
                    "source": "mock"
                },
                {
                    "id": 2,
                    "type": "연소 흔적",
                    "type_en": "burn_mark",
                    "category": "evidence",
                    "shape": "불규칙한 탄화 패턴",
                    "material": "탄화 물질",
                    "purpose": "화재 확산 증거",
                    "risk": "재발화",
                    "confidence": 0.95,
                    "source": "mock"
                }
            ]
            hazard_analysis = {
                "hazard_level": "high",
                "risk_score": 85,
                "findings": ["전기적 화재 위험 감지"]
            }
        
        result = {
            "status": "success",
            "model": "yolov8n-fire" if yolo_model and not yolo_model.use_mock else "mock",
            "filename": file.filename,
            "selected_area": {
                "center_x": center_x,
                "center_y": center_y,
                "radius": radius
            } if center_x else None,
            "objects": detected_objects,
            "hazard_analysis": hazard_analysis,
            "timestamp": datetime.now().isoformat()
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
    AI 화재 원인 분석 API - OpenAI GPT-4 실제 연동
    """
    try:
        evidence = request.get("evidence", {})
        selected_area = request.get("selected_area")
        
        # OpenAI API 호출
        if openai_client:
            prompt = f"""당신은 소방 화재조사 전문가입니다. 다음 증거 정보를 바탕으로 화재 원인을 분석해주세요.

증거 정보:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

선택된 영역: {selected_area if selected_area else '전체 이미지'}

다음 형식으로 HTML 형태의 분석 결과를 제공해주세요:

<h4>🔍 분석 개요</h4>
<p>전체적인 화재 상황 요약</p>

<h4>📊 감지된 주요 증거</h4>
<ul>
<li>증거1 - 설명</li>
</ul>

<h4>🔥 발화지점 추정</h4>
<p>추정 위치 및 근거</p>

<h4>⚠️ 화재 원인 분석</h4>
<p>가능성 있는 원인들</p>
<ul>
<li><strong>원인1</strong>: 설명</li>
</ul>

<h4>📝 권장 사항</h4>
<ul>
<li>조치사항</li>
</ul>

<p style="color: #666; font-size: 12px; margin-top: 20px;">
    * 본 분석은 ChatGPT AI 기반 추론 결과이며, 최종 판단은 담당 조사관이 수행해야 합니다.
</p>
"""
            
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 소방 화재조사 전문가입니다. 과학적 근거에 기반한 객관적인 분석을 제공합니다."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                analysis_html = response.choices[0].message.content
                
                return JSONResponse(content={
                    "status": "success",
                    "analysis": analysis_html,
                    "model": "gpt-4",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"OpenAI API 오류: {e}")
                # API 오류 시 Mock 결과 반환
                return JSONResponse(content={
                    "status": "partial",
                    "analysis": get_mock_analysis(),
                    "error": str(e),
                    "note": "OpenAI API 오류로 인해 기본 분석 결과를 반환합니다."
                })
        else:
            # OpenAI 클라이언트가 없는 경우 Mock 결과
            return JSONResponse(content={
                "status": "mock",
                "analysis": get_mock_analysis(),
                "note": "OpenAI API 키가 설정되지 않아 Mock 결과를 반환합니다."
            })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/api/report")
async def generate_report(request: dict):
    """
    조사보고서 생성 API - OpenAI GPT-4 실제 연동
    """
    try:
        evidence = request.get("evidence", {})
        analysis = request.get("analysis", "")
        
        if openai_client:
            prompt = f"""당신은 소방 화재조사 전문가입니다. 다음 정보를 바탕으로 공식 조사보고서를 작성해주세요.

증거 정보:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

분석 결과:
{analysis}

다음 형식으로 조사보고서를 작성해주세요:

화재조사 보고서

■ 사건 개요
- 사걸번호: FIRE-2024-001A
- 발생일시: (현재 날짜)
- 발생장소: (현장 위치)
- 조사관: 화재조사관

■ 현장 상황
(현장 설명)

■ 증거 수집
(수집된 증거 목록)

■ AI 분석 결과
(AI 분석 요약)

■ 결론
(화재 원인 요약)

■ 조치 사항
(후속 조치 방안)

작성일: {datetime.now().strftime('%Y년 %m월 %d일')}
AI 분석 시스템 v1.1 / 담당 조사관
"""
            
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 소방 화재조사 전문가입니다. 공식적인 보고서 형식으로 작성합니다."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                report = response.choices[0].message.content
                
                return JSONResponse(content={
                    "status": "success",
                    "report": report,
                    "model": "gpt-4",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"OpenAI API 오류 (보고서): {e}")
                return JSONResponse(content={
                    "status": "partial",
                    "report": get_mock_report(),
                    "error": str(e)
                })
        else:
            return JSONResponse(content={
                "status": "mock",
                "report": get_mock_report()
            })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


def get_mock_analysis():
    """Mock AI 분석 결과"""
    return """<h4>🔍 분석 개요</h4>
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
</p>"""


def get_mock_report():
    """Mock 보고서"""
    return """화재조사 보고서

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
AI 분석 시스템 v1.1 / 담당 조사관"""


if __name__ == "__main__":
    import uvicorn
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    uvicorn.run(app, host="0.0.0.0", port=port)
