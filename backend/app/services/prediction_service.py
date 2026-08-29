from backend.app.services.loan_service import loan_state
from fastapi import HTTPException
import pandas as pd
import numpy as np
from src.pipeline.scoring import ScoringPipeline
from backend.app.schemas.prediction import LivePredictionRequest

class PredictionService:
    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            cls._pipeline = ScoringPipeline()
        return cls._pipeline

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

    @classmethod
    def predict_live(cls, req: LivePredictionRequest) -> dict:
        """Runs the custom loan profile through loaded model binaries for live inference."""
        pipeline = cls.get_pipeline()
        
        # Map values to bands
        credit_score_band = cls._map_fico(req.fico_score)
        ltv_band = cls._map_ltv(req.ltv)
        dti_band = cls._map_dti(req.dti)
        
        # Mappings for ordinal risk bands
        fico_map = {"580-619": 0, "620-659": 1, "660-699": 2, "700-739": 3, "740-779": 4, "780+": 5}
        ltv_map = {"0-60": 0, "60-70": 1, "70-80": 2, "80-90": 3, "90-100": 4}
        dti_map = {"0-20": 0, "20-30": 1, "30-40": 2, "40-50": 3}
        
        fico_score_val = fico_map.get(credit_score_band, -1)
        ltv_band_val = ltv_map.get(ltv_band, -1)
        dti_band_val = dti_map.get(dti_band, -1)
        
        balance_ratio = req.current_balance / req.original_balance if req.original_balance > 0 else 1.0
        is_purchase = 1 if req.loan_purpose == "Purchase" else 0
        is_primary_residence = 1 if req.occupancy_type == "Primary Residence" else 0
        
        # Aligned category mappings list
        category_mappings = {
            "credit_score_band": ['580-619', '620-659', '660-699', '700-739', '740-779', '780+'],
            "ltv_band": ['0-60', '60-70', '70-80', '80-90', '90-100'],
            "dti_band": ['0-20', '20-30', '30-40', '40-50'],
            "state": ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'],
            "loan_purpose": ['Purchase', 'Refinance'],
            "occupancy_type": ['Investment', 'Primary Residence', 'Second Home'],
            "property_type": ['Condominium', 'Multi Unit', 'Single Family', 'Townhouse'],
            "servicer_name": ['Servicer_A', 'Servicer_B', 'Servicer_C', 'Servicer_D', 'Servicer_E'],
            "current_status": ['Current', 'Default', 'Delinquent', 'Prepaid'],
            "document_status": ['Complete', 'Missing', 'Pending'],
        }

        # Build feature dict
        raw_record = {
            "month_index": 12,
            "loan_age_months": 12,
            "remaining_term_months": 348,
            "original_balance": req.original_balance,
            "current_balance": req.current_balance,
            "interest_rate": req.interest_rate,
            "credit_score_band": credit_score_band,
            "ltv_band": ltv_band,
            "dti_band": dti_band,
            "state": req.state,
            "loan_purpose": req.loan_purpose,
            "occupancy_type": req.occupancy_type,
            "property_type": req.property_type,
            "servicer_name": req.servicer_name,
            "current_status": req.current_status,
            "days_past_due": req.days_past_due,
            "modification_flag": req.modification_flag,
            "prepayment_flag": req.prepayment_flag,
            "vintage": 2024,
            "balance_ratio": balance_ratio,
            "fico_score_val": fico_score_val,
            "ltv_band_val": ltv_band_val,
            "dti_band_val": dti_band_val,
            "is_purchase": is_purchase,
            "is_primary_residence": is_primary_residence,
            "days_past_due_lag_1": req.days_past_due,
            "days_past_due_lag_2": req.days_past_due,
            "days_past_due_max_3m": req.days_past_due,
            "dpd_trend": 0,
            "modification_flag_cum": req.modification_flag,
            "current_status_lag_1": req.current_status
        }
        
        df_row = pd.DataFrame([raw_record])
        df_encoded = df_row.copy()
        
        # Categorical codes conversion
        for col, categories in category_mappings.items():
            val = df_row.loc[0, col]
            if val in categories:
                df_encoded.loc[0, col] = categories.index(val)
            else:
                df_encoded.loc[0, col] = -1
                
        val_lag1 = df_row.loc[0, "current_status_lag_1"]
        if val_lag1 in category_mappings["current_status"]:
            df_encoded.loc[0, "current_status_lag_1"] = category_mappings["current_status"].index(val_lag1)
        else:
            df_encoded.loc[0, "current_status_lag_1"] = -1
            
        X_live = df_encoded[pipeline.feature_cols].copy()
        for col in X_live.columns:
            X_live[col] = pd.to_numeric(X_live[col], errors="coerce").fillna(0)
            
        # Predict delinquency, default, prepayment
        del_prob = float(pipeline.dlq_model.predict_proba(X_live)[0, 1])
        def_prob = float(pipeline.def_model.predict_proba(X_live)[0, 1])
        pre_prob = float(pipeline.pre_model.predict_proba(X_live)[0, 1])
        
        state_probs = pipeline.state_model.predict_proba(X_live)[0]
        pred_state = str(pipeline.state_model.predict(X_live)[0]).upper()
        confidence = float(state_probs.max())
        
        # ML Anomaly score
        numeric_features = ["original_balance", "current_balance", "interest_rate", "loan_age_months", "days_past_due"]
        X_anom = df_encoded[numeric_features].copy()
        for col in numeric_features:
            X_anom[col] = pd.to_numeric(X_anom[col], errors="coerce").fillna(0.0)
            
        raw_ml = float(pipeline.anomaly_model.decision_function(X_anom)[0])
        # scale decision function score roughly from [-0.5, 0.5] to [0, 1]
        ml_score = 1.0 - (raw_ml + 0.5) / 1.0
        ml_score = max(0.0, min(1.0, ml_score))
        
        # Rule reconciliation checks
        reconcile_row = df_row.copy()
        if req.servicer_status is not None:
            reconcile_row["servicer_current_balance"] = req.servicer_current_balance if req.servicer_current_balance is not None else req.current_balance
            reconcile_row["servicer_days_past_due"] = req.servicer_days_past_due if req.servicer_days_past_due is not None else req.days_past_due
            reconcile_row["servicer_document_status"] = req.servicer_document_status if req.servicer_document_status is not None else req.document_status
            reconcile_row["servicer_status"] = req.servicer_status
            
            rule_scores, drivers = pipeline.run_reconciliation_rules(reconcile_row)
            rule_score = float(rule_scores[0])
            driver = str(drivers[0])
        else:
            rule_score = 0.0
            driver = "None"
            
        anomaly_score = 0.5 * ml_score + 0.5 * rule_score
        
        # Map Exception Type
        if req.current_status == "Default":
            exception_type = "Default Review"
        elif req.days_past_due >= 60:
            exception_type = "Severe Delinquency"
        elif req.document_status == "Missing":
            exception_type = "Documentation Gap"
        elif req.modification_flag > 0:
            exception_type = "Loan Modification"
        else:
            exception_type = "None"
            
        # Map Action
        if anomaly_score >= 0.70:
            action = "Priority Review"
        elif anomaly_score >= 0.40 or driver != "None":
            action = "Investigate Data"
        else:
            action = "No Action"
            
        return {
            "delinquency_probability": del_prob,
            "default_probability": def_prob,
            "prepayment_probability": pre_prob,
            "next_state": pred_state,
            "confidence": confidence,
            "anomaly_score": anomaly_score,
            "exception_type": exception_type,
            "action": action,
            "top_drivers": driver
        }

    @staticmethod
    def _map_fico(score: int) -> str:
        if score < 620: return '580-619'
        elif score < 660: return '620-659'
        elif score < 700: return '660-699'
        elif score < 740: return '700-739'
        elif score < 780: return '740-779'
        else: return '780+'

    @staticmethod
    def _map_ltv(ltv: float) -> str:
        if ltv < 60: return '0-60'
        elif ltv < 70: return '60-70'
        elif ltv < 80: return '70-80'
        elif ltv < 90: return '80-90'
        else: return '90-100'

    @staticmethod
    def _map_dti(dti: float) -> str:
        if dti < 20: return '0-20'
        elif dti < 30: return '20-30'
        elif dti < 40: return '30-40'
        else: return '40-50'
