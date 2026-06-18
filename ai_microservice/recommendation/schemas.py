from pydantic import BaseModel
from typing import List


class QuizRequest(BaseModel):
    goal: str
    lock_in_years: int
    risk_tolerance: str
    capital: float
    experience: str


class PropertyResponse(BaseModel):
    id: int
    title: str
    description: str
    min_investment: float
    lock_in_years: int
    risk_rating: str


class RecommendationResponse(BaseModel):
    recommendations: List[PropertyResponse]
    risk_summary: str
    market_analysis_context: str
