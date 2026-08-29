from pydantic import BaseModel
from typing import Dict

class RiskPredictionResponse(BaseModel):
    loan_id: str
    delinquency_probability: float
    default_probability: float
    prepayment_probability: float
    next_state: str
    confidence: float
    model_versions: Dict[str, str]
