"""
대시보드 및 통계 API 엔드포인트
"""
from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Investigation, Evidence, AnalysisResult, User
from app.models.schemas import DashboardStats, InvestigationResponse

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """대시보드 통계 조회"""
    
    # 기본 통계
    total_investigations = db.query(Investigation).count()
    
    # 이번 달 조사
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    investigations_this_month = db.query(Investigation).filter(
        Investigation.created_at >= first_day_of_month
    ).count()
    
    # 대기 중인 분석
    pending_analysis = db.query(Investigation).filter(
        Investigation.predicted_cause == None
    ).count()
    
    # 완료된 보고서
    completed_reports = db.query(Investigation).filter(
        Investigation.final_report != None
    ).count()
    
    # 최근 사건 (최근 5개)
    recent_cases_query = db.query(Investigation).order_by(
        Investigation.created_at.desc()
    ).limit(5)
    
    # 조사관은 자신의 사걸만
    if current_user.role.value == "investigator":
        recent_cases_query = recent_cases_query.filter(
            Investigation.investigator_id == current_user.id
        )
    
    recent_cases = recent_cases_query.all()
    
    # 원인 분포
    cause_distribution = {}
    causes = db.query(
        Investigation.predicted_cause, 
        func.count(Investigation.id)
    ).filter(
        Investigation.predicted_cause != None
    ).group_by(Investigation.predicted_cause).all()
    
    for cause, count in causes:
        cause_distribution[cause.value] = count
    
    # 평균 처리 시간 (분석 완료까지)
    avg_time_result = db.query(
        func.avg(
            func.extract('epoch', Investigation.updated_at - Investigation.created_at) / 60
        )
    ).filter(
        Investigation.predicted_cause != None
    ).scalar()
    
    return DashboardStats(
        total_investigations=total_investigations,
        investigations_this_month=investigations_this_month,
        pending_analysis=pending_analysis,
        completed_reports=completed_reports,
        recent_cases=[InvestigationResponse.model_validate(c) for c in recent_cases],
        cause_distribution=cause_distribution,
        average_processing_time=float(avg_time_result) if avg_time_result else None
    )


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """최근 활동 내역"""
    
    from app.models.models import AuditLog
    
    query = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    
    # 조사관은 자신의 활동만
    if current_user.role.value == "investigator":
        query = query.filter(AuditLog.user_id == current_user.id)
    
    activities = query.all()
    
    return [
        {
            "id": act.id,
            "timestamp": act.timestamp,
            "username": act.username,
            "action": act.action,
            "resource_type": act.resource_type,
            "resource_id": act.resource_id,
            "investigation_id": act.investigation_id,
            "success": act.success
        }
        for act in activities
    ]


@router.get("/monthly-stats")
async def get_monthly_stats(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """월별 통계"""
    
    stats = []
    today = datetime.now()
    
    for i in range(months):
        month_date = today - timedelta(days=30 * i)
        year = month_date.year
        month = month_date.month
        
        count = db.query(Investigation).filter(
            extract('year', Investigation.created_at) == year,
            extract('month', Investigation.created_at) == month
        ).count()
        
        stats.append({
            "year": year,
            "month": month,
            "count": count
        })
    
    return {"monthly_stats": stats}


@router.get("/performance-metrics")
async def get_performance_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """성능 지표"""
    
    # AI 분석 성공률
    total_evidence = db.query(Evidence).count()
    analyzed_evidence = db.query(Evidence).filter(
        Evidence.has_been_analyzed == True
    ).count()
    
    analysis_success_rate = (analyzed_evidence / total_evidence * 100) if total_evidence > 0 else 0
    
    # 평균 분석 시간
    avg_analysis_time = db.query(
        func.avg(AnalysisResult.processing_time_ms)
    ).scalar()
    
    # 신뢰도 분포
    confidence_distribution = db.query(
        func.case(
            (AnalysisResult.confidence_score >= 0.8, 'high'),
            (AnalysisResult.confidence_score >= 0.5, 'medium'),
            else_='low'
        ),
        func.count(AnalysisResult.id)
    ).group_by(
        func.case(
            (AnalysisResult.confidence_score >= 0.8, 'high'),
            (AnalysisResult.confidence_score >= 0.5, 'medium'),
            else_='low'
        )
    ).all()
    
    return {
        "analysis_success_rate": round(analysis_success_rate, 2),
        "analyzed_evidence": analyzed_evidence,
        "total_evidence": total_evidence,
        "avg_analysis_time_ms": round(float(avg_analysis_time), 2) if avg_analysis_time else None,
        "confidence_distribution": {
            item[0]: item[1] for item in confidence_distribution
        }
    }
