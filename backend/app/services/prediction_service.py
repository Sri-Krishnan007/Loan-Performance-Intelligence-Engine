from backend.app.services.loan_service import loan_state
from fastapi import HTTPException

class PredictionService:
    @staticmethod
    def get_loan_risk(loan_id: str) -> dict:
        """Retrieves predictive risk metrics for the latest reporting month of a loan."""
        if not loan_state.initialized:
            loan_state.initialize()
            
        # Get latest record for the loan
        loan_records = loan_state.merged_df[loan_state.merged_df["loan_id"] == loan_id]
        if loan_records.empty:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found.")
            
        latest_record = loan_records.iloc[-1]
        
        return {
            "loan_id": loan_id,
            "delinquency_probability": float(latest_record.get("delinquency_probability", 0.0)),
            "default_probability": float(latest_record.get("default_probability", 0.0)),
            "prepayment_probability": float(latest_record.get("prepayment_probability", 0.0)),
            "next_state": str(latest_record.get("next_state", "Current")).upper(),
            "confidence": float(latest_record.get("confidence", 0.80)),
            "model_versions": {
                "delinquency_3m": "v1.0",
                "delinquency_6m": "v1.0",
                "default_12m": "v1.0",
                "prepayment_12m": "v1.0",
                "next_state": "v1.0"
            }
        }
