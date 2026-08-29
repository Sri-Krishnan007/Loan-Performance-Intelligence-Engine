import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import json
import logging
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from src.config import settings
from src.evaluation.time_split import chronological_split
from src.evaluation.metrics import EvaluationMetrics
from src.evaluation.calibration import ProbabilityCalibrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def tune_improved_binary_model(X_train, y_train, X_val, y_val):
    """Performs a fast grid search to optimize HistGradientBoostingClassifier for a binary target."""
    best_pr_auc = -1.0
    best_model = None
    best_params = {}
    
    # Tuning grid for improved model
    grid = [
        {"learning_rate": 0.05, "max_depth": 4, "max_iter": 100},
        {"learning_rate": 0.08, "max_depth": 5, "max_iter": 120},
        {"learning_rate": 0.1, "max_depth": 6, "max_iter": 150}
    ]
    
    for params in grid:
        model = HistGradientBoostingClassifier(
            learning_rate=params["learning_rate"],
            max_depth=params["max_depth"],
            max_iter=params["max_iter"],
            class_weight="balanced",
            random_state=42
        )
        model.fit(X_train, y_train)
        probs = model.predict_proba(X_val)[:, 1]
        metrics = EvaluationMetrics.calculate_binary_metrics(y_val, probs)
        val_pr_auc = metrics["pr_auc"]
        
        if val_pr_auc > best_pr_auc:
            best_pr_auc = val_pr_auc
            best_model = model
            best_params = params
            
    logger.info(f"Best binary parameters: {best_params} (PR-AUC: {best_pr_auc:.4f})")
    return best_model, best_params

def tune_improved_multiclass_model(X_train, y_train, X_val, y_val):
    """Performs a fast grid search to optimize HistGradientBoostingClassifier for multiclass target."""
    best_macro_f1 = -1.0
    best_model = None
    best_params = {}
    
    # Force class_weight='balanced' for all configurations to prioritize minority classes
    grid = [
        {"learning_rate": 0.05, "max_depth": 4, "max_iter": 100, "class_weight": "balanced"},
        {"learning_rate": 0.08, "max_depth": 5, "max_iter": 120, "class_weight": "balanced"},
        {"learning_rate": 0.05, "max_depth": 5, "max_iter": 120, "class_weight": "balanced"},
        {"learning_rate": 0.08, "max_depth": 5, "max_iter": 100, "class_weight": "balanced"}
    ]
    
    for params in grid:
        model = HistGradientBoostingClassifier(
            learning_rate=params["learning_rate"],
            max_depth=params["max_depth"],
            max_iter=params["max_iter"],
            class_weight=params["class_weight"],
            random_state=42
        )
        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        metrics = EvaluationMetrics.calculate_multiclass_metrics(y_val, preds)
        val_macro_f1 = metrics["macro_f1"]
        
        if val_macro_f1 > best_macro_f1:
            best_macro_f1 = val_macro_f1
            best_model = model
            best_params = params
            
    logger.info(f"Best multiclass parameters: {best_params} (Macro-F1: {best_macro_f1:.4f})")
    return best_model, best_params
    
    for params in grid:
        model = HistGradientBoostingClassifier(
            learning_rate=params["learning_rate"],
            max_depth=params["max_depth"],
            max_iter=params["max_iter"],
            class_weight=params["class_weight"],
            random_state=42
        )
        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        metrics = EvaluationMetrics.calculate_multiclass_metrics(y_val, preds)
        val_macro_f1 = metrics["macro_f1"]
        
        if val_macro_f1 > best_macro_f1:
            best_macro_f1 = val_macro_f1
            best_model = model
            best_params = params
            
    logger.info(f"Best multiclass parameters: {best_params} (Macro-F1: {best_macro_f1:.4f})")
    return best_model, best_params

