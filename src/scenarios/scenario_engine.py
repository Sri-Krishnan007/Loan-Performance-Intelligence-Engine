import logging
import pandas as pd
import numpy as np
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)

class ScenarioEngine:
    """Simulates portfolio-level credit risk projections under macroeconomic stress scenarios."""
    
    def __init__(self, scenarios_path: Path = settings.MACRO_SCENARIOS_PATH):
        self.scenarios_path = scenarios_path
        self.scenarios = self.load_scenarios()

    def load_scenarios(self) -> pd.DataFrame:
        """Loads macroeconomic stress scenarios from CSV."""
        logger.info(f"Loading macro scenarios from {self.scenarios_path}")
        if not self.scenarios_path.exists():
            raise FileNotFoundError(f"Scenarios file not found: {self.scenarios_path}")
        return pd.read_csv(self.scenarios_path)

    def simulate_portfolio(self, predictions_df: pd.DataFrame, scenario_id: str) -> pd.DataFrame:
        """
        Applies macroeconomic scenario multipliers to base probabilities.
        Returns a copy of predictions_df with stressed probability columns.
        """
        logger.info(f"Simulating portfolio under scenario: {scenario_id}...")
        
        # Find scenario row
        scen_row = self.scenarios[self.scenarios["scenario_id"] == scenario_id]
        if scen_row.empty:
            raise ValueError(f"Scenario ID '{scenario_id}' not found in scenarios config.")
        
        scen = scen_row.iloc[0]
        
        # Load multipliers
        del_mult = float(scen["delinquency_multiplier"])
        def_mult = float(scen["default_multiplier"])
        pre_mult = float(scen["prepayment_multiplier"])
        
        stressed_df = predictions_df.copy()
        
        # Apply multipliers to base predicted probabilities
        # Clip to valid [0.0, 1.0] probability bounds
        if "prob_delinquency_3m" in stressed_df.columns:
            stressed_df["prob_delinquency_3m"] = np.clip(stressed_df["prob_delinquency_3m"] * del_mult, 0.0, 1.0)
        if "prob_default_12m" in stressed_df.columns:
            stressed_df["prob_default_12m"] = np.clip(stressed_df["prob_default_12m"] * def_mult, 0.0, 1.0)
        if "prob_prepayment_12m" in stressed_df.columns:
            stressed_df["prob_prepayment_12m"] = np.clip(stressed_df["prob_prepayment_12m"] * pre_mult, 0.0, 1.0)
            
        # Add scenario identifier column
        stressed_df["scenario_id"] = scenario_id
        
        return stressed_df

    def segment_analysis(self, stressed_df: pd.DataFrame, segment_cols: list[str]) -> pd.DataFrame:
        """
        Aggregates stressed probabilities at segment level.
        Returns summary statistics for the defined categories.
        """
        logger.info(f"Aggregating stress projections across segments: {segment_cols}")
        
        agg_rules = {}
        if "prob_delinquency_3m" in stressed_df.columns:
            agg_rules["prob_delinquency_3m"] = ["mean", "max"]
        if "prob_default_12m" in stressed_df.columns:
            agg_rules["prob_default_12m"] = ["mean", "max"]
        if "prob_prepayment_12m" in stressed_df.columns:
            agg_rules["prob_prepayment_12m"] = ["mean", "max"]
            
        # Group and aggregate
        grouped = stressed_df.groupby(segment_cols).agg(agg_rules)
        
        # Flatten multi-index columns
        grouped.columns = ["_".join(col).strip() for col in grouped.columns.values]
        grouped = grouped.reset_index()
        
        return grouped
