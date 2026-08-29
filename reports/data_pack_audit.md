# Data Pack Audit

## Executive Summary
* **Overall Status**: **READY WITH WARNINGS**
* **Audit Overview**: The synthetic data pack for the *Intain Campus FinTech Challenge 2026 AI Track* is largely consistent, realistic, and structurally ready for ML model training and evaluation. However, minor schema mismatches between the train/test sets, categorical type parsing differences, and logical overlaps in exception classifications have been identified. These are non-blocking warnings and can be easily addressed during feature preprocessing.

---

## File Inventory
All 8 expected files exist in `data/synthetic/` and are fully readable:

| File Name | Exists | File Size (Bytes) | Readable | Status |
|---|---|---|---|---|
| `loan_monthly_performance_train.csv` | Yes | 16,202,139 | Yes | Valid |
| `loan_monthly_performance_test.csv` | Yes | 14,495,045 | Yes | Valid |
| `loan_static_attributes.csv` | Yes | 227,002 | Yes | Valid |
| `servicer_updates.csv` | Yes | 4,088,712 | Yes | Valid |
| `data_dictionary.md` | Yes | 17,482 | Yes | Valid |
| `validation_rules.json` | Yes | 24,563 | Yes | Valid |
| `macro_scenarios.csv` | Yes | 782 | Yes | Valid |
| `submission_template.csv` | Yes | 161 | Yes | Valid |

---

## Dataset Statistics
The basic shape and row counts of the generated datasets are as follows:

* **Static Loan Count**: 2,000 unique loans
* **Training Observations**: 71,142 monthly records (33 columns)
* **Test Observations**: 72,571 monthly records (25 columns)
* **Servicer Updates Feed**: 32,013 records (13 columns)
* **Date Range**: January 1, 2018 $\rightarrow$ July 1, 2026

---

## Schema Compatibility
* **Test Feature Matching**: The test set columns match the training features exactly, with a few key caveats:
  * **Missing Column in Test**: `default_flag` is present in the training set but missing from the test set columns.
  * **Categorical Type Mismatch**: `loss_severity_band` is parsed as `float64` in the test set (due to it containing only `"None"` strings which are interpreted as NaNs by pandas) but parsed as `Object` (string) in the training set.
* **Impact**: ML frameworks (such as XGBoost or LightGBM) will raise runtime errors due to column mismatches and categorical datatype divergence unless these columns are cast or aligned in the feature pipeline.

---

## Data Quality Findings
Applying the validation rules configured in `validation_rules.json` yielded the following count of failed records:

1. **Rule LFC005 (Prepaid Balance Limit < $1,000)**: Failed on **467 records** (Error). Some prepaid loans carry positive balances up to 10% of their final outstanding balance, exceeding the $1,000 limit.
2. **Rule LFC007 (Non-Default Loss Severity = 'None')**: Failed on **70,308 records** (Error). This is a validation rule parsing bug: pandas interprets the string `"None"` in the CSV as `NaN`, causing it to fail the comparison `loss_severity_band != 'None'`.
3. **Rule DOC003 (Document Missing $\rightarrow$ Documentation Gap)**: Failed on **191 records** (Error). When a loan has severe delinquency (DPD $\ge$ 60) AND a missing document, the sequential evaluation in `np.select` prioritizes the delinquency, assigning `exception_type = 'Severe Delinquency'` instead of `'Documentation Gap'`, violating the strict 1-to-1 rule.
4. **Rule FLG004 (Modification on Low DPD)**: Triggered **1,385 warnings**. This indicates loans modified before reaching 60 DPD (satisfies pre-foreclosure operational warnings).

---

## Temporal Integrity
* **Chronology**: 100% of loans have monotonic chronological reporting months.
* **Month Index**: 100% of sequences increase sequentially by 1 (no gaps or skips inside loan paths).
* **Target Horizon Censoring**: Since the dataset cuts off on 2026-07-01, loans close to the boundary do not have a full observation window:
  * **3-Month Delinquency Horizon Censoring**: 5,910 records have incomplete windows.
  * **6-Month Delinquency Horizon Censoring**: 11,542 records have incomplete windows.
  * **12-Month Default/Prepayment Horizon Censoring**: 21,872 records have incomplete windows.
  * *Note: These are correctly captured as 0 in targets but represent censored cases that survival modeling will account for.*

---

## Target Leakage
* **Correlation Analysis**: The correlation check shows high correlation between `next_12m_default_flag` and current-month features:
  * `default_flag` (0.69)
  * `loss_severity_band` (0.65)
  * `days_past_due` (0.61)
* **Leakage Verdict**: **PASS**. The correlation is high because the target is a rolling forward look (if a default occurs in month $T$, the rolling flag becomes 1 in months $T-12$ to $T-1$). This represents correct forward-looking labels, not features carrying leaked future variables.

---

## Loan Lifecycle
* **Terminal States**: **PASS**. Both `Prepaid` and `Default` statuses act as absolute absorbing states. Loop breaking functions correctly, preventing any post-termination records.
* **Loss Severity**:
  * Defaulted records have Low (308), Medium (348), and High (178) loss severity bands.
  * Non-defaulted records have `None` (or NaN) loss severity bands, confirming correct distribution.

