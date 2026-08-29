from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class LocalDrivers(BaseModel):
    positive: List[str]
    negative: List[str]

class ExplanationResponse(BaseModel):
    loan_id: str
    global_features: List[Dict[str, Any]]
    local_drivers: LocalDrivers
    confidence: float
    false_positive_context: Optional[str] = None
    false_negative_context: Optional[str] = None
