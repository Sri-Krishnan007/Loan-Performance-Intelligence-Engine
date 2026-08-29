import os
import sys
from pathlib import Path

# Add root folder to path so backend package can be imported
root_path = str(Path(__file__).resolve().parents[2])
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.loan_service import loan_state
import pytest

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_state():
    # Force data state initialization
    loan_state.initialize()

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] in ["ok", "warning"]
    assert json_data["service"] == "Loan Performance Intelligence Engine"
    assert "artifacts_available" in json_data

def test_overview():
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_loans" in data
    assert "high_risk_loans" in data
    assert "anomalies" in data
    assert "default_rate" in data
    assert "risk_distribution" in data
    assert "monthly_trends" in data

def test_loans_search():
    response = client.get("/api/loans?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 5

def test_loan_details():
    valid_id = loan_state.latest_records["loan_id"].iloc[0]
    response = client.get(f"/api/loans/{valid_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["loan_id"] == valid_id
    assert "original_balance" in data
    assert "current_balance" in data
    assert "current_status" in data

def test_invalid_loan_details():
    response = client.get("/api/loans/INVALID_ID")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_risk_prediction():
    valid_id = loan_state.latest_records["loan_id"].iloc[0]
    response = client.get(f"/api/loans/{valid_id}/risk")
    assert response.status_code == 200
    data = response.json()
    assert data["loan_id"] == valid_id
    assert "delinquency_probability" in data
    assert "default_probability" in data
    assert "next_state" in data

def test_anomaly_details():
    valid_id = loan_state.latest_records["loan_id"].iloc[0]
    response = client.get(f"/api/loans/{valid_id}/anomaly")
    assert response.status_code == 200
    data = response.json()
    assert data["loan_id"] == valid_id
    assert "anomaly_score" in data
    assert "exception_required" in data
    assert "drivers" in data

def test_anomaly_list():
    response = client.get("/api/anomalies?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_explanation():
    valid_id = loan_state.latest_records["loan_id"].iloc[0]
    response = client.get(f"/api/loans/{valid_id}/explanation")
    assert response.status_code == 200
    data = response.json()
    assert data["loan_id"] == valid_id
    assert "global_features" in data
    assert "local_drivers" in data

def test_data_quality():
    response = client.get("/api/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert "batch_quality_score" in data
    assert "missingness" in data
    assert "relationship_breaks" in data

def test_model_health():
    response = client.get("/api/model-health")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "validation" in data

def test_run_scenario_success():
    payload = {
        "scenario": "adverse_credit",
        "segments": ["state", "credit_band"]
    }
    response = client.post("/api/scenarios/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] == "ADVERSE_CREDIT"
    assert "portfolio" in data
    assert "segments" in data

def test_run_scenario_invalid():
    payload = {
        "scenario": "unknown_scenario",
        "segments": ["state"]
    }
    response = client.post("/api/scenarios/run", json=payload)
    assert response.status_code == 400
    assert "invalid scenario" in response.json()["detail"].lower()

def test_reviewer_copilot():
    valid_id = loan_state.latest_records["loan_id"].iloc[0]
    payload = {"loan_id": valid_id}
    response = client.post("/api/reviewer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["loan_id"] == valid_id
    assert "summary" in data
    assert "recommendation" in data
    assert data["disclaimer"] == "Recommendation — Not a Decision"

def test_record_reviewer_decision():
    valid_id = loan_state.latest_records["loan_id"].iloc[0]
    payload = {
        "decision": "accepted",
        "reviewer_note": "Reconciliation resolved with servicer."
    }
    response = client.post(f"/api/reviewer/{valid_id}/decision", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["loan_id"] == valid_id
    assert data["decision"] == "accepted"
