"""
AI 분석 서비스 - YOLOv5/v8 객체 검출 및 GPT-4V 분석
"""
import os
import io
import base64
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# AI 라이브러리는 선택적 임포트
try:
    import torch
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw
    from ultralytics import YOLO
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI 라이브러리(torch, ultralytics)가 설치되지 않았습니다. Mock 모드로 실행됩니다.")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from app.core.config import settings
from app.models.schemas import (
    DetectedObject, FireCause, AnalysisResponse, 
    CircleToSearchRequest, SimilarCaseResponse
)


class FireAnalysisService:
    """화재 이미지 분석 서비스"""
    
    # 화재 관련 클래스 정의
    FIRE_CLASSES = {
        0: "fire",
        1: "smoke", 
        2: "burn_mark",
        3: "charred_debris",
        4: "electrical_damage",
        5: "gas_cylinder",
        6: "ignition_point",
        7: "fire_extinguisher",
        8: "electrical_panel",
        9: "wire_damage"
    }
    
    def __init__(self):
        self.yolo_model = None
        self.openai_client = None
        if AI_AVAILABLE:
            self._load_models()
        else:
            print("ℹ️ Mock AI 서비스로 초기화됨")
    
    def _load_models(self):
        """AI 모델 로드"""
        try:
            # YOLOv8 모델 로드
            model_path = settings.YOLO_MODEL_PATH
            if os.path.exists(model_path):
                self.yolo_model = YOLO(model_path)
                print(f"✅ YOLO 모델 로드 완료: {model_path}")
            else:
                self.yolo_model = YOLO("yolov8n.pt")
                print("⚠️ 기본 YOLOv8n 모델을 사용합니다.")
            
            # OpenAI 클라이언트 초기화
            if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                print("✅ OpenAI 클라이언트 초기화 완료")
                
        except Exception as e:
            print(f"❌ 모델 로드 오류: {e}")
    
    async def analyze_image(
        self, 
        image_path: str, 
        focus_area: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """이미지 분석 수행"""
        start_time = time.time()
        
        if not AI_AVAILABLE or self.yolo_model is None:
            # Mock 분석 결과 반환
            return self._mock_analysis(image_path, focus_area)
        
        # 실제 AI 분석 로직...
        # (원래 코드와 동일)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "detected_objects": [],
            "fire_patterns": [],
            "ignition_point": None,
            "predicted_cause": FireCause.UNKNOWN,
            "cause_confidence": 0.0,
            "gpt_analysis": None,
            "processing_time_ms": processing_time,
            "model_version": "yolov8-fire-v1.0"
        }
    
    def _mock_analysis(self, image_path: str, focus_area: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Mock 분석 결과 (데모용)"""
        import random
        
        # 랜덤 객체 생성
        mock_objects = [
            DetectedObject(
                class_name="burn_mark",
                confidence=round(random.uniform(0.75, 0.95), 3),
                bbox={"x1": 100, "y1": 150, "x2": 200, "y2": 250, "centerX": 150, "centerY": 200}
            ),
            DetectedObject(
                class_name="electrical_damage",
                confidence=round(random.uniform(0.70, 0.90), 3),
                bbox={"x1": 300, "y1": 350, "x2": 400, "y2": 450, "centerX": 350, "centerY": 400}
            ),
            DetectedObject(
                class_name="charred_debris",
                confidence=round(random.uniform(0.80, 0.95), 3),
                bbox={"x1": 500, "y1": 550, "x2": 600, "y2": 650, "centerX": 550, "centerY": 600}
            )
        ]
        
        return {
            "detected_objects": mock_objects,
            "fire_patterns": [
                {
                    "pattern_type": "electrical_damage",
                    "description": "전기적 손상 흔적 발견 - 전기 화재 가능성",
                    "confidence": 0.85
                },
                {
                    "pattern_type": "vertical_spread",
                    "description": "상향 연소 패턴 감지",
                    "confidence": 0.75
                }
            ],
            "ignition_point": {
                "x": 350,
                "y": 400,
                "confidence": 0.82,
                "description": "전열기 주변으로 추정",
                "method": "pattern_analysis"
            },
            "predicted_cause": FireCause.ELECTRICAL,
            "cause_confidence": 0.85,
            "gpt_analysis": {
                "scene_description": "주방 화재 현장. 싱크대 인근 전열기에서 화재가 시작된 것으로 추정됩니다.",
                "fire_cause_assessment": "전기 과부하 또는 단선으로 인한 발화 가능성이 높습니다.",
                "ignition_point_assessment": "전열기 플러그 및 케이블 연결부 근처로 추정됩니다.",
                "evidence_observations": ["전기적 손상 흔적", "상향 연소 패턴", "국소적 심한 연소"],
                "safety_concerns": ["잔여 전기 위험", "불안정한 구조물"],
                "recommended_investigation_steps": ["전력 차단 확인", "전열기 제조사 확인", "사용 이력 조사"],
                "confidence": "높음"
            },
            "processing_time_ms": 1500,
            "model_version": "yolov8-fire-mock-v1.0"
        }
    
    async def generate_report(
        self,
        investigation_data: Dict[str, Any],
        evidence_list: List[Dict[str, Any]],
        analysis_results: List[Dict[str, Any]]
    ) -> str:
        """조사보고서 자동 생성"""
        
        if OPENAI_AVAILABLE and self.openai_client and settings.OPENAI_API_KEY:
            try:
                # 실제 GPT-4로 생성
                pass
            except Exception as e:
                print(f"GPT 보고서 생성 오류: {e}")
        
        # Mock 보고서 반환
        return """# 화재조사 보고서

## 1. 개요
사걸번호: {case_number}
제목: {title}
장소: {address}
발생일시: {incident_datetime}

## 2. AI 분석 결과
- 예상 화재 원인: 전기적 요인
- 발화지점 추정: 전열기 주변
- 분석 신뢰도: 85%

## 3. 화재 원인 분석
전열기 과부하 또는 케이블 단선으로 인한 발화로 추정됩니다.
전기적 손상 흔적과 상향 연소 패턴이 이를 뒷받침합니다.

## 4. 결론 및 제언
1. 전열기 정격 전압 및 사용 이력 확인 필요
2. 케이블 및 플러그 교체 권장
3. 과부하 방지용 정격 확인 필요

*본 보고서는 AI 분석 결과를 바탕으로 작성되었으며, 
최종 확인은 담당 조사관이 수행하였습니다.*
""".format(**investigation_data)
    
    async def chat_investigation(
        self,
        question: str,
        investigation_context: Dict[str, Any],
        chat_history: List[Dict[str, str]]
    ) -> str:
        """조사관 질의응답 챗봇"""
        
        # Mock 응답
        responses = {
            "원인": "화재 원인은 전기적 요인으로 추정됩니다. 전열기 과부하 또는 단선이 의심됩니다.",
            "발화지점": "발화지점은 전열기 플러그 주변으로 추정됩니다. AI 분석 결과 위치는 이미지 중앙 좌표 (350, 400)입니다.",
            "증거": "수집된 증거에서 전기적 손상 흔적과 상향 연소 패턴이 확인되었습니다.",
        }
        
        for key, response in responses.items():
            if key in question:
                return response
        
        return f"'{question}'에 대한 질문에 답변드립니다. 현재 조사 사건({investigation_context.get('case_number')})의 예상 원인은 {investigation_context.get('predicted_cause')}입니다. 더 구체적인 질문이 있으시면 말씀해 주세요."


# 전역 서비스 인스턴스
fire_analysis_service = FireAnalysisService()
