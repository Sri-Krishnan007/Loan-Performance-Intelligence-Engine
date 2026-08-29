from fastapi import APIRouter
from backend.app.schemas.prediction import RiskPredictionResponse, LivePredictionRequest, LivePredictionResponse
from backend.app.services.prediction_service import PredictionService

router = APIRouter(prefix="/loans", tags=["Predictions"])

@router.get("/{loan_id}/risk", response_model=RiskPredictionResponse)
def get_loan_risk_prediction(loan_id: str):
    """Retrieves predicted default, delinquency, and prepayment risk probabilities."""
    return PredictionService.get_loan_risk(loan_id)

@router.post("/predict", response_model=LivePredictionResponse)
def run_live_prediction(payload: LivePredictionRequest):
    """Evaluates custom loan features directly against loaded model binaries for live inference."""
    return PredictionService.predict_live(payload)
