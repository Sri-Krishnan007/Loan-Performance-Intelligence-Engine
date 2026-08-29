import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from src.config import settings
from src.evaluation.time_split import chronological_split
from src.evaluation.metrics import EvaluationMetrics
from src.evaluation.calibration import ProbabilityCalibrator
from src.models.delinquency import DelinquencyModel
from src.models.default import DefaultModel
from src.models.prepayment import PrepaymentModel
from src.models.next_state import NextStateModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("STARTING PHASE 3: ML MODEL TRAINING & CALIBRATION")
    logger.info("==================================================")
    
    # 1. Load Parquet Train Features
    train_features_path = settings.BASE_DIR / "data/processed/features/train_features.parquet"
    if not train_features_path.exists():
        raise FileNotFoundError(f"Engineered train features not found: {train_features_path}. Run Phase 2 first.")
    
    df = pd.read_parquet(train_features_path)
    
    # 2. Chronological Split (Cutoff at 2025-01-01)
    train_df, val_df = chronological_split(df, split_date="2025-01-01")
    
    # Define Feature columns and Target columns
    forbidden_targets = [
        "next_3m_delinquency_flag", "next_6m_delinquency_flag", "next_12m_default_flag", 
        "next_12m_prepayment_flag", "next_state", "exception_required", "exception_type"
    ]
    meta_cols = [
        "loan_id", "reporting_month", "origination_month", 
        "last_updated_at", "source_system", "document_status", 
        "current_status", "loss_severity_band", "default_flag", "prepayment_flag",
        "modification_flag"
    ]
    feature_cols = [c for c in df.columns if c not in forbidden_targets and c not in meta_cols]
    logger.info(f"Targeting {len(feature_cols)} features for model training.")
    
    # Separate input and targets
    X_train = train_df[feature_cols].copy()
    X_val = val_df[feature_cols].copy()
    
    # Encode categoricals as numeric category codes
    for col in X_train.columns:
        if isinstance(X_train[col].dtype, pd.CategoricalDtype) or X_train[col].dtype == "object":
            X_train[col] = X_train[col].astype("category").cat.codes
            X_val[col] = X_val[col].astype("category").cat.codes
            
    # Save feature names list to models metadata
    feature_list_path = settings.MODEL_DIR / "metadata/features_list.json"
    feature_list_path.parent.mkdir(parents=True, exist_ok=True)
    with open(feature_list_path, "w", encoding="utf-8") as f:
        json.dump(list(feature_cols), f, indent=2)
        
    metrics_summary = {}

    # --- MODEL 1: Delinquency 3m ---
    y_train_dlq3 = train_df["next_3m_delinquency_flag"].astype(int)
    y_val_dlq3 = val_df["next_3m_delinquency_flag"].astype(int)
    
    dlq3_model = DelinquencyModel(horizon_months=3)
    dlq3_model.fit(X_train, y_train_dlq3)
    
    # Evaluate raw
    raw_probs = dlq3_model.predict_proba(X_val)[:, 1]
    raw_metrics = EvaluationMetrics.calculate_binary_metrics(y_val_dlq3, raw_probs)
    
    # Calibrate
    calibrator_dlq3 = ProbabilityCalibrator(method="isotonic")
    calibrated_model = calibrator_dlq3.fit_calibration(dlq3_model.model, X_val, y_val_dlq3)
    cal_probs = calibrated_model.predict_proba(X_val)[:, 1]
    cal_metrics = EvaluationMetrics.calculate_binary_metrics(y_val_dlq3, cal_probs)
    
    metrics_summary["delinquency_3m"] = {"raw": raw_metrics, "calibrated": cal_metrics}
    dlq3_model.model = calibrated_model  # save the calibrated model
    dlq3_model.save(settings.MODEL_DIR / "trained/delinquency_3m_model.joblib")

    # --- MODEL 2: Delinquency 6m ---
    y_train_dlq6 = train_df["next_6m_delinquency_flag"].astype(int)
    y_val_dlq6 = val_df["next_6m_delinquency_flag"].astype(int)
    
    dlq6_model = DelinquencyModel(horizon_months=6)
    dlq6_model.fit(X_train, y_train_dlq6)
    
    raw_probs = dlq6_model.predict_proba(X_val)[:, 1]
    raw_metrics = EvaluationMetrics.calculate_binary_metrics(y_val_dlq6, raw_probs)
    
    calibrator_dlq6 = ProbabilityCalibrator(method="isotonic")
    calibrated_model = calibrator_dlq6.fit_calibration(dlq6_model.model, X_val, y_val_dlq6)
    cal_probs = calibrated_model.predict_proba(X_val)[:, 1]
    cal_metrics = EvaluationMetrics.calculate_binary_metrics(y_val_dlq6, cal_probs)
    
    metrics_summary["delinquency_6m"] = {"raw": raw_metrics, "calibrated": cal_metrics}
    dlq6_model.model = calibrated_model
    dlq6_model.save(settings.MODEL_DIR / "trained/delinquency_6m_model.joblib")

    # --- MODEL 3: Default 12m ---
    y_train_def = train_df["next_12m_default_flag"].astype(int)
    y_val_def = val_df["next_12m_default_flag"].astype(int)
    
    def_model = DefaultModel()
    def_model.fit(X_train, y_train_def)
    
    raw_probs = def_model.predict_proba(X_val)[:, 1]
    raw_metrics = EvaluationMetrics.calculate_binary_metrics(y_val_def, raw_probs)
    
    calibrator_def = ProbabilityCalibrator(method="isotonic")
    calibrated_model = calibrator_def.fit_calibration(def_model.model, X_val, y_val_def)
    cal_probs = calibrated_model.predict_proba(X_val)[:, 1]
    cal_metrics = EvaluationMetrics.calculate_binary_metrics(y_val_def, cal_probs)
    
    metrics_summary["default_12m"] = {"raw": raw_metrics, "calibrated": cal_metrics}
    def_model.model = calibrated_model
    def_model.save(settings.MODEL_DIR / "trained/default_model.joblib")

    # --- MODEL 4: Prepayment 12m ---
    y_train_pre = train_df["next_12m_prepayment_flag"].astype(int)
    y_val_pre = val_df["next_12m_prepayment_flag"].astype(int)
    
    pre_model = PrepaymentModel()
    pre_model.fit(X_train, y_train_pre)
    
    raw_probs = pre_model.predict_proba(X_val)[:, 1]
    raw_metrics = EvaluationMetrics.calculate_binary_metrics(y_val_pre, raw_probs)
    
    calibrator_pre = ProbabilityCalibrator(method="isotonic")
    calibrated_model = calibrator_pre.fit_calibration(pre_model.model, X_val, y_val_pre)
    cal_probs = calibrated_model.predict_proba(X_val)[:, 1]
    cal_metrics = EvaluationMetrics.calculate_binary_metrics(y_val_pre, cal_probs)
    
    metrics_summary["prepayment_12m"] = {"raw": raw_metrics, "calibrated": cal_metrics}
    pre_model.model = calibrated_model
    pre_model.save(settings.MODEL_DIR / "trained/prepayment_model.joblib")

    # --- MODEL 5: Next State Multiclass ---
    y_train_state = train_df["next_state"].astype(str)
    y_val_state = val_df["next_state"].astype(str)
    
    state_model = NextStateModel()
    state_model.fit(X_train, y_train_state)
    
    pred_states = state_model.predict(X_val)
    state_metrics = EvaluationMetrics.calculate_multiclass_metrics(y_val_state, pred_states)
    
    metrics_summary["next_state"] = state_metrics
    state_model.save(settings.MODEL_DIR / "trained/next_state_model.joblib")

    # 4. Save Metrics Summary
    with open(settings.MODEL_DIR / "metrics/model_performance.json", "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)
        
    # 5. Write reports/model_metrics.md
    report_path = settings.REPORTS_DIR / "model_metrics.md"
    logger.info(f"Generating Model Performance report at {report_path}...")
    
    report_content = f"""# Model Performance & Calibration Report

This report outlines the performance and calibration of the delinquency, default, prepayment, and multiclass next-state models, evaluated out-of-time (OOT) on validation data (Jan 2025 – Jul 2026).

---

## 1. Delinquency Projections (3-Month Horizon)
* **Raw Model**:
  * ROC-AUC: {metrics_summary['delinquency_3m']['raw']['roc_auc']:.4f}
  * PR-AUC: {metrics_summary['delinquency_3m']['raw']['pr_auc']:.4f}
  * Brier Score: {metrics_summary['delinquency_3m']['raw']['brier_score']:.4f}
* **Calibrated Model**:
  * ROC-AUC: {metrics_summary['delinquency_3m']['calibrated']['roc_auc']:.4f}
  * PR-AUC: {metrics_summary['delinquency_3m']['calibrated']['pr_auc']:.4f}
  * Brier Score: {metrics_summary['delinquency_3m']['calibrated']['brier_score']:.4f} (Probability quality)

---

## 2. Delinquency Projections (6-Month Horizon)
* **Raw Model**:
  * ROC-AUC: {metrics_summary['delinquency_6m']['raw']['roc_auc']:.4f}
  * Brier Score: {metrics_summary['delinquency_6m']['raw']['brier_score']:.4f}
* **Calibrated Model**:
  * ROC-AUC: {metrics_summary['delinquency_6m']['calibrated']['roc_auc']:.4f}
  * Brier Score: {metrics_summary['delinquency_6m']['calibrated']['brier_score']:.4f}

---

## 3. Default Projections (12-Month Horizon)
* **Raw Model**:
  * ROC-AUC: {metrics_summary['default_12m']['raw']['roc_auc']:.4f}
  * Brier Score: {metrics_summary['default_12m']['raw']['brier_score']:.4f}
* **Calibrated Model**:
  * ROC-AUC: {metrics_summary['default_12m']['calibrated']['roc_auc']:.4f}
  * Brier Score: {metrics_summary['default_12m']['calibrated']['brier_score']:.4f}

---

## 4. Prepayment Projections (12-Month Horizon)
* **Raw Model**:
  * ROC-AUC: {metrics_summary['prepayment_12m']['raw']['roc_auc']:.4f}
  * Brier Score: {metrics_summary['prepayment_12m']['raw']['brier_score']:.4f}
* **Calibrated Model**:
  * ROC-AUC: {metrics_summary['prepayment_12m']['calibrated']['roc_auc']:.4f}
  * Brier Score: {metrics_summary['prepayment_12m']['calibrated']['brier_score']:.4f}

---

## 5. Next State Multiclass Model (Month t+1)
* **Macro F1-Score**: {metrics_summary['next_state']['macro_f1']:.4f}
* **Next State Confusion Matrix**:
"""
    # Write multiclass matrix
    report_content += "\n| Actual \\ Predicted | Current | Delinquent | Default | Prepaid |\n|---|---|---|---|---|\n"
    cm = metrics_summary['next_state']['confusion_matrix']
    for row_label in ["Current", "Delinquent", "Default", "Prepaid"]:
        vals = [cm.get(row_label, {}).get(col_label, 0) for col_label in ["Current", "Delinquent", "Default", "Prepaid"]]
        report_content += f"| **{row_label}** | {vals[0]:,} | {vals[1]:,} | {vals[2]:,} | {vals[3]:,} |\n"
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    logger.info("==================================================")
    logger.info("PHASE 3 COMPLETE. MODELS TRAINED & PERSISTED.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
