"""
검색 및 분석 API 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Investigation, Evidence, AnalysisResult, User, FireCause
from app.models.schemas import (
    CircleToSearchRequest, SimilarCaseResponse, AnalysisRequest
)
from app.services.ai_analysis import fire_analysis_service

router = APIRouter()


@router.post("/circle-to-search")
async def circle_to_search(
    search_request: CircleToSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Circle-to-Search: 이미지 내 특정 영역 검색"""
    
    evidence = db.query(Evidence).filter(
        Evidence.id == search_request.evidence_id
    ).first()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="증거 자료를 찾을 수 없습니다")
    
    # 해당 영역 분석
    focus_area = {
        "center_x": search_request.center_x,
        "center_y": search_request.center_y,
        "radius": search_request.radius
    }
    
    result = await fire_analysis_service.analyze_image(
        image_path=evidence.file_path,
        focus_area=focus_area
    )
    
    # 유사 사례 검색
    similar_cases = await search_similar_cases(
        db=db,
        detected_objects=[obj["class_name"] for obj in result["detected_objects"]],
        predicted_cause=result.get("predicted_cause")
    )
    
    return {
        "focus_area": focus_area,
        "analysis_result": result,
        "similar_cases": similar_cases
    }


async def search_similar_cases(
    db: Session,
    detected_objects: List[str],
    predicted_cause: Optional[FireCause] = None,
    limit: int = 5
) -> List[SimilarCaseResponse]:
    """유사 화재 사례 검색"""
    
    # TODO: 벡터 DB나 더 정교한 유사도 검색 구현
    # 현재는 간단한 키워드 매칭
    
    query = db.query(Investigation).filter(
        Investigation.predicted_cause == predicted_cause
    ) if predicted_cause else db.query(Investigation)
    
    similar_cases = query.filter(
        Investigation.is_report_approved == True
    ).order_by(Investigation.created_at.desc()).limit(limit).all()
    
    results = []
    for case in similar_cases:
        results.append(SimilarCaseResponse(
            id=case.id,
            external_case_id=case.case_number,
            title=case.title,
            incident_date=case.incident_datetime,
            location=case.address,
            fire_cause=case.predicted_cause,
            damage_summary=case.analysis_summary,
            lessons_learned=None,
            similarity_score=0.85  # TODO: 실제 유사도 계산
        ))
    
    return results


@router.get("/similar-cases/{investigation_id}")
async def get_similar_cases(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 조사와 유사한 사례 검색"""
    
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="조사 사건을 찾을 수 없습니다")
    
    # 해당 조사의 분석 결과 가져오기
    analysis_results = db.query(AnalysisResult).filter(
        AnalysisResult.investigation_id == investigation_id
    ).all()
    
    # 모든 감지된 객체 수집
    all_objects = []
    for ar in analysis_results:
        if ar.detected_objects:
            all_objects.extend([obj.get("class_name") for obj in ar.detected_objects])
    
    similar_cases = await search_similar_cases(
        db=db,
        detected_objects=list(set(all_objects)),
        predicted_cause=investigation.predicted_cause
    )
    
    return {
        "investigation_id": investigation_id,
        "similar_cases": similar_cases,
        "total_found": len(similar_cases)
    }


@router.post("/batch-analyze/{investigation_id}")
async def batch_analyze(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """한 조사의 모든 증거 일괄 분석"""
    
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="조사 사건을 찾을 수 없습니다")
    
    evidence_list = db.query(Evidence).filter(
        Evidence.investigation_id == investigation_id,
        Evidence.has_been_analyzed == False
    ).all()
    
    results = []
    for evidence in evidence_list:
        try:
            result = await fire_analysis_service.analyze_image(
                image_path=evidence.file_path
            )
            
            # 결과 저장
            db_analysis = AnalysisResult(
                investigation_id=investigation_id,
                evidence_id=evidence.id,
                analysis_type="batch_yolo",
                result_data=result,
                detected_objects=[obj.model_dump() for obj in result["detected_objects"]],
                predicted_cause=result.get("predicted_cause"),
                processing_time_ms=result["processing_time_ms"],
                model_version=result["model_version"]
            )
            db.add(db_analysis)
            
            evidence.has_been_analyzed = True
            results.append({
                "evidence_id": evidence.id,
                "status": "success",
                "predicted_cause": result.get("predicted_cause")
            })
            
        except Exception as e:
            results.append({
                "evidence_id": evidence.id,
                "status": "failed",
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "investigation_id": investigation_id,
        "total": len(evidence_list),
        "processed": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "results": results
    }
