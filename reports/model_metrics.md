# Model Performance, Comparison & Calibration Report

This report outlines the comparative analysis between simple baseline models and optimized machine learning models, evaluated out-of-time (OOT) on validation data (Reporting Months >= 2025-01-01).

---

## 1. Chronological Split Diagnostics
* **Validation Split Date**: 2025-01-01
* **Training Panel**: 55,120 observations (reporting months < 2025-01-01)
* **Validation Panel**: 16,022 observations (reporting months >= 2025-01-01)

### Positive Class Rates (Imbalance Context)
* **Delinquency (3-Month Horizon)**: Train = 8.6538%, Val = 8.4384%
* **Delinquency (6-Month Horizon)**: Train = 15.2794%, Val = 15.4662%
* **Default (12-Month Horizon)**: Train = 2.2678%, Val = 2.4092%
* **Prepayment (12-Month Horizon)**: Train = 1.2264%, Val = 1.6977%

---

## 2. Comparative Analysis (Binary Classification Models)

### Delinquency 3-Month Projections
| Metric | Baseline (Raw) | Baseline (Calibrated) | Improved (Raw) | Improved (Calibrated) |
|---|---|---|---|---|
| **ROC-AUC** | 0.8748 | 0.8748 | 0.8829 | 0.8857 |
| **PR-AUC** | 0.7805 | 0.7805 | 0.7847 | 0.7914 |
| **Brier Score** | 0.0250 | 0.0249 | 0.0643 | 0.0240 |
| **ECE** | 0.0035 | 0.0000 | 0.1858 | 0.0000 |
| **F1-Score** | 0.8202 | 0.8202 | 0.8268 | 0.8279 |
| **Recall @ 10% Prec** | 0.8964 | 0.8964 | 0.9652 | 0.9586 |
| **Recall @ 20% Prec** | 0.8092 | 0.8092 | 0.8417 | 0.7700 |
| **Recall @ 50% Prec** | 0.7175 | 0.7175 | 0.7500 | 0.7463 |
| **Recall @ 90% Prec** | 0.6953 | 0.6953 | 0.7123 | 0.7101 |


### Delinquency 6-Month Projections
| Metric | Baseline (Raw) | Baseline (Calibrated) | Improved (Raw) | Improved (Calibrated) |
|---|---|---|---|---|
| **ROC-AUC** | 0.7947 | 0.7947 | 0.8075 | 0.8137 |
| **PR-AUC** | 0.7241 | 0.7241 | 0.7065 | 0.7212 |
| **Brier Score** | 0.0642 | 0.0641 | 0.1227 | 0.0639 |
| **ECE** | 0.0053 | 0.0000 | 0.2256 | 0.0000 |
| **F1-Score** | 0.7100 | 0.7100 | 0.6932 | 0.7070 |
| **Recall @ 10% Prec** | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **Recall @ 20% Prec** | 0.6872 | 0.6872 | 0.8713 | 0.8442 |
| **Recall @ 50% Prec** | 0.5504 | 0.5504 | 0.6412 | 0.6384 |
| **Recall @ 90% Prec** | 0.5504 | 0.5504 | 0.5646 | 0.5488 |


### Default 12-Month Projections
| Metric | Baseline (Raw) | Baseline (Calibrated) | Improved (Raw) | Improved (Calibrated) |
|---|---|---|---|---|
| **ROC-AUC** | 0.8141 | 0.8141 | 0.8270 | 0.8342 |
| **PR-AUC** | 0.6373 | 0.6373 | 0.5796 | 0.5885 |
| **Brier Score** | 0.0113 | 0.0113 | 0.1043 | 0.0112 |
| **ECE** | 0.0009 | 0.0000 | 0.2936 | 0.0000 |
| **F1-Score** | 0.6892 | 0.6892 | 0.4447 | 0.6893 |
| **Recall @ 10% Prec** | 0.5363 | 0.5363 | 0.6658 | 0.6606 |
| **Recall @ 20% Prec** | 0.5363 | 0.5363 | 0.5751 | 0.5674 |
| **Recall @ 50% Prec** | 0.5363 | 0.5363 | 0.5415 | 0.5363 |
| **Recall @ 90% Prec** | 0.5285 | 0.5285 | 0.5311 | 0.5311 |


### Prepayment 12-Month Projections
| Metric | Baseline (Raw) | Baseline (Calibrated) | Improved (Raw) | Improved (Calibrated) |
|---|---|---|---|---|
| **ROC-AUC** | 0.7563 | 0.7565 | 0.7721 | 0.7833 |
| **PR-AUC** | 0.5208 | 0.6806 | 0.5376 | 0.5555 |
| **Brier Score** | 0.0129 | 0.0096 | 0.1035 | 0.0083 |
| **ECE** | 0.0172 | 0.0000 | 0.2861 | 0.0000 |
| **F1-Score** | 0.6378 | 0.6378 | 0.3825 | 0.6715 |
| **Recall @ 10% Prec** | 0.5441 | 0.5147 | 0.5699 | 0.5478 |
| **Recall @ 20% Prec** | 0.5147 | 0.5147 | 0.5515 | 0.5478 |
| **Recall @ 50% Prec** | 0.5147 | 0.5147 | 0.5074 | 0.5074 |
| **Recall @ 90% Prec** | 0.0000 | 0.0000 | 0.5074 | 0.5074 |



---

## 3. Comparative Analysis (Next State Multiclass Predictions)
* **Baseline (Decision Tree) Macro-F1**: 0.0484
* **Improved (Tuned HistGradientBoosting) Macro-F1**: 0.1674

### Baseline Next State Confusion Matrix:

| Actual \ Predicted | Current | Delinquent | Default | Prepaid |
|---|---|---|---|---|
| **Current** | 123 | 978 | 2,945 | 11,169 |
| **Delinquent** | 0 | 96 | 117 | 276 |
| **Default** | 0 | 26 | 65 | 95 |
| **Prepaid** | 0 | 5 | 20 | 107 |

### Improved Next State Confusion Matrix:

| Actual \ Predicted | Current | Delinquent | Default | Prepaid |
|---|---|---|---|---|
| **Current** | 5,496 | 2,192 | 3,003 | 4,524 |
| **Delinquent** | 132 | 138 | 116 | 103 |
| **Default** | 48 | 54 | 51 | 33 |
| **Prepaid** | 52 | 15 | 19 | 46 |