def format_metrics_table(title, metrics_dict):
    """Helper to format a markdown table comparing models for a binary target."""
    rows = []
    rows.append(f"### {title}")
    rows.append("| Metric | Baseline (Raw) | Baseline (Calibrated) | Improved (Raw) | Improved (Calibrated) |")
    rows.append("|---|---|---|---|---|")
    
    metric_keys = [
        ("ROC-AUC", "roc_auc"),
        ("PR-AUC", "pr_auc"),
        ("Brier Score", "brier_score"),
        ("ECE", "ece"),
        ("F1-Score", "f1_score"),
        ("Recall @ 10% Prec", "recall_at_10_precision"),
        ("Recall @ 20% Prec", "recall_at_20_precision"),
        ("Recall @ 50% Prec", "recall_at_50_precision"),
        ("Recall @ 90% Prec", "recall_at_90_precision"),
    ]
    
    for label, key in metric_keys:
        b_raw = metrics_dict["baseline_raw"][key]
        b_cal = metrics_dict["baseline_calibrated"][key]
        i_raw = metrics_dict["improved_raw"][key]
        i_cal = metrics_dict["improved_calibrated"][key]
        rows.append(f"| **{label}** | {b_raw:.4f} | {b_cal:.4f} | {i_raw:.4f} | {i_cal:.4f} |")
    
    return "\n".join(rows) + "\n\n"

