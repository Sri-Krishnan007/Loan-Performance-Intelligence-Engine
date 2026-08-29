import json
import numpy as np
import pandas as pd
import logging
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)

class DataProfiler:
    """Profiles datasets to identify distributions, missingness patterns, and outliers."""
    
    @staticmethod
    def profile_distributions(df: pd.DataFrame) -> dict:
        """Profiles distribution stats for numerical and categorical variables."""
        profile = {}
        for col in df.columns:
            col_type = str(df[col].dtype)
            null_count = int(df[col].isna().sum())
            null_pct = float(null_count / len(df))
            
            stats = {
                "dtype": col_type,
                "null_count": null_count,
                "null_pct": null_pct,
                "unique_count": int(df[col].nunique())
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                stats.update({
                    "mean": float(df[col].mean()) if not df[col].empty else 0.0,
                    "std": float(df[col].std()) if not df[col].empty else 0.0,
                    "min": float(df[col].min()) if not df[col].empty else 0.0,
                    "max": float(df[col].max()) if not df[col].empty else 0.0,
                    "median": float(df[col].median()) if not df[col].empty else 0.0
                })
            elif isinstance(df[col].dtype, pd.CategoricalDtype) or df[col].dtype == "object":
                # Value counts top 10
                vc = df[col].value_counts().head(10).to_dict()
                stats.update({
                    "top_categories": {str(k): int(v) for k, v in vc.items()}
                })
            profile[col] = stats
        return profile

    @staticmethod
    def detect_outliers(df: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
        """
        Detects outlier records using the Interquartile Range (IQR) method.
        Returns a dataframe summarizing outlier counts.
        """
        outlier_records = []
        for col in numeric_cols:
            if col in df.columns:
                series = df[col].dropna()
                if not series.empty:
                    q1 = series.quantile(0.25)
                    q3 = series.quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    outlier_records.append({
                        "column": col,
                        "lower_bound": float(lower_bound),
                        "upper_bound": float(upper_bound),
                        "outlier_count": len(outliers),
                        "outlier_pct": float(len(outliers) / len(df))
                    })
        return pd.DataFrame(outlier_records)

    @staticmethod
    def identify_missingness_patterns(df: pd.DataFrame) -> pd.DataFrame:
        """Analyzes missingness across columns."""
        missingness = []
        for col in df.columns:
            null_count = int(df[col].isna().sum())
            missingness.append({
                "column": col,
                "missing_count": null_count,
                "missing_pct": float(null_count / len(df))
            })
        return pd.DataFrame(missingness).sort_values("missing_pct", ascending=False)

    @staticmethod
    def calculate_correlation_matrix(df: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
        """Computes a Pearson correlation matrix for numerical features, ignoring targets/identifiers."""
        clean_df = pd.DataFrame()
        for col in numeric_cols:
            if col in df.columns:
                clean_df[col] = pd.to_numeric(df[col], errors="coerce")
        corr = clean_df.corr(method="pearson")
        return corr

    @staticmethod
    def detect_relationship_breaks(df: pd.DataFrame, record_results: pd.DataFrame, validator) -> pd.DataFrame:
        """Identifies violations of cross-column rules from validator results."""
        all_rules = {r["rule_id"]: r for r in validator.get_all_rules()}
        violations = []
        
        for rule_id in record_results.columns:
            if rule_id in all_rules:
                rule = all_rules[rule_id]
                failed_mask = ~record_results[rule_id]
                failed_indices = failed_mask[failed_mask].index
                
                if len(failed_indices) > 0:
                    for idx in failed_indices[:500]: # limit to 500 records per rule for file size safety
                        row_df = df.loc[idx]
                        observed = []
                        for col in rule["columns"]:
                            if col in df.columns:
                                val = df.loc[idx, col]
                                observed.append(f"{col}={val}")
                        
                        violations.append({
                            "loan_id": str(row_df.get("loan_id", "Unknown")),
                            "reporting_month": str(row_df.get("reporting_month", "Unknown")),
                            "rule_id": rule_id,
                            "relationship": rule["name"],
                            "affected_columns": ";".join(rule["columns"]),
                            "observed_values": ";".join(observed),
                            "severity": rule["severity"],
                            "description": rule["description"]
                        })
                        
        return pd.DataFrame(violations)
