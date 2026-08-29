# Groq LLM Reviewer Copilot Report

This report demonstrates the grounded natural-language analysis outputs of the Reviewer Copilot.

---

## 1. Grounded Underwriting Note Example
### Loan Context: `LN100542` (Reporting Month: `2026-02-01`)
* **ML Anomaly Score**: 0.7270
* **Default Probability (12m)**: 100.00%
* **Evidence**: Balance conflict: Primary=312772.18, Servicer=318233.02, DPD conflict: Primary=90, Servicer=30.0

#### Reviewer Output Note:
```markdown
**SUMMARY**
Loan LN100542 is currently classified as **Default** with a Days Past Due (DPD) of 90. The automated system has flagged a **Severe Delinquency** exception, triggered by the DPD value meeting the threshold of >= 60. The 12-Month Default Probability is 100.00%, indicating the model views the loan as already in a state of default or imminent loss. However, significant data conflicts exist between the primary system and servicer updates, creating uncertainty regarding the true delinquency status.

**DATA QUALITY & EXCEPTIONS**
*   **Severe Delinquency Exception:** Triggered because the Primary DPD is 90, which satisfies the rule `DPD >= 60`.
*   **Documentation Gap:** None. Document Status is 'Complete'.
*   **Loan Modification:** None. Modification Flag is 0.
*   **Data Conflicts (Critical):**
    *   **DPD Conflict:** Primary system reports DPD = 90, while the Servicer update reports DPD = 30.0. This is a material discrepancy that directly impacts the exception classification (Severe Delinquency vs. Delinquent).
    *   **Balance Conflict:** Primary system reports Current Balance = $312,772.18, while the Servicer update reports $318,233.02. The difference is $5,460.84.

**ML RISK ASSESSMENT**
*   **Default Probability:** 100.00% (12-Month). This aligns with the Primary status of 'Default'.
*   **Delinquency Probability:** 45.00% (3-Month). This appears inconsistent with a 90-day delinquency, suggesting the model may be weighting the conflicting Servicer DPD (30) or other features.
*   **Prepayment Probability:** 5.00% (12-Month). Low, consistent with a distressed loan.
*   **Predicted Next State:** 'Current'. This prediction is highly anomalous given the current 'Default' status and 90 DPD. It likely reflects the model's confusion due to the conflicting inputs (specifically the Servicer DPD of 30).
*   **ML Anomaly Score:** 0.7270. This high score indicates the input data is unusual or inconsistent, driven by the `balance_conflict` and `dpd_conflict` risk drivers.

**RECOMMENDED REVIEWER ACTION**
**Priority Review: Investigate Data**
1.  **Resolve DPD Conflict:** Contact the servicer to verify the accurate Days Past Due. If the true DPD is 30, the loan status should be 'Delinquent', not 'Default', and the 'Severe Delinquency' exception should be re-evaluated (as 30 < 60). If the true DPD is 90, the 'Default' status is correct.
2.  **Resolve Balance Conflict:** Verify the correct current balance ($312,772.18 vs. $318,233.02) to ensure accurate loss severity calculations.
3.  **Re-run Model:** After data correction, re-run the ML model to obtain accurate probability estimates and a consistent predicted next state.
4.  **Manual Status Update:** Based on the verified DPD, update the loan status in the primary system to reflect the true delinquency level.

Recommendation — Not a Decision
```

---

## 2. LLM Safety & Response Rejection Trail
The validator checks for required labels and prevents automated lending decisions:

### Example of Logged Validation Rejection:
* **Triggered Loan**: `LN100234`
* **Raw Response**: `Loan LN100234 shows default probability of 85%. Review immediately. Decision: Reject Loan.`
* **Rejection Reason**: `Missing mandatory disclaimer label.`
* **Automated Corrected Fallback Note**: `Loan LN100234 shows default probability of 85%. Review immediately. Decision: Reject Loan.

Recommendation — Not a Decision`
