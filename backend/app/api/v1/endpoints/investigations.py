"""
화재 조사 API 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    Investigation, Evidence, AnalysisResult, User, InvestigationStatus
)
from app.models.schemas import (
    InvestigationCreate, InvestigationUpdate, InvestigationResponse,
    InvestigationList, EvidenceResponse, ReportGenerateRequest,
    ReportGenerateResponse, AnalysisRequest
)
from app.services.ai_analysis import fire_analysis_service
from app.services.storage_service import storage_service
from app.utils.audit import log_audit

router = APIRouter()


def generate_case_number() -> str:
    """사걸 번호 생성 (YYYY-XXXXX 형식)"""
    year = datetime.now().year
    random_id = uuid.uuid4().hex[:6].upper()
    return f"FIRE-{year}-{random_id}"


@router.post("/", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    investigation: InvestigationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새로운 화재 조사 사건 생성"""
    
    db_investigation = Investigation(
        case_number=generate_case_number(),
        title=investigation.title,
        description=investigation.description,
        address=investigation.address,
        latitude=investigation.latitude,
        longitude=investigation.longitude,
        incident_datetime=investigation.incident_datetime,
        investigation_datetime=datetime.now(),
        status=InvestigationStatus.PENDING,
        investigator_id=current_user.id
    )
    
    db.add(db_investigation)
    db.commit()
    db.refresh(db_investigation)
    
    # 감사 로그 기록
    await log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        action="CREATE",
        resource_type="investigation",
        resource_id=str(db_investigation.id),
        investigation_id=db_investigation.id,
        details={"case_number": db_investigation.case_number}
    )
    
    return db_investigation


@router.get("/", response_model=InvestigationList)
async def list_investigations(
    skip: int = 0,
    limit: int = 20,
    status: Optional[InvestigationStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """화재 조사 목록 조회"""
    
    query = db.query(Investigation)
    
    # 일반 조사관은 자신의 사걸만 조회
    if current_user.role.value == "investigator":
        query = query.filter(Investigation.investigator_id == current_user.id)
    
    if status:
        query = query.filter(Investigation.status == status)
    
    total = query.count()
    investigations = query.order_by(desc(Investigation.created_at)).offset(skip).limit(limit).all()
    
    return InvestigationList(total=total, items=investigations)


@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 화재 조사 상세 조회"""
    
    investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="조사 사건을 찾을 수 없습니다")
    
    # 권한 체크
    if (current_user.role.value == "investigator" and 
        investigation.investigator_id != current_user.id):
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
    
    # 감사 로그
    await log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        action="READ",
        resource_type="investigation",
        resource_id=str(investigation_id),
        investigation_id=investigation_id
    )
    
    return investigation


@router.put("/{investigation_id}", response_model=InvestigationResponse)
async def update_investigation(
    investigation_id: int,
    update_data: InvestigationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """화재 조사 정보 업데이트"""
    
    investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="조사 사건을 찾을 수 없습니다")
    
    # 권한 체크
    if (current_user.role.value == "investigator" and 
        investigation.investigator_id != current_user.id):
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다")
    
    # 업데이트할 필드
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(investigation, field, value)
    
    investigation.updated_at = datetime.now()
    db.commit()
    db.refresh(investigation)
    
    # 감사 로그
    await log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        action="UPDATE",
        resource_type="investigation",
        resource_id=str(investigation_id),
        investigation_id=investigation_id,
        details={"updated_fields": list(update_dict.keys())}
    )
    
    return investigation


@router.post("/{investigation_id}/evidence", response_model=EvidenceResponse)
async def upload_evidence(
    investigation_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    capture_datetime: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """증거 자료 업로드"""
    
    investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="조사 사건을 찾을 수 없습니다")
    
    # 파일 저장
    file_path, file_hash = await storage_service.save_file(
        file=file,
        investigation_id=investigation_id,
        file_name=file.filename
    )
    
    # 증거 번호 생성
    evidence_count = db.query(Evidence).filter(
        Evidence.investigation_id == investigation_id
    ).count()
    evidence_number = f"EVD-{investigation.case_number}-{evidence_count + 1:03d}"
    
    # DB 저장
    evidence = Evidence(
        investigation_id=investigation_id,
        evidence_number=evidence_number,
        file_name=file_path.split("/")[-1],
        original_file_name=file.filename,
        file_path=file_path,
        file_size=0,  # 실제 크기는 storage_service에서 계산
        file_type=file.content_type.split("/")[1] if "/" in file.content_type else "unknown",
        mime_type=file.content_type,
        description=description,
        capture_datetime=datetime.fromisoformat(capture_datetime) if capture_datetime else datetime.now(),
        capture_location={"lat": latitude, "lng": longitude} if latitude and longitude else None,
        hash_sha256=file_hash,
        uploaded_by=current_user.id
    )
    
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    
    # 상태 업데이트
    investigation.status = InvestigationStatus.IN_PROGRESS
    db.commit()
    
    # 감사 로그
    await log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        action="CREATE",
        resource_type="evidence",
        resource_id=str(evidence.id),
        investigation_id=investigation_id,
        details={"file_name": file.filename, "evidence_number": evidence_number}
    )
    
    return evidence


@router.get("/{investigation_id}/evidence", response_model=List[EvidenceResponse])
async def list_evidence(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """증거 자료 목록 조회"""
    
    evidence_list = db.query(Evidence).filter(
        Evidence.investigation_id == investigation_id
    ).order_by(desc(Evidence.uploaded_at)).all()
    
    return evidence_list


@router.post("/{investigation_id}/analyze")
async def analyze_investigation(
    investigation_id: int,
    analysis_request: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 분석 실행"""
    
    evidence = db.query(Evidence).filter(
        Evidence.id == analysis_request.evidence_id
    ).first()
    
    if not evidence or evidence.investigation_id != investigation_id:
        raise HTTPException(status_code=404, detail="증거 자료를 찾을 수 없습니다")
    
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id
    ).first()
    
    investigation.status = InvestigationStatus.ANALYZING
    db.commit()
    
    # AI 분석 수행
    try:
        analysis_result = await fire_analysis_service.analyze_image(
            image_path=evidence.file_path,
            focus_area=analysis_request.focus_area
        )
        
        # 분석 결과 저장
        db_analysis = AnalysisResult(
            investigation_id=investigation_id,
            evidence_id=evidence.id,
            analysis_type=analysis_request.analysis_type,
            result_data=analysis_result,
            detected_objects=[obj.model_dump() for obj in analysis_result["detected_objects"]],
            fire_patterns=analysis_result.get("fire_patterns"),
            confidence_score=analysis_result.get("cause_confidence", 0),
            predicted_cause=analysis_result.get("predicted_cause"),
            cause_confidence=analysis_result.get("cause_confidence"),
            ignition_point_estimate=analysis_result.get("ignition_point"),
            processing_time_ms=analysis_result["processing_time_ms"],
            model_version=analysis_result["model_version"]
        )
        
        db.add(db_analysis)
        
        # 증거 업데이트
        evidence.has_been_analyzed = True
        evidence.analysis_metadata = {
            "analysis_id": db_analysis.id,
            "predicted_cause": analysis_result.get("predicted_cause"),
            "analyzed_at": datetime.now().isoformat()
        }
        
        # 조사 정보 업데이트
        investigation.predicted_cause = analysis_result.get("predicted_cause")
        investigation.predicted_cause_confidence = analysis_result.get("cause_confidence")
        investigation.ignition_point = analysis_result.get("ignition_point")
        investigation.status = InvestigationStatus.REVIEWING
        
        db.commit()
        db.refresh(db_analysis)
        
        # 감사 로그
        await log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            action="ANALYZE",
            resource_type="evidence",
            resource_id=str(evidence.id),
            investigation_id=investigation_id,
            details={
                "predicted_cause": analysis_result.get("predicted_cause"),
                "confidence": analysis_result.get("cause_confidence")
            }
        )
        
        return {
            "analysis_id": db_analysis.id,
            "result": analysis_result,
            "message": "AI 분석이 완료되었습니다"
        }
        
    except Exception as e:
        investigation.status = InvestigationStatus.IN_PROGRESS
        db.commit()
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")


