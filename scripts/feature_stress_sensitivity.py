import os
import sys
import json
import logging
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.config import settings
from backend.app.services.loan_service import loan_state

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_stress_sensitivity():
    """
    Simulates a 3x3 stress sensitivity matrix across two feature clusters:
    1. Borrower Leverage (DTI & Interest Rate adjustments)
    2. Property Equity (LTV adjustments)
    """
    logger.info("Initializing Feature Cluster Stress Sensitivity Analyzer...")
    
    # Initialize loan data
    loan_state.initialize()
    df = loan_state.merged_df.copy()
    
    # Get latest records
    latest_records = df.sort_values(["loan_id", "reporting_month"]).groupby("loan_id").last().reset_index()
    num_loans = len(latest_records)
    logger.info(f"Analyzing sensitivity on {num_loans} active accounts.")
    
    # Load default model
    model_path = settings.MODEL_DIR / "trained/default_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Trained default model not found at {model_path}")
    default_model = joblib.load(model_path)["model"]
    
    # Feature list expected by model
    feature_list_path = settings.MODEL_DIR / "metadata/features_list.json"
    with open(feature_list_path, "r", encoding="utf-8") as f:
        feature_cols = json.load(f)
        
    # Ordinal mappings list for banding
    category_mappings = {
        "credit_score_band": ['580-619', '620-659', '660-699', '700-739', '740-779', '780+'],
        "ltv_band": ['0-60', '60-70', '70-80', '80-90', '90-100'],
        "dti_band": ['0-20', '20-30', '30-40', '40-50'],
        "state": ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'],
        "loan_purpose": ['Purchase', 'Refinance'],
        "occupancy_type": ['Investment', 'Primary Residence', 'Second Home'],
        "property_type": ['Condominium', 'Multi Unit', 'Single Family', 'Townhouse'],
        "servicer_name": ['Servicer_A', 'Servicer_B', 'Servicer_C', 'Servicer_D', 'Servicer_E'],
        "current_status": ['Current', 'Default', 'Delinquent', 'Prepaid'],
        "document_status": ['Complete', 'Missing', 'Pending'],
    }
    
    # 3x3 Stress Levels definition
    leverage_levels = ["Base Leverage", "Moderate DTI (+5%)", "Severe DTI (+12%)"]
    equity_levels = ["Base Equity", "Moderate LTV (+10%)", "Severe LTV (+20%)"]
    
    results_grid = []
    
    # Helper to map modified DTI/LTV back to bands
    def map_dti_val(dti):
        if dti < 20: return 0
        elif dti < 30: return 1
        elif dti < 40: return 2
        else: return 3
        
    def map_ltv_val(ltv):
        if ltv < 60: return 0
        elif ltv < 70: return 1
        elif ltv < 80: return 2
        elif ltv < 90: return 3
        else: return 4

    for lev_idx, lev_label in enumerate(leverage_levels):
        for eq_idx, eq_label in enumerate(equity_levels):
            # Create a copy of the records to stress-test
            stressed_df = latest_records.copy()
            
            # Apply Leverage stressors (increase DTI and Interest Rate)
            dti_shift = 0.0 if lev_idx == 0 else 5.0 if lev_idx == 1 else 12.0
            interest_shift = 0.0 if lev_idx == 0 else 0.50 if lev_idx == 1 else 1.50
            
            # Apply Equity stressors (increase LTV)
            ltv_shift = 0.0 if eq_idx == 0 else 10.0 if eq_idx == 1 else 20.0
            
            # Stress variables
            stressed_df["interest_rate"] = stressed_df["interest_rate"].astype(float) + interest_shift
            
            # Approximate original numerical representations if bands
            # FICO Band Value -> 700 average
            # DTI Band Value (0-20=10, 20-30=25, 30-40=35, 40-50=45)
            # LTV Band Value (0-60=30, 60-70=65, 70-80=75, 80-90=85, 90-100=95)
            dti_band_to_num = {0: 10.0, 1: 25.0, 2: 35.0, 3: 45.0}
            ltv_band_to_num = {0: 30.0, 1: 65.0, 2: 75.0, 3: 85.0, 4: 95.0}
            
            # Apply shifts and map back to ordinal index values
            for idx, row in stressed_df.iterrows():
                # DTI Dimen
                curr_dti_val = int(row.get("dti_band_val", 1))
                new_dti_num = dti_band_to_num.get(curr_dti_val, 25.0) + dti_shift
                stressed_df.loc[idx, "dti_band_val"] = map_dti_val(new_dti_num)
                
                # LTV Dimen
                curr_ltv_val = int(row.get("ltv_band_val", 2))
                new_ltv_num = ltv_band_to_num.get(curr_ltv_val, 75.0) + ltv_shift
                stressed_df.loc[idx, "ltv_band_val"] = map_ltv_val(new_ltv_num)
                
            # Convert categorical texts to matched codes
            df_encoded = stressed_df.copy()
            for col, categories in category_mappings.items():
                if col in df_encoded.columns:
                    df_encoded[col] = df_encoded[col].astype(str).map(
                        lambda val: categories.index(val) if val in categories else -1
                    )
            
            # Ensure lag status code
            if "current_status_lag_1" in df_encoded.columns:
                df_encoded["current_status_lag_1"] = df_encoded["current_status_lag_1"].astype(str).map(
                    lambda val: category_mappings["current_status"].index(val) if val in category_mappings["current_status"] else -1
                )
                
            # Format inputs vector
            X_stressed = df_encoded[feature_cols].copy()
            for col in X_stressed.columns:
                X_stressed[col] = pd.to_numeric(X_stressed[col], errors="coerce").fillna(0.0)
                
            # Run model predictions
            pred_default_probs = default_model.predict_proba(X_stressed)[:, 1]
            mean_default_rate = float(pred_default_probs.mean())
            
            results_grid.append({
                "leverage_stress": lev_label,
                "equity_stress": eq_label,
                "average_default_probability": mean_default_rate
            })
            
    # Save outputs
    output_dir = PROJECT_ROOT / "outputs/scenarios"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "stress_sensitivity_grid.json", "w", encoding="utf-8") as f:
        json.dump(results_grid, f, indent=2)
        
    logger.info("Feature cluster stress sensitivity grid generated successfully.")
    
    # Write report
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    with open(reports_dir / "stress_sensitivity_report.md", "w", encoding="utf-8") as f:
        f.write("# Feature Cluster Stress Sensitivity Matrix Report\n\n")
        f.write("This report evaluates the portfolio credit loss sensitivity when borrower leverage and property equity feature clusters are stressed simultaneously.\n\n")
        f.write("## 3x3 Default Rate Sensitivity Matrix (%)\n\n")
        f.write("| Borrower Leverage \\ Property Equity | Base Equity | Moderate LTV (+10%) | Severe LTV (+20%) |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        
        # Row 1: Base Leverage
        r1_b = results_grid[0]["average_default_probability"] * 100
        r1_m = results_grid[1]["average_default_probability"] * 100
        r1_s = results_grid[2]["average_default_probability"] * 100
        f.write(f"| **Base Leverage** | {r1_b:.2f}% | {r1_m:.2f}% | {r1_s:.2f}% |\n")
        
        # Row 2: Moderate DTI
        r2_b = results_grid[3]["average_default_probability"] * 100
        r2_m = results_grid[4]["average_default_probability"] * 100
        r2_s = results_grid[5]["average_default_probability"] * 100
        f.write(f"| **Moderate DTI (+5%)** | {r2_b:.2f}% | {r2_m:.2f}% | {r2_s:.2f}% |\n")
        
        # Row 3: Severe DTI
        r3_b = results_grid[6]["average_default_probability"] * 100
        r3_m = results_grid[7]["average_default_probability"] * 100
        r3_s = results_grid[8]["average_default_probability"] * 100
        f.write(f"| **Severe DTI (+12%)** | {r3_b:.2f}% | {r3_m:.2f}% | {r3_s:.2f}% |\n\n")
        
        f.write("## Key Takeaways\n")
        f.write(f"1. **Maximum Stress Exposure**: Under severe double-trigger stress conditions (Severe Leverage + Severe Equity), the average portfolio default probability reaches **{r3_s:.2f}%**.\n")
        f.write(f"2. **Equity Buffer**: High LTV increases default risk even under Base Borrower Leverage scenarios, moving default risk from **{r1_b:.2f}%** to **{r1_s:.2f}%**.\n")

    logger.info("Stress sensitivity report written successfully.")

if __name__ == "__main__":
    run_stress_sensitivity()
