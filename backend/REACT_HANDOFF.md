# React Handoff Document — API Specifications

**BASE API URL**: `http://localhost:8000`

This handbook maps every API endpoint to help the frontend React developer integrate the UI with the backend without needing to touch or understand Python ML files.

---

## 1. Diagnostics & Health

### GET `/api/health`
* **Purpose**: Check service availability and confirm model joblib binaries are loaded.
* **Response**:
  ```json
  {
    "status": "ok",
    "service": "Loan Performance Intelligence Engine",
    "version": "1.0.0",
    "artifacts_available": {
      "delinquency_3m": true,
      "delinquency_6m": true,
      "default_12m": true,
      "prepayment_12m": true,
      "next_state": true,
      "anomaly_detector": true
    }
  }
  ```
* **cURL Command**:
  ```bash
  curl -X GET http://localhost:8000/api/health
  ```

---

## 2. Portfolio Dashboard

### GET `/api/overview`
* **Purpose**: Fetch aggregates and trends for dashboard cards and charts.
* **Response**:
  ```json
  {
    "total_loans": 2000,
    "high_risk_loans": 187,
    "anomalies": 64,
    "default_rate": 0.0241,
    "delinquency_rate": 0.0642,
    "prepayment_rate": 0.0873,
    "risk_distribution": [
      {"level": "low", "count": 1780},
      {"level": "medium", "count": 100},
      {"level": "high", "count": 120}
    ],
    "status_distribution": [
      {"status": "Current", "count": 1812},
      {"status": "Delinquent", "count": 114},
      {"status": "Default", "count": 48},
      {"status": "Prepaid", "count": 26}
    ],
    "monthly_trends": [
      {
        "reporting_month": "2026-07-01",
        "delinquency_rate": 0.087,
        "default_rate": 0.022,
        "prepayment_rate": 0.016
      }
    ]
  }
  ```
* **cURL Command**:
  ```bash
  curl -X GET http://localhost:8000/api/overview
  ```

---

## 3. Loans Searching & Timeline

### GET `/api/loans`
* **Purpose**: Query, filter, and paginate through unique loans in the portfolio.
* **Query Parameters**:
  * `loan_id` (string, optional)
  * `risk_level` (low, medium, high, optional)
  * `credit_band` (string, optional)
  * `state` (string, optional)
  * `servicer` (string, optional)
  * `status` (Current, Delinquent, Default, Prepaid, optional)
  * `anomaly` (boolean, optional)
  * `vintage` (int, optional)
  * `limit` (int, default 20)
  * `offset` (int, default 0)
* **Response**:
  ```json
  {
    "items": [
      {
        "loan_id": "LN100234",
        "credit_score_band": "660-699",
        "ltv_band": "80-90",
        "dti_band": "30-40",
        "state": "CA",
        "servicer_name": "Servicer A",
        "current_status": "Current",
        "original_balance": 350000.00,
        "current_balance": 341000.00,
        "days_past_due": 0,
        "vintage": 2022,
        "risk_level": "low",
        "anomaly_score": 0.09
      }
    ],
    "total": 2000,
    "limit": 20,
    "offset": 0
  }
  ```
* **cURL Command**:
  ```bash
  curl -X GET "http://localhost:8000/api/loans?risk_level=high&limit=1"
  ```

### GET `/api/loans/{loan_id}`
* **Purpose**: Fetch origination parameters and latest performance status of a loan.
* **Response**:
  ```json
  {
    "loan_id": "LN100234",
    "original_balance": 350000.00,
    "interest_rate": 4.5,
    "vintage": 2022,
    "credit_score_band": "660-699",
    "ltv_band": "80-90",
    "dti_band": "30-40",
    "state": "CA",
    "loan_purpose": "Purchase",
    "occupancy_type": "Primary Residence",
    "property_type": "Single Family",
    "servicer_name": "Servicer A",
    "current_status": "Current",
    "current_balance": 341000.00,
    "days_past_due": 0,
    "loan_age_months": 24,
    "remaining_term_months": 336,
    "reporting_month": "2026-07-01",
    "modification_flag": 0
  }
  ```
* **Errors**: `404 Not Found` if the loan ID is invalid.
* **cURL Command**:
  ```bash
  curl -X GET http://localhost:8000/api/loans/LN100234
  ```

