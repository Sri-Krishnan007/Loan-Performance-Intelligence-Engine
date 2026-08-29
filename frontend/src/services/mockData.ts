import * as T from '../types';

export const mockHealth: T.HealthResponse = {
  status: "ok",
  service: "Loan Performance Intelligence Engine (Mock Mode)",
  version: "1.0.0 (Offline Fallback)",
  artifacts_available: {
    "delinquency_3m": true,
    "delinquency_6m": true,
    "default_12m": true,
    "prepayment_12m": true,
    "next_state": true,
    "anomaly_detector": true
  }
};

export const mockOverview: T.OverviewResponse = {
  total_loans: 2000,
  high_risk_loans: 187,
  anomalies: 64,
  default_rate: 0.0241,
  delinquency_rate: 0.0642,
  prepayment_rate: 0.0873,
  risk_distribution: [
    { level: "low", count: 1780 },
    { level: "medium", count: 100 },
    { level: "high", count: 120 }
  ],
  status_distribution: [
    { status: "Current", count: 1812 },
    { status: "Delinquent", count: 114 },
    { status: "Default", count: 48 },
    { status: "Prepaid", count: 26 }
  ],
  monthly_trends: [
    {
      reporting_month: "2026-07-01",
      delinquency_rate: 0.0871,
      default_rate: 0.0223,
      prepayment_rate: 0.0169
    },
    {
      reporting_month: "2026-06-01",
      delinquency_rate: 0.0850,
      default_rate: 0.0210,
      prepayment_rate: 0.0160
    },
    {
      reporting_month: "2026-05-01",
      delinquency_rate: 0.0820,
      default_rate: 0.0205,
      prepayment_rate: 0.0155
    }
  ]
};

export const mockLoansList: T.LoanItem[] = [
  {
    loan_id: "LN100234",
    credit_score_band: "660-699",
    ltv_band: "80-90",
    dti_band: "30-40",
    state: "CA",
    servicer_name: "Servicer A",
    current_status: "Current",
    original_balance: 350000.00,
    current_balance: 341000.00,
    days_past_due: 0,
    vintage: 2022,
    risk_level: "low",
    anomaly_score: 0.09
  },
  {
    loan_id: "LN101264",
    credit_score_band: "580-619",
    ltv_band: "90-100",
    dti_band: "40-50",
    state: "NY",
    servicer_name: "Servicer B",
    current_status: "Delinquent",
    original_balance: 550000.00,
    current_balance: 542000.00,
    days_past_due: 30,
    vintage: 2023,
    risk_level: "high",
    anomaly_score: 0.87
  },
  {
    loan_id: "LN100166",
    credit_score_band: "620-659",
    ltv_band: "70-80",
    dti_band: "20-30",
    state: "TX",
    servicer_name: "Servicer C",
    current_status: "Default",
    original_balance: 245000.00,
    current_balance: 242000.00,
    days_past_due: 90,
    vintage: 2021,
    risk_level: "high",
    anomaly_score: 0.76
  }
];

export const mockLoanDetails: Record<string, T.LoanDetails> = {
  "LN100234": {
    loan_id: "LN100234",
    original_balance: 350000.00,
    interest_rate: 4.5,
    vintage: 2022,
    credit_score_band: "660-699",
    ltv_band: "80-90",
    dti_band: "30-40",
    state: "CA",
    loan_purpose: "Purchase",
    occupancy_type: "Primary Residence",
    property_type: "Single Family",
    servicer_name: "Servicer A",
    current_status: "Current",
    current_balance: 341000.00,
    days_past_due: 0,
    loan_age_months: 24,
    remaining_term_months: 336,
    reporting_month: "2026-07-01",
    modification_flag: 0
  },
  "LN101264": {
    loan_id: "LN101264",
    original_balance: 550000.00,
    interest_rate: 5.2,
    vintage: 2023,
    credit_score_band: "580-619",
    ltv_band: "90-100",
    dti_band: "40-50",
    state: "NY",
    loan_purpose: "Refinance",
    occupancy_type: "Primary Residence",
    property_type: "Condo",
    servicer_name: "Servicer B",
    current_status: "Delinquent",
    current_balance: 542000.00,
    days_past_due: 30,
    loan_age_months: 18,
    remaining_term_months: 342,
    reporting_month: "2026-07-01",
    modification_flag: 1
  },
  "LN100166": {
    loan_id: "LN100166",
    original_balance: 245000.00,
    interest_rate: 6.0,
    vintage: 2021,
    credit_score_band: "620-659",
    ltv_band: "70-80",
    dti_band: "20-30",
    state: "TX",
    loan_purpose: "Purchase",
    occupancy_type: "Second Home",
    property_type: "Single Family",
    servicer_name: "Servicer C",
    current_status: "Default",
    current_balance: 242000.00,
    days_past_due: 90,
    loan_age_months: 36,
    remaining_term_months: 324,
    reporting_month: "2026-07-01",
    modification_flag: 0
  }
};

export const mockRiskPrediction: Record<string, T.RiskPredictionResponse> = {
  "LN100234": {
    loan_id: "LN100234",
    delinquency_probability: 0.033,
    default_probability: 0.015,
    prepayment_probability: 0.007,
    next_state: "CURRENT",
    confidence: 0.84,
    model_versions: { delinquency_3m: "v1.0", default_12m: "v1.0", prepayment_12m: "v1.0" }
  },
  "LN101264": {
    loan_id: "LN101264",
    delinquency_probability: 0.725,
    default_probability: 0.145,
    prepayment_probability: 0.012,
    next_state: "DELINQUENT",
    confidence: 0.78,
    model_versions: { delinquency_3m: "v1.0", default_12m: "v1.0", prepayment_12m: "v1.0" }
  },
  "LN100166": {
    loan_id: "LN100166",
    delinquency_probability: 0.950,
    default_probability: 0.760,
    prepayment_probability: 0.003,
    next_state: "DEFAULT",
    confidence: 0.92,
    model_versions: { delinquency_3m: "v1.0", default_12m: "v1.0", prepayment_12m: "v1.0" }
  }
};

