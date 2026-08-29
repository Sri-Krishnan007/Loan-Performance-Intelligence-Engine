from pydantic import BaseModel
from typing import List, Dict

class ModelHealthItem(BaseModel):
    name: str
    version: str
    roc_auc: float
    pr_auc: float
    f1: float
    brier_score: float
    calibrated: bool
    artifact_available: bool

class ValidationConfig(BaseModel):
    method: str
    train_period: str
    validation_period: str

class ModelHealthResponse(BaseModel):
    models: List[ModelHealthItem]
    validation: ValidationConfig
