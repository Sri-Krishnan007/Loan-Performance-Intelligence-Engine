import logging
from src.llm.groq_client import GroqClient
from src.llm.logger import LLMAuditLogger
from src.llm.prompts import SYSTEM_REVIEWER_PROMPT, USER_LOAN_TEMPLATE

logger = logging.getLogger(__name__)

class LLMReviewer:
    """Coordinates Groq LLM Reviewer Copilot prompts, validations, and audit logs."""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.client = GroqClient(api_key=api_key, model=model)
        self.audit_logger = LLMAuditLogger()

    def generate_reviewer_note(self, loan_record: dict, prediction_metrics: dict) -> str:
        """
        Synthesizes loan static profile, anomalies, and model scores to generate reviewer natural-language reports.
        """
        loan_id = str(loan_record.get("loan_id", "Unknown"))
        logger.info(f"Generating LLM reviewer note for loan {loan_id}...")
        
        # Combine loan features and model predictions
        user_prompt = USER_LOAN_TEMPLATE.format(
            loan_id=loan_id,
            reporting_month=str(loan_record.get("reporting_month")),
            current_status=str(loan_record.get("current_status")),
            days_past_due=int(loan_record.get("days_past_due", 0)),
            original_balance=float(loan_record.get("original_balance", 0.0)),
            current_balance=float(loan_record.get("current_balance", 0.0)),
            interest_rate=float(loan_record.get("interest_rate", 0.0)),
            credit_score_band=str(loan_record.get("credit_score_band")),
            ltv_band=str(loan_record.get("ltv_band")),
            dti_band=str(loan_record.get("dti_band")),
            document_status=str(loan_record.get("document_status")),
            modification_flag=int(loan_record.get("modification_flag", 0)),
            default_probability=float(prediction_metrics.get("default_probability", 0.0)),
            delinquency_probability=float(prediction_metrics.get("delinquency_probability", 0.0)),
            prepayment_probability=float(prediction_metrics.get("prepayment_probability", 0.0)),
            next_state=str(prediction_metrics.get("next_state", "Unknown")),
            anomaly_score=float(prediction_metrics.get("anomaly_score", 0.0)),
            top_drivers=str(prediction_metrics.get("top_drivers", "None")),
            exception_required=int(prediction_metrics.get("exception_required", 0)),
            exception_type=str(prediction_metrics.get("exception_type", "None")),
            anomaly_evidence=str(prediction_metrics.get("anomaly_evidence", "No discrepancies"))
        )
        
        # Call Groq API
        raw_response = self.client.chat_completion(
            system_prompt=SYSTEM_REVIEWER_PROMPT,
            user_prompt=user_prompt
        )
        
        # Check Validity
        is_valid, reason = self.audit_logger.check_response_validity(raw_response)
        
        metadata = {
            "model": self.client.model,
            "predictions": prediction_metrics,
            "disclaimer_checked": is_valid
        }
        
        if is_valid:
            self.audit_logger.log_completion(loan_id, user_prompt, raw_response, metadata)
            return raw_response
        else:
            # Rejection fallback: Log and append a fallback note
            corrected_note = raw_response + "\n\n[Auto-Appended] Recommendation — Not a Decision" if "Recommendation — Not a Decision" not in raw_response else raw_response
            self.audit_logger.log_rejection(loan_id, user_prompt, raw_response, reason, corrected_note)
            self.audit_logger.log_completion(loan_id, user_prompt, corrected_note, metadata)
            return corrected_note
class MockLLMReviewer:
    """Mock reviewer class for API test validation when Groq Key is offline."""
    
    def generate_reviewer_note(self, loan_record: dict, prediction_metrics: dict) -> str:
        loan_id = str(loan_record.get("loan_id", "Unknown"))
        logger.info(f"Generating MOCK LLM reviewer note for loan {loan_id}...")
        
        mock_note = f"""### MOCK REVIEWER NOTE - LOAN {loan_id}
Status is {loan_record.get("current_status")}. DPD = {loan_record.get("days_past_due")}. 
ML 12m Default Risk: {prediction_metrics.get("default_probability", 0.0):.2%}.
Reconciliation Discrepancies: {prediction_metrics.get("anomaly_evidence")}.
Risk drivers flagged: {prediction_metrics.get("top_drivers")}.

Recommendation — Not a Decision"""
        return mock_note
