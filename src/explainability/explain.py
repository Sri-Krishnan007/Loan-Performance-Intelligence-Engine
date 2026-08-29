import logging
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from src.config import settings

logger = logging.getLogger(__name__)

class ModelExplainer:
    """Computes global feature importances and extracts local positive/negative risk drivers."""
    
    def __init__(self, feature_names: list[str]):
        self.feature_names = feature_names

    def get_global_importance(self, model, X_val: pd.DataFrame, y_val: pd.Series, max_samples: int = 1000) -> pd.DataFrame:
        """
        Calculates permutation feature importance on validation data.
        Permutation importance is model-agnostic and robust for HistGradientBoostingClassifier.
        """
        logger.info(f"Calculating global permutation feature importance on {min(len(X_val), max_samples)} samples...")
        
        # Sample for speed
        if len(X_val) > max_samples:
            sample_idx = X_val.sample(max_samples, random_state=42).index
            X_sample = X_val.loc[sample_idx]
            y_sample = y_val.loc[sample_idx]
        else:
            X_sample = X_val
            y_sample = y_val
            
        result = permutation_importance(
            model, X_sample, y_sample, 
            n_repeats=5, random_state=42, n_jobs=-1
        )
        
        importance_df = pd.DataFrame({
            "feature": self.feature_names,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std
        }).sort_values("importance_mean", ascending=False)
        
        logger.info("Global feature importance calculation completed.")
        return importance_df

    def explain_local_instance(self, row: pd.Series, probability: float) -> tuple[str, str]:
        """
        Extracts positive (risk-increasing) and negative (risk-reducing) drivers 
        for an individual loan observation based on domain bounds.
        """
        positive_drivers = []
        negative_drivers = []
        
        # 1. Delinquency triggers
        dpd = row.get("days_past_due", 0)
        max_dpd = row.get("days_past_due_max_3m", 0)
        if dpd >= 60:
            positive_drivers.append(f"severe_delinquency(DPD={int(dpd)})")
        elif dpd > 0:
            positive_drivers.append(f"delinquency(DPD={int(dpd)})")
        elif max_dpd > 0:
            positive_drivers.append(f"recent_delinquency(max_3m={int(max_dpd)})")
        else:
            negative_drivers.append("clean_payment_history")
            
        # 2. Credit score / FICO
        fico = row.get("fico_score_val", -1)
        if fico <= 1 and fico >= 0:  # FICO < 660
            positive_drivers.append("low_credit_score")
        elif fico >= 4:  # FICO >= 740
            negative_drivers.append("high_credit_score")
            
        # 3. LTV / Equity
        ltv = row.get("ltv_band_val", -1)
        if ltv >= 3:  # LTV >= 80%
            positive_drivers.append("high_ltv")
        elif ltv <= 1 and ltv >= 0:  # LTV < 70%
            negative_drivers.append("high_equity_ltv")
            
        # 4. Debt service ratio / DTI
        dti = row.get("dti_band_val", -1)
        if dti >= 2:  # DTI >= 30%
            positive_drivers.append("high_dti")
        elif dti == 0:  # DTI < 20%
            negative_drivers.append("low_dti")
            
        # 5. Loan Modification
        mod_cum = row.get("modification_flag_cum", 0)
        if mod_cum > 0:
            positive_drivers.append(f"prior_modifications(count={int(mod_cum)})")
            
        # 6. Interest Rate risk
        rate = row.get("interest_rate", 0.0)
        if rate >= 7.0:
            positive_drivers.append(f"elevated_rate({rate:.2f}%)")
        elif rate < 4.5 and rate > 0:
            negative_drivers.append(f"low_rate({rate:.2f}%)")
            
        pos_str = ";".join(positive_drivers) if positive_drivers else "None"
        neg_str = ";".join(negative_drivers) if negative_drivers else "None"
        
        return pos_str, neg_str

    def generate_counterfactuals(self, row: pd.Series, default_probability: float) -> list[str]:
        """
        Determines targeted parameter corrections (counterfactual targets) 
        required to move a high-risk loan profile into a low-risk status.
        """
        recommendations = []
        
        # Check if already low risk
        if default_probability <= 0.05:
            return ["Profile meets low-risk criteria. No counterfactual adjustments needed."]
            
        # 1. Delinquency correction
        dpd = row.get("days_past_due", 0)
        if dpd > 0:
            recommendations.append(f"Cure outstanding delinquency (reduce current DPD of {int(dpd)} to 0)")
            
        # 2. Credit score improvements
        fico = row.get("fico_score_val", -1)
        if fico < 4: # FICO score band below 740-779
            recommendations.append("Enhance credit score profile to FICO Band '740-779' or '780+'")
            
        # 3. LTV / Principal payoff
        ltv = row.get("ltv_band_val", -1)
        if ltv >= 3: # LTV ratio >= 80%
            recommendations.append("Increase equity or reduce loan balance to achieve LTV Band '70-80' or lower")
            
        # 4. Debt service ratio reduction
        dti = row.get("dti_band_val", -1)
        if dti >= 2: # DTI ratio >= 30%
            recommendations.append("Verify additional borrower income stream or reduce debt to lower DTI Band to '20-30' or lower")
            
        # 5. Document gaps check
        doc_status = str(row.get("document_status", "Complete"))
        if doc_status == "Missing":
            recommendations.append("Provide and index missing loan compliance documentation")
            
        # Fallback if no specific driver matched but probability is high
        if not recommendations:
            recommendations.append("Review servicer updates and reduce principal balance to lower overall credit exposure")
            
        return recommendations
