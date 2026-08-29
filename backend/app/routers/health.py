from fastapi import APIRouter
from backend.app.schemas.health import HealthResponse
from backend.app.services.model_service import ModelService

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthResponse)
def get_health():
    """Checks the health of the service and availability of trained model artifacts."""
    artifacts = ModelService.get_artifacts_status()
    # If all models are available, status is ok, otherwise warning
    status = "ok" if all(artifacts.values()) else "warning"
    return HealthResponse(
        status=status,
        service="Loan Performance Intelligence Engine",
        version="1.0.0",
        artifacts_available=artifacts
    )
