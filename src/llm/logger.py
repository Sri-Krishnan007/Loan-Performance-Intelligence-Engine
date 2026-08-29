import json
import logging
from datetime import datetime
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)

class LLMAuditLogger:
    """Logs LLM reviewer requests, responses, rejections, and calibration feedback."""
    
    def __init__(self):
        self.notes_file = settings.LLM_OUTPUT_DIR / "reviewer_notes.jsonl"
        self.rejections_file = settings.LLM_OUTPUT_DIR / "rejected_outputs.jsonl"
        
        # Ensure directories exist
        self.notes_file.parent.mkdir(parents=True, exist_ok=True)

    def log_completion(self, loan_id: str, prompt: str, response: str, metadata: dict) -> None:
        """Appends a successful reviewer notes generation record to the audit trail."""
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "loan_id": loan_id,
            "prompt": prompt,
            "response": response,
            "metadata": metadata
        }
        with open(self.notes_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_record) + "\n")
        logger.info(f"Logged successful LLM completion for loan {loan_id}.")

    def log_rejection(self, loan_id: str, prompt: str, response: str, reason: str, corrected_output: str = None) -> None:
        """Logs a rejected, vague, or overconfident LLM completion instance for logging/RAG offline checks."""
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "loan_id": loan_id,
            "prompt": prompt,
            "rejected_response": response,
            "reason": reason,
            "corrected_output": corrected_output
        }
        with open(self.rejections_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_record) + "\n")
        logger.warning(f"Logged LLM rejection for loan {loan_id}. Reason: {reason}")
        
    def check_response_validity(self, response: str) -> tuple[bool, str]:
        """Performs simple heuristic validation checks on LLM responses to detect hallucinations or missing details."""
        # 1. Check for required disclaimer
        if "Recommendation — Not a Decision" not in response:
            return False, "Missing mandatory disclaimer label."
            
        # 2. Check for empty response
        if len(response.strip()) < 50:
            return False, "Response is too short / vague."
            
        # 3. Check for obvious hallucinated state values
        hallucinated_words = ["Approved", "Rejected", "Denied"]
        for word in hallucinated_words:
            if f"State: {word}" in response or f"Status: {word}" in response:
                return False, f"Hallucinated status word '{word}' found."
                
        return True, "Valid"
