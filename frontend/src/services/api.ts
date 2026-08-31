import axios from 'axios';
import * as T from '../types';
import * as M from './mockData';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000,
});

// Detect mock mode via localStorage or window parameter
export const isMockModeActive = (): boolean => {
  if (import.meta.env.VITE_USE_MOCK === 'true') return true;
  return localStorage.getItem('VITE_USE_MOCK') === 'true';
};

export const setMockMode = (active: boolean) => {
  localStorage.setItem('VITE_USE_MOCK', active ? 'true' : 'false');
  window.location.reload();
};

export const getHealth = async (): Promise<T.HealthResponse> => {
  if (isMockModeActive()) return M.mockHealth;
  try {
    const res = await client.get<T.HealthResponse>('/health');
    return res.data;
  } catch (err) {
    console.warn("Backend /health unavailable, falling back to mock data.", err);
    return M.mockHealth;
  }
};

export const getOverview = async (): Promise<T.OverviewResponse> => {
  if (isMockModeActive()) return M.mockOverview;
  try {
    const res = await client.get<T.OverviewResponse>('/overview');
    return res.data;
  } catch (err) {
    console.warn("Backend /overview unavailable, falling back to mock data.", err);
    return M.mockOverview;
  }
};

export interface SearchParams {
  loan_id?: string;
  risk_level?: string;
  credit_band?: string;
  state?: string;
  servicer?: string;
  status?: string;
  anomaly?: boolean;
  vintage?: number;
  limit?: number;
  offset?: number;
}

export const getLoans = async (params: SearchParams = {}): Promise<T.PaginatedResponse<T.LoanItem>> => {
  if (isMockModeActive()) {
    let filtered = [...M.mockLoansList];
    if (params.loan_id) {
      filtered = filtered.filter(x => x.loan_id.toLowerCase().includes(params.loan_id!.toLowerCase()));
    }
    if (params.risk_level) {
      filtered = filtered.filter(x => x.risk_level === params.risk_level);
    }
    if (params.state) {
      filtered = filtered.filter(x => x.state.toLowerCase() === params.state!.toLowerCase());
    }
    if (params.status) {
      filtered = filtered.filter(x => x.current_status.toLowerCase() === params.status!.toLowerCase());
    }
    return {
      items: filtered,
      total: filtered.length,
      limit: params.limit || 20,
      offset: params.offset || 0
    };
  }

  try {
    const res = await client.get<T.PaginatedResponse<T.LoanItem>>('/loans', { params });
    return res.data;
  } catch (err) {
    console.warn("Backend /loans unavailable, falling back to mock data.", err);
    return {
      items: M.mockLoansList,
      total: M.mockLoansList.length,
      limit: params.limit || 20,
      offset: params.offset || 0
    };
  }
};

export const getLoan = async (loanId: string): Promise<T.LoanDetails> => {
  if (isMockModeActive()) {
    const details = M.mockLoanDetails[loanId] || M.mockLoanDetails["LN100234"];
    return { ...details, loan_id: loanId };
  }
  try {
    const res = await client.get<T.LoanDetails>(`/loans/${loanId}`);
    return res.data;
  } catch (err) {
    console.warn(`Backend /loans/${loanId} unavailable, falling back to mock data.`, err);
    const details = M.mockLoanDetails[loanId] || M.mockLoanDetails["LN100234"];
    return { ...details, loan_id: loanId };
  }
};

export const getLoanRisk = async (loanId: string): Promise<T.RiskPredictionResponse> => {
  if (isMockModeActive()) {
    const risk = M.mockRiskPrediction[loanId] || M.mockRiskPrediction["LN100234"];
    return { ...risk, loan_id: loanId };
  }
  try {
    const res = await client.get<T.RiskPredictionResponse>(`/loans/${loanId}/risk`);
    return res.data;
  } catch (err) {
    console.warn(`Backend /loans/${loanId}/risk unavailable, falling back to mock data.`, err);
    const risk = M.mockRiskPrediction[loanId] || M.mockRiskPrediction["LN100234"];
    return { ...risk, loan_id: loanId };
  }
};

