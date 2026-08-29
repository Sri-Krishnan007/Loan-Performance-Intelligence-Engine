from backend.app.services.loan_service import loan_state
from backend.app.config import api_settings
from src.llm.reviewer import LLMReviewer, MockLLMReviewer
from fastapi import HTTPException
import pandas as pd
import csv
import logging
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)

class ReviewerService:
    @staticmethod
    def run_llm_reviewer(loan_id: str) -> dict:
        """Invokes Groq LLM Reviewer with grounded ML metrics context."""
        if not loan_state.initialized:
            loan_state.initialize()
            
        loan_records = loan_state.merged_df[loan_state.merged_df["loan_id"] == loan_id]
        if loan_records.empty:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found.")
            
        latest_record = loan_records.iloc[-1]
        
        # Build dictionary parameters for LLM reviewer
        loan_record_dict = latest_record.to_dict()
        prediction_metrics_dict = {
            "default_probability": float(latest_record.get("default_probability", 0.0)),
            "delinquency_probability": float(latest_record.get("delinquency_probability", 0.0)),
            "prepayment_probability": float(latest_record.get("prepayment_probability", 0.0)),
            "next_state": str(latest_record.get("next_state", "Current")),
            "anomaly_score": float(latest_record.get("anomaly_score", 0.0)),
            "top_drivers": str(latest_record.get("top_drivers", "None")),
            "exception_required": int(str(latest_record.get("exception_type")) != "None"),
            "exception_type": str(latest_record.get("exception_type", "None")),
            "anomaly_evidence": str(loan_state.anomaly_reports.get(loan_id, {}).get("evidence", "No reconciliation discrepancies detected."))
        }
        
        api_key = api_settings.GROQ_API_KEY
        reviewer_note = ""
        model_name = "mock-model"
        
        if api_key and api_key.startswith("gsk_"):
            try:
                reviewer = LLMReviewer(api_key=api_key)
                reviewer_note = reviewer.generate_reviewer_note(loan_record_dict, prediction_metrics_dict)
                model_name = reviewer.client.model
            except Exception as e:
                logger.warning(f"Groq API call failed: {e}. Falling back to MockLLMReviewer.")
                mock = MockLLMReviewer()
                reviewer_note = mock.generate_reviewer_note(loan_record_dict, prediction_metrics_dict)
        else:
            logger.info("GROQ_API_KEY is offline or empty. Using MockLLMReviewer.")
            mock = MockLLMReviewer()
            reviewer_note = mock.generate_reviewer_note(loan_record_dict, prediction_metrics_dict)
            
        # Parse note sections
        summary_idx = reviewer_note.find("**SUMMARY**")
        dq_idx = reviewer_note.find("**DATA QUALITY")
        rec_idx = reviewer_note.find("**RECOMMENDED")
        
        summary = "No summary available."
        recommendation = "No recommendation available."
        
        if summary_idx != -1:
            end_idx = dq_idx if dq_idx != -1 else (rec_idx if rec_idx != -1 else len(reviewer_note))
            summary = reviewer_note[summary_idx + len("**SUMMARY**"):end_idx].strip(": \n*")
            
        if rec_idx != -1:
            recommendation = reviewer_note[rec_idx + len("**RECOMMENDED REVIEWER ACTION**"):].strip(": \n*")
        else:
            paragraphs = [p for p in reviewer_note.split("\n\n") if p.strip()]
            if len(paragraphs) > 1:
                summary = paragraphs[0].strip()
                recommendation = paragraphs[-1].strip()
            else:
                summary = reviewer_note
                recommendation = "Investigate flagged conflicts."
                
        evidence = [prediction_metrics_dict["anomaly_evidence"]]
        
        return {
            "loan_id": loan_id,
            "summary": summary,
            "recommendation": recommendation,
            "action": str(latest_record.get("action", "No Action")),
            "confidence": float(latest_record.get("confidence", 0.80)),
            "disclaimer": "Recommendation — Not a Decision",
            "model": model_name,
            "timestamp": pd.Timestamp.now().isoformat(),
            "evidence": evidence
        }

    @staticmethod
    def save_reviewer_decision(loan_id: str, decision: str, reviewer_note: str) -> dict:
        """Saves human review action to human_decisions.csv file."""
        if not loan_state.initialized:
            loan_state.initialize()
            
        if loan_state.merged_df[loan_state.merged_df["loan_id"] == loan_id].empty:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found.")
            
        csv_path = settings.BASE_DIR / "outputs/submissions/human_decisions.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_exists = csv_path.exists()
        timestamp = pd.Timestamp.now().isoformat()
        
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["loan_id", "decision", "reviewer_note", "timestamp"])
            writer.writerow([loan_id, decision, reviewer_note, timestamp])
            
        return {
            "status": "success",
            "loan_id": loan_id,
            "decision": decision,
            "timestamp": timestamp
        }