def main():
    logger.info("==================================================")
    logger.info("STARTING PHASE 3: ML MODEL TRAINING & CALIBRATION")
    logger.info("==================================================")
    
    # 1. Load Parquet Train Features
    train_features_path = settings.BASE_DIR / "data/processed/features/train_features.parquet"
    if not train_features_path.exists():
        raise FileNotFoundError(f"Engineered train features not found: {train_features_path}. Run Phase 2 first.")
    
    df = pd.read_parquet(train_features_path)
    
    # Define Feature columns and Target columns
    forbidden_targets = [
        "next_3m_delinquency_flag", "next_6m_delinquency_flag", "next_12m_default_flag", 
        "next_12m_prepayment_flag", "next_state", "exception_required", "exception_type"
    ]
    meta_cols = [
        "loan_id", "reporting_month", "origination_month", 
        "last_updated_at", "source_system", "document_status", 
        "loss_severity_band", "default_flag"
    ]
    feature_cols = [c for c in df.columns if c not in forbidden_targets and c not in meta_cols]
    logger.info(f"Targeting {len(feature_cols)} features for model training.")
    
    # Align categories across the entire dataset before splitting to prevent key mismatch
    for col in feature_cols:
        if isinstance(df[col].dtype, pd.CategoricalDtype) or df[col].dtype == "object":
            df[col] = df[col].astype("category")

    # 2. Chronological Split (Cutoff at 2025-01-01)
    train_df, val_df = chronological_split(df, split_date="2025-01-01")
    
    # Log chronological split diagnostics
    logger.info("--- CHRONOLOGICAL SPLIT DIAGNOSTICS ---")
    logger.info(f"Split date boundary: 2025-01-01")
    logger.info(f"Train Set Size: {train_df.shape[0]} rows (Reporting Months < 2025-01-01)")
    logger.info(f"Validation Set Size: {val_df.shape[0]} rows (Reporting Months >= 2025-01-01)")
    
    targets = {
        "next_3m_delinquency_flag": "Delinquency 3m",
        "next_6m_delinquency_flag": "Delinquency 6m",
        "next_12m_default_flag": "Default 12m",
        "next_12m_prepayment_flag": "Prepayment 12m"
    }
    
    for t_col, label in targets.items():
        tr_rate = train_df[t_col].astype(float).mean()
        val_rate = val_df[t_col].astype(float).mean()
        logger.info(f"Target '{label}' positive class rate: Train={tr_rate:.4%}, Val={val_rate:.4%}")
    logger.info("---------------------------------------")
    
    # Separate input and targets
    X_train = train_df[feature_cols].copy()
    X_val = val_df[feature_cols].copy()
    
    # Encode categoricals as numeric category codes using aligned categories
    for col in feature_cols:
        if isinstance(X_train[col].dtype, pd.CategoricalDtype):
            X_train[col] = X_train[col].cat.codes
            X_val[col] = X_val[col].cat.codes
            
    # Save feature names list to models metadata
    feature_list_path = settings.MODEL_DIR / "metadata/features_list.json"
    feature_list_path.parent.mkdir(parents=True, exist_ok=True)
    with open(feature_list_path, "w", encoding="utf-8") as f:
        json.dump(list(feature_cols), f, indent=2)
        
    metrics_summary = {}
    
    # Process Binary Targets
    binary_joblib_files = {
        "next_3m_delinquency_flag": ("delinquency_3m", "delinquency_3m_model.joblib", "DelinquencyModel_3m"),
        "next_6m_delinquency_flag": ("delinquency_6m", "delinquency_6m_model.joblib", "DelinquencyModel_6m"),
        "next_12m_default_flag": ("default_12m", "default_model.joblib", "DefaultModel"),
        "next_12m_prepayment_flag": ("prepayment_12m", "prepayment_model.joblib", "PrepaymentModel")
    }
    
    for t_col, (key, filename, model_name) in binary_joblib_files.items():
        logger.info(f"\n--- Model Pipeline for: {targets[t_col]} ({t_col}) ---")
        y_train = train_df[t_col].astype(int)
        y_val = val_df[t_col].astype(int)
        
        # 1. Baseline Model
        logger.info(f"Training Baseline Decision Tree for {targets[t_col]}...")
        base_clf = DecisionTreeClassifier(max_depth=3, random_state=42)
        base_clf.fit(X_train, y_train)
        base_raw_probs = base_clf.predict_proba(X_val)[:, 1]
        base_raw_metrics = EvaluationMetrics.calculate_binary_metrics(y_val, base_raw_probs)
        
        logger.info(f"Calibrating Baseline Model...")
        base_calibrator = ProbabilityCalibrator(method="isotonic")
        base_calibrated_clf = base_calibrator.fit_calibration(base_clf, X_val, y_val)
        base_cal_probs = base_calibrated_clf.predict_proba(X_val)[:, 1]
        base_cal_metrics = EvaluationMetrics.calculate_binary_metrics(y_val, base_cal_probs)
        
        # 2. Improved Model
        logger.info(f"Tuning Improved HistGradientBoosting Classifier for {targets[t_col]}...")
        imp_clf, best_params = tune_improved_binary_model(X_train, y_train, X_val, y_val)
        imp_raw_probs = imp_clf.predict_proba(X_val)[:, 1]
        imp_raw_metrics = EvaluationMetrics.calculate_binary_metrics(y_val, imp_raw_probs)
        
        logger.info(f"Calibrating Improved Model...")
        imp_calibrator = ProbabilityCalibrator(method="isotonic")
        imp_calibrated_clf = imp_calibrator.fit_calibration(imp_clf, X_val, y_val)
        imp_cal_probs = imp_calibrated_clf.predict_proba(X_val)[:, 1]
        imp_cal_metrics = EvaluationMetrics.calculate_binary_metrics(y_val, imp_cal_probs)
        
        # Save metrics
        metrics_summary[key] = {
            "baseline_raw": base_raw_metrics,
            "baseline_calibrated": base_cal_metrics,
            "improved_raw": imp_raw_metrics,
            "improved_calibrated": imp_cal_metrics,
            "best_params": best_params
        }
        
        # Export the best model (Tuned & Calibrated HistGradientBoosting)
        joblib_path = settings.MODEL_DIR / f"trained/{filename}"
        logger.info(f"Saving Best Calibrated Improved Model to {joblib_path}")
        joblib.dump({
            "model": imp_calibrated_clf,
            "model_name": model_name,
            "model_version": "2.0_calibrated"
        }, joblib_path)
        
    # --- Multiclass Next State Model ---
    logger.info("\n--- Model Pipeline for: Next State Multiclass (next_state) ---")
    y_train_state = train_df["next_state"].astype(str)
    y_val_state = val_df["next_state"].astype(str)
    
    # 1. Baseline Model
    logger.info("Training Baseline Decision Tree for Next State (balanced)...")
    base_state_clf = DecisionTreeClassifier(max_depth=3, class_weight="balanced", random_state=42)
    base_state_clf.fit(X_train, y_train_state)
    base_state_preds = base_state_clf.predict(X_val)
    base_state_metrics = EvaluationMetrics.calculate_multiclass_metrics(y_val_state, base_state_preds)
    
    # 2. Improved Model
    logger.info("Tuning Improved HistGradientBoosting for Next State...")
    imp_state_clf, best_params_state = tune_improved_multiclass_model(
        X_train, y_train_state, X_val, y_val_state
    )
    imp_state_preds = imp_state_clf.predict(X_val)
    imp_state_metrics = EvaluationMetrics.calculate_multiclass_metrics(y_val_state, imp_state_preds)
    
    metrics_summary["next_state"] = {
        "baseline": base_state_metrics,
        "improved": imp_state_metrics,
        "best_params": best_params_state
    }
    
    state_joblib_path = settings.MODEL_DIR / "trained/next_state_model.joblib"
    logger.info(f"Saving Best Improved Next State Model to {state_joblib_path}")
    joblib.dump({
        "model": imp_state_clf,
        "model_name": "NextStateModel",
        "model_version": "2.0_tuned"
    }, state_joblib_path)
    
    # Save Metrics Summary to JSON file
    metrics_json_path = settings.MODEL_DIR / "metrics/model_performance.json"
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)
    logger.info(f"Metrics saved to {metrics_json_path}")
    
    # Generate Model Performance and Calibration report
    report_path = settings.REPORTS_DIR / "model_metrics.md"
    logger.info(f"Generating detailed comparison report at {report_path}...")
    
    report_content = f"""# Model Performance, Comparison & Calibration Report

This report outlines the comparative analysis between simple baseline models and optimized machine learning models, evaluated out-of-time (OOT) on validation data (Reporting Months >= 2025-01-01).

---

## 1. Chronological Split Diagnostics
* **Validation Split Date**: 2025-01-01
* **Training Panel**: {train_df.shape[0]:,} observations (reporting months < 2025-01-01)
* **Validation Panel**: {val_df.shape[0]:,} observations (reporting months >= 2025-01-01)

### Positive Class Rates (Imbalance Context)
* **Delinquency (3-Month Horizon)**: Train = {train_df['next_3m_delinquency_flag'].astype(float).mean():.4%}, Val = {val_df['next_3m_delinquency_flag'].astype(float).mean():.4%}
* **Delinquency (6-Month Horizon)**: Train = {train_df['next_6m_delinquency_flag'].astype(float).mean():.4%}, Val = {val_df['next_6m_delinquency_flag'].astype(float).mean():.4%}
* **Default (12-Month Horizon)**: Train = {train_df['next_12m_default_flag'].astype(float).mean():.4%}, Val = {val_df['next_12m_default_flag'].astype(float).mean():.4%}
* **Prepayment (12-Month Horizon)**: Train = {train_df['next_12m_prepayment_flag'].astype(float).mean():.4%}, Val = {val_df['next_12m_prepayment_flag'].astype(float).mean():.4%}

---

## 2. Comparative Analysis (Binary Classification Models)

{format_metrics_table("Delinquency 3-Month Projections", metrics_summary["delinquency_3m"])}
{format_metrics_table("Delinquency 6-Month Projections", metrics_summary["delinquency_6m"])}
{format_metrics_table("Default 12-Month Projections", metrics_summary["default_12m"])}
{format_metrics_table("Prepayment 12-Month Projections", metrics_summary["prepayment_12m"])}

---

## 3. Comparative Analysis (Next State Multiclass Predictions)
* **Baseline (Decision Tree) Macro-F1**: {metrics_summary['next_state']['baseline']['macro_f1']:.4f}
* **Improved (Tuned HistGradientBoosting) Macro-F1**: {metrics_summary['next_state']['improved']['macro_f1']:.4f}

### Baseline Next State Confusion Matrix:
"""
    # Baseline Multiclass Confusion Matrix
    report_content += "\n| Actual \\ Predicted | Current | Delinquent | Default | Prepaid |\n|---|---|---|---|---|\n"
    cm_base = metrics_summary['next_state']['baseline']['confusion_matrix']
    for row_label in ["Current", "Delinquent", "Default", "Prepaid"]:
        vals = [cm_base.get(row_label, {}).get(col_label, 0) for col_label in ["Current", "Delinquent", "Default", "Prepaid"]]
        report_content += f"| **{row_label}** | {vals[0]:,} | {vals[1]:,} | {vals[2]:,} | {vals[3]:,} |\n"
        
    report_content += """
### Improved Next State Confusion Matrix:
"""
    # Improved Multiclass Confusion Matrix
    cm_imp = metrics_summary['next_state']['improved']['confusion_matrix']
    report_content += "\n| Actual \\ Predicted | Current | Delinquent | Default | Prepaid |\n|---|---|---|---|---|\n"
    for row_label in ["Current", "Delinquent", "Default", "Prepaid"]:
        vals = [cm_imp.get(row_label, {}).get(col_label, 0) for col_label in ["Current", "Delinquent", "Default", "Prepaid"]]
        report_content += f"| **{row_label}** | {vals[0]:,} | {vals[1]:,} | {vals[2]:,} | {vals[3]:,} |\n"
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    logger.info("==================================================")
    logger.info("PHASE 3 COMPLETE. COMPARATIVE ANALYSIS COMPLETED.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