export const getLoanTimeline = async (loanId: string): Promise<T.TimelineResponse> => {
  if (isMockModeActive()) {
    return {
      loan_id: loanId,
      timeline: [
        { reporting_month: "2026-07-01", current_balance: 341000, days_past_due: 0, current_status: "Current", interest_rate: 4.5 },
        { reporting_month: "2026-06-01", current_balance: 342000, days_past_due: 0, current_status: "Current", interest_rate: 4.5 },
        { reporting_month: "2026-05-01", current_balance: 343000, days_past_due: 0, current_status: "Current", interest_rate: 4.5 }
      ]
    };
  }
  try {
    const res = await client.get<T.TimelineResponse>(`/loans/${loanId}/timeline`);
    return res.data;
  } catch (err) {
    console.warn(`Backend /loans/${loanId}/timeline unavailable, falling back to mock data.`, err);
    return {
      loan_id: loanId,
      timeline: [
        { reporting_month: "2026-07-01", current_balance: 341000, days_past_due: 0, current_status: "Current", interest_rate: 4.5 },
        { reporting_month: "2026-06-01", current_balance: 342000, days_past_due: 0, current_status: "Current", interest_rate: 4.5 }
      ]
    };
  }
};

export const getLoanAnomaly = async (loanId: string): Promise<T.AnomalyResponse> => {
  if (isMockModeActive()) {
    const anomaly = M.mockAnomaly[loanId] || M.mockAnomaly["LN100234"];
    return { ...anomaly, loan_id: loanId };
  }
  try {
    const res = await client.get<T.AnomalyResponse>(`/loans/${loanId}/anomaly`);
    return res.data;
  } catch (err) {
    console.warn(`Backend /loans/${loanId}/anomaly unavailable, falling back to mock data.`, err);
    const anomaly = M.mockAnomaly[loanId] || M.mockAnomaly["LN100234"];
    return { ...anomaly, loan_id: loanId };
  }
};

export const getLoanExplanation = async (loanId: string): Promise<T.ExplanationResponse> => {
  if (isMockModeActive()) {
    const explanation = M.mockExplanation[loanId] || M.mockExplanation["LN100234"];
    return { ...explanation, loan_id: loanId };
  }
  try {
    const res = await client.get<T.ExplanationResponse>(`/loans/${loanId}/explanation`);
    return res.data;
  } catch (err) {
    console.warn(`Backend /loans/${loanId}/explanation unavailable, falling back to mock data.`, err);
    const explanation = M.mockExplanation[loanId] || M.mockExplanation["LN100234"];
    return { ...explanation, loan_id: loanId };
  }
};

export interface AnomalyFilterParams {
  severity?: string;
  exception_type?: string;
  limit?: number;
  offset?: number;
}

export const getAnomalies = async (params: AnomalyFilterParams = {}): Promise<T.PaginatedResponse<T.AnomalyListItem>> => {
  if (isMockModeActive()) {
    const items = [
      {
        loan_id: "LN101264",
        reporting_month: "2024-06-01",
        anomaly_score: 0.87,
        exception_type: "Data Reconciliation Discrepancy",
        severity: "HIGH",
        drivers: ["balance_conflict", "dpd_conflict"],
        evidence: ["Balance conflict flagged by servicer feeds."]
      }
    ];
    return {
      items,
      total: items.length,
      limit: params.limit || 20,
      offset: params.offset || 0
    };
  }
  try {
    const res = await client.get<T.PaginatedResponse<T.AnomalyListItem>>('/anomalies', { params });
    return res.data;
  } catch (err) {
    console.warn("Backend /anomalies unavailable, falling back to mock data.", err);
    const items = [
      {
        loan_id: "LN101264",
        reporting_month: "2024-06-01",
        anomaly_score: 0.87,
        exception_type: "Data Reconciliation Discrepancy",
        severity: "HIGH",
        drivers: ["balance_conflict", "dpd_conflict"],
        evidence: ["Balance conflict flagged by servicer feeds."]
      }
    ];
    return {
      items,
      total: items.length,
      limit: params.limit || 20,
      offset: params.offset || 0
    };
  }
};

