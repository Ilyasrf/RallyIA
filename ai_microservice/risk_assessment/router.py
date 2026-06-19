import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.database import SessionLocal, Property
from recommendation.schemas import QuizRequest
from risk_assessment.schemas import (
    RiskAssessmentResponse,
    BatchRiskRequest,
    BatchRiskResponse,
)
from risk_assessment.engine import assess_risk

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assess-risk", tags=["Risk Assessment"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=RiskAssessmentResponse)
def assess_single(
    property_id: int,
    quiz: QuizRequest,
    db: Session = Depends(get_db),
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail=f"Property {property_id} not found.")

    result = assess_risk(property, quiz.risk_tolerance, quiz.experience)
    return RiskAssessmentResponse(property_id=property.id, **result)


@router.post("/batch", response_model=BatchRiskResponse)
def assess_batch(
    request: BatchRiskRequest,
    db: Session = Depends(get_db),
):
    properties = db.query(Property).filter(Property.id.in_(request.property_ids)).all()
    if not properties:
        raise HTTPException(status_code=404, detail="No properties found.")

    found_ids = {p.id for p in properties}
    missing = [pid for pid in request.property_ids if pid not in found_ids]
    if missing:
        logger.warning("Properties not found: %s", missing)

    assessments = [
        RiskAssessmentResponse(
            property_id=p.id,
            **assess_risk(p, request.risk_tolerance, request.experience),
        )
        for p in properties
    ]

    return BatchRiskResponse(assessments=assessments)
