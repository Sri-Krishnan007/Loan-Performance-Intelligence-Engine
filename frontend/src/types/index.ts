export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  artifacts_available: Record<string, boolean>;
}

export interface RiskDistributionItem {
  level: string;
  count: number;
}

export interface StatusDistributionItem {
  status: string;
  count: number;
}

export interface MonthlyTrendItem {
  reporting_month: string;
  delinquency_rate: number;
  default_rate: number;
  prepayment_rate: number;
}

export interface OverviewResponse {
  total_loans: number;
  high_risk_loans: number;
  anomalies: number;
  default_rate: number;
  delinquency_rate: number;
  prepayment_rate: number;
  risk_distribution: RiskDistributionItem[];
  status_distribution: StatusDistributionItem[];
  monthly_trends: MonthlyTrendItem[];
}

export interface LoanItem {
  loan_id: string;
  credit_score_band: string;
  ltv_band: string;
  dti_band: string;
  state: string;
  servicer_name: string;
  current_status: string;
  original_balance: number;
  current_balance: number;
  days_past_due: number;
  vintage: number;
  risk_level: string;
  anomaly_score: number;
}

export interface LoanDetails {
  loan_id: string;
  original_balance: number;
  interest_rate: number;
  vintage: number;
  credit_score_band: string;
  ltv_band: string;
  dti_band: string;
  state: string;
  loan_purpose: string;
  occupancy_type: string;
  property_type: string;
  servicer_name: string;
  current_status: string;
  current_balance: number;
  days_past_due: number;
  loan_age_months: number;
  remaining_term_months: number;
  reporting_month: string;
  modification_flag: number;
}

export interface TimelineRecord {
  reporting_month: string;
  current_balance: number;
  days_past_due: number;
  current_status: string;
  interest_rate: number;
}

export interface TimelineResponse {
  loan_id: string;
  timeline: TimelineRecord[];
}

export interface RiskPredictionResponse {
  loan_id: string;
  delinquency_probability: number;
  default_probability: number;
  prepayment_probability: number;
  next_state: string;
  confidence: number;
  model_versions: Record<string, string>;
}

export interface AnomalyResponse {
  loan_id: string;
  anomaly_score: number;
  exception_required: boolean;
  exception_type: string;
  severity: string;
  drivers: string[];
  evidence: string[];
}

export interface AnomalyListItem {
  loan_id: string;
  reporting_month: string;
  anomaly_score: number;
  exception_type: string;
  severity: string;
  drivers: string[];
  evidence: string[];
}

export interface GlobalFeatureItem {
  feature: string;
  importance: number;
}

export interface LocalDrivers {
  positive: string[];
  negative: string[];
}

export interface ExplanationResponse {
  loan_id: string;
  global_features: GlobalFeatureItem[];
  local_drivers: LocalDrivers;
  confidence: number;
  false_positive_context: string | null;
  false_negative_context: string | null;
}

export interface ScenarioPortfolio {
  delinquency_rate: number;
  default_rate: number;
  prepayment_rate: number;
}

export interface ScenarioSegmentItem {
  [key: string]: string | number;
  delinquency_rate: number;
  default_rate: number;
  prepayment_rate: number;
}

export interface ScenarioDriverItem {
  variable: string;
  value: number;
}

export interface ScenarioResponse {
  scenario: string;
  portfolio: ScenarioPortfolio;
  segments: ScenarioSegmentItem[];
  drivers: ScenarioDriverItem[];
}

export interface ReviewerResponse {
  loan_id: string;
  summary: string;
  recommendation: string;
  action: string;
  confidence: number;
  disclaimer: string;
  model: string;
  timestamp: string;
  evidence: string[];
}

export interface DecisionResponse {
  status: string;
  loan_id: string;
  decision: string;
  timestamp: string;
}

export interface ModelHealthItem {
  name: string;
  version: string;
  roc_auc: number;
  pr_auc: number;
  f1: number;
  brier_score: number;
  calibrated: boolean;
  artifact_available: boolean;
}

export interface ValidationConfig {
  method: string;
  train_period: string;
  validation_period: string;
}

export interface ModelHealthResponse {
  models: ModelHealthItem[];
  validation: ValidationConfig;
}

export interface DataQualityResponse {
  batch_quality_score: number;
  missingness: Array<{ column: string; missing_count: number; missing_pct: number }>;
  outliers: Array<{ column: string; lower_bound: number; upper_bound: number; outlier_count: number; outlier_pct: number }>;
  relationship_breaks: Array<{
    loan_id: string;
    reporting_month: string;
    rule_id: string;
    relationship: string;
    affected_columns: string;
    observed_values: string;
    severity: string;
    description: string;
  }>;
  drift: Array<{ column: string; psi: number; status: string }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}