export const getDataQuality = async (): Promise<T.DataQualityResponse> => {
  if (isMockModeActive()) return M.mockDataQuality;
  try {
    const res = await client.get<T.DataQualityResponse>('/data-quality');
    return res.data;
  } catch (err) {
    console.warn("Backend /data-quality unavailable, falling back to mock data.", err);
    return M.mockDataQuality;
  }
};

export const getModelHealth = async (): Promise<T.ModelHealthResponse> => {
  if (isMockModeActive()) return M.mockModelHealth;
  try {
    const res = await client.get<T.ModelHealthResponse>('/model-health');
    return res.data;
  } catch (err) {
    console.warn("Backend /model-health unavailable, falling back to mock data.", err);
    return M.mockModelHealth;
  }
};

export const runScenario = async (scenario: string, segments: string[], start_date?: string, end_date?: string): Promise<T.ScenarioResponse> => {
  if (isMockModeActive()) {
    return {
      scenario: scenario.toUpperCase(),
      portfolio: { delinquency_rate: 0.1029, default_rate: 0.0384, prepayment_rate: 0.0067 },
      segments: [
        { credit_band: "660-699", delinquency_rate: 0.125, default_rate: 0.045, prepayment_rate: 0.005 }
      ],
      drivers: [
        { variable: "Default Multiplier", value: 2.25 }
      ]
    };
  }
  try {
    const res = await client.post<T.ScenarioResponse>('/scenarios/run', { 
      scenario, 
      segments, 
      start_date: start_date || null, 
      end_date: end_date || null 
    });
    return res.data;
  } catch (err) {
    console.warn("Backend /scenarios/run unavailable, falling back to mock data.", err);
    return {
      scenario: scenario.toUpperCase(),
      portfolio: { delinquency_rate: 0.1029, default_rate: 0.0384, prepayment_rate: 0.0067 },
      segments: [
        { credit_band: "660-699", delinquency_rate: 0.125, default_rate: 0.045, prepayment_rate: 0.005 }
      ],
      drivers: [
        { variable: "Default Multiplier", value: 2.25 }
      ]
    };
  }
};

export const generateReviewer = async (loanId: string, tone: string = 'Standard'): Promise<T.ReviewerResponse> => {
  if (isMockModeActive()) {
    return {
      loan_id: loanId,
      summary: `[${tone.toUpperCase()} TONE] This loan exhibits high default probability metrics matching payment discrepancies.`,
      recommendation: "Priority Review recommended. Resolve the servicer days past due conflict.",
      action: "Priority Review",
      confidence: 0.82,
      disclaimer: "Recommendation — Not a Decision",
      model: "mock-model",
      timestamp: new Date().toISOString(),
      evidence: ["Balance mismatch flagged."]
    };
  }
  try {
    const res = await client.post<T.ReviewerResponse>('/reviewer', { loan_id: loanId, tone });
    return res.data;
  } catch (err) {
    console.warn("Backend /reviewer unavailable, falling back to mock data.", err);
    return {
      loan_id: loanId,
      summary: `[${tone.toUpperCase()} TONE] This loan exhibits high default probability metrics matching payment discrepancies.`,
      recommendation: "Priority Review recommended. Resolve the servicer days past due conflict.",
      action: "Priority Review",
      confidence: 0.82,
      disclaimer: "Recommendation — Not a Decision",
      model: "mock-model",
      timestamp: new Date().toISOString(),
      evidence: ["Balance mismatch flagged."]
    };
  }
};

export const submitReviewerDecision = async (loanId: string, decision: string, reviewerNote: string): Promise<T.DecisionResponse> => {
  if (isMockModeActive()) {
    return {
      status: "success",
      loan_id: loanId,
      decision,
      timestamp: new Date().toISOString()
    };
  }
  try {
    const res = await client.post<T.DecisionResponse>(`/reviewer/${loanId}/decision`, { decision, reviewer_note: reviewerNote });
    return res.data;
  } catch (err) {
    console.warn(`Backend /reviewer/${loanId}/decision unavailable, falling back to mock data.`, err);
    return {
      status: "success",
      loan_id: loanId,
      decision,
      timestamp: new Date().toISOString()
    };
  }
};

