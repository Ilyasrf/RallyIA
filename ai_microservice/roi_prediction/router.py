import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.database import SessionLocal, Property
from roi_prediction.schemas import (
    ROIPredictionResponse,
    BatchROIRequest,
    BatchROIResponse,
)
from roi_prediction.engine import predict_roi

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict-roi", tags=["ROI Prediction"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ROIPredictionResponse)
def predict_single(
    property_id: int,
    capital: float,
    lock_in_years: int,
    db: Session = Depends(get_db),
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail=f"Property {property_id} not found.")

    result = predict_roi(property, capital, lock_in_years)
    return ROIPredictionResponse(property_id=property.id, **result)


@router.post("/batch", response_model=BatchROIResponse)
def predict_batch(
    request: BatchROIRequest,
    db: Session = Depends(get_db),
):
    properties = db.query(Property).filter(Property.id.in_(request.property_ids)).all()
    if not properties:
        raise HTTPException(status_code=404, detail="No properties found.")

    found_ids = {p.id for p in properties}
    missing = [pid for pid in request.property_ids if pid not in found_ids]
    if missing:
        logger.warning("Properties not found: %s", missing)

    predictions = [
        ROIPredictionResponse(
            property_id=p.id,
            **predict_roi(p, request.capital, request.lock_in_years),
        )
        for p in properties
    ]

    return BatchROIResponse(predictions=predictions)
