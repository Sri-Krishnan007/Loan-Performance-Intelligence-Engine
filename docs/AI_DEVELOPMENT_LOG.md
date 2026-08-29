# AI Development Log - Loan Performance Intelligence Engine

This document outlines the AI-assisted development history, human review processes, and engineering corrections applied during the development of the Loan Performance Intelligence Engine.

---

## 1. AI Tools and Collaboration Profile
* **AI Tool Used**: Gemini Antigravity Agentic Developer
* **Role**: Autonomous coding agent and pair programmer.
* **Human Reviewer**: Senior FinTech ML Architect
* **Approximate AI-Generated Code Share**: 92%
* **Human Oversight Level**: Continuous validation of schemas, model configurations, and script execution outputs.

---

## 2. Chronological Milestones & Prompt History (Reconstructed Documentation)

### A. Phase 1 & 2: Setup, Loader, & Feature Pipeline
* **Representative Prompt**:
  *"Create a feature engineering pipeline that merges static attributes, computes financial ratios, and builds historical lags while preventing temporal leakage."*
* **Accepted Suggestion**: chronological sorting by `["loan_id", "reporting_month"]` before calculating shifts and rolling maximums.
* **Human Correction**: Cast categorical columns to string using `.astype(str)` prior to mapping risk bands, resolving a `CategoricalDtype` setitem TypeError when filling NaNs with `-1`.

### B. Phase 3 & 4: Model Training & Validation
* **Representative Prompt**:
  *"Train non-LLM risk models chronologically, apply probability calibration on validation splits, and evaluate ROC-AUC and Brier scores."*
* **Accepted Suggestion**: Chronological Out-of-Time split (Cutoff at 2025-01-01) and isotonic probability calibration.
* **Human Correction**: Fixed a calibration error in scikit-learn 1.8.0 where `cv='prefit'` threw parameter constraints exceptions, replacing it with the new `FrozenEstimator` wrapper.

### C. Phase 5 & 6: Anomalies & Explainability
* **Representative Prompt**:
  *"Implement a hybrid anomaly detector using Isolation Forest and cross-source update reconciliation rules."*
* **Accepted Suggestion**: Combined anomaly scoring formula: `0.5 * ML_score + 0.5 * Rule_score`, generating 20 reviewer examples.
* **Rejected Suggestion**: Using SHAP in documentation when the actual implementation uses permutation feature importance for HistGradientBoosting.

### D. Phase 7, 8, & 9: Stress Scenarios, LLM reviews, & Pipeline
* **Representative Prompt**:
  *"Configure a Groq LLM reviewer copilot using prompts grounded on the data dictionary, and write completed predictions to submission.csv."*
* **Accepted Suggestion**: Grounded underwriter prompt layouts and validation logs for safety disclaimers.
* **Human Correction**: 
  1. Updated the Groq default model from decommissioned `llama3-70b-8192` to the active `qwen/qwen3.8-27b` to avoid decommission errors.
  2. Fixed a `KeyError: 'servicer_name'` in the scoring pipeline caused by columns renaming to `_primary` / `_servicer` suffix formats after left-joining test features.
  3. Resolved a syntax error in f-strings containing backslashes inside curly brace expressions.

---

## 3. Human Verification Examples
1. **Transition Row Sums**: Enforced verification check inside [`run_phase4.py`](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/run_phase4.py) to assert that transition matrix row sums equal `1.000` exactly.
2. **Leakage Controls**: Asserted that test parquet files contain **zero** target labels or future variables.
3. **LLM Safety Validator**: Audited LLM responses for the required label `"Recommendation — Not a Decision"` and logged safety rejections.

---

## 4. Key Lessons Learned
* **API Decommissioning Audits**: Relying on static model parameters risks code rot. Real-time endpoint lists must be verified.
* **Scikit-Learn Evolution**: Advanced packages regularly deprecate historical settings. Upgrading code to scikit-learn 1.8.0 standards (like `FrozenEstimator`) is crucial for maintainability.
* **f-string Syntax Bounds**: Backslashes inside f-string expressions are rejected in Python < 3.12, requiring variables to be defined outside string formatting blocks.
