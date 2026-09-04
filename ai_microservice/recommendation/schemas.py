from pydantic import BaseModel
from typing import List, Optional

from risk_assessment.schemas import RiskAssessmentResponse
from roi_prediction.schemas import ROIPredictionResponse


from typing import Literal

class QuizRequest(BaseModel):
    goal: Literal['passive_income', 'capital_appreciation', 'balanced', 'short_term_flip']
    lock_in_years: Literal[1, 3, 5, 7]
    risk_tolerance: Literal['low', 'moderate', 'high']
    capital: float
    experience: Literal['beginner', 'intermediate', 'advanced']


class PropertyResponse(BaseModel):
    id: str
    risk_assessment: Optional[RiskAssessmentResponse] = None
    roi_prediction: Optional[ROIPredictionResponse] = None


class RecommendationResponse(BaseModel):
    recommendations: List[PropertyResponse]
    risk_summary: str
    market_analysis_context: str
