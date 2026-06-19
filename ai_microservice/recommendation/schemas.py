from pydantic import BaseModel
from typing import List, Optional

from risk_assessment.schemas import RiskAssessmentResponse
from roi_prediction.schemas import ROIPredictionResponse


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
    expected_yield: Optional[float] = None
    location: Optional[str] = None
    property_type: Optional[str] = None
    risk_assessment: Optional[RiskAssessmentResponse] = None
    roi_prediction: Optional[ROIPredictionResponse] = None


class RecommendationResponse(BaseModel):
    recommendations: List[PropertyResponse]
    risk_summary: str
    market_analysis_context: str
