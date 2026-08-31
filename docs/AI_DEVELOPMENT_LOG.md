# AI Development Log - Loan Performance Intelligence Engine

This document provides a detailed log of the collaborative development process, machine learning strategies, domain architecture decisions, and human review corrections implemented during the build of the **Loan Performance Intelligence Engine**.

---

## 1. AI Tools Used
* **Google Antigravity IDE Agent**: Managed pair programming, codebase diagnostics, automatic directory audits, and file refactoring.
* **Gemini 3.5 Flash / Pro**: Handled real-time code synthesis, complex mathematical script suggestions, and schema troubleshooting.
* **pytest Automation Task**: Background terminal runner to dynamically test and verify python router validations.

---

## 2. Representative Prompts
* **Ingestion Pipeline**: 
  > *"Initialize a Feature Store style pipeline loading raw csv segments. Build rolling maximums on days past due and count modifications without creating temporal target leakage."*
* **Calibration Sweep**: 
  > *"Create an agentic experiment sweeps runner script. Split data chronologically before 2025. Log parameters, ROC-AUC, and F1-Scores to mlruns local folder structures. Select the champion model configuration."*
* **Explainability Interface**: 
  > *"Write a counterfactual suggestion generator. If default risk exceeds 5%, list the adjustments needed for DTI, LTV, and FICO to achieve prime credit risk status."*
* **Model Health Metrics Fix**: 
  > *"Correct the dictionary key lookups in model_service.py to correctly parse improved_calibrated and improved next_state model metrics from model_performance.json to prevent 0.0000 outputs in the frontend."*
* **Dynamic Time Period Scaling**: 
  > *"Update the scenario simulator to accept start_date and end_date. Filter the portfolio dataframe dynamically, and mathematically scale the Monte Carlo credit VaR rates, VaR amounts, and Stress Matrix default probabilities using the baseline ratios."*

---

## 3. Accepted & Rejected Outputs

### A. Accepted Agentic Outputs (Implemented Fixes & Features)
* **Case Study A (Pydantic V2 Environment Crash)**: Autonomously updated [`config.py`](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/LAC/loan-verification-copilot/backend/app/config.py) to append Pydantic's `extra = 'ignore'` rule to prevent env configuration crashes.
* **Case Study B (Left Join Suffix Reconciliation)**: Resolved a `KeyError: 'servicer_name'` by adjusting expected dataframe join suffixes.
* **Case Study C (TypeScript Compiler Warnings)**: Prefixing unused React properties with underscores (`_entry: any`) to satisfy strict `noUnusedLocals` validation rules.
* **Case Study D (Model Health Metrics Correction)**: Fixed backend [`model_service.py`](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/LAC/loan-verification-copilot/backend/app/services/model_service.py) path mappings querying `"improved_calibrated"` and `"improved"` keys to show true Brier score metrics.
* **Case Study E (Scenarios Recharts & Dynamic Scaling)**: Bound Recharts `<BarChart>` columns to `"Baseline"` and `"Stressed"` data keys and updated simulator routes to accept optional dates, scaling Monte Carlo VaR tail risk boundaries and Stress Matrix default probabilities dynamically.

### B. Rejected AI Outputs (Human ML Architect Decisions)
* **SHAP Library integration for Local Explanations**: The AI suggested using the SHAP library. This was rejected due to slow computation times for real-time dashboards and compilation dependencies.
  * *Resolution*: Swapped for pre-calculated feature importance maps and category rules to yield immediate UI responsiveness.
* **Naive `cv='prefit'` calibration in Scikit-Learn**: The AI proposed simple prefit estimators in `CalibratedClassifierCV`. This was rejected due to strict frozen estimator exceptions thrown by scikit-learn version constraints.
  * *Resolution*: Built a custom calibration wrapper verifying fit states across package updates.
* **Decommissioned Groq LLM Models**: The AI originally parameterized LLM calls to Groq's decommissioned `llama3-70b-8192` model, resulting in HTTP 400 API errors.
  * *Resolution*: Pivot configs to active `qwen/qwen3.8-27b` parameters.

---

## 4. Human Review Process
1. **Chronological Splitting Audits**: The human reviewer rejected random cross-validation to prevent temporal target leakage, enforcing a strict chronological separator split.
2. **Reconciliation Break Rule Verification**: Enforced a manual balance-break exception threshold ($10.00 difference between servicer ledger and primary records) to supplement unsupervised Isolation Forest models.
3. **Interactive Simulation Verification**: Audited the dynamic scaling logic under different date ranges to verify mathematical proportion boundaries.

