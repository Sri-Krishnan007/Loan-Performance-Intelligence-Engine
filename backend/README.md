# Loan Performance Intelligence Engine — FastAPI Backend

This directory houses the FastAPI production-ready API layer for the Loan Performance Intelligence Engine. It wraps the core machine learning classifiers (delinquency, default, prepayment, next-state), the empirical competing-risk survival curves, and the Groq LLM reviewer copilot.

---

## 1. Purpose
The backend exposes clean REST endpoints returning predictable JSON responses. It abstracts the complex data science, feature engineering, and model inference from the React developer, enabling independent frontend development.

---

## 2. Architecture
```
React Frontend (localhost:3000 / 5173)
      │
      │ (HTTP / JSON / CORS Allowed)
      ▼
FastAPI Backend (localhost:8000)
      │
      │ (Invokes Python services & caches data at startup)
      ▼
Existing ML Engine (Scikit-Learn, Pandas, Parquet, Groq Client)
```

---

## 3. Installation & Setup
1. Navigate to the backend folder or run from the project root.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Copy the environment template:
   ```bash
   copy backend\.env.example backend\.env
   ```
4. Update `GROQ_API_KEY` in `backend/.env` or the root `.env` file.

---

## 4. Run Command
Run the server using Uvicorn with auto-reload:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
Visit the self-documenting APIs:
* **Swagger OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 5. API Endpoints List

### Health & Diagnostics
* `GET /api/health`: General service diagnostics and model joblib files availability flags.
* `GET /api/model-health`: Out-of-time (OOT) validation metrics, roc-auc, and Brier scores.
* `GET /api/data-quality`: Data profiling metrics (missingness, outliers, drift, validation breaks).

### Portfolio & Loans
* `GET /api/overview`: Unified stats for dashboard cards (total loans, default rate, trends, distributions).
* `GET /api/loans`: Search and pagination for unique loans (filters by risk, status, state, anomalies, vintage).
* `GET /api/loans/{loan_id}`: Static parameters and latest monthly performance details.
* `GET /api/loans/{loan_id}/timeline`: Chronological month-by-month historical timeline.

### Predictions & Explainability
* `GET /api/loans/{loan_id}/risk`: Delinquency, default, and prepayment risk probabilities.
* `GET /api/loans/{loan_id}/explanation`: Permutation importances and local positive/negative risk drivers.

### Anomalies & Exceptions
* `GET /api/anomalies`: Paginated operational anomaly feed (mismatched updates and documentation gaps).
* `GET /api/loans/{loan_id}/anomaly`: Detailed anomaly scores, exception details, and evidence.

### Stress Testing & Reviewer
* `POST /api/scenarios/run`: Runs scenario simulation aggregates (BASE, ADVERSE_CREDIT, HIGH_PREPAYMENT) on the active portfolio.
* `POST /api/reviewer`: Generates grounded LLM summary and action plan for a loan.
* `POST /api/reviewer/{loan_id}/decision`: Persists human underwriter decision (accepted/rejected) and reviewer note.

---

## 6. How ML Artifacts Are Loaded
At startup, `LoanDataState` is initialized inside `app/services/loan_service.py`. It parses `test_features.parquet` and `submission.csv` predictions once, caching them in memory for near-instantaneous indexing. This eliminates disk reading overhead on every individual request.

---

## 7. Known Limitations
* **Cold Start**: First initialization can take up to 2 seconds to load parquet features.
* **Censoring**: Model risk scores reflect rolling lookaheads up to the July 2026 cutoff window.
