import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates datasets dynamically using rules from validation_rules.json."""
    
    def __init__(self, rules_path: Path = settings.VALIDATION_RULES_PATH):
        self.rules_path = rules_path
        self.rules = self.load_rules()
        self.scoring_config = self.rules.get("quality_scoring", settings.SCORING_CONFIG)
        
    def load_rules(self) -> dict:
        """Loads and parses validation rules JSON."""
        logger.info(f"Loading validation rules from {self.rules_path}")
        if not self.rules_path.exists():
            logger.warning(f"Validation rules file not found: {self.rules_path}. Using empty rules.")
            return {}
        with open(self.rules_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_rules(self) -> list:
        """Flattens rules list across all categories."""
        all_rules = []
        categories = [
            "financial_rules", "temporal_rules", "delinquency_rules", "lifecycle_rules",
            "flag_consistency_rules", "documentation_rules", "categorical_rules",
            "servicer_reconciliation_rules", "duplicate_rules"
        ]
        for cat in categories:
            if cat in self.rules:
                all_rules.extend(self.rules[cat])
        return all_rules

    def validate_dataset(self, df: pd.DataFrame, dataset_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Validates a dataframe against rules assigned to dataset_name.
        Returns:
            - record_results: DataFrame with column flags (True=passed, False=failed) for each rule.
            - summary_report: Summary DataFrame containing rules, status, and failure counts.
        """
        # Ensure dates are parsed and temp string cols are handled for eval
        temp_df = df.copy()
        for col in temp_df.columns:
            if isinstance(temp_df[col].dtype, pd.CategoricalDtype):
                temp_df[col] = temp_df[col].astype(str)
            # Handle float NaNs in string comparisons
            if temp_df[col].dtype == 'object':
                temp_df[col] = temp_df[col].fillna("None")

        dataset_rules = [r for r in self.get_all_rules() if r.get("dataset") == dataset_name or 
                         (dataset_name == "loan_monthly_performance_train" and r.get("dataset") == "loan_monthly_performance") or
                         (dataset_name == "loan_monthly_performance_test" and r.get("dataset") == "loan_monthly_performance")]

        record_results = pd.DataFrame(index=df.index)
        summary_records = []

        for rule in dataset_rules:
            rule_id = rule["rule_id"]
            rule_type = rule["type"]
            severity = rule["severity"]
            cols = rule["columns"]
            
            # Ensure target columns exist in dataset
            missing_cols = [c for c in cols if c not in df.columns]
            if missing_cols:
                logger.debug(f"Skipping rule {rule_id} as columns {missing_cols} are missing in {dataset_name}.")
                continue
                
            passed_mask = pd.Series(True, index=df.index)
            
            try:
                if rule_type == "row_condition":
                    cond = rule["condition"]
                    # If condition is string, evaluate
                    if isinstance(cond, str):
                        # Handle specific NaN/None issues for LFC007 or similar comparisons
                        if "loss_severity_band != 'None'" in cond:
                            # Robust comparison for None/NaN
                            passed_mask = ~((temp_df["current_status"] != "Default") & 
                                            (temp_df["loss_severity_band"].astype(str).isin(["Low", "Medium", "High"])))
                        else:
                            passed_mask = temp_df.eval(cond)
                    
                elif rule_type == "allowed_values":
                    allowed = rule["condition"]
                    passed_mask = temp_df[cols[0]].isin(allowed)
                    
                elif rule_type == "allowed_values_or_null":
                    allowed = rule["condition"]
                    passed_mask = df[cols[0]].isna() | temp_df[cols[0]].isin(allowed)
                    
                elif rule_type == "dataset_uniqueness":
                    target_cols = rule["condition"]
                    if isinstance(target_cols, str):
                        target_cols = [target_cols]
                    passed_mask = ~df.duplicated(subset=target_cols, keep=False)
                    
                elif rule_type == "group_consistency":
                    cond_info = rule["condition"]
                    group_by = cond_info["group_by"]
                    target = cond_info["target"]
                    metric = cond_info["metric"]
                    expected = cond_info["expected"]
                    
                    if metric == "nunique":
                        counts = df.groupby(group_by)[target].transform("nunique")
                        passed_mask = counts == expected
                        
                elif rule_type == "sequential_group":
                    cond_info = rule["condition"]
                    group_by = cond_info["group_by"]
                    target = cond_info["target"]
                    start = cond_info["start"]
                    step = cond_info["step"]
                    
                    # Sort internally to verify sequence
                    # We group by group_by and verify that target is sequential starting at start with step
                    # To do this in vectorized format, we compare target to row number within group
                    row_nums = df.groupby(group_by).cumcount() * step + start
                    passed_mask = df[target] == row_nums
                    
                elif rule_type == "chronological_group":
                    cond_info = rule["condition"]
                    group_by = cond_info["group_by"]
                    target = cond_info["target"]
                    
                    # Check if sorted chronologically within group
                    diffs = df.groupby(group_by)[target].diff()
                    # It's passed if it's NaT (first row) or positive
                    passed_mask = diffs.isna() | (diffs > pd.Timedelta(0))
                    
                elif rule_type == "terminal_state":
                    terminal_val = rule["condition"]
                    # If current_status is terminal, no rows for this loan should appear with a larger month_index
                    # Group and find min index of terminal state
                    terminal_idx = df[df["current_status"] == terminal_val].groupby("loan_id")["month_index"].min()
                    if len(terminal_idx) > 0:
                        loan_terminal_idx = df["loan_id"].map(terminal_idx)
                        passed_mask = loan_terminal_idx.isna() | (df["month_index"] <= loan_terminal_idx)
                    else:
                        passed_mask = pd.Series(True, index=df.index)
                        
                elif rule_type == "transition_validation":
                    # Transition roll rates validation
                    cond_info = rule["condition"]
                    group_by = cond_info["group_by"]
                    target = cond_info["target"]
                    permitted = cond_info["permitted_rolls"]
                    
                    prev_val = df.groupby(group_by)[target].shift(1)
                    # Create boolean mask
                    temp_passed = []
                    for val, prev in zip(df[target], prev_val):
                        if pd.isna(prev):
                            temp_passed.append(True)
                        else:
                            # Check if transition from prev to val is permitted
                            prev_str = str(int(prev))
                            if prev_str in permitted:
                                temp_passed.append(int(val) in permitted[prev_str])
                            else:
                                temp_passed.append(False)
                    passed_mask = pd.Series(temp_passed, index=df.index)
                    
                elif rule_type == "conditional_info":
                    # Just informational, check triggers
                    cond_info = rule["condition"]
                    if isinstance(cond_info, str):
                        triggered = temp_df.eval(cond_info)
                        # Info rule fails when trigger is true, else passes (or passes always for metrics)
                        passed_mask = ~triggered
                    else:
                        # Map triggers, e.g. for PARTIAL_UPDATE null expectations
                        trigger = cond_info["if_trigger"]
                        triggered = temp_df.eval(trigger)
                        # Passed unless triggered and violates expectation
                        passed_mask = ~triggered
                        
            except Exception as e:
                logger.error(f"Rule evaluation failed for {rule_id}: {e}")
                passed_mask = pd.Series(False, index=df.index)
                
            record_results[rule_id] = passed_mask
            failures = (~passed_mask).sum()
            summary_records.append({
                "rule_id": rule_id,
                "name": rule["name"],
                "description": rule["description"],
                "severity": severity,
                "dataset": dataset_name,
                "failures": int(failures),
                "status": "PASS" if failures == 0 else ("WARNING" if severity == "warning" else "FAIL")
            })
            
        summary_report = pd.DataFrame(summary_records)
        return record_results, summary_report

    def calculate_scores(self, record_results: pd.DataFrame, dataset_name: str) -> pd.Series:
        """Calculates numerical quality scores for each record in record_results dataframe."""
        initial_score = self.scoring_config.get("record_score_initial", 100)
        err_penalty = self.scoring_config.get("error_penalty", 20)
        warn_penalty = self.scoring_config.get("warning_penalty", 5)
        info_penalty = self.scoring_config.get("info_penalty", 0)
        min_score = self.scoring_config.get("minimum_score", 0)
        
        all_rules = {r["rule_id"]: r for r in self.get_all_rules()}
        
        # Track total penalty sum per row
        total_penalties = np.zeros(len(record_results))
        
        for rule_id in record_results.columns:
            if rule_id in all_rules:
                severity = all_rules[rule_id]["severity"]
                penalty = err_penalty if severity == "error" else (warn_penalty if severity == "warning" else info_penalty)
                
                # Wherever record_results is False (failed check), apply penalty
                failed_mask = ~record_results[rule_id]
                total_penalties += failed_mask.astype(int) * penalty
                
        scores = initial_score - total_penalties
        scores = np.clip(scores, min_score, initial_score)
        return pd.Series(scores, index=record_results.index)
