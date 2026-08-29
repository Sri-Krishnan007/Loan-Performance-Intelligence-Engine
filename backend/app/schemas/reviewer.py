from pydantic import BaseModel
from typing import List, Optional

class ReviewerRequest(BaseModel):
    loan_id: str
    tone: Optional[str] = "Standard"

class ReviewerResponse(BaseModel):
    loan_id: str
    summary: str
    recommendation: str
    action: str
    confidence: float
    disclaimer: str = "Recommendation — Not a Decision"
    model: str
    timestamp: str
    evidence: List[str]

class DecisionRequest(BaseModel):
    decision: str
    reviewer_note: str

class DecisionResponse(BaseModel):
    status: str
    loan_id: str
    decision: str
    timestamp: str
