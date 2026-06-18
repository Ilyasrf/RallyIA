from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from shared.database import SessionLocal, Property
from shared.embedding_service import get_embedding
from recommendation.schemas import QuizRequest, RecommendationResponse, PropertyResponse

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
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    try:
        query = (
            select(Property)
            .filter(Property.min_investment <= quiz.capital)
            .filter(Property.lock_in_years <= quiz.lock_in_years)
            .order_by(Property.embedding.cosine_distance(user_embedding))
            .limit(3)
        )

        results = db.execute(query).scalars().all()

        recommendations = [
            PropertyResponse(
                id=prop.id,
                title=prop.title,
                description=prop.description,
                min_investment=prop.min_investment,
                lock_in_years=prop.lock_in_years,
                risk_rating=prop.risk_rating,
            )
            for prop in results
        ]

        profile = quiz.model_dump()
        risk_summary = (
            f"Based on your {profile['risk_tolerance']} risk tolerance and "
            f"{profile['experience']} experience, these properties offer a "
            f"balanced approach to your goal of {profile['goal']}."
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
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
