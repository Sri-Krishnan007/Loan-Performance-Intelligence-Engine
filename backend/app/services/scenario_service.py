from backend.app.services.loan_service import loan_state
from src.scenarios.scenario_engine import ScenarioEngine
from fastapi import HTTPException
import pandas as pd

class ScenarioService:
    @staticmethod
    def run_scenario_simulation(scenario: str, segments: list[str]) -> dict:
        """Runs the macroeconomic stress scenario simulation on the active portfolio."""
        if not loan_state.initialized:
            loan_state.initialize()
            
        scen_id = scenario.upper()
        engine = ScenarioEngine()
        valid_scenarios = list(engine.scenarios["scenario_id"].values)
        if scen_id not in valid_scenarios:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scenario: '{scenario}'. Valid options: {valid_scenarios}"
            )
            
        # Prepare predictions DataFrame for active loans
        active_df = pd.DataFrame({
            "loan_id": loan_state.latest_records["loan_id"],
            "reporting_month": loan_state.latest_records["reporting_month"],
            "credit_score_band": loan_state.latest_records["credit_score_band"],
            "ltv_band": loan_state.latest_records["ltv_band"],
            "vintage": loan_state.latest_records["vintage"],
            "state": loan_state.latest_records["state"],
            "servicer_name": loan_state.latest_records["servicer_name"],
            "prob_delinquency_3m": loan_state.latest_records["delinquency_probability"],
            "prob_default_12m": loan_state.latest_records["default_probability"],
            "prob_prepayment_12m": loan_state.latest_records["prepayment_probability"]
        })
        
        # Simulate stressed probabilities
        stressed_df = engine.simulate_portfolio(active_df, scen_id)
        
        # Portfolio aggregates
        portfolio = {
            "delinquency_rate": float(stressed_df["prob_delinquency_3m"].mean()),
            "default_rate": float(stressed_df["prob_default_12m"].mean()),
            "prepayment_rate": float(stressed_df["prob_prepayment_12m"].mean())
        }
        
        # Segment analysis mappings
        col_mapping = {
            "credit_band": "credit_score_band",
            "state": "state",
            "servicer": "servicer_name",
            "vintage": "vintage"
        }
        
        segment_cols = []
        for seg in segments:
            mapped_col = col_mapping.get(seg.lower())
            if mapped_col and mapped_col in stressed_df.columns:
                segment_cols.append(mapped_col)
                
        segment_list = []
        if len(segment_cols) > 0:
            grouped_df = engine.segment_analysis(stressed_df, segment_cols)
            for _, row in grouped_df.iterrows():
                seg_dict = {}
                for seg, col in zip(segments, segment_cols):
                    seg_dict[seg] = str(row[col])
                seg_dict.update({
                    "delinquency_rate": float(row.get("prob_delinquency_3m_mean", 0.0)),
                    "default_rate": float(row.get("prob_default_12m_mean", 0.0)),
                    "prepayment_rate": float(row.get("prob_prepayment_12m_mean", 0.0))
                })
                segment_list.append(seg_dict)
                
        # Drivers (macroeconomic multipliers from scenario config)
        scen_row = engine.scenarios[engine.scenarios["scenario_id"] == scen_id].iloc[0]
        drivers = [
            {"variable": "Delinquency Multiplier", "value": float(scen_row["delinquency_multiplier"])},
            {"variable": "Default Multiplier", "value": float(scen_row["default_multiplier"])},
            {"variable": "Prepayment Multiplier", "value": float(scen_row["prepayment_multiplier"])}
        ]
        
        return {
            "scenario": scen_id,
            "portfolio": portfolio,
            "segments": segment_list,
            "drivers": drivers
        }
