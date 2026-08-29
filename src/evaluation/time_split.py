import pandas as pd
import logging

logger = logging.getLogger(__name__)

def chronological_split(df: pd.DataFrame, split_date: str = "2025-01-01") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the monthly loan performance panel chronologically.
    Returns:
        - train_subset: records where reporting_month < split_date
        - val_subset: records where reporting_month >= split_date
    """
    logger.info(f"Spliting dataset chronologically on {split_date}...")
    
    # Ensure reporting_month is datetime
    reporting_month_dt = pd.to_datetime(df["reporting_month"])
    split_date_dt = pd.to_datetime(split_date)
    
    train_mask = reporting_month_dt < split_date_dt
    train_df = df[train_mask].copy()
    val_df = df[~train_mask].copy()
    
    logger.info(f"Splitting completed: Train rows={len(train_df)} (dates < {split_date}), Val rows={len(val_df)} (dates >= {split_date})")
    return train_df, val_df
