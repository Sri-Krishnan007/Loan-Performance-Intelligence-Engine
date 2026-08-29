# Model Card - Loan Performance Intelligence Engine

This model card documents the design, validation, and performance parameters of the predictive risk models implemented in the Loan Performance Intelligence Engine.

---

## 1. Model Details
* **Developed By**: Gemini Antigravity Agentic Pair
* **Model Date**: August 2026
* **Model Type**: Gradient Boosting Trees (scikit-learn `HistGradientBoostingClassifier`)
* **Target Configurations**:
  * **delinquency_3m**: Predicts probability of reaching $\ge 30$ DPD in the next 3 months.
  * **delinquency_6m**: Predicts probability of reaching $\ge 30$ DPD in the next 6 months.
  * **default_12m**: Predicts probability of reaching Default status (90 DPD) in the next 12 months.
  * **prepayment_12m**: Predicts probability of prepayment (early payoff) in the next 12 months.
  * **next_state**: Predicts next-month state transitions ('Current', 'Delinquent', 'Default', 'Prepaid').
* **Probability Calibration**: Calibrated on validation datasets using Isotonic Regression via scikit-learn `FrozenEstimator`.

---

## 2. Intended Use
* **Intended Use Case**: Decision support tool for mortgage loan risk assessment, servicer exception auditing, and scenario stress testing.
* **Non-Intended Use Cases**: Automated credit approval/rejection or autonomous loan pricing without human underwriter review.
* **Reviewer Disclaimer**: Mandatory output label is `"Recommendation — Not a Decision"`.

---

## 3. Dataset & Features
* **Source Data**: Curated synthetic mortgage loan performance panel (71,142 train observations, 2,000 unique loans).
* **Feature Categories**:
  * **Static Attributes**: Original balance, FICO score band, LTV band, DTI band, state, loan purpose, property type, vintage.
  * **Monthly Performance**: Current balance, interest rate, days past due, modification flag.
  * **Engineered Features**: Amortization balance ratio, categorical codes, days past due lags (lag 1, lag 2), rolling maximum DPD (past 3 months), and cumulative loan modification count.

---

## 4. Time-Aware Validation Setup
* **Chronological out-of-time split**:
  * **Split Cutoff Date**: 2025-01-01
  * **Training Set**: January 1, 2018 $\rightarrow$ December 1, 2024 (55,120 rows)
  * **Validation Set**: January 1, 2025 $\rightarrow$ July 1, 2026 (16,022 rows)
  * **Leakage Controls**: All targets are rolling forward look-aheads, masking feature inputs from future periods. Observation rows are completely disjoint.

---

## 5. Performance Metrics (OOT Validation Set)

### A. Binary Risk Predictors
| Model Name | ROC-AUC | Brier Score (Raw) | Brier Score (Calibrated) |
|---|---|---|---|
| **Delinquency 3m** | 0.8836 | 0.0571 | 0.0240 |
| **Delinquency 6m** | 0.8122 | 0.1181 | 0.0640 |
| **Default 12m** | 0.8090 | 0.0948 | 0.0114 |
| **Prepayment 12m** | 0.7791 | 0.1073 | 0.0083 |

### B. Next-State Multiclass Predictor
* **Macro F1-Score**: 0.1676
* **Confusion Matrix**:
  * Current $\rightarrow$ Current: 5,474 | Delinquent: 2,390 | Default: 3,166 | Prepaid: 4,185
  * Delinquent $\rightarrow$ Current: 139 | Delinquent: 144 | Default: 116 | Prepaid: 90
  * Default $\rightarrow$ Current: 45 | Delinquent: 47 | Default: 62 | Prepaid: 32
  * Prepaid $\rightarrow$ Current: 56 | Delinquent: 16 | Default: 17 | Prepaid: 43

---

## 6. Model Explainability
* **Global Importance**: Model-agnostic **Permutation Feature Importance** indicates `days_past_due` as the primary risk driver.
* **Local Explanations**: Multi-feature rules extract specific risk-increasing elements (e.g. DPD, low FICO, high DTI) and risk-reducing elements (e.g. low rate, high equity).

---

## 7. Known Limitations & Failure Modes
* **Censoring Boundary**: Observations within 12 months of the July 2026 data cutoff have incomplete forward horizons, meaning true default/prepayment events may occur outside the observed panel window.
* **Imbalance Sensitivity**: Low default (2.30%) and prepayment (1.33%) rates require class weighting adjustment during model fitting to prevent bias towards majority status.
* **Data Conflict Vulnerability**: Prediction quality relies on data integrity. Reconciled feed conflicts (e.g., mismatched servicer days past due) directly affect probability accuracy, requiring manual review.

---

## 8. Reproducibility
* **Random Seeds**: Set to `42` across all classifiers and splits.
* **Python Environment**: `requirements.txt` pins required packages (`pandas`, `numpy`, `scikit-learn`, `joblib`, `requests`, `pyarrow`).
