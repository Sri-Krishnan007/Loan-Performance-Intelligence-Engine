from pydantic import BaseModel
from typing import Optional, List

class LoanItem(BaseModel):
    loan_id: str
    credit_score_band: str
    ltv_band: str
    dti_band: str
    state: str
    servicer_name: str
    current_status: str
    original_balance: float
    current_balance: float
    days_past_due: int
    vintage: int
    risk_level: str
    anomaly_score: float

class LoanDetails(BaseModel):
    loan_id: str
    original_balance: float
    interest_rate: float
    vintage: int
    credit_score_band: str
    ltv_band: str
    dti_band: str
    state: str
    loan_purpose: str
    occupancy_type: str
    property_type: str
    servicer_name: str
    current_status: str
    current_balance: float
    days_past_due: int
    loan_age_months: int
    remaining_term_months: int
    reporting_month: str
    modification_flag: int

class TimelineRecord(BaseModel):
    reporting_month: str
    current_balance: float
    days_past_due: int
    current_status: str
    interest_rate: float

class TimelineResponse(BaseModel):
    loan_id: str
    timeline: List[TimelineRecord]
