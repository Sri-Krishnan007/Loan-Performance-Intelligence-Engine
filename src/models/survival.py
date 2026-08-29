import logging
import pandas as pd
import numpy as np
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)

class TransitionSurvivalModel:
    """Estimates credit transition matrices and competing-risk hazard curves."""
    
    def __init__(self):
        self.states = ["Current", "Delinquent", "Default", "Prepaid"]
        self.transition_matrix = None
        self.hazard_curves = None

    def calculate_transition_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes the empirical 4x4 monthly credit state transition matrix.
        Assures absorbing states (Default, Prepaid) transition to themselves with 1.0 probability.
        """
        logger.info("Calculating empirical state transition matrix...")
        
        # Sort chronologically per loan
        df_sorted = df.sort_values(["loan_id", "reporting_month"]).copy()
        
        # Compute shifts
        df_sorted["state_t"] = df_sorted["current_status"].astype(str)
        df_sorted["state_t_plus_1"] = df_sorted.groupby("loan_id")["state_t"].shift(-1)
        
        # Drop the last observation per loan (where next state is NaN)
        transitions = df_sorted.dropna(subset=["state_t_plus_1"]).copy()
        
        # Cross tabulate counts
        ct = pd.crosstab(transitions["state_t"], transitions["state_t_plus_1"])
        
        # Reindex to force 4x4 matrix
        ct = ct.reindex(index=self.states, columns=self.states, fill_value=0.0)
        
        # Absolute absorbing states override (enforce terminal behavior)
        # Default -> Default = 1.0
        # Prepaid -> Prepaid = 1.0
        ct.loc["Default", :] = 0.0
        ct.loc["Default", "Default"] = 1.0
        ct.loc["Prepaid", :] = 0.0
        ct.loc["Prepaid", "Prepaid"] = 1.0
        
        # Normalize to probabilities
        row_sums = ct.sum(axis=1)
        # Avoid division by zero
        row_sums = row_sums.replace(0, 1.0)
        
        prob_matrix = ct.div(row_sums, axis=0)
        self.transition_matrix = prob_matrix
        
        logger.info("Transition matrix calculated successfully.")
        return prob_matrix

    def estimate_hazard_curves(self, df: pd.DataFrame, max_age: int = 60) -> pd.DataFrame:
        """
        Computes competing-risk empirical hazard rates and cumulative survival curves
        by loan age in months.
        """
        logger.info("Estimating empirical default and prepayment hazard curves...")
        
        records = []
        cumulative_survival = 1.0
        
        for age in range(1, max_age + 1):
            # Exposure count at age-1: active loans that reached at least this age
            # (i.e. did not default or prepay in previous months)
            active_at_prev_age = df[(df["loan_age_months"] == age - 1) & 
                                    (df["current_status"].isin(["Current", "Delinquent"]))]
            
            exposure = len(active_at_prev_age)
            
            if exposure > 0:
                # Event counts observed in transition to age
                events = df[df["loan_age_months"] == age]
                
                # Default events at age
                default_events = len(events[(events["loan_id"].isin(active_at_prev_age["loan_id"])) & 
                                            (events["current_status"] == "Default")])
                
                # Prepayment events at age
                prepay_events = len(events[(events["loan_id"].isin(active_at_prev_age["loan_id"])) & 
                                           (events["current_status"] == "Prepaid")])
                
                # Hazard rates
                default_hazard = default_events / exposure
                prepay_hazard = prepay_events / exposure
            else:
                default_hazard = 0.0
                prepay_hazard = 0.0
            
            # Competing risk survival update
            total_hazard = default_hazard + prepay_hazard
            cumulative_survival *= (1.0 - total_hazard)
            
            records.append({
                "loan_age_months": age,
                "exposure": exposure,
                "default_hazard_rate": default_hazard,
                "prepayment_hazard_rate": prepay_hazard,
                "cumulative_survival_probability": cumulative_survival
            })
            
        hazard_df = pd.DataFrame(records)
        self.hazard_curves = hazard_df
        logger.info("Hazard curves estimated successfully.")
        return hazard_df

    def save(self, output_dir: Path = settings.MODEL_OUTPUT_DIR) -> None:
        """Saves calculated matrices and curves to output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        if self.transition_matrix is not None:
            self.transition_matrix.to_csv(output_dir / "transition_matrix.csv")
            logger.info(f"Saved transition matrix to {output_dir / 'transition_matrix.csv'}")
        if self.hazard_curves is not None:
            self.hazard_curves.to_csv(output_dir / "hazard_curves.csv", index=False)
            logger.info(f"Saved hazard curves to {output_dir / 'hazard_curves.csv'}")
