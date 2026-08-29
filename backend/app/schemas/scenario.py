from pydantic import BaseModel
from typing import List, Dict, Any

class ScenarioRequest(BaseModel):
    scenario: str
    segments: List[str]

class ScenarioResponse(BaseModel):
    scenario: str
    portfolio: Dict[str, float]
    segments: List[Dict[str, Any]]
    drivers: List[Dict[str, Any]]
