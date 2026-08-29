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
from src.scenarios.scenario_engine import ScenarioEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("STARTING PHASE 7: MACRO SCENARIO SIMULATION")
    logger.info("==================================================")
    
    # 1. Load Parquet Train Features & Feature names list
    train_features_path = settings.BASE_DIR / "data/processed/features/train_features.parquet"
    df = pd.read_parquet(train_features_path)
    
    feature_list_path = settings.MODEL_DIR / "metadata/features_list.json"
    with open(feature_list_path, "r", encoding="utf-8") as f:
        feature_cols = json.load(f)
        
    # 2. Chronological Split (Validation cohort)
    train_df, val_df = chronological_split(df, split_date="2025-01-01")
    
    # 3. Load Trained Models
    dlq_model = joblib.load(settings.MODEL_DIR / "trained/delinquency_3m_model.joblib")["model"]
    def_model = joblib.load(settings.MODEL_DIR / "trained/default_model.joblib")["model"]
    pre_model = joblib.load(settings.MODEL_DIR / "trained/prepayment_model.joblib")["model"]
    
    # Prep Validation data inputs
    X_val = val_df[feature_cols].copy()
    for col in X_val.columns:
        if isinstance(X_val[col].dtype, pd.CategoricalDtype) or X_val[col].dtype == "object":
            X_val[col] = X_val[col].astype("category").cat.codes
            
    # Generate Base Predictions
    logger.info("Generating baseline probability predictions...")
    base_preds = pd.DataFrame({
        "loan_id": val_df["loan_id"],
        "reporting_month": val_df["reporting_month"],
        "credit_score_band": val_df["credit_score_band"],
        "ltv_band": val_df["ltv_band"],
        "vintage": val_df["vintage"],
        "prob_delinquency_3m": dlq_model.predict_proba(X_val)[:, 1],
        "prob_default_12m": def_model.predict_proba(X_val)[:, 1],
        "prob_prepayment_12m": pre_model.predict_proba(X_val)[:, 1]
    })
    
    # 4. Initialize Scenario Simulation
    engine = ScenarioEngine()
    
    # Run simulations
    logger.info("Simulating scenarios...")
    base_sim = engine.simulate_portfolio(base_preds, "BASE")
    adverse_sim = engine.simulate_portfolio(base_preds, "ADVERSE_CREDIT")
    prepay_sim = engine.simulate_portfolio(base_preds, "HIGH_PREPAYMENT")
    
    # Calculate portfolio averages
    sims = {"BASE": base_sim, "ADVERSE_CREDIT": adverse_sim, "HIGH_PREPAYMENT": prepay_sim}
    summary_records = []
    
    for name, sim in sims.items():
        summary_records.append({
            "scenario_id": name,
            "avg_delinquency_prob": float(sim["prob_delinquency_3m"].mean()),
            "avg_default_prob": float(sim["prob_default_12m"].mean()),
            "avg_prepayment_prob": float(sim["prob_prepayment_12m"].mean())
        })
    summary_df = pd.DataFrame(summary_records)
    
    # Assert logical direction of scenario adjustments
    logger.info("Validating scenario logic constraints...")
    base_default = summary_df[summary_df["scenario_id"] == "BASE"]["avg_default_prob"].values[0]
    adverse_default = summary_df[summary_df["scenario_id"] == "ADVERSE_CREDIT"]["avg_default_prob"].values[0]
    prepay_default = summary_df[summary_df["scenario_id"] == "HIGH_PREPAYMENT"]["avg_default_prob"].values[0]
    
    base_prepay = summary_df[summary_df["scenario_id"] == "BASE"]["avg_prepayment_prob"].values[0]
    prepay_prepay = summary_df[summary_df["scenario_id"] == "HIGH_PREPAYMENT"]["avg_prepayment_prob"].values[0]
    
    if adverse_default <= base_default:
        logger.error("ADVERSE_CREDIT default multiplier check failed.")
        raise ValueError("Adverse default probability must exceed Base default probability.")
    if prepay_prepay <= base_prepay:
        logger.error("HIGH_PREPAYMENT prepayment multiplier check failed.")
        raise ValueError("High Prepayment probability must exceed Base prepayment probability.")
        
    logger.info("Scenario logic constraints check: PASSED.")
    
    # Segment-level impacts (vintage and credit band)
    logger.info("Generating segment-level stress impacts...")
    segments = ["vintage", "credit_score_band"]
    
    base_seg = engine.segment_analysis(base_sim, segments)
    base_seg["scenario_id"] = "BASE"
    
    adverse_seg = engine.segment_analysis(adverse_sim, segments)
    adverse_seg["scenario_id"] = "ADVERSE_CREDIT"
    
    prepay_seg = engine.segment_analysis(prepay_sim, segments)
    prepay_seg["scenario_id"] = "HIGH_PREPAYMENT"
    
    all_segs = pd.concat([base_seg, adverse_seg, prepay_seg])
    
    # 5. Save Outputs
    summary_path = settings.SCENARIO_OUTPUT_DIR / "scenario_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    logger.info(f"Saved scenario summary to {summary_path}")
    
    seg_path = settings.SCENARIO_OUTPUT_DIR / "segment_impacts.csv"
    all_segs.to_csv(seg_path, index=False)
    logger.info(f"Saved segment impacts to {seg_path}")
    
    # 6. Generate reports/scenario_report.md
    report_path = settings.REPORTS_DIR / "scenario_report.md"
    logger.info(f"Generating Scenario Simulation Report at {report_path}...")
    
    report_content = f"""# Portfolio Scenario & Stress Testing Report

This report summarizes projected portfolio risk averages and segment impacts under macroeconomic stress.

---

## 1. Portfolio Stress Projections
Applying scenario adjustments to baseline calibrated predictions:

| Scenario ID | Delinquency (3m) Prob | Default (12m) Prob | Prepayment (12m) Prob |
|---|---|---|---|
| **BASE** | {summary_records[0]['avg_delinquency_prob']:.4%} | {summary_records[0]['avg_default_prob']:.4%} | {summary_records[0]['avg_prepayment_prob']:.4%} |
| **ADVERSE_CREDIT** | {summary_records[1]['avg_delinquency_prob']:.4%} | {summary_records[1]['avg_default_prob']:.4%} | {summary_records[1]['avg_prepayment_prob']:.4%} |
| **HIGH_PREPAYMENT** | {summary_records[2]['avg_delinquency_prob']:.4%} | {summary_records[2]['avg_default_prob']:.4%} | {summary_records[2]['avg_prepayment_prob']:.4%} |

---

## 2. Segment-Level Impact (Adverse vs Base)
Comparison of default rates across credit score bands:

| Credit Score Band | Base Default Prob | Adverse Default Prob | Stress Multiplier |
|---|---|---|---|
"""
    # Filter credit score bands
    base_band = base_seg.groupby("credit_score_band")["prob_default_12m_mean"].mean()
    adverse_band = adverse_seg.groupby("credit_score_band")["prob_default_12m_mean"].mean()
    
    for band in base_band.index:
        b_val = base_band[band]
        a_val = adverse_band[band]
        mult = a_val / b_val if b_val > 0 else 1.0
        report_content += f"| {band} | {b_val:.4%} | {a_val:.4%} | {mult:.2f}x |\n"
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    # Print summary to console
    print("\nPortfolio Projections Summary:")
    print(summary_df.round(5))
    
    logger.info("==================================================")
    logger.info("PHASE 7 COMPLETE. SCENARIO ARTIFACTS PERSISTED.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
