import logging
import pandas as pd
from pathlib import Path
from src.config import settings
from src.data.loader import DataLoader
from src.pipeline.scoring import ScoringPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("STARTING PHASE 9: END-TO-END SCORING PIPELINE")
    logger.info("==================================================")
    
    # 1. Load Test Feature Parquet & Servicer Updates Feeds
    test_features_path = settings.BASE_DIR / "data/processed/features/test_features.parquet"
    if not test_features_path.exists():
        raise FileNotFoundError(f"Engineered test features not found: {test_features_path}. Run Phase 2 first.")
        
    test_df = pd.read_parquet(test_features_path)
    logger.info(f"Loaded {len(test_df)} records from test features parquet.")
    
    servicer_df = DataLoader.load_servicer_updates()
    
    # 2. Execute Scoring Pipeline
    pipeline = ScoringPipeline()
    submission_df = pipeline.execute_pipeline(test_df, servicer_df)
    
    # 3. Validation Assertions
    logger.info("Running submission schema and content assertions...")
    
    # Check row count
    expected_rows = len(test_df)
    actual_rows = len(submission_df)
    if expected_rows != actual_rows:
        logger.error(f"Row count mismatch! Expected {expected_rows}, got {actual_rows}")
        raise ValueError("Scored submission row count must exactly match test features row count.")
    else:
        logger.info("Submission row count check: PASSED.")
        
    # Check columns match template
    template_cols = [
        "loan_id", "reporting_month", "delinquency_probability", "default_probability",
        "prepayment_probability", "next_state", "exception_type", "anomaly_score",
        "top_drivers", "action", "confidence"
    ]
    missing_cols = set(template_cols) - set(submission_df.columns)
    if missing_cols:
        logger.error(f"Missing required submission columns: {missing_cols}")
        raise ValueError(f"Submission is missing required columns: {missing_cols}")
    else:
        logger.info("Submission column schema check: PASSED.")
        
    # Force schema column ordering
    submission_df = submission_df[template_cols]
    
    # Clean any accidental NaNs (defensive engineering)
    nan_counts = submission_df.isna().sum()
    logger.info(f"NaN occurrence counts per column:\n{nan_counts}")
    
    submission_df["delinquency_probability"] = submission_df["delinquency_probability"].fillna(0.0)
    submission_df["default_probability"] = submission_df["default_probability"].fillna(0.0)
    submission_df["prepayment_probability"] = submission_df["prepayment_probability"].fillna(0.0)
    submission_df["anomaly_score"] = submission_df["anomaly_score"].fillna(0.0)
    submission_df["confidence"] = submission_df["confidence"].fillna(1.0)
    submission_df["next_state"] = submission_df["next_state"].fillna("Current")
    submission_df["exception_type"] = submission_df["exception_type"].fillna("None")
    submission_df["top_drivers"] = submission_df["top_drivers"].fillna("None")
    submission_df["action"] = submission_df["action"].fillna("No Action")
    
    # 4. Save Scored Output
    submission_output_dir = settings.BASE_DIR / "outputs/submissions"
    submission_output_dir.mkdir(parents=True, exist_ok=True)
    
    submission_csv_path = submission_output_dir / "submission.csv"
    submission_df.to_csv(submission_csv_path, index=False)
    logger.info(f"Saved completed submission pack to {submission_csv_path}")
    
    # Print summary statistics
    print("\nSubmission Summary Stats:")
    print(submission_df.describe().round(5))
    
    print("\nPredicted Class Counts (next_state):")
    print(submission_df["next_state"].value_counts())
    
    print("\nAction Code Counts:")
    print(submission_df["action"].value_counts())
    
    logger.info("==================================================")
    logger.info("PHASE 9 COMPLETE. SCORING DELIVERABLES EXPORTED.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
