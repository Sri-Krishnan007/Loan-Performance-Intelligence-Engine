from fastapi import APIRouter, Query, HTTPException
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.loan import LoanItem, LoanDetails, TimelineResponse, TimelineRecord
from backend.app.services.loan_service import loan_state
from typing import Optional
import pandas as pd

router = APIRouter(prefix="/loans", tags=["Loans"])

@router.get("", response_model=PaginatedResponse)
def search_loans(
    loan_id: Optional[str] = Query(None, description="Filter by loan ID substring"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (low, medium, high)"),
    credit_band: Optional[str] = Query(None, description="Filter by credit score band"),
    state: Optional[str] = Query(None, description="Filter by US state"),
    servicer: Optional[str] = Query(None, description="Filter by servicer name"),
    status: Optional[str] = Query(None, description="Filter by current payment status"),
    anomaly: Optional[bool] = Query(None, description="Filter for loans with anomaly score > 0.5"),
    vintage: Optional[int] = Query(None, description="Filter by loan vintage year"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Searches and paginates unique loans matching specific portfolio filters."""
    if not loan_state.initialized:
        loan_state.initialize()
        
    df = loan_state.latest_records.copy()
    
    if loan_id:
        df = df[df["loan_id"].astype(str).str.contains(loan_id, case=False)]
    if risk_level:
        df = df[df["risk_level"] == risk_level.lower()]
    if credit_band:
        df = df[df["credit_score_band"].astype(str) == credit_band]
    if state:
        df = df[df["state"].astype(str).str.lower() == state.lower()]
    if servicer:
        df = df[df["servicer_name"].astype(str).str.lower() == servicer.lower()]
    if status:
        df = df[df["current_status"].astype(str).str.lower() == status.lower()]
    if anomaly is not None:
        if anomaly:
            df = df[df["anomaly_score"] > 0.5]
        else:
            df = df[df["anomaly_score"] <= 0.5]
    if vintage:
        df = df[df["vintage"] == vintage]
        
    total = len(df)
    paginated_df = df.iloc[offset : offset + limit]
    
    items = []
    for _, row in paginated_df.iterrows():
        items.append(LoanItem(
            loan_id=str(row["loan_id"]),
            credit_score_band=str(row["credit_score_band"]),
            ltv_band=str(row["ltv_band"]),
            dti_band=str(row["dti_band"]),
            state=str(row["state"]),
            servicer_name=str(row["servicer_name"]),
            current_status=str(row["current_status"]),
            original_balance=float(row["original_balance"]),
            current_balance=float(row["current_balance"]),
            days_past_due=int(row["days_past_due"]),
            vintage=int(row["vintage"]),
            risk_level=str(row["risk_level"]),
            anomaly_score=float(row["anomaly_score"])
        ))
        
    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)

@router.get("/{loan_id}", response_model=LoanDetails)
def get_loan_details(loan_id: str):
    """Retrieves original parameters and latest monthly performance details for a loan."""
    if not loan_state.initialized:
        loan_state.initialize()
        
    loan_records = loan_state.merged_df[loan_state.merged_df["loan_id"] == loan_id]
    if loan_records.empty:
        raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found.")
        
    latest_record = loan_records.iloc[-1]
    
    return LoanDetails(
        loan_id=loan_id,
        original_balance=float(latest_record["original_balance"]),
        interest_rate=float(latest_record["interest_rate"]),
        vintage=int(latest_record["vintage"]),
        credit_score_band=str(latest_record["credit_score_band"]),
        ltv_band=str(latest_record["ltv_band"]),
        dti_band=str(latest_record["dti_band"]),
        state=str(latest_record["state"]),
        loan_purpose=str(latest_record["loan_purpose"]),
        occupancy_type=str(latest_record["occupancy_type"]),
        property_type=str(latest_record["property_type"]),
        servicer_name=str(latest_record["servicer_name"]),
        current_status=str(latest_record["current_status"]),
        current_balance=float(latest_record["current_balance"]),
        days_past_due=int(latest_record["days_past_due"]),
        loan_age_months=int(latest_record["loan_age_months"]),
        remaining_term_months=int(latest_record["remaining_term_months"]),
        reporting_month=str(latest_record["reporting_month"]),
        modification_flag=int(latest_record.get("modification_flag", 0))
    )

@router.get("/{loan_id}/timeline", response_model=TimelineResponse)
def get_loan_timeline(loan_id: str):
    """Retrieves chronological monthly performance history for a single loan."""
    if not loan_state.initialized:
        loan_state.initialize()
        
    loan_records = loan_state.merged_df[loan_state.merged_df["loan_id"] == loan_id]
    if loan_records.empty:
        raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found.")
        
    sorted_records = loan_records.sort_values("reporting_month")
    
    timeline = []
    for _, row in sorted_records.iterrows():
        timeline.append(TimelineRecord(
            reporting_month=str(row["reporting_month"]),
            current_balance=float(row["current_balance"]),
            days_past_due=int(row["days_past_due"]),
            current_status=str(row["current_status"]),
            interest_rate=float(row["interest_rate"])
        ))
        
    return TimelineResponse(loan_id=loan_id, timeline=timeline)
