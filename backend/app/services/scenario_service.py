from backend.app.services.loan_service import loan_state
from src.scenarios.scenario_engine import ScenarioEngine
from fastapi import HTTPException
import pandas as pd

class ScenarioService:
    @staticmethod
    def run_scenario_simulation(scenario: str, segments: list[str], start_date: str = None, end_date: str = None) -> dict:
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
            
        # Determine source records: filter by date range if provided, otherwise latest_records
        if start_date or end_date:
            df = loan_state.merged_df
            if start_date:
                df = df[df["reporting_month"] >= start_date]
            if end_date:
                df = df[df["reporting_month"] <= end_date]
            
            # Group by loan_id and take the latest record per loan in that period
            grouped_df = df.sort_values("reporting_month").groupby("loan_id").last().reset_index()
            
            if grouped_df.empty:
                raise HTTPException(
                    status_code=400,
                    detail=f"No loan records found between '{start_date}' and '{end_date}'. Note: Reporting months are recorded on the 1st of each month (e.g. 2019-02-01)."
                )
        else:
            grouped_df = loan_state.latest_records

        # Prepare predictions DataFrame for active loans
        active_df = pd.DataFrame({
            "loan_id": grouped_df["loan_id"],
            "reporting_month": grouped_df["reporting_month"],
            "credit_score_band": grouped_df["credit_score_band"],
            "ltv_band": grouped_df["ltv_band"],
            "vintage": grouped_df["vintage"],
            "state": grouped_df["state"],
            "servicer_name": grouped_df["servicer_name"],
            "prob_delinquency_3m": grouped_df["delinquency_probability"],
            "prob_default_12m": grouped_df["default_probability"],
            "prob_prepayment_12m": grouped_df["prepayment_probability"]
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