---

## 5. Approximate AI-Generated Code Share
* **AI-Generated Code Share**: **~85%** of the codebase (FastAPI routers, React/TypeScript components, Recharts visualizations, math scripts, and data profilers).
* **Human-Architected Share**: **~15%** (Ingestion structure rules, temporal leakage controls, validation constraints, and final code reviews).

---

## 6. Lessons Learned
1. **Finance Model Leakage**: Standard random train/test splits leak future economic trends. Implementing **chronological out-of-time splits** is mandatory for credit validation.
2. **Probability Calibration**: Calibrating default probabilities via **Isotonic Regression** is critical to optimize Brier Scores and align model outputs with true empirical default rates.
3. **Dynamic Performance Optimization**: Heavy calculations (like Monte Carlo simulations) must be scaled using backend ratio estimators to maintain sub-second UI updates.
4. **Strict Chart Mappings**: Double-check chart binding keys (`dataKey`) to ensure they match target data formats; otherwise, Recharts components will render blank without throwing syntax errors.

---

## 7. Directory Structure & Source Code Inventory
```
├── backend/                  # FastAPI Application Server
│   ├── app/
│   │   ├── main.py           # Application entrypoint & CORS middleware
│   │   ├── config.py         # Pydantic settings & environmental validation
│   │   ├── routers/          # API Routers (loans, scenarios, anomalies, quality)
│   │   └── services/         # Business logic layer (state coordination)
│   └── main.py
├── frontend/                 # React (Vite + TypeScript) Dashboard Client
│   ├── src/
│   │   ├── pages/            # View components (Dashboard, Explorer, Workstation)
│   │   ├── components/       # Reusable layout UI components
│   │   ├── services/         # Axios client and API declarations
│   │   └── types/            # TypeScript schema types
├── src/                      # ML Modeling Core Package
│   ├── anomaly/              # Isolation Forest anomaly scoring
│   ├── data/                 # Raw dataset handlers & IO loader
│   ├── features/             # Feature store pipeline builder
│   ├── models/               # Classifiers, Calibrators, and Markov state models
│   ├── explainability/       # Permutation importance & counterfactual generators
│   ├── scenarios/            # Macroeconomic stress multiplier curves
│   └── llm/                  # Grounded underwriter prompt agents
├── scripts/                  # Command Line Phase Runners & Tuning scripts
│   ├── run_phase1.py         # Setup & Data Ingestion
│   ├── run_phase2.py         # Feature Store Construction
│   ├── run_phase3.py         # HistGradientBoosting Training & Isotonic Calibration
│   ├── run_phase4.py         # Delinquency Transition Matrix Builder
│   ├── run_phase5.py         # Isolation Forest Anomaly Trainer
│   ├── run_phase6.py         # Permutation Feature Importance Run
│   ├── run_phase7.py         # Segment-Level Macro Projections
│   ├── run_phase8.py         # Grounded LLM Advisory Verification
│   ├── run_phase9.py         # Submission File Export & Scoring Run
│   ├── run_monte_carlo.py    # Vectorized Monte Carlo Portfolio VaR Simulator
│   ├── agentic_experiment_runner.py  # Auto-hyperparameter Tuning Runner
│   └── feature_stress_sensitivity.py # DTI vs LTV joint stress sensitivity grid
├── outputs/                  # Exported models, JSON matrices, and logs
└── reports/                  # Markdown files summarizing outputs
```

---

## 8. Mathematical Models & Financial Risk Strategy

### A. Delinquency Migration Markov Transition Matrix
Credit performance is treated as a stochastic process. The system models migration probabilities between states:
1. **State 0 (Current)**: Account in good standing.
2. **State 2 (Default)**: 90+ DPD or write-off.
3. **State 1 (Delinquent)**: 30–89 Days Past Due (DPD).
4. **State 3 (Prepaid)**: Loan fully paid off before maturity.

A transition matrix $T$ is computed from historical reporting records, where entry $P_{ij}$ represents the probability of transitioning from state $i$ to state $j$ in the next month:

$$T = \begin{pmatrix} 
P_{00} & P_{01} & P_{02} & P_{03} \\ 
P_{10} & P_{11} & P_{12} & P_{13} \\ 
P_{20} & P_{21} & P_{22} & P_{23} \\ 
P_{30} & P_{31} & P_{32} & P_{33} 
\end{pmatrix}$$

* **Verification Constraint**: Row probability sums are enforced to equal $1.000$ exactly ($\sum_{j=1}^{4} P_{ij} = 1.0$) to maintain probability conservation.

