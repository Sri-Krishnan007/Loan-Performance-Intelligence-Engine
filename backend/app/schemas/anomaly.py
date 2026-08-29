from pydantic import BaseModel
from typing import List

class AnomalyResponse(BaseModel):
    loan_id: str
    anomaly_score: float
    exception_required: bool
    exception_type: str
    severity: str
    drivers: List[str]
    evidence: List[str]

class AnomalyListItem(BaseModel):
    loan_id: str
    reporting_month: str
    anomaly_score: float
    exception_type: str
    severity: str
    drivers: List[str]
    evidence: List[str]
