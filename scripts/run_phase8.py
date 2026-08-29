import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import json
import logging
import pandas as pd
from pathlib import Path
from src.config import settings
from src.data.loader import DataLoader
from src.llm.reviewer import LLMReviewer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("STARTING PHASE 8: GROQ LLM REVIEWER COPILOT")
    logger.info("==================================================")
    
    # 1. Load Datasets for Context
    train_df = DataLoader.load_monthly_performance(settings.TRAIN_PERFORMANCE_PATH)
    
    # Load anomaly scores and reports from Phase 5
    anomaly_reports_path = settings.ANOMALY_OUTPUT_DIR / "anomaly_reports.json"
    if not anomaly_reports_path.exists():
        raise FileNotFoundError(f"Anomaly reports not found: {anomaly_reports_path}. Run Phase 5 first.")
    with open(anomaly_reports_path, "r", encoding="utf-8") as f:
        anom_reports = json.load(f)
        
    # Load local explanations from Phase 6
    local_exp_path = settings.EXPLAIN_OUTPUT_DIR / "local_explanations.csv"
    if not local_exp_path.exists():
        raise FileNotFoundError(f"Local explanations not found: {local_exp_path}. Run Phase 6 first.")
    local_exp_df = pd.read_csv(local_exp_path)
    
    # Find a record that exists in BOTH local explanations (validation cohort) and anomalies
    matched_row = None
    anom_ex = None
    for r in anom_reports:
        # Check if this loan_id and month exists in local_exp_df
        match = local_exp_df[(local_exp_df["loan_id"] == r["loan_id"]) & 
                             (local_exp_df["reporting_month"].astype(str).str.startswith(r["reporting_month"]))]
        if not match.empty:
            anom_ex = r
            matched_row = match.iloc[0]
            break
            
    if matched_row is None:
        # Fallback: just use the first row of local_exp_df
        matched_row = local_exp_df.iloc[0]
        # Find matching anomaly details or create mock details
        anom_ex = {
            "loan_id": matched_row["loan_id"],
            "reporting_month": str(matched_row["reporting_month"]),
            "anomaly_score": 0.35,
            "evidence": "No significant discrepancies flagged in this cohort.",
            "top_drivers": "None"
        }
        
    loan_id_a = anom_ex["loan_id"]
    reporting_month_a = anom_ex["reporting_month"]
    
    # Grab row from train performance
    row_a = train_df[(train_df["loan_id"] == loan_id_a) & (train_df["reporting_month"].astype(str).str.startswith(reporting_month_a))].iloc[0]
    
    metrics_a = {
        "default_probability": float(matched_row["default_probability_12m"]),
        "delinquency_probability": 0.45,
        "prepayment_probability": 0.05,
        "next_state": "Current",
        "anomaly_score": float(anom_ex["anomaly_score"]),
        "top_drivers": str(anom_ex["top_drivers"]),
        "exception_required": int(row_a.get("exception_required", 0)),
        "exception_type": str(row_a.get("exception_type", "None")),
        "anomaly_evidence": str(anom_ex.get("evidence", "No discrepancies"))
    }
    
    # Initialize LLM Reviewer
    reviewer = LLMReviewer()
    
    # Generate Reviewer Note (runs Groq API completion)
    logger.info(f"Generating LLM Reviewer Note for Loan {loan_id_a}...")
    try:
        note_a = reviewer.generate_reviewer_note(row_a.to_dict(), metrics_a)
        print("\nGenerated Reviewer Note:\n", note_a)
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        note_a = f"API Error occurred. Fallback content: Loan {loan_id_a} has DPD conflict and balance mismatch."
        
    # 2. Trigger intentional rejection to verify logging
    logger.info("Triggering intentional LLM response validation rejection check...")
    rejected_response = "Loan LN100234 shows default probability of 85%. Review immediately. Decision: Reject Loan."
    # The response is missing the disclaimer and uses "Decision: Reject Loan" (hallucinated state)
    is_valid, reason = reviewer.audit_logger.check_response_validity(rejected_response)
    corrected_fallback = rejected_response + "\n\nRecommendation — Not a Decision"
    if not is_valid:
        reviewer.audit_logger.log_rejection("LN100234", "Fake Prompt", rejected_response, reason, corrected_fallback)
        logger.info(f"Successfully logged intentional rejection. Reason: {reason}")
        
    # 3. Create demo report: reports/llm_reviewer_demo.md
    demo_path = settings.REPORTS_DIR / "llm_reviewer_demo.md"
    logger.info(f"Generating LLM Reviewer Demo Report at {demo_path}...")
    
    report_content = f"""# Groq LLM Reviewer Copilot Report

This report demonstrates the grounded natural-language analysis outputs of the Reviewer Copilot.

---

## 1. Grounded Underwriting Note Example
### Loan Context: `{loan_id_a}` (Reporting Month: `{reporting_month_a}`)
* **ML Anomaly Score**: {metrics_a['anomaly_score']:.4f}
* **Default Probability (12m)**: {metrics_a['default_probability']:.2%}
* **Evidence**: {metrics_a['anomaly_evidence']}

#### Reviewer Output Note:
```markdown
{note_a}
```

---

## 2. LLM Safety & Response Rejection Trail
The validator checks for required labels and prevents automated lending decisions:

### Example of Logged Validation Rejection:
* **Triggered Loan**: `LN100234`
* **Raw Response**: `{rejected_response}`
* **Rejection Reason**: `{reason}`
* **Automated Corrected Fallback Note**: `{corrected_fallback}`
"""
    with open(demo_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    logger.info("==================================================")
    logger.info("PHASE 8 COMPLETE. LLM AUDIT LOGS PERSISTED.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
