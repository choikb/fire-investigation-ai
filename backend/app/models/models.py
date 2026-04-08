"""
화재조사 시스템 데이터베이스 모델
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """사용자 역할"""
    INVESTIGATOR = "investigator"  # 현장 조사관
    SUPERVISOR = "supervisor"      # 지휘관/책임자
    ADMIN = "admin"                # 관리자
    FORENSIC_EXPERT = "forensic_expert"  # 법과학자


class InvestigationStatus(str, enum.Enum):
    """조사 상태"""
    PENDING = "pending"           # 대기 중
    IN_PROGRESS = "in_progress"   # 진행 중
    ANALYZING = "analyzing"       # AI 분석 중
    REVIEWING = "reviewing"       # 검토 중
    COMPLETED = "completed"       # 완료
    ARCHIVED = "archived"         # 아카이브


class FireCause(str, enum.Enum):
    """화재 원인 분류"""
    ELECTRICAL = "electrical"     # 전기적 요인
    GAS_LEAK = "gas_leak"         # 가스 누출
    ARSON = "arson"               # 방화
    ACCIDENTAL = "accidental"     # 실수/부주의
    MECHANICAL = "mechanical"     # 기계적 결함
    CHEMICAL = "chemical"         # 화학 반응
    UNKNOWN = "unknown"           # 불명
    OTHER = "other"               # 기타


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    badge_number = Column(String(50), unique=True)  # 소방관 번호
    department = Column(String(100))  # 소속 부서
    role = Column(Enum(UserRole), default=UserRole.INVESTIGATOR)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # 관계
    investigations = relationship("Investigation", back_populates="investigator")
    audit_logs = relationship("AuditLog", back_populates="user")


class Investigation(Base):
    """화재 조사 사건 모델"""
    __tablename__ = "investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 위치 정보
    address = Column(String(300))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # 조사 정보
    incident_datetime = Column(DateTime(timezone=True))
    investigation_datetime = Column(DateTime(timezone=True))
    status = Column(Enum(InvestigationStatus), default=InvestigationStatus.PENDING)
    
    # AI 분석 결과
    predicted_cause = Column(Enum(FireCause))
    predicted_cause_confidence = Column(Float)
    ignition_point = Column(JSON)  # {"x": 100, "y": 200, "description": "..."}
    analysis_summary = Column(Text)
    
    # 최종 보고서
    final_report = Column(Text)
    is_report_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # 메타데이터
    investigator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_synced = Column(Boolean, default=True)  # 오프라인 동기화 상태
    
    # 관계
    investigator = relationship("User", back_populates="investigations")
    evidence_items = relationship("Evidence", back_populates="investigation")
    analysis_results = relationship("AnalysisResult", back_populates="investigation")
    audit_logs = relationship("AuditLog", back_populates="investigation")


class Evidence(Base):
    """증거 자료 모델"""
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)
    evidence_number = Column(String(50), nullable=False)
    
    # 파일 정보
    file_name = Column(String(255), nullable=False)
    original_file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # MinIO/S3 경로
    file_size = Column(Integer)  # 바이트
    file_type = Column(String(50))  # image/jpeg, video/mp4 등
    mime_type = Column(String(100))
    
    # 메타데이터
    description = Column(Text)
    capture_datetime = Column(DateTime(timezone=True))
    capture_location = Column(JSON)  # {"lat": 37.5, "lng": 127.0}
    device_info = Column(JSON)  # {"device_id": "...", "model": "..."}
    
    # AI 분석 메타데이터
    has_been_analyzed = Column(Boolean, default=False)
    analysis_metadata = Column(JSON)  # AI 분석 관련 추가 정보
    
    # 개인정보 보호
    is_pii_blurred = Column(Boolean, default=False)  # 개인정보 모자이크 처리 여부
    blur_regions = Column(JSON)  # 모자이크 영역 좌표
    
    # 체인 오브 커스터디
    hash_md5 = Column(String(32))
    hash_sha256 = Column(String(64))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    is_synced = Column(Boolean, default=True)
    
    # 관계
    investigation = relationship("Investigation", back_populates="evidence_items")


class AnalysisResult(Base):
    """AI 분석 결과 모델"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)
    evidence_id = Column(Integer, ForeignKey("evidence.id"))
    
    # 분석 유형
    analysis_type = Column(String(50), nullable=False)  # yolo_detection, gpt4v_analysis, similarity_search
    
    # 분석 결과
    result_data = Column(JSON)  # 상세 분석 결과
    detected_objects = Column(JSON)  # 감지된 객체 목록
    fire_patterns = Column(JSON)  # 화재 패턴 분석
    confidence_score = Column(Float)
    
    # 원인 추정
    predicted_cause = Column(Enum(FireCause))
    cause_confidence = Column(Float)
    ignition_point_estimate = Column(JSON)  # 발화지점 추정
    
    # 유사 사례
    similar_cases = Column(JSON)  # 유사 사례 ID 목록
    
    # 메타데이터
    processing_time_ms = Column(Integer)  # 처리 시간
    model_version = Column(String(50))  # 사용된 모델 버전
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    investigation = relationship("Investigation", back_populates="analysis_results")


class SimilarCase(Base):
    """유사 화재 사례 모델 (빅데이터 연계)"""
    __tablename__ = "similar_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    external_case_id = Column(String(100), unique=True)  # 외부 DB의 사건 ID
    title = Column(String(200), nullable=False)
    incident_date = Column(DateTime(timezone=True))
    location = Column(String(200))
    fire_cause = Column(Enum(FireCause))
    damage_summary = Column(Text)
    lessons_learned = Column(Text)
    source_database = Column(String(100))  # 데이터 출처
    case_data = Column(JSON)  # 전체 사건 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """감사 로그 모델"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # 사용자 정보
    user_id = Column(Integer, ForeignKey("users.id"))
    username = Column(String(50))
    
    # 작업 정보
    action = Column(String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE, LOGIN, EXPORT
    resource_type = Column(String(50), nullable=False)  # investigation, evidence, report
    resource_id = Column(String(50))
    
    # 상세 정보
    investigation_id = Column(Integer, ForeignKey("investigations.id"))
    details = Column(JSON)  # 변경 전/후 데이터 등
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # 결과
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # 관계
    user = relationship("User", back_populates="audit_logs")
    investigation = relationship("Investigation", back_populates="audit_logs")


class OfflineQueue(Base):
    """오프라인 동기화 대기열"""
    __tablename__ = "offline_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), nullable=False)
    operation = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    entity_type = Column(String(50), nullable=False)  # investigation, evidence
    entity_id = Column(String(50))
    payload = Column(JSON)  # 동기화할 데이터
    file_attachments = Column(JSON)  # 첨부 파일 정보
    
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    synced_at = Column(DateTime(timezone=True))
