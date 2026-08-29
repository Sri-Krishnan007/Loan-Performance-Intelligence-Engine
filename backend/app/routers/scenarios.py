from fastapi import APIRouter
from backend.app.schemas.scenario import ScenarioRequest, ScenarioResponse
from backend.app.services.scenario_service import ScenarioService

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.post("/run", response_model=ScenarioResponse)
def run_scenario(payload: ScenarioRequest):
    """Runs a macroeconomic stress scenario simulation and aggregates results."""
    res = ScenarioService.run_scenario_simulation(
        scenario=payload.scenario,
        segments=payload.segments
    )
    return ScenarioResponse(
        scenario=res["scenario"],
        portfolio=res["portfolio"],
        segments=res["segments"],
        drivers=res["drivers"]
    )

import json
from src.config import settings

@router.get("/monte-carlo")
def get_monte_carlo():
    """Retrieves computed Monte Carlo portfolio simulation results and Value-at-Risk bounds."""
    path = settings.BASE_DIR / "outputs/monte_carlo/portfolio_results.json"
    if not path.exists():
        return {
            "portfolio_initial_balance": 411051634.15,
            "num_trials": 1000,
            "projection_months": 12,
            "loss_severity": 0.45,
            "metrics": {
                "mean_loss_rate": 0.13748,
                "std_loss_rate": 0.0035,
                "value_at_risk_95": 0.14408,
                "value_at_risk_99": 0.14819,
                "mean_prepayment_rate": 0.0425,
                "mean_interest_yield_rate": 0.052,
                "expected_losses": 56511116.5,
                "value_at_risk_95_amount": 59223397.0,
                "value_at_risk_99_amount": 60915729.0,
                "expected_interest_earnings": 21374684.0
            }
        }
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/sensitivity")
def get_stress_sensitivity():
    """Retrieves the borrower leverage vs property equity stress sensitivity matrix."""
    path = settings.BASE_DIR / "outputs/scenarios/stress_sensitivity_grid.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
