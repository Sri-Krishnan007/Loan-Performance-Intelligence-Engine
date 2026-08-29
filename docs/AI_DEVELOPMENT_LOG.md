# AI Development Log & System Architecture: Loan Performance Intelligence Engine

This document provides a highly detailed log of the collaborative development process, architectural design decisions, mathematical models, machine learning strategies, and expert human review corrections implemented during the build of the **Loan Performance Intelligence Engine**.

---

## 1. Directory Structure & Source Code Inventory

A complete analysis of the codebase reveals a modular, production-ready system split into logical components. The human ML architect guided this layout to ensure separation of concerns:

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
│   ├── features/             # Financial feature store pipeline builder
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

## 2. Mathematical Models & Financial Risk Strategy

The system contains robust mathematical formulations verifying credit risk, prepayment rates, and portfolio stability:

### A. Delinquency Migration Markov Transition Matrix
Credit performance is treated as a stochastic process. The system models migration probabilities between states:
1. **State 0 (Current)**: Account in good standing.
2. **State 1 (Delinquent)**: 30–89 Days Past Due (DPD).
3. **State 2 (Default)**: 90+ DPD or write-off.
4. **State 3 (Prepaid)**: Loan fully paid off before maturity.

A transition matrix $T$ is computed from historical reporting records, where entry $P_{ij}$ represents the probability of transitioning from state $i$ to state $j$ in the next month:

$$T = \begin{pmatrix} 
P_{00} & P_{01} & P_{02} & P_{03} \\ 
P_{10} & P_{11} & P_{12} & P_{13} \\ 
P_{20} & P_{21} & P_{22} & P_{23} \\ 
P_{30} & P_{31} & P_{32} & P_{33} 
\end{pmatrix}$$

* **Verification Constraint**: Row probability sums are enforced to equal $1.000$ exactly ($\sum_{j=1}^{4} P_{ij} = 1.0$) to maintain probability conservation during multi-month projections.

### B. Vectorized Monte Carlo Portfolio Simulator
To compute tail risk limits over a 12-month projection horizon, the Monte Carlo engine performs 1,000 trials on the portfolio's active principal balance:
* **Prepayment Transition**: Simulates voluntary early prepayments, adjusting the interest-earning balance.
* **Write-offs**: Models transition to default, applying a standard **Loss Given Default (LGD) / Loss Severity** rate of $45\%$.
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

## 3. Machine Learning Modeling & Calibration Pipeline

### A. Non-LLM Predictive Modeling Strategy
* **Algorithms**: Standard risk predictions utilize a `HistGradientBoostingClassifier` trained on engineered features (interest rates, original balances, current balances, delinquency histories, and modifications).
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

## 4. High-Fidelity UI/UX Showcase Layout

The frontend is built to highlight the system's underlying analytical intelligence using premium design choices:

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

## 5. Reviewer Verification Log & Corrections

The human ML architect monitored outputs and corrected several issues during the collaborative build:

| Milestone | Human Architect Guidance / Corrective Action | AI Agent Resolution |
| :--- | :--- | :--- |
| **Phase 2 & 3** | **Categorical Setitem mismatch**: "When mapping ordinal categories to numerical bands, ensure that missing codes don't raise type errors on `CategoricalDtype` vectors." | Pre-converted categorical columns to standard string objects (`.astype(str)`) before applying ordinal mappings. |
| **Phase 3** | **Scikit-learn Prefit Calibration Error**: "Scikit-learn 1.8.0 throws parameter constraints exceptions if `cv='prefit'` is specified for calibration wrapper fits." | Integrated the new `FrozenEstimator` pattern to handle pre-fit models. |
| **Phase 8** | **Groq LLM Decommissioning**: "Llama3-70b-8192 endpoint is decommissioned by the provider, causing connection failures." | Transitioned the LLM service default parameter to `qwen/qwen3.8-27b` to restore API communication. |
| **Phase 9** | **Left Join Suffix Collision**: "Scoring pipeline crashed with KeyError because left-joining test features renamed columns to `_primary` / `_servicer` formats." | Added cleanup steps to resolve join suffix collisions. |
| **Advanced Features** | **Strict Author Identifiers**: "Git commits must strictly use `Sri-Krishnan007 <srikrish2705guru@gmail.com>` as author details." | Verified git author config. Commits successfully aligned to the owner profile. |

---

## 6. Responsible AI & Compliance

* **Underwriter Advisory Clause**: Every automated LLM review or prediction is marked with a compliance header: `"Recommendation — Not a Decision"` to align with regulatory requirements for human-in-the-loop credit verification.
* **Confidence Metrics**: Predicted targets are output with statistical confidence scores.
* **Context Grounding**: Prompt templates isolate data schemas and check lists to prevent hallucinations in AI reviews.