@router.post("/{investigation_id}/report", response_model=ReportGenerateResponse)
async def generate_report(
    investigation_id: int,
    report_request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """조사보고서 자동 생성"""
    
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="조사 사건을 찾을 수 없습니다")
    
    # 관련 데이터 수집
    evidence_list = db.query(Evidence).filter(
        Evidence.investigation_id == investigation_id
    ).all()
    
    analysis_results = db.query(AnalysisResult).filter(
        AnalysisResult.investigation_id == investigation_id
    ).all()
    
    # 보고서 생성
    try:
        report = await fire_analysis_service.generate_report(
            investigation_data={
                "case_number": investigation.case_number,
                "title": investigation.title,
                "address": investigation.address,
                "incident_datetime": investigation.incident_datetime.isoformat() if investigation.incident_datetime else None,
                "predicted_cause": investigation.predicted_cause.value if investigation.predicted_cause else None,
                "analysis_summary": investigation.analysis_summary
            },
            evidence_list=[{"id": e.id, "file_name": e.original_file_name} for e in evidence_list],
            analysis_results=[{
                "predicted_cause": ar.predicted_cause.value if ar.predicted_cause else None,
                "cause_confidence": ar.cause_confidence,
                "ignition_point": ar.ignition_point_estimate
            } for ar in analysis_results]
        )
        
        # 보고서 저장
        investigation.final_report = report
        db.commit()
        
        # 감사 로그
        await log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            action="GENERATE_REPORT",
            resource_type="investigation",
            resource_id=str(investigation_id),
            investigation_id=investigation_id
        )
        
        return ReportGenerateResponse(
            investigation_id=investigation_id,
            generated_report=report,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보고서 생성 중 오류: {str(e)}")
