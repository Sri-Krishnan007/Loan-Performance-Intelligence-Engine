# Model Performance & Calibration Report

This report outlines the performance and calibration of the delinquency, default, prepayment, and multiclass next-state models, evaluated out-of-time (OOT) on validation data (Jan 2025 – Jul 2026).

---

## 1. Delinquency Projections (3-Month Horizon)
* **Raw Model**:
  * ROC-AUC: 0.8809
  * PR-AUC: 0.7832
  * Brier Score: 0.0571
* **Calibrated Model**:
  * ROC-AUC: 0.8836
  * PR-AUC: 0.7888
  * Brier Score: 0.0240 (Probability quality)

---

## 2. Delinquency Projections (6-Month Horizon)
* **Raw Model**:
  * ROC-AUC: 0.8074
  * Brier Score: 0.1181
* **Calibrated Model**:
  * ROC-AUC: 0.8122
  * Brier Score: 0.0640

---

## 3. Default Projections (12-Month Horizon)
* **Raw Model**:
  * ROC-AUC: 0.8020
  * Brier Score: 0.0948
* **Calibrated Model**:
  * ROC-AUC: 0.8090
  * Brier Score: 0.0114

---

## 4. Prepayment Projections (12-Month Horizon)
* **Raw Model**:
  * ROC-AUC: 0.7627
  * Brier Score: 0.1073
* **Calibrated Model**:
  * ROC-AUC: 0.7791
  * Brier Score: 0.0083

---

## 5. Next State Multiclass Model (Month t+1)
* **Macro F1-Score**: 0.1676
* **Next State Confusion Matrix**:

| Actual \ Predicted | Current | Delinquent | Default | Prepaid |
|---|---|---|---|---|
| **Current** | 5,474 | 2,390 | 3,166 | 4,185 |
| **Delinquent** | 139 | 144 | 116 | 90 |
| **Default** | 45 | 47 | 62 | 32 |
| **Prepaid** | 56 | 16 | 17 | 43 |