export const mockAnomaly: Record<string, T.AnomalyResponse> = {
  "LN100234": {
    loan_id: "LN100234",
    anomaly_score: 0.09,
    exception_required: false,
    exception_type: "None",
    severity: "LOW",
    drivers: [],
    evidence: ["No operational updates discrepancies detected."]
  },
  "LN101264": {
    loan_id: "LN101264",
    anomaly_score: 0.87,
    exception_required: true,
    exception_type: "Data Reconciliation Discrepancy",
    severity: "HIGH",
    drivers: ["balance_conflict", "dpd_conflict", "missing_document"],
    evidence: ["Balance conflict: Primary=1,366,653.97, Servicer=1,444,691.13; DPD conflict: Primary=0, Servicer=30.0; Document status is Missing in primary database."]
  },
  "LN100166": {
    loan_id: "LN100166",
    anomaly_score: 0.76,
    exception_required: true,
    exception_type: "Data Reconciliation Discrepancy",
    severity: "HIGH",
    drivers: ["balance_conflict", "dpd_conflict"],
    evidence: ["Balance conflict: Primary=239,597.89, Servicer=242,528.77; DPD conflict: Primary=90, Servicer=30.0."]
  }
};

export const mockExplanation: Record<string, T.ExplanationResponse> = {
  "LN100234": {
    loan_id: "LN100234",
    global_features: [
      { feature: "days_past_due", importance: 0.0184 },
      { feature: "month_index", importance: 0.0005 },
      { feature: "original_balance", importance: 0.0002 }
    ],
    local_drivers: {
      positive: ["high_credit_score", "favorable_interest_rate"],
      negative: ["high_dti_ratio"]
    },
    confidence: 0.84,
    false_positive_context: "Prediction false alarms occur mostly when servicer balance updates conflict with primary records.",
    false_negative_context: "Target omissions are mitigated by checking cumulative modification counts."
  },
  "LN101264": {
    loan_id: "LN101264",
    global_features: [
      { feature: "days_past_due", importance: 0.0184 },
      { feature: "month_index", importance: 0.0005 }
    ],
    local_drivers: {
      positive: ["high_dti_ratio", "recent_delinquency", "balance_reconciliation_conflict"],
      negative: ["high_equity"]
    },
    confidence: 0.78,
    false_positive_context: "Discrepancy false alarms are common under loan modification requests.",
    false_negative_context: "Target omissions are mitigated by monitoring cumulative modification flag trends."
  },
  "LN100166": {
    loan_id: "LN100166",
    global_features: [
      { feature: "days_past_due", importance: 0.0184 },
      { feature: "month_index", importance: 0.0005 }
    ],
    local_drivers: {
      positive: ["recent_delinquency", "lower_credit_score", "balance_reconciliation_conflict"],
      negative: ["low_rate"]
    },
    confidence: 0.92,
    false_positive_context: "Default triggers are sensitive to servicer reporting cycles.",
    false_negative_context: "Default target flags are robustly aligned to DPD >= 90 terminal rules."
  }
};

export const mockDataQuality: T.DataQualityResponse = {
  batch_quality_score: 99.66,
  missingness: [
    { column: "loss_severity_band", missing_count: 70308, missing_pct: 0.9882 },
    { column: "current_status", missing_count: 0, missing_pct: 0.0 }
  ],
  outliers: [
    { column: "original_balance", lower_bound: -100000, upper_bound: 1100000, outlier_count: 48, outlier_pct: 0.00067 }
  ],
  relationship_breaks: [
    {
      loan_id: "LN101264",
      reporting_month: "2024-06-01",
      rule_id: "DLQ006",
      relationship: "Logical Delinquency Progression",
      affected_columns: "loan_id;days_past_due",
      observed_values: "loan_id=LN101264;days_past_due=90",
      severity: "warning",
      description: "Delinquency transitions should roll sequentially (e.g., 0 to 30, 30 to 60, 60 to 90). Skipped DPD buckets raise warnings."
    }
  ],
  drift: [
    { column: "credit_score_band", psi: 0.0012, status: "Stable" },
    { column: "interest_rate", psi: 0.0034, status: "Stable" }
  ]
};

export const mockModelHealth: T.ModelHealthResponse = {
  models: [
    { name: "delinquency_3m", version: "v1.0", roc_auc: 0.8836, pr_auc: 0.7887, f1: 0.8279, brier_score: 0.0240, calibrated: true, artifact_available: true },
    { name: "delinquency_6m", version: "v1.0", roc_auc: 0.8122, pr_auc: 0.7143, f1: 0.7073, brier_score: 0.0640, calibrated: true, artifact_available: true },
    { name: "default_12m", version: "v1.0", roc_auc: 0.8090, pr_auc: 0.5990, f1: 0.6869, brier_score: 0.0113, calibrated: true, artifact_available: true },
    { name: "prepayment_12m", version: "v1.0", roc_auc: 0.7790, pr_auc: 0.5522, f1: 0.6699, brier_score: 0.0083, calibrated: true, artifact_available: true }
  ],
  validation: {
    method: "time-aware-split",
    train_period: "2018-01-01 to 2024-12-01",
    validation_period: "2025-01-01 to 2026-07-01"
  }
};
