from fastapi import APIRouter
from backend.app.schemas.explanation import ExplanationResponse
from backend.app.services.explanation_service import ExplanationService

router = APIRouter(prefix="/loans", tags=["Explainability"])

@router.get("/{loan_id}/explanation", response_model=ExplanationResponse)
def get_loan_risk_explanation(loan_id: str):
    """Retrieves global importance rankings and local risk drivers for a loan."""
    return ExplanationService.get_loan_explanation(loan_id)
