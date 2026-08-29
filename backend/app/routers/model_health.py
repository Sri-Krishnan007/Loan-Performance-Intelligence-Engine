from fastapi import APIRouter
from backend.app.schemas.model_health import ModelHealthResponse
from backend.app.services.model_service import ModelService

router = APIRouter(prefix="/model-health", tags=["Model Health"])

@router.get("", response_model=ModelHealthResponse)
def get_model_health_performance():
    """Retrieves standard metrics, versions, and validation parameters for ML models."""
    return ModelService.get_model_health()
