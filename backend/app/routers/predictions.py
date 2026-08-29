from fastapi import APIRouter
from backend.app.schemas.prediction import RiskPredictionResponse
from backend.app.services.prediction_service import PredictionService

router = APIRouter(prefix="/loans", tags=["Predictions"])

@router.get("/{loan_id}/risk", response_model=RiskPredictionResponse)
def get_loan_risk_prediction(loan_id: str):
    """Retrieves predicted default, delinquency, and prepayment risk probabilities."""
    return PredictionService.get_loan_risk(loan_id)
