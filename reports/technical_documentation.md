# Loan Performance Intelligence Engine - Technical Documentation

This document compiles the design, modeling outputs, operational findings, stress-testing aggregates, and copilot configurations of the **Loan Performance Intelligence Engine** for the **Intain Campus FinTech Challenge 2026 AI Track**.

---

## 1. Setup, Data Loading, & Validation Engine (Phase 1)
* **Datatypes Loader**: standardizes datetimes and categories using [`loader.py`](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/src/data/loader.py).
* **Validation Engine**: checks range constraints, allowed categories, and balance reconciliation using [`validator.py`](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/src/data/validator.py).
* **Data quality stats**:
  * **Audited Records**: 71,142
  * **Average Quality Score**: **99.66 / 100**
  * **Drift Check (PSI)**: All features are highly stable (PSI < 0.10, maximum PSI is 0.016 for `state`).

---

## 2. Feature Engineering & Leakage Controls (Phase 2)
* **Lag Features**: Computes rolling maximum DPD, trend flags, and cumulative modification counts.
* **leakage controls**: Checked that the test features parquet file contains **zero** target labels or future variables.
* **Persisted Sets**:
  * Train set: [`train_features.parquet`](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/data/processed/features/train_features.parquet) (71,142 rows)
  * Test set: [`test_features.parquet`](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/data/processed/features/test_features.parquet) (72,571 rows)

---

## 3. Supervised ML Models & Calibration (Phase 3)
* **Time-Split Splitting**: Splitting chronologically on **2025-01-01** (Train: 55,120 rows; Validation: 16,022 rows).
* **Calibrated Estimators**: Uses LightGBM-style `HistGradientBoostingClassifier` with probability calibration using `FrozenEstimator` (scikit-learn 1.8.0).
* **OOT Validation Metrics**:
  * **3-Month Delinquency**: ROC-AUC: **0.8836** | Calibrated Brier Score: **0.0240**
  * **6-Month Delinquency**: ROC-AUC: **0.8122** | Calibrated Brier Score: **0.0640**
  * **12-Month Default**: ROC-AUC: **0.8090** | Calibrated Brier Score: **0.0114**
  * **12-Month Prepayment**: ROC-AUC: **0.7791** | Calibrated Brier Score: **0.0083**
  * **Next State Multiclass**: Macro F1-Score: **0.1676**

---

## 4. Survival & Transition Modeling (Phase 4)
* **Transition Matrix**: Markovian state-transition probabilities with absorbing terminal state overrides:
  * Current -> Delinquent: **2.93%**
  * Current -> Default: **1.06%**
  * Current -> Prepaid: **0.70%**
  * Absorbing states Default -> Default (100%), Prepaid -> Prepaid (100%).
* **Competing Hazard Curves**: Computes default and prepayment hazards over loan ages (1 to 60 months).

---

## 5. Anomaly & Exception Detection (Phase 5)
* **Hybrid Engine**: Isolation Forest on financial attributes + reconciliation discrepancy rules.
* **Reconciliation Findings**:
  * Audited 32,013 merged servicer updates.
  * Extracted **20** detailed, reviewer-ready anomaly reports detailing balance mismatches, DPD status conflicts, and missing documents.

---

## 6. Explainability & Risk Drivers (Phase 6)
* **Global Permutation Importance**: `days_past_due` stands out as the single most critical driver for default predictions.
* **Local Risk Explanations**: Mapped individual risk-increasing factors (e.g. `severe_delinquency(DPD=90)`, `high_dti`) and risk-reducing factors (e.g. `high_credit_score`, `low_rate`).

---

## 7. Scenario stress Projections (Phase 7)
Stressing baseline projections under macroeconomic multipliers:
* **BASE**: Delinquency = **8.44%** | Default = **2.41%** | Prepayment = **1.70%**
* **ADVERSE_CREDIT**: Delinquency = **10.30%** | Default = **3.85%** | Prepayment = **0.68%**
* **HIGH_PREPAYMENT**: Delinquency = **7.17%** | Default = **1.93%** | Prepayment = **3.38%**

---

## 8. Groq LLM Reviewer Copilot (Phase 8)
* **Active Model**: Configured to use the high-performance `qwen/qwen3.8-27b` model.
* **Grounded Prompts**: Prompt templates designed using project terminology and DPD exceptions thresholds.
* **disclaimers**: Every response includes `"Recommendation — Not a Decision"`. Vague or decision-making outputs are automatically rejected and corrected, logging history in [`rejected_outputs.jsonl`](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/outputs/llm/rejected_outputs.jsonl).

---

## 9. End-to-End Scoring Pipeline (Phase 9)
* **Scored Output**: Scores test partition features (72,571 rows) and populates the competition template columns:
  `loan_id,reporting_month,delinquency_probability,default_probability,prepayment_probability,next_state,exception_type,anomaly_score,top_drivers,action,confidence`
* **Output Path**: [`submission.csv`](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/outputs/submissions/submission.csv) contains zero NaN values and matches row/column constraints.