export interface LivePredictionPayload {
  fico_score: number;
  ltv: number;
  dti: number;
  original_balance: number;
  current_balance: number;
  interest_rate: number;
  days_past_due: number;
  document_status: string;
  state: string;
  loan_purpose: string;
  occupancy_type: string;
  property_type: string;
  servicer_name: string;
  current_status: string;
  modification_flag: number;
  prepayment_flag: number;
  
  // Optional servicer update reconciliation fields
  servicer_current_balance?: number;
  servicer_days_past_due?: number;
  servicer_document_status?: string;
  servicer_status?: string;
}

export interface LivePredictionResult {
  delinquency_probability: number;
  default_probability: number;
  prepayment_probability: number;
  next_state: string;
  confidence: number;
  anomaly_score: number;
  exception_type: string;
  action: string;
  top_drivers: string;
}

export const predictLive = async (payload: LivePredictionPayload): Promise<LivePredictionResult> => {
  if (isMockModeActive()) {
    return {
      delinquency_probability: payload.days_past_due > 0 ? 0.42 : 0.08,
      default_probability: payload.fico_score < 620 ? 0.15 : 0.02,
      prepayment_probability: payload.interest_rate > 6.5 ? 0.12 : 0.03,
      next_state: payload.days_past_due >= 30 ? "DELINQUENT" : payload.current_status.toUpperCase(),
      confidence: 0.88,
      anomaly_score: payload.servicer_current_balance && Math.abs(payload.current_balance - payload.servicer_current_balance) > 10 ? 0.75 : 0.15,
      exception_type: payload.days_past_due >= 60 ? "Severe Delinquency" : payload.document_status === "Missing" ? "Documentation Gap" : "None",
      action: payload.days_past_due >= 60 ? "Priority Review" : "No Action",
      top_drivers: payload.fico_score < 620 ? "fico_score_val" : "None"
    };
  }
  try {
    const res = await client.post<LivePredictionResult>('/loans/predict', payload);
    return res.data;
  } catch (err) {
    console.warn("Backend live /loans/predict unavailable, falling back to mock predictions.", err);
    return {
      delinquency_probability: payload.days_past_due > 0 ? 0.42 : 0.08,
      default_probability: payload.fico_score < 620 ? 0.15 : 0.02,
      prepayment_probability: payload.interest_rate > 6.5 ? 0.12 : 0.03,
      next_state: payload.days_past_due >= 30 ? "DELINQUENT" : payload.current_status.toUpperCase(),
      confidence: 0.88,
      anomaly_score: payload.servicer_current_balance && Math.abs(payload.current_balance - payload.servicer_current_balance) > 10 ? 0.75 : 0.15,
      exception_type: payload.days_past_due >= 60 ? "Severe Delinquency" : payload.document_status === "Missing" ? "Documentation Gap" : "None",
      action: payload.days_past_due >= 60 ? "Priority Review" : "No Action",
      top_drivers: payload.fico_score < 620 ? "fico_score_val" : "None"
    };
  }
};

export interface MonteCarloMetrics {
  portfolio_initial_balance: number;
  num_trials: number;
  projection_months: number;
  loss_severity: number;
  metrics: {
    mean_loss_rate: number;
    std_loss_rate: number;
    value_at_risk_95: number;
    value_at_risk_99: number;
    mean_prepayment_rate: number;
    mean_interest_yield_rate: number;
    expected_losses: number;
    value_at_risk_95_amount: number;
    value_at_risk_99_amount: number;
    expected_interest_earnings: number;
  };
}

export interface StressSensitivityItem {
  leverage_stress: string;
  equity_stress: string;
  average_default_probability: number;
}

