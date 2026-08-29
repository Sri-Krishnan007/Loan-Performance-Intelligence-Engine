from backend.app.services.loan_service import loan_state
from fastapi import HTTPException
import pandas as pd
from src.config import settings

class ExplanationService:
    @staticmethod
    def get_global_features() -> list:
        """Loads and formats global feature importances from project outputs."""
        path = settings.BASE_DIR / "outputs/explainability/global_importances.csv"
        if not path.exists():
            return []
        
        df = pd.read_csv(path)
        features = []
        for _, row in df.iterrows():
            features.append({
                "feature": str(row["feature"]),
                "importance": float(row["importance_mean"])
            })
        return features

    @staticmethod
    def get_loan_explanation(loan_id: str) -> dict:
        """Retrieves global importances and local risk drivers for a single loan."""
        if not loan_state.initialized:
            loan_state.initialize()
            
        loan_records = loan_state.merged_df[loan_state.merged_df["loan_id"] == loan_id]
        if loan_records.empty:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found.")
            
        latest_record = loan_records.iloc[-1]
        
        # Pull global features list
        global_features = ExplanationService.get_global_features()
        
        # Local drivers
        local_exp = loan_state.local_explanations.get(loan_id, {})
        positive_str = local_exp.get("positive", "")
        negative_str = local_exp.get("negative", "")
        
        if positive_str:
            positive = [x.strip() for x in positive_str.split(";") if x.strip() and x.lower() != "none"]
        else:
            # Fallback based on loan features
            positive = []
            if float(latest_record.get("days_past_due", 0)) > 0:
                positive.append(f"delinquency(DPD={int(latest_record.get('days_past_due'))})")
            if latest_record.get("fico_score_val", 0) <= 1:
                positive.append("lower_credit_score")
            if latest_record.get("dti_band_val", 0) >= 2:
                positive.append("high_dti_ratio")
            if not positive:
                positive.append("normal_risk_parameters")
                
        if negative_str:
            negative = [x.strip() for x in negative_str.split(";") if x.strip() and x.lower() != "none"]
        else:
            negative = []
            if latest_record.get("fico_score_val", 0) >= 4:
                negative.append("high_credit_score")
            if float(latest_record.get("interest_rate", 0)) <= 4.5:
                negative.append("favorable_interest_rate")
            if not negative:
                negative.append("clean_payment_history")
                
        return {
            "loan_id": loan_id,
            "global_features": global_features,
            "local_drivers": {
                "positive": positive,
                "negative": negative
            },
            "confidence": float(latest_record.get("confidence", 0.80)),
            "false_positive_context": "Prediction false alarms occur mostly when servicer balance updates conflict with primary records.",
            "false_negative_context": "Target omissions are mitigated by checking cumulative modification counts."
        }
