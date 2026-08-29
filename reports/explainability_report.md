# Portfolio Explainability Report

This report outlines global portfolio-level risk drivers and local loan-level explanations.

---

## 1. Global Feature Importance (Top 10 Drivers)
Feature importance is computed using model-agnostic **Permutation Feature Importance** on validation observations.

| Rank | Feature Column | Permutation Importance Mean | Variance Std |
|---|---|---|---|
| 1 | `days_past_due` | 0.018400 | 0.002332 |
| 2 | `month_index` | 0.000000 | 0.000000 |
| 3 | `remaining_term_months` | 0.000000 | 0.000000 |
| 4 | `loan_age_months` | 0.000000 | 0.000000 |
| 5 | `current_balance` | 0.000000 | 0.000000 |
| 6 | `interest_rate` | 0.000000 | 0.000000 |
| 7 | `credit_score_band` | 0.000000 | 0.000000 |
| 8 | `ltv_band` | 0.000000 | 0.000000 |
| 9 | `dti_band` | 0.000000 | 0.000000 |
| 10 | `state` | 0.000000 | 0.000000 |

---

## 2. Local Risk-Driver Analysis
Local explanations are computed for individual loans to map positive (risk-increasing) and negative (risk-reducing) drivers.

### High Default Probability Examples (Top 5 Anomalous Risk Loans)
| Loan ID | Reporting Month | Default Prob (12m) | Positive Drivers | Negative Drivers |
|---|---|---|---|---|
| LN100918 | 2025-03-01 | 100.0000% | `severe_delinquency(DPD=90);high_dti;prior_modifications(count=3)` | `high_credit_score;low_rate(3.96%)` |
| LN100930 | 2025-04-01 | 100.0000% | `severe_delinquency(DPD=90);high_dti;prior_modifications(count=1)` | `high_credit_score;low_rate(3.23%)` |
| LN100038 | 2025-12-01 | 100.0000% | `severe_delinquency(DPD=90);high_dti;prior_modifications(count=1)` | `high_equity_ltv;low_rate(3.83%)` |
| LN101897 | 2025-01-01 | 100.0000% | `severe_delinquency(DPD=90)` | `low_dti` |
| LN101951 | 2025-09-01 | 100.0000% | `severe_delinquency(DPD=90);high_ltv;high_dti` | `high_credit_score` |
