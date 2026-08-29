from fastapi import APIRouter
from backend.app.schemas.overview import OverviewResponse
from backend.app.services.loan_service import loan_state
import pandas as pd

router = APIRouter(prefix="/overview", tags=["Overview"])

@router.get("", response_model=OverviewResponse)
def get_portfolio_overview():
    """Generates dynamic summary metrics and trends for the active mortgage portfolio."""
    if not loan_state.initialized:
        loan_state.initialize()
        
    latest = loan_state.latest_records
    merged = loan_state.merged_df
    
    total_loans = len(latest)
    
    high_risk_loans = len(latest[
        (latest["action"] == "Priority Review") | (latest["default_probability"] > 0.10)
    ])
    
    anomalies = len(latest[latest["anomaly_score"] > 0.5])
    
    default_rate = float((latest["current_status"] == "Default").mean()) if total_loans > 0 else 0.0
    delinquency_rate = float((latest["current_status"] == "Delinquent").mean()) if total_loans > 0 else 0.0
    prepayment_rate = float((latest["current_status"] == "Prepaid").mean()) if total_loans > 0 else 0.0
    
    risk_vc = latest["risk_level"].value_counts()
    risk_dist = [{"level": str(k), "count": int(v)} for k, v in risk_vc.items()]
    
    status_vc = latest["current_status"].value_counts()
    status_dist = [{"status": str(k), "count": int(v)} for k, v in status_vc.items()]
    
    # Monthly trends (past 12 active reporting months)
    monthly_agg = merged.groupby("reporting_month").agg({
        "delinquency_probability": "mean",
        "default_probability": "mean",
        "prepayment_probability": "mean"
    }).reset_index()
    
    monthly_agg = monthly_agg.sort_values("reporting_month").tail(12)
    
    monthly_trends = []
    for _, row in monthly_agg.iterrows():
        monthly_trends.append({
            "reporting_month": str(row["reporting_month"]),
            "delinquency_rate": float(row["delinquency_probability"]),
            "default_rate": float(row["default_probability"]),
            "prepayment_rate": float(row["prepayment_probability"])
        })
        
    return OverviewResponse(
        total_loans=total_loans,
        high_risk_loans=high_risk_loans,
        anomalies=anomalies,
        default_rate=default_rate,
        delinquency_rate=delinquency_rate,
        prepayment_rate=prepayment_rate,
        risk_distribution=risk_dist,
        status_distribution=status_dist,
        monthly_trends=monthly_trends
    )
