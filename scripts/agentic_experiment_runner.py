import os
import sys
import json
import uuid
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, f1_score

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.config import settings
from backend.app.services.loan_service import loan_state

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def create_mlflow_run(run_name: str, params: dict, metrics: dict):
    """
    Writes a local MLflow file structure under mlruns/ so that the mlflow UI 
    can read it directly, without requiring active mlflow package installation.
    """
    run_uuid = uuid.uuid4().hex
    run_dir = PROJECT_ROOT / f"mlruns/0/{run_uuid}"
    
    # Create directory tree
    (run_dir / "params").mkdir(parents=True, exist_ok=True)
    (run_dir / "metrics").mkdir(parents=True, exist_ok=True)
    (run_dir / "tags").mkdir(parents=True, exist_ok=True)
    
    # 1. Write params
    for k, v in params.items():
        with open(run_dir / "params" / str(k), "w") as f:
            f.write(str(v))
            
    # 2. Write metrics
    for k, v in metrics.items():
        with open(run_dir / "metrics" / str(k), "w") as f:
            f.write(f"{v} 0 0") # MLflow format: <value> <timestamp> <step>
            
    # 3. Write tags
    with open(run_dir / "tags" / "mlflow.runName", "w") as f:
        f.write(run_name)
        
    # 4. Write meta.yaml
    meta = f"""artifact_uri: file:///{run_dir.as_posix()}/artifacts
end_time: 1716912000000
entry_point_name: ''
experiment_id: '0'
lifecycle_stage: active
run_id: {run_uuid}
run_name: {run_name}
run_uuid: {run_uuid}
source_name: scripts/agentic_experiment_runner.py
source_type: 4
start_time: 1716911990000
status: 3
user_id: Sri-Krishnan007
"""
    with open(run_dir / "meta.yaml", "w") as f:
        f.write(meta)
        
    return run_uuid

def run_agentic_tuner():
    """
    Agentic model training runner. Auto-evaluates multiple hyperparameter configs 
    for default models, selects the champion model, and logs everything to MLflow.
    """
    logger.info("Initializing Agentic Model Experiment Runner...")
    
    # Load processed training features parquet
    train_features_path = settings.BASE_DIR / "data/processed/features/train_features.parquet"
    if not train_features_path.exists():
        raise FileNotFoundError(f"Engineered train features not found at {train_features_path}")
        
    df = pd.read_parquet(train_features_path)
    
    # Chronological out-of-time split (Cutoff at 2025-01-01)
    if "reporting_month" in df.columns:
        df["reporting_month"] = df["reporting_month"].astype(str)
        train_df = df[df["reporting_month"] < "2025-01-01"].copy()
        val_df = df[df["reporting_month"] >= "2025-01-01"].copy()
    else:
        total_months = df["month_index"].max()
        split_month = int(total_months * 0.8)
        train_df = df[df["month_index"] <= split_month].copy()
        val_df = df[df["month_index"] > split_month].copy()
    
    feature_cols = [
        "month_index", "loan_age_months", "remaining_term_months", 
        "original_balance", "current_balance", "interest_rate",
        "days_past_due", "modification_flag", "prepayment_flag", "vintage"
    ]
    
    # Make sure all features are numeric floats
    X_train = train_df[feature_cols].copy().astype(float)
    y_train = train_df["next_12m_default_flag"].copy().astype(int)
    X_val = val_df[feature_cols].copy().astype(float)
    y_val = val_df["next_12m_default_flag"].copy().astype(int)
    
    # Hyperparameter search grid configuration
    candidate_configs = [
        {"learning_rate": 0.05, "max_iter": 80, "max_depth": 4},
        {"learning_rate": 0.10, "max_iter": 120, "max_depth": 6},
        {"learning_rate": 0.20, "max_iter": 160, "max_depth": 8}
    ]
    
    champion_config = None
    champion_auc = -1.0
    champion_run_id = None
    
    runs_log = []
    
    # Create experiment metadata file in mlruns root
    exp_dir = PROJECT_ROOT / "mlruns/0"
    exp_dir.mkdir(parents=True, exist_ok=True)
    with open(exp_dir.parent / "meta.yaml", "w") as f:
        f.write("artifact_location: file:///mlruns/0\nexperiment_id: '0'\nlifecycle_stage: active\nname: DefaultRiskModel\n")
        
    for i, config in enumerate(candidate_configs):
        logger.info(f"Evaluating candidate config {i+1}/{len(candidate_configs)}: {config}")
        
        # Train model
        model = HistGradientBoostingClassifier(
            learning_rate=config["learning_rate"],
            max_iter=config["max_iter"],
            max_depth=config["max_depth"],
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # Predict probabilities
        y_pred_probs = model.predict_proba(X_val)[:, 1]
        y_pred = model.predict(X_val)
        
        # Calculate scores
        roc_auc = roc_auc_score(y_val, y_pred_probs)
        f1 = f1_score(y_val, y_pred)
        
        metrics = {
            "roc_auc": float(roc_auc),
            "f1_score": float(f1)
        }
        
        logger.info(f"Candidate {i+1} results: ROC-AUC={roc_auc:.4f}, F1-Score={f1:.4f}")
        
        # Log to MLflow local structure
        run_uuid = create_mlflow_run(f"HistGradientBoosting_Config_{i+1}", config, metrics)
        
        runs_log.append({
            "run_uuid": run_uuid,
            "hyperparameters": config,
            "metrics": metrics
        })
        
        # Check if champion
        if roc_auc > champion_auc:
            champion_auc = roc_auc
            champion_config = config
            champion_run_id = run_uuid
            
    logger.info(f"Agentic selection complete. Champion Configuration: {champion_config} (ROC-AUC={champion_auc:.4f})")
    
    # Save search summaries
    output_path = PROJECT_ROOT / "outputs/experiments/experiment_tracker.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "experiment": "DefaultRiskModel",
            "champion": {
                "run_uuid": champion_run_id,
                "hyperparameters": champion_config,
                "roc_auc": champion_auc
            },
            "all_runs": runs_log
        }, f, indent=2)
        
    logger.info("Agentic experiment tracker output written successfully.")

if __name__ == "__main__":
    run_agentic_tuner()
