import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DriftDetector:
    """Detects feature drift between training and testing datasets using PSI (Population Stability Index)."""
    
    @staticmethod
    def calculate_psi(expected: pd.Series, actual: pd.Series, num_bins: int = 10) -> float:
        """
        Calculates Population Stability Index (PSI) between expected (train) and actual (test) distributions.
        Interpretation:
            PSI < 0.10: No significant change / Stable
            0.10 <= PSI < 0.25: Moderate change / Drift Warning
            PSI >= 0.25: Significant change / High Drift
        """
        # Remove NaNs
        expected = expected.dropna()
        actual = actual.dropna()
        
        if expected.empty or actual.empty:
            return 0.0
            
        try:
            # Handle numeric features by binning
            if pd.api.types.is_numeric_dtype(expected):
                # Use quantiles from expected to define bins
                percentiles = np.linspace(0, 100, num_bins + 1)
                bins = np.percentile(expected, percentiles)
                bins = np.unique(bins) # remove duplicates
                
                # If unique values are too small, fall back to value counts
                if len(bins) < 2:
                    return DriftDetector.calculate_categorical_psi(expected, actual)
                    
                # Adjust boundaries to prevent out of bounds
                bins[0] = -np.inf
                bins[-1] = np.inf
                
                expected_counts = pd.cut(expected, bins=bins).value_counts()
                actual_counts = pd.cut(actual, bins=bins).value_counts()
            else:
                return DriftDetector.calculate_categorical_psi(expected, actual)
                
            # Convert counts to percentages
            expected_pcts = expected_counts / len(expected)
            actual_pcts = actual_counts / len(actual)
            
            # Align indices
            df = pd.DataFrame({"expected": expected_pcts, "actual": actual_pcts}).fillna(0)
            
            # Handle zero percentages by smoothing (add small epsilon)
            eps = 1e-4
            df["expected"] = df["expected"].replace(0, eps)
            df["actual"] = df["actual"].replace(0, eps)
            
            # Re-normalize
            df["expected"] = df["expected"] / df["expected"].sum()
            df["actual"] = df["actual"] / df["actual"].sum()
            
            # Calculate PSI
            psi_value = np.sum((df["actual"] - df["expected"]) * np.log(df["actual"] / df["expected"]))
            return float(psi_value)
            
        except Exception as e:
            logger.error(f"Error calculating PSI: {e}")
            return 0.0

    @staticmethod
    def calculate_categorical_psi(expected: pd.Series, actual: pd.Series) -> float:
        """Calculates categorical proportions PSI."""
        expected_counts = expected.value_counts()
        actual_counts = actual.value_counts()
        
        expected_pcts = expected_counts / len(expected)
        actual_pcts = actual_counts / len(actual)
        
        # Align indices
        all_cats = list(set(expected_pcts.index).union(set(actual_pcts.index)))
        expected_pcts = expected_pcts.reindex(all_cats, fill_value=0)
        actual_pcts = actual_pcts.reindex(all_cats, fill_value=0)
        
        df = pd.DataFrame({"expected": expected_pcts, "actual": actual_pcts})
        
        eps = 1e-4
        df["expected"] = df["expected"].replace(0, eps)
        df["actual"] = df["actual"].replace(0, eps)
        
        df["expected"] = df["expected"] / df["expected"].sum()
        df["actual"] = df["actual"] / df["actual"].sum()
        
        psi_value = np.sum((df["actual"] - df["expected"]) * np.log(df["actual"] / df["expected"]))
        return float(psi_value)

    def generate_drift_report(self, train_df: pd.DataFrame, test_df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """Generates a dataset-wide drift report across a set of columns."""
        report = []
        for col in columns:
            if col in train_df.columns and col in test_df.columns:
                psi = self.calculate_psi(train_df[col], test_df[col])
                
                # Interpret drift status
                if psi < 0.10:
                    status = "Stable"
                elif psi < 0.25:
                    status = "Moderate Drift"
                else:
                    status = "High Drift"
                    
                report.append({
                    "column": col,
                    "psi": psi,
                    "status": status
                })
        return pd.DataFrame(report).sort_values("psi", ascending=False)
