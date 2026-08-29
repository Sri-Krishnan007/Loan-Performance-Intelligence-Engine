from backend.app.services.loan_service import loan_state
from fastapi import HTTPException
import pandas as pd

class AnomalyService:
    @staticmethod
    def get_loan_anomaly(loan_id: str) -> dict:
        """Retrieves operational anomaly details for a single loan."""
        if not loan_state.initialized:
            loan_state.initialize()
            
        loan_records = loan_state.merged_df[loan_state.merged_df["loan_id"] == loan_id]
        if loan_records.empty:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found.")
            
        latest_record = loan_records.iloc[-1]
        
        # Drivers list
        drivers_str = str(latest_record.get("top_drivers", "None"))
        drivers = [d.strip() for d in drivers_str.split(";") if d.strip() and d.lower() != "none"]
        
        # Pull detailed evidence if this loan is in top reports
        rep = loan_state.anomaly_reports.get(loan_id, {})
        evidence_str = rep.get("evidence", "")
        if evidence_str:
            evidence = [evidence_str]
        else:
            evidence = []
            if str(latest_record.get("exception_type")) != "None":
                evidence.append(f"Exception triggered: {latest_record.get('exception_type')}")
            if len(drivers) > 0:
                evidence.append(f"Reconciliation conflict flagged on: {', '.join(drivers)}")
            else:
                evidence.append("No material discrepancies found.")
                
        # Severity mapping
        action = str(latest_record.get("action", "No Action"))
        if action == "Priority Review":
            severity = "HIGH"
        elif action == "Investigate Data":
            severity = "MEDIUM"
        else:
            severity = "LOW"
            
        return {
            "loan_id": loan_id,
            "anomaly_score": float(latest_record.get("anomaly_score", 0.0)),
            "exception_required": bool(str(latest_record.get("exception_type")) != "None"),
            "exception_type": str(latest_record.get("exception_type", "None")),
            "severity": severity,
            "drivers": drivers,
            "evidence": evidence
        }

    @staticmethod
    def list_anomalies(severity: str = None, exception_type: str = None, limit: int = 20, offset: int = 0) -> dict:
        """Retrieves and paginates anomaly records."""
        if not loan_state.initialized:
            loan_state.initialize()
            
        # Get all records with non-zero anomaly score or exceptions
        df = loan_state.latest_records.copy()
        
        # Apply filters
        if severity:
            sev_lower = severity.lower()
            if sev_lower == "high":
                df = df[df["action"] == "Priority Review"]
            elif sev_lower == "medium":
                df = df[df["action"] == "Investigate Data"]
            elif sev_lower == "low":
                df = df[df["action"] == "No Action"]
                
        if exception_type:
            df = df[df["exception_type"].astype(str).str.lower() == exception_type.lower()]
        else:
            df = df[(df["exception_type"].astype(str) != "None") | (df["anomaly_score"] > 0.3)]
            
        df = df.sort_values("anomaly_score", ascending=False)
        
        total = len(df)
        paginated_df = df.iloc[offset : offset + limit]
        
        items = []
        for _, row in paginated_df.iterrows():
            loan_id = str(row["loan_id"])
            rep = loan_state.anomaly_reports.get(loan_id, {})
            evidence_str = rep.get("evidence", "")
            
            drivers_str = str(row.get("top_drivers", "None"))
            drivers = [d.strip() for d in drivers_str.split(";") if d.strip() and d.lower() != "none"]
            
            evidence = [evidence_str] if evidence_str else []
            if not evidence:
                if str(row.get("exception_type")) != "None":
                    evidence.append(f"Exception triggered: {row.get('exception_type')}")
                if len(drivers) > 0:
                    evidence.append(f"Reconciliation conflict flagged on: {', '.join(drivers)}")
                else:
                    evidence.append("Audit threshold discrepancy.")
                    
            action = str(row.get("action", "No Action"))
            row_severity = "HIGH" if action == "Priority Review" else ("MEDIUM" if action == "Investigate Data" else "LOW")
            
            items.append({
                "loan_id": loan_id,
                "reporting_month": str(row.get("reporting_month")),
                "anomaly_score": float(row.get("anomaly_score", 0.0)),
                "exception_type": str(row.get("exception_type", "None")),
                "severity": row_severity,
                "drivers": drivers,
                "evidence": evidence
            })
            
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset
        }
