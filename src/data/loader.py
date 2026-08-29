import pandas as pd
import logging
from pathlib import Path
from src.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class DataLoader:
    """Loads and standardizes mortgage loan and performance datasets."""
    
    @staticmethod
    def load_static_attributes(path: Path = settings.STATIC_ATTRIBUTES_PATH) -> pd.DataFrame:
        """Loads loan origination parameters and static attributes."""
        logger.info(f"Loading static attributes from {path}")
        if not path.exists():
            raise FileNotFoundError(f"Static attributes file not found: {path}")
        
        df = pd.read_csv(path)
        
        # Parse origination date
        df["origination_month"] = pd.to_datetime(df["origination_month"])
        
        # Cast categorical columns
        cat_cols = [
            "credit_score_band", "ltv_band", "dti_band", "state", 
            "loan_purpose", "occupancy_type", "property_type", "servicer_name"
        ]
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].astype("category")
                
        # Numeric conversions
        df["original_balance"] = pd.to_numeric(df["original_balance"], errors="coerce")
        df["interest_rate"] = pd.to_numeric(df["interest_rate"], errors="coerce")
        df["vintage"] = pd.to_numeric(df["vintage"], errors="coerce").astype("Int64")
        
        logger.info(f"Successfully loaded {len(df)} static attributes records.")
        return df

    @staticmethod
    def load_monthly_performance(path: Path) -> pd.DataFrame:
        """Loads training or testing monthly performance panels."""
        logger.info(f"Loading monthly performance records from {path}")
        if not path.exists():
            raise FileNotFoundError(f"Performance file not found: {path}")
        
        df = pd.read_csv(path)
        
        # Parse date columns
        date_cols = ["reporting_month", "origination_month"]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        if "last_updated_at" in df.columns:
            df["last_updated_at"] = pd.to_datetime(df["last_updated_at"])
            
        # Cast categorical columns
        cat_cols = [
            "current_status", "loss_severity_band", "source_system", 
            "document_status", "credit_score_band", "ltv_band", "dti_band", 
            "state", "loan_purpose", "occupancy_type", "property_type", "servicer_name"
        ]
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].astype("category")
                
        # Numeric conversions
        numeric_cols = [
            "month_index", "loan_age_months", "remaining_term_months", 
            "original_balance", "current_balance", "interest_rate", "days_past_due"
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                
        # Binary conversions
        binary_cols = ["modification_flag", "prepayment_flag", "default_flag", "exception_required"]
        for col in binary_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                
        logger.info(f"Successfully loaded {len(df)} performance records.")
        return df

    @staticmethod
    def load_servicer_updates(path: Path = settings.SERVICER_UPDATES_PATH) -> pd.DataFrame:
        """Loads the secondary servicer updates reconciliation feed."""
        logger.info(f"Loading servicer updates from {path}")
        if not path.exists():
            raise FileNotFoundError(f"Servicer updates file not found: {path}")
        
        df = pd.read_csv(path)
        
        # Parse dates
        date_cols = ["reporting_month", "last_updated_at", "record_received_at"]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
                
        # Cast categoricals
        cat_cols = ["servicer_name", "servicer_update_type", "servicer_status", "servicer_document_status", "source_system"]
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].astype("category")
                
        # Numeric
        df["servicer_current_balance"] = pd.to_numeric(df["servicer_current_balance"], errors="coerce")
        df["servicer_days_past_due"] = pd.to_numeric(df["servicer_days_past_due"], errors="coerce")
        if "servicer_modification_flag" in df.columns:
            df["servicer_modification_flag"] = pd.to_numeric(df["servicer_modification_flag"], errors="coerce").astype("Int64")
            
        logger.info(f"Successfully loaded {len(df)} servicer updates records.")
        return df
