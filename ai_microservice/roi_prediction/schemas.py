from pydantic import BaseModel
from typing import List, Optional


class ROIBreakdown(BaseModel):
    base_yield: float
    location_appreciation: float
    risk_premium: float
    property_type_modifier: float


class ROIPredictionResponse(BaseModel):
    property_id: str
    annual_return_pct: float
    total_return_pct: float
    annual_return_mad: float
    total_return_mad: float
    breakdown: ROIBreakdown
    explanation: str


class BatchROIRequest(BaseModel):
    property_ids: List[str]
    capital: float
    lock_in_years: int


class BatchROIResponse(BaseModel):
    predictions: List[ROIPredictionResponse]
