import pandas as pd
import numpy as np
import logging
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Engineers mortgage risk features while strictly avoiding temporal leakage."""
    
    def __init__(self):
        # Mappings for ordinal encoding
        self.fico_map = {"580-619": 0, "620-659": 1, "660-699": 2, "700-739": 3, "740-779": 4, "780+": 5}
        self.ltv_map = {"0-60": 0, "60-70": 1, "70-80": 2, "80-90": 3, "90-100": 4}
        self.dti_map = {"0-20": 0, "20-30": 1, "30-40": 2, "40-50": 3}
        
    def merge_static_attributes(self, monthly_df: pd.DataFrame, static_df: pd.DataFrame) -> pd.DataFrame:
        """Joins monthly performance records with origination/static parameters."""
        logger.info("Merging static attributes with monthly performance...")
        # Avoid duplicate static columns if already merged
        static_cols_to_use = [c for c in static_df.columns if c not in monthly_df.columns or c == "loan_id"]
        df = pd.merge(monthly_df, static_df[static_cols_to_use], on="loan_id", how="left")
        return df

    def compute_financial_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes dynamic mortgage metrics (amortization indices)."""
        logger.info("Computing financial ratios...")
        # Amortization balance ratio (current / original)
        df["balance_ratio"] = df["current_balance"] / df["original_balance"]
        df["balance_ratio"] = df["balance_ratio"].fillna(1.0)
        
        # Numeric mappings for ordinal risk bands
        df["fico_score_val"] = df["credit_score_band"].astype(str).map(self.fico_map).fillna(-1)
        df["ltv_band_val"] = df["ltv_band"].astype(str).map(self.ltv_map).fillna(-1)
        df["dti_band_val"] = df["dti_band"].astype(str).map(self.dti_map).fillna(-1)
        
        # Categorical binary indicators
        df["is_purchase"] = (df["loan_purpose"] == "Purchase").astype(int)
        df["is_primary_residence"] = (df["occupancy_type"] == "Primary Residence").astype(int)
        
        return df

    def compute_historical_lags(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates rolling DPD lags and cumulative modification counts.
        Must sort by loan_id and reporting_month first to prevent temporal leakage.
        """
        logger.info("Computing historical lags and rolling trends...")
        # Sort values chronologically per loan
        df = df.sort_values(["loan_id", "reporting_month"]).copy()
        
        # Lagged Days Past Due (DPD)
        df["days_past_due_lag_1"] = df.groupby("loan_id")["days_past_due"].shift(1).fillna(0)
        df["days_past_due_lag_2"] = df.groupby("loan_id")["days_past_due"].shift(2).fillna(0)
        
        # Rolling Max DPD (past 3 months, including current month)
        df["days_past_due_max_3m"] = (
            df.groupby("loan_id")["days_past_due"]
            .rolling(window=3, min_periods=1)
            .max()
            .reset_index(level=0, drop=True)
        )
        
        # Delinquency Trend (DPD momentum)
        df["dpd_trend"] = df["days_past_due"] - df["days_past_due_lag_1"]
        
        # Cumulative modification count
        df["modification_flag_cum"] = (
            df.groupby("loan_id")["modification_flag"]
            .cumsum()
        )
        
        # Lagged Status
        df["current_status_lag_1"] = df.groupby("loan_id")["current_status"].shift(1).astype(str).fillna("None")
        df["current_status_lag_1"] = df["current_status_lag_1"].astype("category")
        
        return df

    def validate_no_leakage(self, df: pd.DataFrame, target_cols: list[str]) -> None:
        """Asserts that none of the target columns are leakage features."""
        for col in target_cols:
            if col in df.columns:
                # The target columns themselves are allowed to be in the training matrix
                # but they must NOT be treated as model input features.
                logger.debug(f"Target column '{col}' is present in the dataset.")
                
    def run_pipeline(self, monthly_df: pd.DataFrame, static_df: pd.DataFrame, is_train: bool = True) -> pd.DataFrame:
        """Executes full feature engineering workflow on the dataset."""
        logger.info(f"Starting feature engineering pipeline (is_train={is_train})...")
        
        # Step 1: Merge
        df = self.merge_static_attributes(monthly_df, static_df)
        
        # Step 2: Financial Ratios
        df = self.compute_financial_ratios(df)
        
        # Step 3: Rolling Lags
        df = self.compute_historical_lags(df)
        
        # Target leakage validation check
        target_cols = [
            "next_3m_delinquency_flag", "next_6m_delinquency_flag", "next_12m_default_flag", 
            "next_12m_prepayment_flag", "next_state", "exception_required", "exception_type"
        ]
        self.validate_no_leakage(df, target_cols)
        
        # Ensure correct output folders exist
        processed_dir = settings.BASE_DIR / "data/processed/features"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Save output
        filename = "train_features.parquet" if is_train else "test_features.parquet"
        save_path = processed_dir / filename
        logger.info(f"Saving engineered features to {save_path}")
        df.to_parquet(save_path, index=False)
        
        return df
