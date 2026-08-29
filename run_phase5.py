import json
import logging
import pandas as pd
from pathlib import Path
from src.config import settings
from src.data.loader import DataLoader
from src.anomaly.detector import AnomalyDetector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("STARTING PHASE 5: ANOMALY & EXCEPTION DETECTION")
    logger.info("==================================================")
    
    # 1. Load Datasets
    train_df = DataLoader.load_monthly_performance(settings.TRAIN_PERFORMANCE_PATH)
    servicer_df = DataLoader.load_servicer_updates()
    
    # 2. Run Anomaly Detection
    detector = AnomalyDetector()
    output_df, reports = detector.run_detection(train_df, servicer_df)
    
    # 3. Validation Checks
    logger.info(f"Anomaly detection output shape: {output_df.shape}")
    logger.info(f"Reviewer anomaly reports count: {len(reports)}")
    
    if len(reports) < 20:
        logger.error(f"Fewer than 20 anomaly reports generated: {len(reports)}")
        raise ValueError("Must generate at least 20 reviewer-ready anomaly examples.")
    else:
        logger.info("Anomaly report count check: PASSED. Generated 20 reviewer examples.")
        
    # Save the Isolation Forest model binary
    trained_model_dir = settings.BASE_DIR / "models/trained"
    trained_model_dir.mkdir(parents=True, exist_ok=True)
    import joblib
    joblib.dump(detector.iso_forest, trained_model_dir / "anomaly_model.joblib")
    logger.info(f"Saved Isolation Forest model to {trained_model_dir / 'anomaly_model.joblib'}")

    # 4. Save Outputs
    output_scores_path = settings.ANOMALY_OUTPUT_DIR / "anomaly_scores.csv"
    output_df[["loan_id", "reporting_month", "ml_anomaly_score", "rule_anomaly_score", "anomaly_score", "top_drivers", "action"]].to_csv(output_scores_path, index=False)
    logger.info(f"Saved anomaly scores to {output_scores_path}")
    
    output_reports_path = settings.ANOMALY_OUTPUT_DIR / "anomaly_reports.json"
    with open(output_reports_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)
    logger.info(f"Saved reviewer reports to {output_reports_path}")
    
    # 5. Generate reports/anomaly_report.md
    report_path = settings.REPORTS_DIR / "anomaly_report.md"
    logger.info(f"Generating Anomaly Report at {report_path}...")
    
    report_content = f"""# Portfolio Anomaly & Operational Exception Report

This report summarizes anomalies, operational document gaps, and reconciliation conflicts identified in the servicing feeds.

---

## 1. Summary Statistics
* **Total Audited Records**: {len(output_df):,}
* **Flagged Priority Review Count (Score $\ge$ 0.70)**: {len(output_df[output_df['anomaly_score'] >= 0.70]):,} ({len(output_df[output_df['anomaly_score'] >= 0.70])/len(output_df):.2%})
* **Flagged Investigate Data Count (0.40 $\le$ Score < 0.70)**: {len(output_df[(output_df['anomaly_score'] >= 0.40) & (output_df['anomaly_score'] < 0.70)]):,} ({len(output_df[(output_df['anomaly_score'] >= 0.40) & (output_df['anomaly_score'] < 0.70)])/len(output_df):.2%})
* **No Action Count**: {len(output_df[output_df['anomaly_score'] < 0.40]):,} ({len(output_df[output_df['anomaly_score'] < 0.40])/len(output_df):.2%})

---

## 2. Top Anomaly Driver Occurrences
* **Balance Conflicts**: {len(output_df[output_df['top_drivers'].str.contains('balance_conflict')]):,}
* **Days Past Due (DPD) Conflicts**: {len(output_df[output_df['top_drivers'].str.contains('dpd_conflict')]):,}
* **Status Conflicts**: {len(output_df[output_df['top_drivers'].str.contains('status_conflict')]):,}
* **Missing Document exceptions**: {len(output_df[output_df['top_drivers'].str.contains('missing_document')]):,}

---

## 3. Top 10 Detailed Anomaly Review Examples
| Loan ID | Reporting Month | Score | Type | Top Drivers | Recommended Action |
|---|---|---|---|---|---|
"""
    for row in reports[:10]:
        report_content += f"| {row['loan_id']} | {row['reporting_month']} | {row['anomaly_score']:.4f} | {row['anomaly_type']} | `{row['top_drivers']}` | **{row['recommended_action']}** |\n"
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    # Print summary to console
    print("\nTop 5 Flagged Portfolio Anomalies:")
    for i, r in enumerate(reports[:5]):
        print(f"{i+1}. Loan: {r['loan_id']} | Month: {r['reporting_month']} | Score: {r['anomaly_score']:.4f} | Drivers: {r['top_drivers']}")
        print(f"   Evidence: {r['evidence']}")
        
    logger.info("==================================================")
    logger.info("PHASE 5 COMPLETE. ANOMALY REPORTS GENERATED.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
