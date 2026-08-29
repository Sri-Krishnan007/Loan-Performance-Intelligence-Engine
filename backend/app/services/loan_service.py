import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)

class LoanDataState:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LoanDataState, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self):
        if self.initialized:
            return
        
        logger.info("Initializing LoanDataState by loading project artifacts...")
        
        # Paths
        static_path = settings.BASE_DIR / "data/synthetic/loan_static_attributes.csv"
        test_path = settings.BASE_DIR / "data/processed/features/test_features.parquet"
        submission_path = settings.BASE_DIR / "outputs/submissions/submission.csv"
        anomaly_reports_path = settings.BASE_DIR / "outputs/anomaly/anomaly_reports.json"
        local_explain_path = settings.BASE_DIR / "outputs/explainability/local_explanations.csv"
        
        # Load DataFrames
        self.static_df = pd.read_csv(static_path)
        self.test_df = pd.read_parquet(test_path)
        self.submission_df = pd.read_csv(submission_path)
        
        # Parse Dates & Cast Types to avoid merge warnings
        self.test_df["reporting_month"] = self.test_df["reporting_month"].astype(str)
        self.submission_df["reporting_month"] = self.submission_df["reporting_month"].astype(str)
        
        # Merge features and predictions
        self.merged_df = pd.merge(
            self.test_df,
            self.submission_df[[
                "loan_id", "reporting_month", "delinquency_probability", 
                "default_probability", "prepayment_probability", "next_state", 
                "exception_type", "anomaly_score", "top_drivers", "action", "confidence"
            ]],
            on=["loan_id", "reporting_month"],
            how="left"
        )
        
        # Merge static fields if not already populated
        static_cols = [c for c in self.static_df.columns if c not in self.merged_df.columns or c == "loan_id"]
        if len(static_cols) > 1:
            self.merged_df = pd.merge(self.merged_df, self.static_df[static_cols], on="loan_id", how="left")
        
        # Define risk_level based on default probability or action
        conditions = [
            (self.merged_df["action"] == "Priority Review") | (self.merged_df["default_probability"] > 0.10),
            (self.merged_df["default_probability"] > 0.02) & (self.merged_df["default_probability"] <= 0.10)
        ]
        choices = ["high", "medium"]
        self.merged_df["risk_level"] = np.select(conditions, choices, default="low")
        
        # Sort values and compile latest months per loan
        self.merged_df = self.merged_df.sort_values("reporting_month")
        self.latest_records = self.merged_df.groupby("loan_id").last().reset_index()
        
        # Index anomaly reports
        self.anomaly_reports = {}
        if anomaly_reports_path.exists():
            with open(anomaly_reports_path, "r", encoding="utf-8") as f:
                reports_list = json.load(f)
                for rep in reports_list:
                    self.anomaly_reports[rep["loan_id"]] = rep
                    
        # Load local explanations
        self.local_explanations = {}
        if local_explain_path.exists():
            local_exp_df = pd.read_csv(local_explain_path)
            latest_local = local_exp_df.sort_values("reporting_month").groupby("loan_id").last().reset_index()
            for _, row in latest_local.iterrows():
                self.local_explanations[row["loan_id"]] = {
                    "positive": str(row["positive_risk_drivers"]),
                    "negative": str(row["negative_risk_drivers"])
                }
                
        self.initialized = True
        logger.info(f"LoanDataState loaded successfully: {len(self.latest_records)} loans, {len(self.merged_df)} historical records.")

loan_state = LoanDataState()
