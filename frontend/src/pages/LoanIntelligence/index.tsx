import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  getLoan,
  getLoanRisk,
  getLoanTimeline,
  getLoanExplanation,
  getLoanAnomaly
} from '../../services/api';
import type * as T from '../../types';
import {
  ArrowLeft,
  AlertTriangle,
  TrendingDown,
  Info,
  ChevronRight,
  TrendingUp,
  Fingerprint
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  Cell
} from 'recharts';

export const LoanIntelligence: React.FC = () => {
  const { loanId } = useParams<{ loanId: string }>();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<'overview' | 'risk' | 'timeline' | 'explain' | 'anomaly'>('overview');
  
  // Data states
  const [loan, setLoan] = useState<T.LoanDetails | null>(null);
  const [risk, setRisk] = useState<T.RiskPredictionResponse | null>(null);
  const [timeline, setTimeline] = useState<T.TimelineRecord[]>([]);
  const [explanation, setExplanation] = useState<T.ExplanationResponse | null>(null);
  const [anomaly, setAnomaly] = useState<T.AnomalyResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loanId) return;

    const fetchAllData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch concurrently
        const [loanRes, riskRes, timelineRes, explainRes, anomalyRes] = await Promise.all([
          getLoan(loanId),
          getLoanRisk(loanId),
          getLoanTimeline(loanId),
          getLoanExplanation(loanId),
          getLoanAnomaly(loanId)
        ]);

        setLoan(loanRes);
        setRisk(riskRes);
        setTimeline(timelineRes.timeline);
        setExplanation(explainRes);
        setAnomaly(anomalyRes);
      } catch (err) {
        console.error(err);
        setError(`Unable to load audit details for Loan ${loanId}.`);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, [loanId]);

  if (loading) {
    return (
      <div className="flex-1 p-8 space-y-6 animate-pulse">
        <div className="flex items-center space-x-3">
          <div className="h-6 w-6 bg-slate-800 rounded"></div>
          <div className="h-8 w-48 bg-slate-800 rounded"></div>
        </div>
        <div className="h-10 bg-slate-800 rounded-lg"></div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-96 bg-slate-800 rounded-xl"></div>
          <div className="h-96 bg-slate-800 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (error || !loan) {
    return (
      <div className="flex-1 p-8 flex flex-col items-center justify-center text-center space-y-4">
        <AlertTriangle className="h-16 w-16 text-rose-500" />
        <h2 className="text-xl font-bold text-white">Investigation Failed</h2>
        <p className="text-slate-400 text-sm max-w-md">{error}</p>
        <button
          onClick={() => navigate('/loans')}
          className="flex items-center space-x-2 px-4 py-2 border border-slate-700 bg-slate-800 text-slate-300 rounded-lg text-sm transition"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Loan Explorer</span>
        </button>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Loan Profile' },
    { id: 'risk', label: 'ML Predictions' },
    { id: 'timeline', label: 'Servicing Timeline' },
    { id: 'explain', label: 'Risk Drivers' },
    { id: 'anomaly', label: 'Anomaly Audit' },
  ];

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto max-h-[calc(100vh-4rem)]">
      {/* Back link & Header */}
      <div className="flex justify-between items-start">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/loans')}
            className="p-2 border border-slate-700 bg-slate-800/40 rounded-lg hover:text-white text-slate-400 transition"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-wide flex items-center">
              Loan Intelligence: <span className="text-brand-400 ml-2 font-mono">{loan.loan_id}</span>
            </h1>
            <p className="text-slate-400 text-xs mt-1">
              Active servicer is <span className="font-semibold text-slate-300">{loan.servicer_name}</span>. Vintage year is <span className="font-semibold text-slate-300">{loan.vintage}</span>.
            </p>
          </div>
        </div>

        {/* AI review shortcut */}
        <button
          onClick={() => navigate(`/reviewer?loan_id=${loan.loan_id}`)}
          className="flex items-center space-x-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg px-4 py-2.5 text-sm font-semibold shadow-md transition"
        >
          <span>Run AI Reviewer Copilot</span>
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-6 py-3 text-sm font-semibold border-b-2 transition-all ${
              activeTab === tab.id
                ? 'border-brand-500 text-white bg-brand-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      <div className="bg-slate-900 border border-slate-800/60 rounded-xl p-6 min-h-[400px]">
        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Origination Parameters & Static Profile</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { label: 'Outstanding Balance', value: `$${loan.current_balance.toLocaleString()}` },
                { label: 'Original Principal', value: `$${loan.original_balance.toLocaleString()}` },
                { label: 'Annual Interest Rate', value: `${loan.interest_rate.toFixed(3)}%` },
                { label: 'Loan Status', value: loan.current_status },
                { label: 'Loan Age (months)', value: loan.loan_age_months },
                { label: 'Remaining Term (months)', value: loan.remaining_term_months },
                { label: 'Credit Score Band (FICO)', value: loan.credit_score_band },
                { label: 'LTV Ratio Band', value: loan.ltv_band },
                { label: 'DTI Ratio Band', value: loan.dti_band },
                { label: 'Property State', value: loan.state },
                { label: 'Loan Purpose', value: loan.loan_purpose },
                { label: 'Property Type', value: loan.property_type },
                { label: 'Occupancy Type', value: loan.occupancy_type },
                { label: 'Reporting Month', value: loan.reporting_month },
              ].map((item, idx) => (
                <div key={idx} className="bg-slate-800/20 border border-slate-800 rounded-lg p-4 flex flex-col justify-between">
                  <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">{item.label}</span>
                  <span className="text-sm font-bold text-white mt-1.5">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 2: Risk */}
        {activeTab === 'risk' && risk && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Credit Risk Predictor Results</h3>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: 'Delinquency Prob (3m)', val: risk.delinquency_probability, color: 'text-amber-400' },
                  { label: 'Default Prob (12m)', val: risk.default_probability, color: 'text-rose-400' },
                  { label: 'Prepayment Prob (12m)', val: risk.prepayment_probability, color: 'text-emerald-400' },
                ].map((item, i) => (
                  <div key={i} className="bg-slate-800/30 border border-slate-800 rounded-lg p-5">
                    <span className="text-[10px] text-slate-500 font-semibold tracking-wide uppercase">{item.label}</span>
                    <h2 className={`text-2xl font-bold mt-2 ${item.color}`}>{(item.val * 100).toFixed(1)}%</h2>
                  </div>
                ))}
              </div>

              {/* Classification Info */}
              <div className="bg-slate-800/20 border border-slate-800 rounded-lg p-5 grid grid-cols-2 gap-6">
                <div>
                  <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wide">Predicted Next State Transition</span>
                  <h3 className="text-lg font-bold text-white mt-1.5">{risk.next_state}</h3>
                  <p className="text-[11px] text-slate-500 mt-1">Classifier output for next monthly status transition.</p>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wide">Model Inference Confidence</span>
                  <h3 className="text-lg font-bold text-slate-300 mt-1.5">{(risk.confidence * 100).toFixed(0)}%</h3>
                  <p className="text-[11px] text-slate-500 mt-1">Based on probability bounds threshold calibrations.</p>
                </div>
              </div>
            </div>

            {/* Model Checklist */}
            <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-5">
              <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase mb-3">Model Versions Details</h3>
              <div className="space-y-3 text-xs">
                {Object.entries(risk.model_versions).map(([model, ver]) => (
                  <div key={model} className="flex justify-between border-b border-slate-800/60 pb-2">
                    <span className="capitalize text-slate-400">{model.replace('_', ' ')}</span>
                    <span className="font-mono text-white font-semibold">{ver}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Timeline */}
        {activeTab === 'timeline' && (
          <div className="space-y-8">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Historical Servicing Timeline</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Amortization Chart */}
              <div className="bg-slate-800/30 border border-slate-800 p-5 rounded-lg">
                <h4 className="text-xs font-semibold text-slate-400 mb-3">Balance Amortization Path</h4>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={timeline}>
                      <XAxis dataKey="reporting_month" stroke="#475569" fontSize={9} />
                      <YAxis stroke="#475569" fontSize={9} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                      <Area type="monotone" dataKey="current_balance" name="Current Balance" stroke="#0e83e3" fill="#0e83e3" fillOpacity={0.1} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* DPD Chart */}
              <div className="bg-slate-800/30 border border-slate-800 p-5 rounded-lg">
                <h4 className="text-xs font-semibold text-slate-400 mb-3">Delinquency Tracking (DPD)</h4>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={timeline}>
                      <XAxis dataKey="reporting_month" stroke="#475569" fontSize={9} />
                      <YAxis stroke="#475569" fontSize={9} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                      <Area type="monotone" dataKey="days_past_due" name="Days Past Due" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.1} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Explainability */}
        {activeTab === 'explain' && explanation && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Local Drivers */}
            <div className="lg:col-span-2 space-y-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Local Risk Drivers</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Positive (Risk-Increasing) */}
                <div className="bg-rose-950/20 border border-rose-900/50 rounded-xl p-5 space-y-3">
                  <div className="flex items-center space-x-2 text-rose-400 font-semibold text-xs uppercase tracking-wide">
                    <TrendingUp className="h-4 w-4" />
                    <span>Risk-Increasing Drivers</span>
                  </div>
                  <ul className="space-y-2 text-xs">
                    {explanation.local_drivers.positive.map((driver, idx) => (
                      <li key={idx} className="flex items-start space-x-2 text-slate-300">
                        <span className="h-1.5 w-1.5 rounded-full bg-rose-500 mt-1.5"></span>
                        <span>{driver.replace(/_/g, ' ')}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Negative (Protective) */}
                <div className="bg-emerald-950/20 border border-emerald-900/50 rounded-xl p-5 space-y-3">
                  <div className="flex items-center space-x-2 text-emerald-400 font-semibold text-xs uppercase tracking-wide">
                    <TrendingDown className="h-4 w-4" />
                    <span>Protective Factors</span>
                  </div>
                  <ul className="space-y-2 text-xs">
                    {explanation.local_drivers.negative.map((driver, idx) => (
                      <li key={idx} className="flex items-start space-x-2 text-slate-300">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mt-1.5"></span>
                        <span>{driver.replace(/_/g, ' ')}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Responsible AI Context */}
              <div className="bg-slate-800/10 border border-slate-800 p-4 rounded-lg flex space-x-3 text-xs text-slate-400">
                <Info className="h-5 w-5 text-slate-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-slate-300">Auditor Context Notes</h4>
                  <p className="mt-1">{explanation.false_positive_context}</p>
                </div>
              </div>
            </div>

            {/* Global Ranks Chart */}
            <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-5">
              <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase mb-4">Global Features Importance</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={explanation.global_features} layout="vertical">
                    <XAxis type="number" stroke="#475569" fontSize={8} />
                    <YAxis dataKey="feature" type="category" stroke="#475569" fontSize={8} width={80} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                    <Bar dataKey="importance" fill="#38a0f8" radius={[0, 4, 4, 0]}>
                      {explanation.global_features.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#38a0f8' : '#1e293b'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-[10px] text-slate-500 mt-2 text-center">Computed via Model-Agnostic Permutation Feature Importance.</p>
            </div>
          </div>
        )}

        {/* Tab 5: Anomaly */}
        {activeTab === 'anomaly' && anomaly && (
          <div className="space-y-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Operational Update Reconciliation Audit</h3>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Anomaly Indicator */}
              <div className="bg-slate-800/30 border border-slate-800 rounded-xl p-5 flex flex-col justify-between items-center text-center">
                <div className="space-y-1">
                  <Fingerprint className="h-10 w-10 text-amber-500" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mt-2">Anomaly Audit Score</h4>
                </div>
                <h1 className="text-4xl font-extrabold text-white mt-4">{(anomaly.anomaly_score * 100).toFixed(0)}%</h1>
                <span
                  className={`px-3 py-1 rounded-full text-[10px] font-semibold uppercase mt-4 ${
                    anomaly.severity === 'HIGH'
                      ? 'bg-rose-950/50 text-rose-400 border border-rose-800'
                      : anomaly.severity === 'MEDIUM'
                      ? 'bg-amber-950/50 text-amber-400 border border-amber-800'
                      : 'bg-emerald-950/50 text-emerald-400 border border-emerald-800'
                  }`}
                >
                  {anomaly.severity} SEVERITY
                </span>
              </div>

              {/* Exception Details */}
              <div className="lg:col-span-2 bg-slate-800/20 border border-slate-800 rounded-xl p-5 space-y-4">
                <div>
                  <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Deterministic Exception Mappings</span>
                  <h3 className="text-lg font-bold text-white mt-1">{anomaly.exception_type}</h3>
                </div>

                <div className="border-t border-slate-800 pt-4">
                  <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Reconciliation Audit Evidence</span>
                  <div className="mt-2 space-y-2">
                    {anomaly.evidence.map((ev, idx) => (
                      <div key={idx} className="bg-slate-900 border border-slate-800/60 p-3 rounded-lg text-xs text-slate-300">
                        {ev}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
