import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import logging
import pandas as pd
import numpy as np
from src.config import settings
from src.data.loader import DataLoader
from src.models.survival import TransitionSurvivalModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("STARTING PHASE 4: SURVIVAL & TRANSITION MODELING")
    logger.info("==================================================")
    
    # 1. Load Train Dataset
    train_df = DataLoader.load_monthly_performance(settings.TRAIN_PERFORMANCE_PATH)
    
    # 2. Run Modeling
    survival_model = TransitionSurvivalModel()
    
    # Calculate transition matrix
    prob_matrix = survival_model.calculate_transition_matrix(train_df)
    
    # Validate transition matrix
    row_sums = prob_matrix.sum(axis=1)
    logger.info(f"Row sums checks:\n{row_sums}")
    
    row_sums_check = np.allclose(row_sums, 1.0, atol=1e-7)
    if not row_sums_check:
        logger.error("TRANSITION MATRIX VALIDATION FAILED! Row sums are not 1.0.")
        raise ValueError("Transition matrix row sums must equal 1.0.")
    else:
        logger.info("Transition matrix row sums check: PASSED. All rows sum to 1.0.")
        
    # Estimate competing risk hazard curves
    hazard_df = survival_model.estimate_hazard_curves(train_df, max_age=60)
    
    # 3. Save Artifacts
    survival_model.save(settings.MODEL_OUTPUT_DIR)
    
    # Print results
    print("\nEmpirical Transition Probability Matrix:")
    print(prob_matrix.round(4))
    
    print("\nHazard Curves Summary (First 10 months):")
    print(hazard_df.head(10).round(5))
    
    # Save the output matrices directly to the models subdirectory
    trained_model_dir = settings.BASE_DIR / "models/trained"
    trained_model_dir.mkdir(parents=True, exist_ok=True)
    prob_matrix.to_csv(trained_model_dir / "transition_matrix.csv")
    hazard_df.to_csv(trained_model_dir / "hazard_curves.csv", index=False)
    
    logger.info("==================================================")
    logger.info("PHASE 4 COMPLETE. SURVIVAL ARTIFACTS PERSISTED.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
