from fastapi import APIRouter
from backend.app.schemas.reviewer import ReviewerRequest, ReviewerResponse, DecisionRequest, DecisionResponse
from backend.app.services.reviewer_service import ReviewerService

router = APIRouter(prefix="/reviewer", tags=["Reviewer"])

@router.post("", response_model=ReviewerResponse)
def run_reviewer_copilot(payload: ReviewerRequest):
    """Generates a natural-language copilot review summary grounded on ML indicators."""
    res = ReviewerService.run_llm_reviewer(payload.loan_id, payload.tone)
    return ReviewerResponse(
        loan_id=res["loan_id"],
        summary=res["summary"],
        recommendation=res["recommendation"],
        action=res["action"],
        confidence=res["confidence"],
        disclaimer=res["disclaimer"],
        model=res["model"],
        timestamp=res["timestamp"],
        evidence=res["evidence"]
    )

@router.post("/{loan_id}/decision", response_model=DecisionResponse)
def record_reviewer_decision(loan_id: str, payload: DecisionRequest):
    """Saves a reviewer human verification action in a persistent database."""
    res = ReviewerService.save_reviewer_decision(
        loan_id=loan_id,
        decision=payload.decision,
        reviewer_note=payload.reviewer_note
    )
    return DecisionResponse(
        status=res["status"],
        loan_id=res["loan_id"],
        decision=res["decision"],
        timestamp=res["timestamp"]
    )
