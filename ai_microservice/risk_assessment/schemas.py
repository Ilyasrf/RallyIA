from pydantic import BaseModel
from typing import List, Optional


class RiskBreakdown(BaseModel):
    base_risk: float
    lock_in_penalty: float
    yield_factor: float
    user_alignment: float


class RiskAssessmentResponse(BaseModel):
    property_id: str
    overall_score: float
    risk_level: str
    breakdown: RiskBreakdown
    user_alignment: str
    explanation: str


class BatchRiskRequest(BaseModel):
    property_ids: List[str]
    goal: str
    lock_in_years: int
    risk_tolerance: str
    capital: float
    experience: str


class BatchRiskResponse(BaseModel):
    assessments: List[RiskAssessmentResponse]
