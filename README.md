# Loan Performance Intelligence Engine

An ML-first system for loan-data profiling, performance prediction, operational anomaly detection, scenario simulation, model explainability, and grounded LLM-assisted review. Built for the **Intain Campus FinTech Challenge 2026 (AI Track)**.

---

## 📚 Deep-Dive & Domain Documentation
* **[AI Development Log & Architecture](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/LAC/loan-verification-copilot/docs/AI_DEVELOPMENT_LOG.md)**: A detailed log of the collaborative development process, including:
  - **Case Studies**: Resolving Pydantic V2 environment crashes, join collisions, and TypeScript strict unused locals.
  - **Mathematical Formulations**: Markov transitions, Monte Carlo Expected Loss, and joint double-trigger stress sensitivity math.
  - **Human Review Process**: Rejected AI outputs (e.g. SHAP, prefit calibration, decommissioned llama3 Groq model parameters).
* **[ML Deep-Dive & Interview Preparation Guide](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/LAC/loan-verification-copilot/docs/ml_deep_dive_interview_guide.md)**: A comprehensive guide covering:
  - **Phase-by-Phase Process & Workflow** detailing the engineering rationale.
  - **Metric Selection Rationale** (Why we use ROC-AUC, PR-AUC, F1, Recall at Fixed Precision, Brier, and ECE).
  - **Probability Calibration & Monotonicity** (Isotonic Regression vs. Platt Scaling).
  - **Survival Modeling** for competing default and prepayment risks.
  - **Interview Q&A Prep Sheet** with expected questions and architectural defense strategies.
* **[Mortgage Underwriting & Credit Domain Intelligence Guide](file:///c:/Sk%20PC/My%20Guidelines/Placement%20Prep/INTAIN/LAC/loan-verification-copilot/docs/loan_domain_intelligence_guide.md)**: A domain training guide explaining:
  - **Underwriting Parameters & Limits** (FICO credit bands, LTV ratios, DTI bands).
  - **Credit State Transitions** (Current, Delinquent [30+ DPD], Default [90+ DPD], and Prepayment).
  - **Operational Exception & Auditing Rules** (Balance reconciliation conflicts, document status gaps).
  - **Regulatory GSE Guidelines (Fannie Mae & Freddie Mac)** conforming thresholds.
  - **Expected Loss & Loss Given Default (LGD)** formulas and stress-testing Presets.

---

## 🚀 Key Pipeline Phases & Advanced Features

The engine processes data chronologically through a 9-phase pipeline combined with 5 advanced simulation features:

### Core Pipeline Phases:
1. **Phase 1: Data Loader, Validation & Profiling**: Computes train vs. test feature drift (PSI) and generates automated record-level quality scores.
2. **Phase 2: Feature Engineering & Preprocessing**: Computes financial ratios and aggregates rolling monthly statistics with chronological leakage controls.
3. **Phase 3: Risk Model Training & Calibration**: Trains classification models for multi-outcome prediction with chronological Out-of-Time (OOT) splits and Isotonic Calibration.
4. **Phase 4: Competing Risk & Transition Survival Curves**: Estimates monthly credit state transitions using a Markov transition matrix.
5. **Phase 5: Operational Anomaly Detection**: Combines Isolation Forest scores with balance ledger reconciliation discrepancies.
6. **Phase 6: Model Explainability**: Computes global importances using Permutation Importance and extracts local risk drivers.
7. **Phase 7: Stress Scenario Projections**: Simulates portfolio performance under `BASE`, `ADVERSE_CREDIT`, and `HIGH_PREPAYMENT` stress curves.
8. **Phase 8: Grounded LLM Reviewer Copilot**: Generates compliant underwriter reviews grounded in data dictionary schemas.
9. **Phase 9: Unified Inference & Scoring**: Runs end-to-end scoring pipeline and exports predictions.

### Advanced Risk & Simulation Modules:
* **Monte Carlo Portfolio Simulator**: Runs 1,000 trials over a 12-month projection horizon to compute expected portfolio credit losses, standard deviations, and Credit Value-at-Risk limits (95% and 99% VaR).
* **Feature Cluster Stress Sensitivity Grid**: Generates a 3x3 default probability matrix evaluating borrower risk under joint stress of Borrower Leverage (DTI + rates) and Property Equity Loss (LTV).
* **Agentic Experiment Runner**: Automatically sweeps classifier hyperparameter configurations (learning rate, iterations, depth) and tunes predictions.
* **Local MLflow Runs Tracker**: Structures local metadata and parameters logs inside `mlruns/` compliant with MLflow UI servers.
* **Counterfactual Risk Explanations**: Computes targeted underwriting adjustments required to transition high-risk loan profiles back to prime compliance status.

---

## 📂 Project Structure

```text
├── backend/          # Python FastAPI REST API server
├── frontend/         # React + TypeScript + Tailwind client (Glassmorphic UI)
├── scripts/          # Loose execution, generator and tuning scripts
│   ├── 01_...py      # Data generators
│   ├── run_phase.py  # Phase runners (Phases 1-9)
│   ├── run_monte_carlo.py          # Vectorized portfolio Monte Carlo simulation
│   ├── agentic_experiment_runner.py # MLflow hyperparameter tuning sweeps
│   └── feature_stress_sensitivity.py # Joint LTV vs DTI stress test grid
├── src/              # Core ML engine modules (profiling, modeling, LLM, explainability)
├── data/             # Synthetic datasets and dictionary metadata
├── models/           # Pre-trained ML model joblib files
├── mlruns/           # MLflow local run tracking logs
├── outputs/          # Pipeline runs intermediate outputs & JSON matrices
├── reports/          # Data reports (anomaly, scenario, calibration, sensitivity, VaR)
└── package.json      # Monorepo task configurations
```

---

## 🛠️ Getting Started (How to Clone and Run)

### 1. Clone the Repository
```bash
git clone https://github.com/Sri-Krishnan007/Loan-Performance-Intelligence-Engine.git
cd Loan-Performance-Intelligence-Engine
```

### 2. Install All Dependencies
Install node dependencies (for monorepo and React frontend) and Python requirements:
```bash
# Install root and frontend npm packages
npm run install:all

# Install Python backend and ML pipeline requirements
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` in the root folder, and `.env.example` in the backend folder:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```
*Note: Make sure to add your `GROQ_API_KEY` to the `.env` file to enable the AI Reviewer Copilot features.*

### 4. Run Development Servers (Parallel Mode)
To launch the React client and the FastAPI backend server in parallel, run:
```bash
npm run dev
```
* The **FastAPI backend** will run at: http://localhost:8000
* The **React frontend UI** will run at: http://localhost:5173

---

## 💻 Running the Data Pipeline & Advanced Simulations

All processing scripts are situated in the `scripts/` directory and can be executed directly from the project root:

### Core Ingestion & Pipelines:
```bash
# Generate synthetic raw datasets
python scripts/01_create_static_attributes.py
python scripts/02_create_monthly_performance_train.py
python scripts/03_create_monthly_performance_test.py
python scripts/04_create_servicer_updates.py

# Execute Pipeline Phase Scripts (Phases 1 through 9)
python scripts/run_phase1.py
python scripts/run_phase3.py
python scripts/run_phase9.py
```

### Advanced Simulation Engines:
```bash
# Execute Monte Carlo Portfolio Simulation & VaR Limits
python scripts/run_monte_carlo.py

# Execute Joint DTI vs LTV Stress Sensitivity Grid
python scripts/feature_stress_sensitivity.py

# Run Agentic Hyperparameter Sweeping & Local MLflow logging
python scripts/agentic_experiment_runner.py
```
