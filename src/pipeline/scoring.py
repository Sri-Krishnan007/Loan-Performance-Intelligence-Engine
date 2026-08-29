import json
import joblib
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from src.config import settings
from src.data.loader import DataLoader

logger = logging.getLogger(__name__)

class ScoringPipeline:
    """Combines all trained models, calibration, anomaly detectors, and rule reconcilers to score portfolios."""
    
    def __init__(self):
        self.feature_cols = None
        self.dlq_model = None
        self.def_model = None
        self.pre_model = None
        self.state_model = None
        self.anomaly_model = None
        self.load_models()

    def load_models(self) -> None:
        """Loads trained predictive and anomaly models from models directory."""
        logger.info("Loading trained models for pipeline execution...")
        
        feature_list_path = settings.MODEL_DIR / "metadata/features_list.json"
        with open(feature_list_path, "r", encoding="utf-8") as f:
            self.feature_cols = json.load(f)
            
        self.dlq_model = joblib.load(settings.MODEL_DIR / "trained/delinquency_3m_model.joblib")["model"]
        self.def_model = joblib.load(settings.MODEL_DIR / "trained/default_model.joblib")["model"]
        self.pre_model = joblib.load(settings.MODEL_DIR / "trained/prepayment_model.joblib")["model"]
        self.state_model = joblib.load(settings.MODEL_DIR / "trained/next_state_model.joblib")["model"]
        self.anomaly_model = joblib.load(settings.MODEL_DIR / "trained/anomaly_model.joblib")
        
        logger.info("All model binaries successfully loaded.")

    def run_reconciliation_rules(self, df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
        """Evaluates operational discrepancies on merged test records."""
        rule_scores = np.zeros(len(df))
        drivers_list = []
        
        temp = df.copy()
        for col in ["current_balance", "servicer_current_balance", "days_past_due", "servicer_days_past_due"]:
            if col in temp.columns:
                temp[col] = pd.to_numeric(temp[col], errors="coerce").fillna(0.0)
                
        for idx, row in temp.iterrows():
            drivers = []
            score = 0.0
            
            # Skip evaluation if no secondary update record matched (no updates available)
            if "servicer_status" not in df.columns or pd.isna(df.loc[idx, "servicer_status"]):
                drivers_list.append("None")
                rule_scores[idx] = 0.0
                continue
                
            # 1. Balance conflict
            if "servicer_current_balance" in row and not pd.isna(df.loc[idx, "servicer_current_balance"]):
                if abs(row["current_balance"] - row["servicer_current_balance"]) > 10.0:
                    drivers.append("balance_conflict")
                    score += 0.40
                    
            # 2. DPD conflict
            if "servicer_days_past_due" in row and not pd.isna(df.loc[idx, "servicer_days_past_due"]):
                if row["days_past_due"] != row["servicer_days_past_due"]:
                    drivers.append("dpd_conflict")
                    score += 0.30
                    
            # 3. Status conflict
            if "servicer_status" in row and not pd.isna(df.loc[idx, "servicer_status"]):
                if str(row["current_status"]) != str(row["servicer_status"]):
                    drivers.append("status_conflict")
                    score += 0.20
                    
            # 4. Document mismatch
            if "servicer_document_status" in row and not pd.isna(df.loc[idx, "servicer_document_status"]):
                if str(row["document_status"]) != str(row["servicer_document_status"]):
                    drivers.append("document_mismatch")
                    score += 0.10
                    
            # 5. Missing Document
            if str(row.get("document_status", "")) == "Missing":
                drivers.append("missing_document")
                score += 0.15
                
            rule_scores[idx] = min(score, 1.0)
            drivers_list.append(";".join(drivers) if drivers else "None")
            
        return rule_scores, drivers_list

    def execute_pipeline(self, test_df: pd.DataFrame, servicer_df: pd.DataFrame) -> pd.DataFrame:
        """Runs the entire end-to-end predictive and anomaly detection pipeline on testing panel."""
        logger.info("Executing pipeline on test partition features...")
        
        # Prepare model inputs
        X_test = test_df[self.feature_cols].copy()
        for col in X_test.columns:
            if isinstance(X_test[col].dtype, pd.CategoricalDtype) or X_test[col].dtype == "object":
                X_test[col] = X_test[col].astype("category").cat.codes
                
        # 1. Predictions
        logger.info("Predicting delinquency, default, and prepayment probabilities...")
        del_prob = self.dlq_model.predict_proba(X_test)[:, 1]
        def_prob = self.def_model.predict_proba(X_test)[:, 1]
        pre_prob = self.pre_model.predict_proba(X_test)[:, 1]
        
        logger.info("Predicting next credit state transition...")
        state_probs = self.state_model.predict_proba(X_test)
        pred_states = self.state_model.predict(X_test)
        
        # Confidence score defined as probability of the predicted class
        confidence = state_probs.max(axis=1)
        
        # 2. Anomaly Scoring
        logger.info("Running Isolation Forest anomaly predictions...")
        numeric_features = ["original_balance", "current_balance", "interest_rate", "loan_age_months", "days_past_due"]
        X_anom = test_df[numeric_features].copy()
        for col in numeric_features:
            X_anom[col] = pd.to_numeric(X_anom[col], errors="coerce").fillna(0.0)
            
        raw_ml = self.anomaly_model.decision_function(X_anom)
        ml_scores = 1.0 - (raw_ml - raw_ml.min()) / (raw_ml.max() - raw_ml.min() + 1e-7)
        
        # 3. Join with Servicer Updates and Run Discrepancy Checks
        logger.info("Performing left join with servicer updates feeds...")
        t_df = test_df.copy()
        s_df = servicer_df.copy()
        t_df["reporting_month"] = pd.to_datetime(t_df["reporting_month"])
        s_df["reporting_month"] = pd.to_datetime(s_df["reporting_month"])
        
        joined = pd.merge(t_df, s_df, on=["loan_id", "reporting_month"], how="left", suffixes=("_primary", "_servicer"))
        
        rule_scores, drivers = self.run_reconciliation_rules(joined)
        
        # Combined Anomaly Score: 50% ML + 50% Rules
        anomaly_scores = 0.5 * ml_scores + 0.5 * rule_scores
        
        # 4. Map Exception Types
        exception_types = []
        for idx, row in joined.iterrows():
            if str(row["current_status"]) == "Default":
                exception_types.append("Default Review")
            elif int(row.get("days_past_due", 0)) >= 60:
                exception_types.append("Severe Delinquency")
            elif str(row.get("document_status", "")) == "Missing" or str(row.get("servicer_document_status", "")) == "Missing":
                exception_types.append("Documentation Gap")
            elif int(row.get("modification_flag", 0)) > 0:
                exception_types.append("Loan Modification")
            else:
                exception_types.append("None")
                
        # 5. Map Actions
        actions = []
        for score, drv in zip(anomaly_scores, drivers):
            if score >= 0.70:
                actions.append("Priority Review")
            elif score >= 0.40 or drv != "None":
                actions.append("Investigate Data")
            else:
                actions.append("No Action")
                
        # 6. Format Submission Columns
        submission = pd.DataFrame({
            "loan_id": test_df["loan_id"],
            "reporting_month": test_df["reporting_month"].astype(str),
            "delinquency_probability": del_prob,
            "default_probability": def_prob,
            "prepayment_probability": pre_prob,
            "next_state": pred_states,
            "exception_type": exception_types,
            "anomaly_score": anomaly_scores,
            "top_drivers": drivers,
            "action": actions,
            "confidence": confidence
        })
        
        logger.info("Pipeline execution completed successfully.")
        return submission
