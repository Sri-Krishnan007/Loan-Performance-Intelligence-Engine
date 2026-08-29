from pydantic import BaseModel
from typing import List, Dict, Any

class DataQualityResponse(BaseModel):
    batch_quality_score: float
    missingness: List[Dict[str, Any]]
    outliers: List[Dict[str, Any]]
    relationship_breaks: List[Dict[str, Any]]
    drift: List[Dict[str, Any]]
