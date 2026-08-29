from fastapi import APIRouter
from backend.app.schemas.data_quality import DataQualityResponse
from src.config import settings
import json
import pandas as pd

router = APIRouter(prefix="/data-quality", tags=["Data Quality"])

@router.get("", response_model=DataQualityResponse)
def get_data_quality_report():
    """Retrieves batch scores, missingness profiles, outliers, and validation relationship breaks."""
    batch_score = 0.0
    batch_json_path = settings.BASE_DIR / "outputs/profiling/batch_quality_score.json"
    if batch_json_path.exists():
        with open(batch_json_path, "r", encoding="utf-8") as f:
            batch_score = float(json.load(f).get("average_quality_score", 0.0))
            
    missingness = []
    missing_path = settings.BASE_DIR / "outputs/profiling/missingness.csv"
    if missing_path.exists():
        df = pd.read_csv(missing_path)
        for _, row in df.iterrows():
            missingness.append({
                "column": str(row["column"]),
                "missing_count": int(row["missing_count"]),
                "missing_pct": float(row["missing_pct"])
            })
            
    outliers = []
    outlier_path = settings.BASE_DIR / "outputs/profiling/outliers.csv"
    if outlier_path.exists():
        df = pd.read_csv(outlier_path)
        for _, row in df.iterrows():
            outliers.append({
                "column": str(row["column"]),
                "lower_bound": float(row["lower_bound"]),
                "upper_bound": float(row["upper_bound"]),
                "outlier_count": int(row["outlier_count"]),
                "outlier_pct": float(row["outlier_pct"])
            })
            
    breaks = []
    breaks_path = settings.BASE_DIR / "outputs/profiling/relationship_breaks.csv"
    if breaks_path.exists():
        df = pd.read_csv(breaks_path).head(100)
        for _, row in df.iterrows():
            breaks.append({
                "loan_id": str(row["loan_id"]),
                "reporting_month": str(row["reporting_month"]),
                "rule_id": str(row["rule_id"]),
                "relationship": str(row["relationship"]),
                "affected_columns": str(row["affected_columns"]),
                "observed_values": str(row["observed_values"]),
                "severity": str(row["severity"]),
                "description": str(row["description"])
            })
            
    drift = []
    drift_path = settings.BASE_DIR / "outputs/profiling/drift_report.csv"
    if drift_path.exists():
        df = pd.read_csv(drift_path)
        for _, row in df.iterrows():
            drift.append({
                "column": str(row["column"]),
                "psi": float(row["psi"]),
                "status": str(row["status"])
            })
            
    return DataQualityResponse(
        batch_quality_score=batch_score,
        missingness=missingness,
        outliers=outliers,
        relationship_breaks=breaks,
        drift=drift
    )
