from fastapi import APIRouter, Query
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.anomaly import AnomalyResponse, AnomalyListItem
from backend.app.services.anomaly_service import AnomalyService
from typing import Optional

router = APIRouter(tags=["Anomalies"])

@router.get("/loans/{loan_id}/anomaly", response_model=AnomalyResponse)
def get_loan_anomaly_details(loan_id: str):
    """Retrieves operational anomaly score and reconciliation audit details for a loan."""
    return AnomalyService.get_loan_anomaly(loan_id)

@router.get("/anomalies", response_model=PaginatedResponse)
def list_portfolio_anomalies(
    severity: Optional[str] = Query(None, description="Filter by anomaly severity (LOW, MEDIUM, HIGH)"),
    exception_type: Optional[str] = Query(None, description="Filter by deterministic exception type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieves and paginates loans flagged with reconciliation updates discrepancies."""
    res = AnomalyService.list_anomalies(
        severity=severity,
        exception_type=exception_type,
        limit=limit,
        offset=offset
    )
    return PaginatedResponse(
        items=res["items"],
        total=res["total"],
        limit=res["limit"],
        offset=res["offset"]
    )
