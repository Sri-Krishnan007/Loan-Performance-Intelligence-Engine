import logging
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
from src.config import settings

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Detects operational credit anomalies using a hybrid ML & rules engine."""
    
    def __init__(self, contamination: float = 0.02):
        self.contamination = contamination
        self.iso_forest = None
        self.numeric_features = ["original_balance", "current_balance", "interest_rate", "loan_age_months", "days_past_due"]

    def fit_unsupervised(self, df: pd.DataFrame) -> None:
        """Trains an Isolation Forest on key financial and delinquency features."""
        logger.info(f"Training unsupervised Isolation Forest on features: {self.numeric_features}")
        
        # Prepare training data
        X = df[self.numeric_features].copy()
        for col in self.numeric_features:
            X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0.0)
            
        self.iso_forest = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1
        )
        self.iso_forest.fit(X)
        logger.info("Unsupervised Isolation Forest training completed.")

    def compute_ml_scores(self, df: pd.DataFrame) -> np.ndarray:
        """Computes Isolation Forest raw decision scores scaled to [0.0, 1.0] (high is anomalous)."""
        if self.iso_forest is None:
            raise ValueError("Isolation Forest must be fitted first.")
            
        X = df[self.numeric_features].copy()
        for col in self.numeric_features:
            X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0.0)
            
        # decision_function outputs negative values for anomalies, positive for normal
        raw_scores = self.iso_forest.decision_function(X)
        
        # Shift and scale to [0, 1] range where 1 is highly anomalous
        # decision_function range is roughly [-0.5, 0.5]
        ml_scores = 1.0 - (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min() + 1e-7)
        return ml_scores

    def evaluate_rule_anomalies(self, joined_df: pd.DataFrame) -> tuple[np.ndarray, list[list[str]], list[str]]:
        """
        Evaluates discrepancies between primary servicing data and secondary servicer updates.
        Returns:
            - rule_scores: Array of rule discrepancy scores scaled [0.0, 1.0].
            - evidence_list: Detailed validation discrepancy lists.
            - drivers_list: Compact risk drivers string representations.
        """
        logger.info("Evaluating cross-source reconciliation discrepancy rules...")
        
        rule_scores = np.zeros(len(joined_df))
        evidence_list = []
        drivers_list = []
        
        # Temp copy with filled na for comparison
        temp = joined_df.copy()
        for col in ["current_balance", "servicer_current_balance", "days_past_due", "servicer_days_past_due"]:
            if col in temp.columns:
                temp[col] = pd.to_numeric(temp[col], errors="coerce").fillna(0.0)
        
        for idx, row in temp.iterrows():
            evidence = []
            drivers = []
            score = 0.0
            
            # 1. Balance conflict
            if "servicer_current_balance" in row and not pd.isna(joined_df.loc[idx, "servicer_current_balance"]):
                bal_diff = abs(row["current_balance"] - row["servicer_current_balance"])
                if bal_diff > 10.0:  # tolerance threshold
                    evidence.append(f"Balance conflict: Primary={row['current_balance']:.2f}, Servicer={row['servicer_current_balance']:.2f}")
                    drivers.append("balance_conflict")
                    score += 0.40
            
            # 2. DPD conflict
            if "servicer_days_past_due" in row and not pd.isna(joined_df.loc[idx, "servicer_days_past_due"]):
                if row["days_past_due"] != row["servicer_days_past_due"]:
                    evidence.append(f"DPD conflict: Primary={row['days_past_due']}, Servicer={row['servicer_days_past_due']}")
                    drivers.append("dpd_conflict")
                    score += 0.30
                    
            # 3. Status conflict
            if "servicer_status" in row and not pd.isna(joined_df.loc[idx, "servicer_status"]):
                if str(row["current_status"]) != str(row["servicer_status"]):
                    evidence.append(f"Status conflict: Primary='{row['current_status']}', Servicer='{row['servicer_status']}'")
                    drivers.append("status_conflict")
                    score += 0.20
                    
            # 4. Document discrepancy
            if "servicer_document_status" in row and not pd.isna(joined_df.loc[idx, "servicer_document_status"]):
                if str(row["document_status"]) != str(row["servicer_document_status"]):
                    evidence.append(f"Document mismatch: Primary='{row['document_status']}', Servicer='{row['servicer_document_status']}'")
                    drivers.append("document_mismatch")
                    score += 0.10
                    
            # 5. Document missing in primary core
            if str(row.get("document_status", "")) == "Missing":
                evidence.append("Document status is Missing in primary database.")
                drivers.append("missing_document")
                score += 0.15
                
            rule_scores[idx] = min(score, 1.0)
            evidence_list.append(evidence)
            drivers_list.append(";".join(drivers) if drivers else "None")
            
        return rule_scores, evidence_list, drivers_list

    def run_detection(self, primary_df: pd.DataFrame, servicer_df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
        """
        Runs the full hybrid anomaly detection pipeline.
        Returns:
            - output_df: Joined DataFrame containing anomaly scores and explanation fields.
            - reviewer_reports: List of top 20 reviewer-ready anomaly reports.
        """
        logger.info("Running hybrid anomaly detection pipeline...")
        
        # Train Isolation Forest on primary performance dataset
        self.fit_unsupervised(primary_df)
        
        # Merge primary with servicer updates on loan_id and reporting_month
        # Ensure correct datatypes for join keys
        p_df = primary_df.copy()
        s_df = servicer_df.copy()
        p_df["reporting_month"] = pd.to_datetime(p_df["reporting_month"])
        s_df["reporting_month"] = pd.to_datetime(s_df["reporting_month"])
        
        logger.info("Merging datasets for reconciliation audit...")
        joined = pd.merge(p_df, s_df, on=["loan_id", "reporting_month"], suffixes=("_primary", "_servicer"))
        
        # Compute ML scores
        ml_scores = self.compute_ml_scores(joined)
        
        # Compute Rule scores
        rule_scores, evidence, drivers = self.evaluate_rule_anomalies(joined)
        
        # Combined Anomaly Score: 50% ML + 50% Rule discrepancies
        combined_scores = 0.5 * ml_scores + 0.5 * rule_scores
        
        joined["ml_anomaly_score"] = ml_scores
        joined["rule_anomaly_score"] = rule_scores
        joined["anomaly_score"] = combined_scores
        joined["anomaly_evidence"] = [", ".join(ev) if ev else "No discrepancies" for ev in evidence]
        joined["top_drivers"] = drivers
        
        # Map reviewer actions
        actions = []
        for score, drv in zip(combined_scores, drivers):
            if score >= 0.70:
                actions.append("Priority Review")
            elif score >= 0.40 or drv != "None":
                actions.append("Investigate Data")
            else:
                actions.append("No Action")
        joined["action"] = actions
        
        # Sort and extract top 20 anomalies for reviewer ready reports
        top_20 = joined.sort_values("anomaly_score", ascending=False).head(20)
        
        reviewer_reports = []
        for _, row in top_20.iterrows():
            report = {
                "loan_id": str(row["loan_id"]),
                "reporting_month": str(row["reporting_month"].date()) if isinstance(row["reporting_month"], pd.Timestamp) else str(row["reporting_month"]),
                "anomaly_score": float(row["anomaly_score"]),
                "anomaly_type": "Data Reconciliation Discrepancy" if row["rule_anomaly_score"] > 0 else "Statistical Profile Outlier",
                "top_drivers": str(row["top_drivers"]),
                "evidence": str(row["anomaly_evidence"]),
                "recommended_action": str(row["action"])
            }
            reviewer_reports.append(report)
            
        return joined, reviewer_reports
