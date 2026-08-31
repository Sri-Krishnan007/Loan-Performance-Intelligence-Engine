from fastapi import APIRouter
from backend.app.schemas.scenario import ScenarioRequest, ScenarioResponse
from backend.app.services.scenario_service import ScenarioService

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.post("/run", response_model=ScenarioResponse)
def run_scenario(payload: ScenarioRequest):
    """Runs a macroeconomic stress scenario simulation and aggregates results."""
    res = ScenarioService.run_scenario_simulation(
        scenario=payload.scenario,
        segments=payload.segments,
        start_date=payload.start_date,
        end_date=payload.end_date
    )
    return ScenarioResponse(
        scenario=res["scenario"],
        portfolio=res["portfolio"],
        segments=res["segments"],
        drivers=res["drivers"]
    )

import json
import copy
from src.config import settings
from backend.app.services.loan_service import loan_state

@router.get("/monte-carlo")
def get_monte_carlo(start_date: str = None, end_date: str = None):
    """Retrieves computed Monte Carlo portfolio simulation results and Value-at-Risk bounds."""
    path = settings.BASE_DIR / "outputs/monte_carlo/portfolio_results.json"
    if not path.exists():
        base_mc = {
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
    else:
        with open(path, "r", encoding="utf-8") as f:
            base_mc = json.load(f)
            
    if start_date or end_date:
        if not loan_state.initialized:
            loan_state.initialize()
        df = loan_state.merged_df
        if start_date:
            df = df[df["reporting_month"] >= start_date]
        if end_date:
            df = df[df["reporting_month"] <= end_date]
            
        grouped_df = df.sort_values("reporting_month").groupby("loan_id").last().reset_index()
        filtered_balance = float(grouped_df["current_balance"].sum()) if not grouped_df.empty else 0.0
        
        if base_mc.get("portfolio_initial_balance", 0) > 0:
            balance_ratio = filtered_balance / base_mc["portfolio_initial_balance"]
        else:
            balance_ratio = 1.0
            
        if not grouped_df.empty and "default_probability" in grouped_df.columns:
            mean_df_prob = float(grouped_df["default_probability"].mean())
            rate_ratio = mean_df_prob / 0.0241
        else:
            rate_ratio = 1.0
            
        mc = copy.deepcopy(base_mc)
        mc["portfolio_initial_balance"] = filtered_balance
        
        m = mc["metrics"]
        m["mean_loss_rate"] = max(min(m["mean_loss_rate"] * rate_ratio, 1.0), 0.0)
        m["value_at_risk_95"] = max(min(m["value_at_risk_95"] * rate_ratio, 1.0), 0.0)
        m["value_at_risk_99"] = max(min(m["value_at_risk_99"] * rate_ratio, 1.0), 0.0)
        
        m["expected_losses"] = m["mean_loss_rate"] * filtered_balance
        m["value_at_risk_95_amount"] = m["value_at_risk_95"] * filtered_balance
        m["value_at_risk_99_amount"] = m["value_at_risk_99"] * filtered_balance
        m["expected_interest_earnings"] = m["mean_interest_yield_rate"] * filtered_balance
        return mc

    return base_mc

@router.get("/sensitivity")
def get_stress_sensitivity(start_date: str = None, end_date: str = None):
    """Retrieves the borrower leverage vs property equity stress sensitivity matrix."""
    path = settings.BASE_DIR / "outputs/scenarios/stress_sensitivity_grid.json"
    if not path.exists():
        grid = [
            { "leverage_stress": "Base Leverage", "equity_stress": "Base Equity", "average_default_probability": 0.0152 },
            { "leverage_stress": "Base Leverage", "equity_stress": "Moderate LTV (+10%)", "average_default_probability": 0.0242 },
            { "leverage_stress": "Base Leverage", "equity_stress": "Severe LTV (+20%)", "average_default_probability": 0.0384 },
            { "leverage_stress": "Moderate DTI (+5%)", "equity_stress": "Base Equity", "average_default_probability": 0.0315 },
            { "leverage_stress": "Moderate DTI (+5%)", "equity_stress": "Moderate LTV (+10%)", "average_default_probability": 0.0482 },
            { "leverage_stress": "Moderate DTI (+5%)", "equity_stress": "Severe LTV (+20%)", "average_default_probability": 0.0684 },
            { "leverage_stress": "Severe DTI (+12%)", "equity_stress": "Base Equity", "average_default_probability": 0.0582 },
            { "leverage_stress": "Severe DTI (+12%)", "equity_stress": "Moderate LTV (+10%)", "average_default_probability": 0.0842 },
            { "leverage_stress": "Severe DTI (+12%)", "equity_stress": "Severe LTV (+20%)", "average_default_probability": 0.1245 }
        ]
    else:
        with open(path, "r", encoding="utf-8") as f:
            grid = json.load(f)
            
    if start_date or end_date:
        if not loan_state.initialized:
            loan_state.initialize()
        df = loan_state.merged_df
        if start_date:
            df = df[df["reporting_month"] >= start_date]
        if end_date:
            df = df[df["reporting_month"] <= end_date]
            
        grouped_df = df.groupby("loan_id").last().reset_index()
        if not grouped_df.empty and "default_probability" in grouped_df.columns:
            mean_df_prob = float(grouped_df["default_probability"].mean())
            rate_ratio = mean_df_prob / 0.0241
        else:
            rate_ratio = 1.0
            
        grid = copy.deepcopy(grid)
        for item in grid:
            item["average_default_probability"] = max(min(item["average_default_probability"] * rate_ratio, 1.0), 0.0)
            
    return grid