### GET `/api/loans/{loan_id}/timeline`
* **Purpose**: Fetch chronological monthly panel history for charts.
* **Response**:
  ```json
  {
    "loan_id": "LN100234",
    "timeline": [
      {
        "reporting_month": "2024-01-01",
        "current_balance": 348000.00,
        "days_past_due": 0,
        "current_status": "Current",
        "interest_rate": 4.5
      }
    ]
  }
  ```
* **cURL Command**:
  ```bash
  curl -X GET http://localhost:8000/api/loans/LN100234/timeline
  ```

---

## 4. Risk Prediction & Explainability

### GET `/api/loans/{loan_id}/risk`
* **Purpose**: Get ML delinquency, default, and prepayment probabilities.
* **Response**:
  ```json
  {
    "loan_id": "LN100234",
    "delinquency_probability": 0.033,
    "default_probability": 0.015,
    "prepayment_probability": 0.007,
    "next_state": "CURRENT",
    "confidence": 0.84,
    "model_versions": {
      "delinquency_3m": "v1.0",
      "delinquency_6m": "v1.0",
      "default_12m": "v1.0",
      "prepayment_12m": "v1.0",
      "next_state": "v1.0"
    }
  }
  ```
* **cURL Command**:
  ```bash
  curl -X GET http://localhost:8000/api/loans/LN100234/risk
  ```

### GET `/api/loans/{loan_id}/explanation`
* **Purpose**: Fetch global permutation importance ranks and local risk factors.
* **Response**:
  ```json
  {
    "loan_id": "LN100234",
    "global_features": [
      {"feature": "days_past_due", "importance": 0.0184}
    ],
    "local_drivers": {
      "positive": ["high_dti_ratio"],
      "negative": ["high_credit_score"]
    },
    "confidence": 0.84,
    "false_positive_context": "...",
    "false_negative_context": "..."
  }
  ```
* **cURL Command**:
  ```bash
  curl -X GET http://localhost:8000/api/loans/LN100234/explanation
  ```

---

## 5. Stress Scenario Simulations

### POST `/api/scenarios/run`
* **Purpose**: Stress test the active portfolio under a scenario.
* **Request Body**:
  ```json
  {
    "scenario": "adverse_credit",
    "segments": ["credit_band", "state"]
  }
  ```
  *(Valid scenarios: `BASE`, `ADVERSE_CREDIT`, `HIGH_PREPAYMENT`)*
* **Response**:
  ```json
  {
    "scenario": "ADVERSE_CREDIT",
    "portfolio": {
      "delinquency_rate": 0.1029,
      "default_rate": 0.0384,
      "prepayment_rate": 0.0067
    },
    "segments": [
      {
        "credit_band": "660-699",
        "state": "CA",
        "delinquency_rate": 0.125,
        "default_rate": 0.045,
        "prepayment_rate": 0.005
      }
    ],
    "drivers": [
      {"variable": "Default Multiplier", "value": 2.25}
    ]
  }
  ```
* **cURL Command**:
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"scenario":"adverse_credit","segments":["state"]}' http://localhost:8000/api/scenarios/run
  ```

---

## 6. Underwriter Review Copilot

### POST `/api/reviewer`
* **Purpose**: Ground and trigger LLM reviewer copilot summary.
* **Request Body**:
  ```json
  {
    "loan_id": "LN100234"
  }
  ```
* **Response**:
  ```json
  {
    "loan_id": "LN100234",
    "summary": "This loan has reconciliation conflicts...",
    "recommendation": "Priority Review recommended due to...",
    "action": "Priority Review",
    "confidence": 0.82,
    "disclaimer": "Recommendation — Not a Decision",
    "model": "qwen/qwen3.8-27b",
    "timestamp": "2026-08-26T20:30:00",
    "evidence": ["Balance conflict: Primary=1366653.97, Servicer=1444691.13"]
  }
  ```
* **cURL Command**:
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"loan_id":"LN101264"}' http://localhost:8000/api/reviewer
  ```

### POST `/api/reviewer/{loan_id}/decision`
* **Purpose**: Record human review decisions (Accepted / Rejected).
* **Request Body**:
  ```json
  {
    "decision": "accepted",
    "reviewer_note": "Conflicts resolved with servicer. Balance adjusted."
  }
  ```
* **Response**:
  ```json
  {
    "status": "success",
    "loan_id": "LN100234",
    "decision": "accepted",
    "timestamp": "2026-08-26T20:30:05"
  }
  ```
* **cURL Command**:
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"decision":"accepted","reviewer_note":"ok"}' http://localhost:8000/api/reviewer/LN101264/decision
  ```
