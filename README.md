# Loan Performance Intelligence Engine

An ML-first system for loan-data profiling, performance prediction, operational anomaly detection, scenario simulation, model explainability, and grounded LLM-assisted review. Built for the **Intain Campus FinTech Challenge 2026 (AI Track)**.

---

## 📚 Deep-Dive & Domain Documentation
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

## 🚀 The Pipeline Flow (Tasks Completed)

The engine processes data chronologically through a 9-phase pipeline:

1. **Phase 1: Data Loader, Validation & Profiling**
   * Profiles column distributions, missingness patterns, and outliers.
   * Computes train vs. test feature drift (PSI) and generates automated record-level quality scores.
2. **Phase 2: Feature Engineering & Preprocessing**
   * Processes static attributes, computes financial ratios, and aggregates rolling monthly statistics.
   * Employs time-aware target engineering (3m/6m delinquency, 12m default, and 12m prepayment flags) preventing temporal leakage.
3. **Phase 3: Risk Model Training & Calibration**
   * Trains classification models for multi-outcome prediction (delinquency, default, prepayment).
   * Implements chronological Out-of-Time (OOT) validation splits and applies Isotonic Probability Calibration to ensure reliable outputs.
4. **Phase 4: Competing Risk & Transition Survival Curves**
   * Estimates monthly state transitions (Current, Delinquent, Default, Prepaid) using a Markov transition matrix.
   * Generates event-specific cumulative survival and hazard curves.
5. **Phase 5: operational Anomaly Detection**
   * Builds a hybrid scoring system combining machine learning (Isolation Forest) with deterministic cross-source reconciliation checks (detecting conflicting servicer updates and document gaps).
6. **Phase 6: Model Explainability**
   * Outputs global feature importances using Permutation Importance.
   * Calculates local prediction drivers (positive and negative risk factors) for individual loan reviews.
7. **Phase 7: Stress Scenario Projections**
   * Simulates portfolio performance under three macro scenarios: `BASE`, `ADVERSE_CREDIT`, and `HIGH_PREPAYMENT`.
   * Projects delinquency, default, and prepayment curves at segment levels (vintage, credit band).
8. **Phase 8: Grounded LLM Reviewer Copilot**
   * Employs an LLM reviewer powered by Groq to generate underwriter review summaries and reviewer notes.
   * Grounded with static data dictionaries and validation rules, outputs are strictly classified as *recommendations*.
9. **Phase 9: Unified Inference & Scoring Pipeline**
   * Connects all preceding phases into an automated end-to-end execution pipeline, generating the final submission predictions.

---

## 📂 Project Structure

```text
├── backend/          # Python FastAPI REST API server
├── frontend/         # React + TypeScript + Tailwind UI client
├── scripts/          # Loose execution and data generation scripts
│   ├── 01_...py      # Data generators
│   └── run_phase.py  # Phase runners (Phases 1-9)
├── src/              # Core ML engine modules (profiling, modeling, LLM, scenarios)
├── data/             # Synthetic datasets and dictionary metadata
├── models/           # Pre-trained ML model joblib files
├── outputs/          # Pipeline runs intermediate outputs
├── reports/          # Data reports (anomaly, scenario, calibration, etc.)
└── package.json      # Monorepo task configurations
```

---

## 🛠️ Getting Started (How to Clone and Run)

### 1. Clone the Repository
```bash
git clone https://github.com/shubh100802/loan-verification-copilot.git
cd loan-verification-copilot
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
* The **React frontend UI** will run at: http://localhost:5173 (or http://localhost:3000)

---

## 💻 Running the Data Pipeline & Phase Scripts

All processing scripts are situated in the `scripts/` directory and can be executed directly from the project root:

* **To generate the synthetic datasets**:
  ```bash
  python scripts/01_create_static_attributes.py
  python scripts/02_create_monthly_performance_train.py
  python scripts/03_create_monthly_performance_test.py
  python scripts/04_create_servicer_updates.py
  ```

* **To run any pipeline phase script individually**:
  ```bash
  # Execute Phase 1 (Data Validation & Profiling)
  python scripts/run_phase1.py

  # Execute Phase 3 (Model Training)
  python scripts/run_phase3.py

  # Run any phase script through Phase 9 (End-to-End Scoring)
  python scripts/run_phase9.py
  ```
