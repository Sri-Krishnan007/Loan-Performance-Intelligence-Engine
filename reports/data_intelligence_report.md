# Data Intelligence and Profiling Report

## 1. Executive Summary
This report profiles and validates the primary training performance panel, static attributes, and servicer updates. The baseline dataset consists of **71,142** performance records representing **2,000** unique mortgage loans. 

* **Train / Test Cohort Drift (PSI)**: Feature distributions are stable across sets, showing zero high-drift variables.
* **Batch Quality Score**: The training data scored an average of **99.66 / 100** under the validation engine logic.
* **Data-Quality Verdict**: **READY FOR ML PIPELINE** (warnings must be handled in preprocessing).

---

## 2. Validation Findings & Failures
Applying `validation_rules.json` mapped the following failures in training performance data:

| Rule ID | Failure Count | Severity | Failure Message |
|---|---|---|---|
| DLQ006 | 784 | warning | Delinquency transitions should roll sequentially (e.g., 0 to 30, 30 to 60, 60 to 90). Skipped DPD buckets raise warnings. |
| LFC005 | 467 | error | A prepaid loan must have a balance close to zero. |
| FLG004 | 1,385 | warning | Loan modifications normally occur for delinquent accounts (DPD >= 60). Modifications on current/mildly delinquent loans trigger a warning. |
| DOC003 | 191 | error | If the document status is Missing, exception_type must indicate Documentation Gap. |
| DLQ006 | 738 | warning | Delinquency transitions should roll sequentially (e.g., 0 to 30, 30 to 60, 60 to 90). Skipped DPD buckets raise warnings. |
| LFC005 | 454 | error | A prepaid loan must have a balance close to zero. |
| FLG004 | 1,337 | warning | Loan modifications normally occur for delinquent accounts (DPD >= 60). Modifications on current/mildly delinquent loans trigger a warning. |
| SRV007 | 1,653 | info | Updates marked as PARTIAL_UPDATE are expected to contain missing fields; this should be flagged as informational, not a data error. |
| SRV008 | 1,290 | info | Updates marked as STALE represent unprocessed local system updates. Timestamp lag is expected. |
| SRV009 | 942 | info | Updates marked as CONFLICT represent feed errors or mismatch flags for reconciliation testing. |

---

## 3. Data Quality Score Metrics
Deduction rules (Errors = -20, Warnings = -5, Infos = -0) were applied row-by-row on the training performance set:

* **Average Record Score**: 99.66
* **Median Record Score**: 100.00
* **Proportion Score $\ge$ 90**: 99.08%
* **Proportion Score 70-89**: 0.92%
* **Proportion Score < 70**: 0.00%

---

## 4. Train / Test Feature Drift (Top 10 PSI values)
| Feature Column | Population Stability Index (PSI) | Drift Classification |
|---|---|---|
| state | 0.01609 | Stable |
| remaining_term_months | 0.00610 | Stable |
| interest_rate | 0.00342 | Stable |
| credit_score_band | 0.00268 | Stable |
| property_type | 0.00217 | Stable |
| dti_band | 0.00139 | Stable |
| current_balance | 0.00104 | Stable |
| ltv_band | 0.00100 | Stable |
| original_balance | 0.00091 | Stable |
| servicer_name | 0.00058 | Stable |

---

## 5. Key Missingness Summary
| Column | Missing Count | Missing % |
|---|---|---|
| loss_severity_band | 70,308 | 98.83% |
| exception_type | 55,107 | 77.46% |
| loan_id | 0 | 0.00% |
| month_index | 0 | 0.00% |
| reporting_month | 0 | 0.00% |
| remaining_term_months | 0 | 0.00% |
| original_balance | 0 | 0.00% |
| origination_month | 0 | 0.00% |

---

## 6. Outlier Profile Summary (IQR Method)
| Numeric Column | Lower IQR Bound | Upper IQR Bound | Outlier Count | Outlier % |
|---|---|---|---|---|
| original_balance | -90446.22 | 625008.29 | 2,993 | 4.21% |
| current_balance | -95595.54 | 599409.78 | 2,996 | 4.21% |
| interest_rate | 0.13 | 8.57 | 30 | 0.04% |
| loan_age_months | -34.50 | 81.50 | 998 | 1.40% |
| remaining_term_months | 137.50 | 469.50 | 496 | 0.70% |
