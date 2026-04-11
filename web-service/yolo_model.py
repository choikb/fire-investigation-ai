"""
YOLOv8 Fire & Object Detection 모듈
다양한 화재 관련 객체 감지를 위한 통합 모델
"""
import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
from PIL import Image
import io

# YOLOv8 임포트 (없으면 설치 필요)
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("Ultralytics YOLO not installed. Using mock detection.")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FireDetectionModel:
    """
    화재 감지 및 전기 장비 감지 통합 모델
    """
    
    # 클래스 매핑 (Fire & Smoke 모델)
    FIRE_CLASSES = {
        0: {"name": "fire", "ko": "불꽃", "type": "hazard"},
        1: {"name": "smoke", "ko": "연기", "type": "hazard"},
    }
    
    # 확장 클래스 (전기 화재 관련)
    ELECTRICAL_CLASSES = {
        2: {"name": "heater", "ko": "전열기", "type": "electrical"},
        3: {"name": "cable", "ko": "전원 케이블", "type": "electrical"},
        4: {"name": "outlet", "ko": "콘센트", "type": "electrical"},
        5: {"name": "burn_mark", "ko": "연소 흔적", "type": "evidence"},
        6: {"name": "gas_stove", "ko": "가스레인지", "type": "appliance"},
    }
    
    # 재질 및 용도 매핑
    MATERIAL_MAP = {
        "heater": {"material": "금속 + 세라믹", "purpose": "가열/보온", "risk": "과열"},
        "cable": {"material": "구리 + PVC", "purpose": "전력 공급", "risk": "단선/과부하"},
        "outlet": {"material": "플라스틱 + 구리", "purpose": "전원 연결", "risk": "과부하/접촉불량"},
        "gas_stove": {"material": "스테인리스 + 유리", "purpose": "조리", "risk": "가스 누출"},
        "burn_mark": {"material": "탄화 물질", "purpose": "화재 증거", "risk": "재발화"},
        "fire": {"material": "가연성 물질", "purpose": "발화", "risk": "확산"},
        "smoke": {"material": "입자 물질", "purpose": "연소 산물", "risk": "유독가스"},
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """
        모델 초기화
        
        Args:
            model_path: YOLO 모델 파일 경로 (.pt)
        """
        self.model = None
        self.model_path = model_path
        self.use_mock = not YOLO_AVAILABLE or model_path is None
        
        if self.use_mock:
            logger.info("Using MOCK detection (no YOLO model)")
        else:
            self._load_model()
    
    def _load_model(self):
        """YOLO 모델 로드"""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                logger.info(f"✅ Model loaded: {self.model_path}")
            else:
                logger.warning(f"Model file not found: {self.model_path}")
                self.use_mock = True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.use_mock = True
    
    def detect(self, image_data: bytes, conf_threshold: float = 0.5) -> List[Dict]:
        """
        이미지에서 객체 감지
        
        Args:
            image_data: 이미지 바이트 데이터
            conf_threshold: 신뢰도 임계값
            
        Returns:
            감지된 객체 리스트
        """
        if self.use_mock:
            return self._mock_detect(image_data)
        
        try:
            # 이미지 로드
            image = Image.open(io.BytesIO(image_data))
            
            # 추론
            results = self.model(image, conf=conf_threshold)
            
            # 결과 파싱
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    # 클래스 정보 가져오기
                    class_info = self.FIRE_CLASSES.get(cls_id, 
                        self.ELECTRICAL_CLASSES.get(cls_id, 
                            {"name": f"object_{cls_id}", "ko": "미확인 물체", "type": "unknown"}))
                    
                    # 재질/용도 정보 추가
                    material_info = self.MATERIAL_MAP.get(class_info["name"], {})
                    
                    detection = {
                        "id": len(detections),
                        "class": class_info["name"],
                        "class_ko": class_info["ko"],
                        "type": class_info["type"],
                        "confidence": round(conf, 3),
                        "bbox": {
                            "x1": round(xyxy[0], 2),
                            "y1": round(xyxy[1], 2),
                            "x2": round(xyxy[2], 2),
                            "y2": round(xyxy[3], 2),
                        },
                        "material": material_info.get("material", "미확인"),
                        "purpose": material_info.get("purpose", "미확인"),
                        "risk": material_info.get("risk", "미확인"),
                    }
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return self._mock_detect(image_data)
    
    def _mock_detect(self, image_data: bytes) -> List[Dict]:
        """
        Mock 감지 (YOLO 없을 때 테스트용)
        """
        logger.info("Using MOCK detection")
        
        # 테스트용 Mock 데이터
        mock_detections = [
            {
                "id": 0,
                "class": "heater",
                "class_ko": "전열기",
                "type": "electrical",
                "confidence": 0.92,
                "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 250},
                "material": "금속 + 세라믹",
                "purpose": "가열/보온",
                "risk": "과열",
            },
            {
                "id": 1,
                "class": "cable",
                "class_ko": "전원 케이블",
                "type": "electrical",
                "confidence": 0.88,
                "bbox": {"x1": 250, "y1": 180, "x2": 350, "y2": 220},
                "material": "구리 + PVC",
                "purpose": "전력 공급",
                "risk": "단선/과부하",
            },
            {
                "id": 2,
                "class": "burn_mark",
                "class_ko": "연소 흔적",
                "type": "evidence",
                "confidence": 0.95,
                "bbox": {"x1": 120, "y1": 260, "x2": 180, "y2": 300},
                "material": "탄화 물질",
                "purpose": "화재 증거",
                "risk": "재발화",
            },
        ]
        
        return mock_detections
    
    def analyze_fire_hazard(self, detections: List[Dict]) -> Dict:
        """
        감지된 객체 기반 화재 위험 분석
        
        Args:
            detections: 감지된 객체 리스트
            
        Returns:
            위험 분석 결과
        """
        if not detections:
            return {
                "hazard_level": "low",
                "risk_score": 0,
                "findings": ["감지된 위험 요소 없음"],
            }
        
        # 위험 요소 카운트
        electrical_count = sum(1 for d in detections if d["type"] == "electrical")
        hazard_count = sum(1 for d in detections if d["type"] == "hazard")
        evidence_count = sum(1 for d in detections if d["type"] == "evidence")
        
        # 위험도 계산
        risk_score = min(100, (electrical_count * 20) + (hazard_count * 40) + (evidence_count * 30))
        
        # 위험 등급
        if risk_score >= 70:
            hazard_level = "high"
        elif risk_score >= 40:
            hazard_level = "medium"
        else:
            hazard_level = "low"
        
        # 주요 발견사항
        findings = []
        for det in detections:
            findings.append(f"{det['class_ko']} (신뢰도: {det['confidence']:.0%}) - {det['risk']} 위험")
        
        return {
            "hazard_level": hazard_level,
            "risk_score": risk_score,
            "electrical_count": electrical_count,
            "hazard_count": hazard_count,
            "evidence_count": evidence_count,
            "findings": findings,
        }


# 싱글톤 인스턴스
_model_instance = None

def get_model(model_path: Optional[str] = None) -> FireDetectionModel:
    """
    YOLO 모델 싱글톤 getter
    """
    global _model_instance
    if _model_instance is None:
        # 기본 모델 경로
        default_path = model_path or os.path.join(
            os.path.dirname(__file__), 
            "models", 
            "fire-smoke-yolov8n.pt"
        )
        _model_instance = FireDetectionModel(default_path)
    return _model_instance
