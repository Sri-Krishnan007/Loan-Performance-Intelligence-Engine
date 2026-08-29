import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import json
import joblib
import logging
import pandas as pd
from pathlib import Path
from src.config import settings
from src.evaluation.time_split import chronological_split
from src.explainability.explain import ModelExplainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("STARTING PHASE 6: GLOBAL & LOCAL EXPLAINABILITY")
    logger.info("==================================================")
    
    # 1. Load Parquet Train Features & Feature names list
    train_features_path = settings.BASE_DIR / "data/processed/features/train_features.parquet"
    if not train_features_path.exists():
        raise FileNotFoundError(f"Engineered train features not found: {train_features_path}. Run Phase 2 first.")
    
    df = pd.read_parquet(train_features_path)
    
    feature_list_path = settings.MODEL_DIR / "metadata/features_list.json"
    with open(feature_list_path, "r", encoding="utf-8") as f:
        feature_cols = json.load(f)
        
    # 2. Chronological Split (Validation cohort)
    train_df, val_df = chronological_split(df, split_date="2025-01-01")
    
    # 3. Load Trained Model Joblib (Default 12m model)
    default_model_path = settings.MODEL_DIR / "trained/default_model.joblib"
    if not default_model_path.exists():
        raise FileNotFoundError(f"Trained default model not found: {default_model_path}. Run Phase 3 first.")
    
    default_model_pack = joblib.load(default_model_path)
    model = default_model_pack["model"] # HistGradientBoosting (calibrated or raw)
    
    # Prep Validation data inputs
    X_val = val_df[feature_cols].copy()
    for col in X_val.columns:
        if isinstance(X_val[col].dtype, pd.CategoricalDtype) or X_val[col].dtype == "object":
            X_val[col] = X_val[col].astype("category").cat.codes
            
    y_val_def = val_df["next_12m_default_flag"].astype(int)
    
    # 4. Global Permutation Importance
    explainer = ModelExplainer(feature_cols)
    global_imp = explainer.get_global_importance(model, X_val, y_val_def, max_samples=1000)
    
    # 5. Local Instance Explanations
    logger.info("Generating local positive and negative risk drivers...")
    local_pos = []
    local_neg = []
    
    # Calculate probabilities
    probs = model.predict_proba(X_val)[:, 1]
    
    # Generate explanations row-by-row on the validation cohort
    for idx, row in val_df.iterrows():
        prob = probs[len(local_pos)] # align index
        pos, neg = explainer.explain_local_instance(row, prob)
        local_pos.append(pos)
        local_neg.append(neg)
        
    explanations_df = pd.DataFrame({
        "loan_id": val_df["loan_id"],
        "reporting_month": val_df["reporting_month"],
        "default_probability_12m": probs,
        "positive_risk_drivers": local_pos,
        "negative_risk_drivers": local_neg
    })
    
    # 6. Save Outputs
    global_output_path = settings.EXPLAIN_OUTPUT_DIR / "global_importances.csv"
    global_imp.to_csv(global_output_path, index=False)
    logger.info(f"Saved global feature importances to {global_output_path}")
    
    local_output_path = settings.EXPLAIN_OUTPUT_DIR / "local_explanations.csv"
    explanations_df.to_csv(local_output_path, index=False)
    logger.info(f"Saved local explanations to {local_output_path}")
    
    # 7. Write reports/explainability_report.md
    report_path = settings.REPORTS_DIR / "explainability_report.md"
    logger.info(f"Generating Explainability Report at {report_path}...")
    
    report_content = f"""# Portfolio Explainability Report

This report outlines global portfolio-level risk drivers and local loan-level explanations.

---

## 1. Global Feature Importance (Top 10 Drivers)
Feature importance is computed using model-agnostic **Permutation Feature Importance** on validation observations.

| Rank | Feature Column | Permutation Importance Mean | Variance Std |
|---|---|---|---|
"""
    for i, (_, row) in enumerate(global_imp.head(10).iterrows()):
        report_content += f"| {i+1} | `{row['feature']}` | {row['importance_mean']:.6f} | {row['importance_std']:.6f} |\n"
        
    report_content += f"""
---

## 2. Local Risk-Driver Analysis
Local explanations are computed for individual loans to map positive (risk-increasing) and negative (risk-reducing) drivers.

### High Default Probability Examples (Top 5 Anomalous Risk Loans)
| Loan ID | Reporting Month | Default Prob (12m) | Positive Drivers | Negative Drivers |
|---|---|---|---|---|
"""
    # Grab top 5 highest risk loans
    high_risk = explanations_df.sort_values("default_probability_12m", ascending=False).head(5)
    for _, row in high_risk.iterrows():
        report_content += f"| {row['loan_id']} | {row['reporting_month'].date() if isinstance(row['reporting_month'], pd.Timestamp) else row['reporting_month']} | {row['default_probability_12m']:.4%} | `{row['positive_risk_drivers']}` | `{row['negative_risk_drivers']}` |\n"
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    # Print results to console
    print("\nTop 5 Global Permutation Feature Importances:")
    print(global_imp.head(5).to_string(index=False))
    
    print("\nLocal Explanation Example (High Default Risk):")
    print(high_risk.head(2).to_string(index=False))
    
    logger.info("==================================================")
    logger.info("PHASE 6 COMPLETE. EXPLAINABILITY DATA PERSISTED.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