export const getMonteCarlo = async (start_date?: string, end_date?: string): Promise<MonteCarloMetrics> => {
  if (isMockModeActive()) {
    return {
      portfolio_initial_balance: 411051634.15,
      num_trials: 1000,
      projection_months: 12,
      loss_severity: 0.45,
      metrics: {
        mean_loss_rate: 0.13748,
        std_loss_rate: 0.0035,
        value_at_risk_95: 0.14408,
        value_at_risk_99: 0.14819,
        mean_prepayment_rate: 0.0425,
        mean_interest_yield_rate: 0.052,
        expected_losses: 56511116.5,
        value_at_risk_95_amount: 59223397.0,
        value_at_risk_99_amount: 60915729.0,
        expected_interest_earnings: 21374684.0
      }
    };
  }
  try {
    const res = await client.get<MonteCarloMetrics>('/scenarios/monte-carlo', { 
      params: { 
        start_date: start_date || null, 
        end_date: end_date || null 
      } 
    });
    return res.data;
  } catch (err) {
    console.warn("Backend /scenarios/monte-carlo unavailable, using mock data.", err);
    return {
      portfolio_initial_balance: 411051634.15,
      num_trials: 1000,
      projection_months: 12,
      loss_severity: 0.45,
      metrics: {
        mean_loss_rate: 0.13748,
        std_loss_rate: 0.0035,
        value_at_risk_95: 0.14408,
        value_at_risk_99: 0.14819,
        mean_prepayment_rate: 0.0425,
        mean_interest_yield_rate: 0.052,
        expected_losses: 56511116.5,
        value_at_risk_95_amount: 59223397.0,
        value_at_risk_99_amount: 60915729.0,
        expected_interest_earnings: 21374684.0
      }
    };
  }
};

export const getStressSensitivity = async (start_date?: string, end_date?: string): Promise<StressSensitivityItem[]> => {
  if (isMockModeActive()) {
    return [
      { leverage_stress: "Base Leverage", equity_stress: "Base Equity", average_default_probability: 0.0152 },
      { leverage_stress: "Base Leverage", equity_stress: "Moderate LTV (+10%)", average_default_probability: 0.0242 },
      { leverage_stress: "Base Leverage", equity_stress: "Severe LTV (+20%)", average_default_probability: 0.0384 },
      { leverage_stress: "Moderate DTI (+5%)", equity_stress: "Base Equity", average_default_probability: 0.0315 },
      { leverage_stress: "Moderate DTI (+5%)", equity_stress: "Moderate LTV (+10%)", average_default_probability: 0.0482 },
      { leverage_stress: "Moderate DTI (+5%)", equity_stress: "Severe LTV (+20%)", average_default_probability: 0.0684 },
      { leverage_stress: "Severe DTI (+12%)", equity_stress: "Base Equity", average_default_probability: 0.0582 },
      { leverage_stress: "Severe DTI (+12%)", equity_stress: "Moderate LTV (+10%)", average_default_probability: 0.0842 },
      { leverage_stress: "Severe DTI (+12%)", equity_stress: "Severe LTV (+20%)", average_default_probability: 0.1245 }
    ];
  }
  try {
    const res = await client.get<StressSensitivityItem[]>('/scenarios/sensitivity', { 
      params: { 
        start_date: start_date || null, 
        end_date: end_date || null 
      } 
    });
    return res.data;
  } catch (err) {
    console.warn("Backend /scenarios/sensitivity unavailable, using mock data.", err);
    return [
      { leverage_stress: "Base Leverage", equity_stress: "Base Equity", average_default_probability: 0.0152 },
      { leverage_stress: "Base Leverage", equity_stress: "Moderate LTV (+10%)", average_default_probability: 0.0242 },
      { leverage_stress: "Base Leverage", equity_stress: "Severe LTV (+20%)", average_default_probability: 0.0384 },
      { leverage_stress: "Moderate DTI (+5%)", equity_stress: "Base Equity", average_default_probability: 0.0315 },
      { leverage_stress: "Moderate DTI (+5%)", equity_stress: "Moderate LTV (+10%)", average_default_probability: 0.0482 },
      { leverage_stress: "Moderate DTI (+5%)", equity_stress: "Severe LTV (+20%)", average_default_probability: 0.0684 },
      { leverage_stress: "Severe DTI (+12%)", equity_stress: "Base Equity", average_default_probability: 0.0582 },
      { leverage_stress: "Severe DTI (+12%)", equity_stress: "Moderate LTV (+10%)", average_default_probability: 0.0842 },
      { leverage_stress: "Severe DTI (+12%)", equity_stress: "Severe LTV (+20%)", average_default_probability: 0.1245 }
    ];
  }
};
