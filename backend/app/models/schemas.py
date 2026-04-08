"""
Pydantic 스키마 정의 (요청/응답 모델)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# 공통 스키마
class FireCause(str, Enum):
    ELECTRICAL = "electrical"
    GAS_LEAK = "gas_leak"
    ARSON = "arson"
    ACCIDENTAL = "accidental"
    MECHANICAL = "mechanical"
    CHEMICAL = "chemical"
    UNKNOWN = "unknown"
    OTHER = "other"


class InvestigationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ANALYZING = "analyzing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class UserRole(str, Enum):
    INVESTIGATOR = "investigator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    FORENSIC_EXPERT = "forensic_expert"


# 사용자 스키마
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    badge_number: Optional[str] = None
    department: Optional[str] = None
    role: UserRole = UserRole.INVESTIGATOR


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# 인증 스키마
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


# 화재 조사 스키마
class InvestigationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    incident_datetime: Optional[datetime] = None


class InvestigationCreate(InvestigationBase):
    pass


class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    incident_datetime: Optional[datetime] = None
    status: Optional[InvestigationStatus] = None
    final_report: Optional[str] = None


class InvestigationResponse(InvestigationBase):
    id: int
    case_number: str
    status: InvestigationStatus
    investigation_datetime: Optional[datetime]
    
    # AI 분석 결과
    predicted_cause: Optional[FireCause]
    predicted_cause_confidence: Optional[float]
    ignition_point: Optional[Dict[str, Any]]
    analysis_summary: Optional[str]
    
    # 보고서
    final_report: Optional[str]
    is_report_approved: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    
    # 메타데이터
    investigator_id: int
    investigator: UserResponse
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InvestigationList(BaseModel):
    total: int
    items: List[InvestigationResponse]


# 증거 자료 스키마
class EvidenceBase(BaseModel):
    description: Optional[str] = None
    capture_datetime: Optional[datetime] = None
    capture_location: Optional[Dict[str, float]] = None


class EvidenceCreate(EvidenceBase):
    investigation_id: int


class EvidenceResponse(EvidenceBase):
    id: int
    investigation_id: int
    evidence_number: str
    file_name: str
    original_file_name: str
    file_path: str
    file_size: int
    file_type: str
    mime_type: str
    
    # AI 분석
    has_been_analyzed: bool
    analysis_metadata: Optional[Dict[str, Any]]
    
    # 개인정보 보호
    is_pii_blurred: bool
    blur_regions: Optional[List[Dict[str, Any]]]
    
    # 해시 (증거 무결성)
    hash_md5: Optional[str]
    hash_sha256: Optional[str]
    
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# AI 분석 스키마
class DetectedObject(BaseModel):
    class_name: str
    confidence: float
    bbox: Dict[str, float]  # {x1, y1, x2, y2}


class AnalysisRequest(BaseModel):
    evidence_id: int
    analysis_type: str = "full"  # yolo, gpt4v, full
    focus_area: Optional[Dict[str, float]] = None  # Circle-to-Search 영역


class AnalysisResponse(BaseModel):
    id: int
    investigation_id: int
    evidence_id: Optional[int]
    analysis_type: str
    
    # 분석 결과
    detected_objects: List[DetectedObject]
    fire_patterns: Optional[List[Dict[str, Any]]]
    confidence_score: float
    
    # 원인 추정
    predicted_cause: Optional[FireCause]
    cause_confidence: Optional[float]
    ignition_point_estimate: Optional[Dict[str, Any]]
    
    # 유사 사례
    similar_cases: Optional[List[Dict[str, Any]]]
    
    # 메타데이터
    processing_time_ms: int
    model_version: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Circle-to-Search 스키마
class CircleToSearchRequest(BaseModel):
    evidence_id: int
    center_x: float  # 0-1 사이 정규화된 좌표
    center_y: float
    radius: float    # 0-1 사이 정규화된 반지름


class SimilarCaseResponse(BaseModel):
    id: int
    external_case_id: str
    title: str
    incident_date: Optional[datetime]
    location: Optional[str]
    fire_cause: Optional[FireCause]
    damage_summary: Optional[str]
    lessons_learned: Optional[str]
    similarity_score: float


# 보고서 생성 스키마
class ReportGenerateRequest(BaseModel):
    investigation_id: int
    include_ai_analysis: bool = True
    include_evidence_summary: bool = True
    template_type: str = "standard"  # standard, detailed, summary


class ReportGenerateResponse(BaseModel):
    investigation_id: int
    generated_report: str
    ai_summary: Optional[str]
    confidence_level: Optional[str]
    recommendations: Optional[List[str]]
    generated_at: datetime


# 챗봇/질의응답 스키마
class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    investigation_id: int
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    investigation_id: int
    response: str
    sources: Optional[List[Dict[str, Any]]]  # 참고한 증거/분석 결과
    confidence: Optional[float]


# 감사 로그 스키마
class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    username: str
    action: str
    resource_type: str
    resource_id: str
    investigation_id: Optional[int]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    success: bool
    
    class Config:
        from_attributes = True


# 오프라인 동기화 스키마
class SyncRequest(BaseModel):
    device_id: str
    pending_operations: List[Dict[str, Any]]


class SyncResponse(BaseModel):
    synced_count: int
    failed_count: int
    conflicts: Optional[List[Dict[str, Any]]]


# 대시보드/통계 스키마
class DashboardStats(BaseModel):
    total_investigations: int
    investigations_this_month: int
    pending_analysis: int
    completed_reports: int
    recent_cases: List[InvestigationResponse]
    cause_distribution: Dict[str, int]
    average_processing_time: Optional[float]  # 분 단위
