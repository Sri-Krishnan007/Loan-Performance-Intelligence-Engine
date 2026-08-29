import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import logging
import pandas as pd
from pathlib import Path
from src.config import settings
from src.data.loader import DataLoader
from src.features.feature_engineering import FeatureEngineer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("STARTING PHASE 2: TIME-AWARE FEATURE ENGINEERING")
    logger.info("==================================================")
    
    # 1. Load Datasets
    static_df = DataLoader.load_static_attributes()
    train_df = DataLoader.load_monthly_performance(settings.TRAIN_PERFORMANCE_PATH)
    test_df = DataLoader.load_monthly_performance(settings.TEST_PERFORMANCE_PATH)
    
    # 2. Run Feature Engineering
    fe = FeatureEngineer()
    
    logger.info("Engineering Training Features...")
    train_fe = fe.run_pipeline(train_df, static_df, is_train=True)
    logger.info(f"Train features output: {train_fe.shape[0]} rows, {train_fe.shape[1]} columns.")
    
    logger.info("Engineering Testing Features...")
    test_fe = fe.run_pipeline(test_df, static_df, is_train=False)
    logger.info(f"Test features output: {test_fe.shape[0]} rows, {test_fe.shape[1]} columns.")
    
    # 3. Assertions & Verification
    # Ensure no leakage columns are present in the test set features Parquet
    test_features_path = settings.BASE_DIR / "data/processed/features/test_features.parquet"
    loaded_test_fe = pd.read_parquet(test_features_path)
    
    forbidden_targets = [
        "next_3m_delinquency_flag", "next_6m_delinquency_flag", "next_12m_default_flag", 
        "next_12m_prepayment_flag", "next_state", "exception_required", "exception_type"
    ]
    found_forbidden = [col for col in forbidden_targets if col in loaded_test_fe.columns]
    
    if found_forbidden:
        logger.error(f"LEAKAGE DETECTED! Test features parquet contains forbidden target columns: {found_forbidden}")
        raise ValueError(f"Target leakage in test features: {found_forbidden}")
    else:
        logger.info("leakage check: PASSED. Test features parquet contains zero forbidden target columns.")
        
    # Ensure train and test sets have identical features (excluding target columns)
    train_features_path = settings.BASE_DIR / "data/processed/features/train_features.parquet"
    loaded_train_fe = pd.read_parquet(train_features_path)
    
    train_input_features = set(loaded_train_fe.columns) - set(forbidden_targets)
    test_input_features = set(loaded_test_fe.columns)
    
    only_in_train = train_input_features - test_input_features
    only_in_test = test_input_features - train_input_features
    
    if only_in_train:
        logger.warning(f"Feature mismatch! Columns only in train features: {only_in_train}")
    if only_in_test:
        logger.warning(f"Feature mismatch! Columns only in test features: {only_in_test}")
        
    if not only_in_train and not only_in_test:
        logger.info("Schema compatibility check: PASSED. Train and Test set feature columns align perfectly.")
        
    logger.info("==================================================")
    logger.info("PHASE 2 COMPLETE. ENGINEERED FEATURES PERSISTED.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
