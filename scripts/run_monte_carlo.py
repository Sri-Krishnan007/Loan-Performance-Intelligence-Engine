import os
import sys
import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.config import settings
from backend.app.services.loan_service import loan_state

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_monte_carlo_simulation(num_trials: int = 1000, projection_months: int = 12, loss_severity: float = 0.45):
    """
    Executes a Monte Carlo trial simulation on the active loan portfolio 
    to measure credit Value-at-Risk (VaR) and cash flow volatility.
    """
    logger.info("Initializing Monte Carlo Portfolio Simulator...")
    
    # Initialize loan state and load data
    loan_state.initialize()
    df = loan_state.merged_df.copy()
    
    # Get latest record for each unique loan
    latest_records = df.sort_values(["loan_id", "reporting_month"]).groupby("loan_id").last().reset_index()
    num_loans = len(latest_records)
    logger.info(f"Loaded {num_loans} active loans for simulation.")
    
    # Extract arrays for vectorized operations
    balances = latest_records["current_balance"].astype(float).values
    interest_rates = latest_records["interest_rate"].astype(float).values / 1200.0 # Monthly rate
    default_probs = latest_records.get("default_probability", 0.02).astype(float).values / 12.0 # Monthly proxy
    prepay_probs = latest_records.get("prepayment_probability", 0.05).astype(float).values / 12.0 # Monthly proxy
    
    portfolio_initial_balance = balances.sum()
    logger.info(f"Initial Portfolio Principal Balance: ${portfolio_initial_balance:,.2f}")
    
    trial_losses = []
    trial_prepayments = []
    trial_interest = []
    
    # Seed for reproducibility
    np.random.seed(42)
    
    logger.info(f"Running {num_trials} simulation trials...")
    
    for trial in range(num_trials):
        # Tracking vectors for active status per loan
        # status: 1 = Active, 0 = Terminated
        active_status = np.ones(num_loans)
        cumulative_loss = 0.0
        cumulative_prepay = 0.0
        cumulative_interest = 0.0
        
        current_balances = balances.copy()
        
        for month in range(projection_months):
            # Compute monthly interest generated
            interest = current_balances * interest_rates * active_status
            cumulative_interest += interest.sum()
            
            # Generate random uniform outcomes for defaults & prepayments
            rand_default = np.random.uniform(0, 1, num_loans)
            rand_prepay = np.random.uniform(0, 1, num_loans)
            
            # Identify events (only for active loans)
            defaults = (rand_default < default_probs) & (active_status == 1)
            prepayments = (rand_prepay < prepay_probs) & (active_status == 1) & (~defaults)
            
            # Record losses (Outstanding Balance * Severity)
            losses = current_balances * loss_severity * defaults
            cumulative_loss += losses.sum()
            
            # Record prepayments
            prepays = current_balances * prepayments
            cumulative_prepay += prepays.sum()
            
            # Deactivate terminated loans
            active_status[defaults] = 0
            active_status[prepayments] = 0
            
            # Simple amortization reduction (2% principal reduction per month for active loans)
            current_balances = current_balances * (1.0 - 0.02 * active_status)
            
        trial_losses.append(cumulative_loss)
        trial_prepayments.append(cumulative_prepay)
        trial_interest.append(cumulative_interest)
        
        if (trial + 1) % 200 == 0:
            logger.info(f"Completed {trial + 1}/{num_trials} trials...")
            
    # Calculate metrics
    trial_losses = np.array(trial_losses)
    trial_prepayments = np.array(trial_prepayments)
    trial_interest = np.array(trial_interest)
    
    loss_rates = trial_losses / portfolio_initial_balance
    prepay_rates = trial_prepayments / portfolio_initial_balance
    interest_yields = trial_interest / portfolio_initial_balance
    
    mean_loss = float(loss_rates.mean())
    std_loss = float(loss_rates.std())
    var_95 = float(np.percentile(loss_rates, 95))
    var_99 = float(np.percentile(loss_rates, 99))
    
    mean_prepay = float(prepay_rates.mean())
    mean_interest = float(interest_yields.mean())
    
    results = {
        "portfolio_initial_balance": portfolio_initial_balance,
        "num_trials": num_trials,
        "projection_months": projection_months,
        "loss_severity": loss_severity,
        "metrics": {
            "mean_loss_rate": mean_loss,
            "std_loss_rate": std_loss,
            "value_at_risk_95": var_95,
            "value_at_risk_99": var_99,
            "mean_prepayment_rate": mean_prepay,
            "mean_interest_yield_rate": mean_interest,
            "expected_losses": mean_loss * portfolio_initial_balance,
            "value_at_risk_95_amount": var_95 * portfolio_initial_balance,
            "value_at_risk_99_amount": var_99 * portfolio_initial_balance,
            "expected_interest_earnings": mean_interest * portfolio_initial_balance
        }
    }
    
    # Save output
    output_dir = PROJECT_ROOT / "outputs/monte_carlo"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "portfolio_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"Monte Carlo simulation completed. Expected Portfolio Loss Rate: {mean_loss:.4%}")
    logger.info(f"Portfolio credit Value-at-Risk (95% VaR): {var_95:.4%}")
    logger.info(f"Portfolio credit Value-at-Risk (99% VaR): {var_99:.4%}")
    
    # Write reports file
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    with open(reports_dir / "monte_carlo_report.md", "w", encoding="utf-8") as f:
        f.write(f"""# Monte Carlo Portfolio Simulation Report

This report summarizes the statistical credit loss forecasting and prepayment volatility simulations executed across the active mortgage pool.

## 📊 Simulation Design Parameters
* **Total Trials Simulated**: {num_trials:,}
* **Projection Horizon**: {projection_months} Months
* **Assumed Loss Severity (LGD)**: {loss_severity:.1%}
* **Active Loan Cohort**: {num_loans:,} Accounts

## 📈 Portfolio Statistical Metrics
* **Total Portfolio Principal Balance**: ${portfolio_initial_balance:,.2f}
* **Expected Cumulative Loss Rate**: **{mean_loss:.4%}** (Amount: ${results['metrics']['expected_losses']:,.2f})
* **Value-at-Risk (95% VaR)**: **{var_95:.4%}** (Amount: ${results['metrics']['value_at_risk_95_amount']:,.2f})
* **Value-at-Risk (99% VaR)**: **{var_99:.4%}** (Amount: ${results['metrics']['value_at_risk_99_amount']:,.2f})
* **Expected Prepayment Rate**: **{mean_prepay:.4%}** (Amount: ${mean_prepay * portfolio_initial_balance:,.2f})
* **Expected Monthly Interest Yield**: **{mean_interest:.4%}** (Amount: ${results['metrics']['expected_interest_earnings']:,.2f})

## 🔍 Key Risk Insights
1. **Value-at-Risk Limits**: Under normal operating scenarios, maximum portfolio loss will not exceed **{var_95:.2%}** with 95% confidence. Under severe stress conditions (99th percentile), cumulative losses could escalate to **{var_99:.2%}**.
2. **Prepayment Volatility**: An expected prepayment rate of **{mean_prepay:.2%}** suggests moderate refinancing activity, indicating stable yield duration.
""")
        
    logger.info("Monte Carlo simulation report written successfully.")

if __name__ == "__main__":
    run_monte_carlo_simulation()