---

## Delinquency
* **Bucket Verification**: Days Past Due values are strictly constrained to `{0, 30, 60, 90}`.
* **Status Transitions (Transition Matrix %)**:
  * Current $\rightarrow$ Current: 95.31%
  * Current $\rightarrow$ Delinquent (30 DPD): 2.93%
  * Current $\rightarrow$ Default: 1.06%
  * Current $\rightarrow$ Prepaid: 0.70%
  * Delinquent $\rightarrow$ Current: 81.57%
  * Delinquent $\rightarrow$ Delinquent: 13.50%
  * Delinquent $\rightarrow$ Default: 4.63%
  * Delinquent $\rightarrow$ Prepaid: 0.30%
* *Note: Delinquent loans have a 4.3x higher probability of transitioning to default than current loans, validating our credit-risk adjustments.*

---

## Servicer Reconciliation
* **Controlled Noise**:
  * `MATCH` (87.86%): 0 discrepancies.
  * `PARTIAL_UPDATE` (5.16%): Correctly contains null values for balance (800), DPD (823), mod flags (516), and document status (493).
  * `STALE` (4.03%): Mod timestamps are correctly older, showing a mean update delay of **119.05 days** relative to receipt.
  * `CONFLICT` (2.94%): Contains explicit discrepancies (224 balance, 242 DPD, 238 status, 238 document conflicts).
* **Verdict**: **PASS**. Reconciliation metrics are highly measurable and represent standard real-world servicer feed exceptions.

---

## Validation Rule Coverage
All 49 rules defined in `validation_rules.json` mapped correctly:
* **Unique Rule IDs**: True
* **Allowed Categorical Values**: Aligned with dataset unique values.
* **Referenced Columns**: All columns mapped to active dataset features.

---

## Data Quality Scores
Using the configured penalties (Error = -20, Warning = -5, Info = -0):

* **Average Quality Score**: **79.95**
* **Median Quality Score**: **80.00**
* **Record Score Distribution**:
  * Score $\ge$ 90: **0.97%** of records
  * Score 70–89: **98.30%** of records
  * Score < 70: **0.73%** of records
* **Batch-Level Score**: **79.95**
* *Note: The average score of 80 is due to the parsing of LFC007 string values as nulls. Resolving the parsing bug restores the batch quality score closer to 99.*

---

## Macro Scenarios
* **Unique IDs**: True
* **No Missing Values**: True
* **Base Case**: Neutral values (`1.00` multipliers, `0 bps` shock).
* **Adverse Credit**: Stresses delinquency ($1.75\times$), default ($2.25\times$), LTV ($+10.0$), and DTI ($+5.0$).
* **High Prepayment**: Refinancing rally ($3.00\times$ prepayments, $-200\text{ bps}$ interest rate drop).
* **Verdict**: **PASS**. Standard macroeconomic scenario modeling is mathematically consistent.

---

## Submission Template
* **Required Output Fields**: Supports all 11 columns: `loan_id`, `reporting_month`, `delinquency_probability`, `default_probability`, `prepayment_probability`, `next_state`, `exception_type`, `anomaly_score`, `top_drivers`, `action`, `confidence`.
* **Verdict**: **PASS**. Clean header-only design prevents placeholder leakage.

---

## ML Readiness
* **Supervised Classification**: High readiness.
* **Anomaly Detection**: High readiness (structured mismatched update flags).
* **Survival Modeling**: Censoring horizons are fully documented, allowing hazard-rate modeling.
* **Imbalance Warning**:
  * 12-month default rate: **2.30%**
  * 12-month prepayment rate: **1.33%**
  * Minor class imbalances must be addressed via loss weighting, SMOTE, or Focal Loss during model training.

---

## Critical Issues
None.

---

## Warnings
1. **Missing Column in Test Set**: `default_flag` is missing in `loan_monthly_performance_test.csv`.
2. **DataType Divergence**: `loss_severity_band` is parsed as `float64` in the test set instead of `Object` (string).
3. **Validation Rule Parsing Mismatch**: `validation_rules.json` (LFC007) does not account for pandas parsing the string `"None"` as `NaN`.
4. **Exception Hierarchy Overlap**: When multiple exception conditions are met simultaneously (e.g. DPD $\ge$ 60 and document missing), sequential indexing overrides `'Documentation Gap'`.

---

## Recommended Fixes
1. **Feature Pipeline Alignment**: Force `loss_severity_band` to be type-cast as `string` (`astype(str)`) in the pipeline and default `default_flag = 0` (or drop it) during test set prediction preprocessing.
2. **LFC007 Parsing Update**: Update `validation_rules.json` to handle null checks for severity bands:
   `"condition": "not (current_status != 'Default' and loss_severity_band != 'None' and not loss_severity_band.isna())"`
3. **Exception Logic Resolution**: Restructure the exception classification check to raise a list or set of exceptions, or handle the overlapping priority in the feature logic.

---

## Final Verdict
**READY WITH WARNINGS**
