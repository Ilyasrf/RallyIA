import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from shared.database import SessionLocal, Property
from shared.embedding_service import get_embedding
from recommendation.schemas import QuizRequest, RecommendationResponse, PropertyResponse
from risk_assessment.engine import assess_risk
from risk_assessment.schemas import RiskAssessmentResponse as RiskAssessSchema
from roi_prediction.engine import predict_roi
from roi_prediction.schemas import ROIPredictionResponse as ROISchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommend", tags=["Recommendation"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=RecommendationResponse)
def recommend_properties(quiz: QuizRequest, db: Session = Depends(get_db)):
    persona_text = (
        f"Investor seeking: {quiz.goal}. "
        f"Risk tolerance: {quiz.risk_tolerance}. "
        f"Experience level: {quiz.experience}."
    )

    try:
        user_embedding = get_embedding(persona_text)
    except Exception as e:
        logger.exception("Embedding failed")
        raise HTTPException(status_code=500, detail="Embedding failed.")

    try:
        query = (
            select(Property)
            .filter(Property.min_investment <= quiz.capital)
            .filter(Property.lock_in_years <= quiz.lock_in_years)
            .order_by(Property.embedding.cosine_distance(user_embedding))
            .limit(3)
        )

        results = db.execute(query).scalars().all()

        recommendations = []
        for prop in results:
            risk_data = assess_risk(prop, quiz.risk_tolerance, quiz.experience)
            risk_assessment = RiskAssessSchema(property_id=prop.id, **risk_data)

            roi_data = predict_roi(prop, quiz.capital, quiz.lock_in_years)
            roi_prediction = ROISchema(property_id=prop.id, **roi_data)

            recommendations.append(
                PropertyResponse(
                    id=prop.id,
                    title=prop.title,
                    description=prop.description,
                    min_investment=prop.min_investment,
                    lock_in_years=prop.lock_in_years,
                    risk_rating=prop.risk_rating,
                    expected_yield=prop.expected_yield,
                    location=prop.location,
                    property_type=prop.property_type,
                    risk_assessment=risk_assessment,
                    roi_prediction=roi_prediction,
                )
            )

        profile = quiz.model_dump()
        aligned = sum(1 for r in recommendations if r.risk_assessment and r.risk_assessment.user_alignment == "Well-aligned")
        risk_summary = (
            f"Based on your {profile['risk_tolerance']} risk tolerance and "
            f"{profile['experience']} experience, {aligned} of {len(recommendations)} "
            f"recommended properties are well-aligned with your profile."
        )
        market_analysis_context = (
            "The Moroccan real estate market currently shows strong demand "
            "in these sectors, aligning with your specified lock-in period "
            "and capital."
        )

        return RecommendationResponse(
            recommendations=recommendations,
            risk_summary=risk_summary,
            market_analysis_context=market_analysis_context,
        )

    except Exception as e:
        logger.exception("Search failed")
        raise HTTPException(status_code=500, detail="Search failed.")
