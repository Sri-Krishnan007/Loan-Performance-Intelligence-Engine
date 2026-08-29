from pydantic import BaseModel
from typing import Dict

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    artifacts_available: Dict[str, bool]
