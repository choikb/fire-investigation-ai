"""
감사 로그 유틸리티
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any

from app.models.models import AuditLog


async def log_audit(
    db: Session,
    user_id: int,
    username: str,
    action: str,
    resource_type: str,
    resource_id: str,
    investigation_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None
):
    """
    감사 로그 기록
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        username: 사용자명
        action: 수행된 작업 (CREATE, READ, UPDATE, DELETE, LOGIN, etc.)
        resource_type: 리소스 유형 (investigation, evidence, report, etc.)
        resource_id: 리소스 ID
        investigation_id: 관련 조사 ID (있는 경우)
        details: 추가 상세 정보
        ip_address: 클라이언트 IP
        user_agent: User-Agent 문자열
        success: 작업 성공 여부
        error_message: 오류 메시지 (실패 시)
    """
    audit_log = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        investigation_id=investigation_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        error_message=error_message
    )
    
    db.add(audit_log)
    db.commit()


def get_audit_logs(
    db: Session,
    investigation_id: Optional[int] = None,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """감사 로그 조회"""
    query = db.query(AuditLog)
    
    if investigation_id:
        query = query.filter(AuditLog.investigation_id == investigation_id)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
