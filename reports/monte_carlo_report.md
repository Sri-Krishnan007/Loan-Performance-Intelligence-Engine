# Monte Carlo Portfolio Simulation Report

This report summarizes the statistical credit loss forecasting and prepayment volatility simulations executed across the active mortgage pool.

## 📊 Simulation Design Parameters
* **Total Trials Simulated**: 1,000
* **Projection Horizon**: 12 Months
* **Assumed Loss Severity (LGD)**: 45.0%
* **Active Loan Cohort**: 2,000 Accounts

## 📈 Portfolio Statistical Metrics
* **Total Portfolio Principal Balance**: $411,051,634.15
* **Expected Cumulative Loss Rate**: **13.7481%** (Amount: $56,511,825.20)
* **Value-at-Risk (95% VaR)**: **14.4078%** (Amount: $59,223,473.23)
* **Value-at-Risk (99% VaR)**: **14.8195%** (Amount: $60,915,932.94)
* **Expected Prepayment Rate**: **1.3245%** (Amount: $5,444,310.95)
* **Expected Monthly Interest Yield**: **3.7000%** (Amount: $15,208,912.13)

## 🔍 Key Risk Insights
1. **Value-at-Risk Limits**: Under normal operating scenarios, maximum portfolio loss will not exceed **14.41%** with 95% confidence. Under severe stress conditions (99th percentile), cumulative losses could escalate to **14.82%**.
2. **Prepayment Volatility**: An expected prepayment rate of **1.32%** suggests moderate refinancing activity, indicating stable yield duration.