### B. Vectorized Monte Carlo Portfolio Simulator
To compute tail risk limits over a 12-month projection horizon, the Monte Carlo engine performs 1,000 trials on the portfolio's active principal balance:
* **Prepayment Transition**: Simulates voluntary prepayments, adjusting the interest-earning balance.
* **Write-offs**: Models transition to default, applying a **Loss Given Default (LGD) / Loss Severity** rate of $45\%$.
* **Metrics Calculated**:
  * **Expected Loss Rate**: The mean write-off rate across all simulation paths.
  * **95% Credit Value-at-Risk (VaR)**: The loss threshold that will not be exceeded with $95\%$ confidence.
  * **99% Credit Value-at-Risk (VaR)**: Extreme tail risk representing a severe economic downturn scenario.
  * **Net Yield**: Expected interest earnings offset by credit defaults.

### C. Double-Trigger Stress Sensitivity Matrix
Default risk behaves non-linearly. The system builds a $3\times3$ joint stress matrix evaluating borrower risk under double-trigger scenarios (Simultaneous leverage increase and property equity depreciation):

$$\text{Leverage Stress} \in \{\text{Base}, \text{Moderate (DTI +5\%)}, \text{Severe (DTI +12\%)}\}$$
$$\text{Equity Stress} \in \{\text{Base}, \text{Moderate (LTV +10\%)}, \text{Severe (LTV +20\%)}\}$$

* For each cell, DTI and LTV features are shifted across the active portfolio, and predicted default probabilities are recalculated using the calibrated classifier.

---

## 9. Machine Learning Modeling & Calibration Pipeline

### A. Non-LLM Predictive Modeling Strategy
* **Algorithms**: Standard risk predictions utilize a `HistGradientBoostingClassifier` trained on engineered features.
* **Leakage Controls**:
  * **Chronological Out-of-Time Separation**: Training features are separated chronologically at `2025-01-01` to isolate validation data. Random cross-validation is forbidden to prevent target leakage.
  * **Target Elimination**: Target indicators (`next_12m_default_flag`, `next_state`) are removed from input vectors.
* **Isotonic Calibration**: Machine learning classifiers tend to output uncalibrated probabilities under stress. The system calibrates probabilities using **Isotonic Regression**, mapping predicted default probabilities to actual default rates to optimize the **Brier Score**.

### B. Hybrid Anomaly Detection Engine
Anomalies are detected using a combination of machine learning outputs and reconciliation rules:
1. **Isolation Forest Anomaly Score**: Computes multivariate out-of-distribution values for incoming accounts.
2. **Deterministic Reconciliation Breaks**: Evaluates discrepancies between servicer ledger balances and primary records:

$$\text{Balance Break} = | \text{Primary Balance} - \text{Servicer Balance} | > \$10.00$$

* The final anomaly score is weighted: `0.5 * Isolation_Forest_Score + 0.5 * Reconciliation_Break_Score`.

---

## 10. High-Fidelity UI/UX Showcase Layout
1. **Ambient Glassmorphism**: Containers feature semi-transparent backdrop blur parameters, soft border gradients, and distinct active highlights to create a premium interface.
2. **Real-time Live Predictor Workstation**:
   * Underwriters can input test parameters (FICO score, LTV, DTI) to calculate risk probabilities dynamically.
   * Prompts suggest recommended actions (e.g. *"Priority Review"*, *"Documentation Audit"*) based on custom risk bands.
3. **Explainability Tabs with Counterfactual Paths**:
   * Rather than showing only a high default risk score, the system renders a **Counterfactual Recommendations Panel**.
   * It calculates the minimal parameter adjustments (e.g., reduce DTI by $5\%$, clear delinquency DPD) required to transition a high-risk profile back into low-risk compliance.
4. **Scenario Simulator Dashboard**:
   * Interactive sliders allow underwriters to simulate custom macroeconomic shocks.
   * Dynamically displays Monte Carlo VaR boundaries, expected yields, and the $3\times3$ stress sensitivity matrix.

---

## 11. Responsible AI & Compliance
* **Underwriter Advisory Clause**: Every automated LLM review or prediction is marked with a compliance header: `"Recommendation — Not a Decision"` to align with regulatory requirements for human-in-the-loop credit verification.
* **Confidence Metrics**: Predicted targets are output with statistical confidence scores.
* **Context Grounding**: Prompt templates isolate data schemas and check lists to prevent hallucinations in AI reviews.
