from pydantic import BaseModel
from typing import Dict, Optional

class RiskPredictionResponse(BaseModel):
    loan_id: str
    delinquency_probability: float
    default_probability: float
    prepayment_probability: float
    next_state: str
    confidence: float
    model_versions: Dict[str, str]

class LivePredictionRequest(BaseModel):
    fico_score: int
    ltv: float
    dti: float
    original_balance: float
    current_balance: float
    interest_rate: float
    days_past_due: int
    document_status: str
    state: str
    loan_purpose: str
    occupancy_type: str
    property_type: str
    servicer_name: str
    current_status: str
    modification_flag: int
    prepayment_flag: int
    servicer_current_balance: Optional[float] = None
    servicer_days_past_due: Optional[int] = None
    servicer_document_status: Optional[str] = None
    servicer_status: Optional[str] = None

class LivePredictionResponse(BaseModel):
    delinquency_probability: float
    default_probability: float
    prepayment_probability: float
    next_state: str
    confidence: float
    anomaly_score: float
    exception_type: str
    action: str
    top_drivers: str
