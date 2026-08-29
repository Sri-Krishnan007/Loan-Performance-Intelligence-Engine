from pydantic import BaseModel
from typing import List, Dict, Any

class OverviewResponse(BaseModel):
    total_loans: int
    high_risk_loans: int
    anomalies: int
    default_rate: float
    delinquency_rate: float
    prepayment_rate: float
    risk_distribution: List[Dict[str, Any]]
    status_distribution: List[Dict[str, Any]]
    monthly_trends: List[Dict[str, Any]]
