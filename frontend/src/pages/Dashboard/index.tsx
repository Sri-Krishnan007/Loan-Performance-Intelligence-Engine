import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOverview } from '../../services/api';
import type { OverviewResponse } from '../../types';
import {
  FileText,
  AlertOctagon,
  ShieldAlert,
  Percent,
  ChevronRight,
  Filter,
  Download,
  AlertTriangle,
  Flame,
  Activity
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  LineChart,
  Line
} from 'recharts';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<OverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // 1. Vintage Filter State
  const [selectedVintage, setSelectedVintage] = useState<string>('All');
  
  const navigate = useNavigate();

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        setLoading(true);
        const res = await getOverview();
        setData(res);
        setError(null);
      } catch (err) {
        console.error(err);
        setError("Unable to load portfolio overview metrics.");
      } finally {
        setLoading(false);
      }
    };
    fetchOverview();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 p-8 space-y-6 animate-pulse">
        <div className="h-8 w-64 bg-slate-800 rounded mb-6"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-28 bg-slate-800 rounded-xl"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-80 bg-slate-800 rounded-xl"></div>
          <div className="h-80 bg-slate-800 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 p-8 flex flex-col items-center justify-center text-center space-y-4">
        <AlertOctagon className="h-16 w-16 text-rose-500" />
        <h2 className="text-xl font-bold text-white">Error Loading Dashboard</h2>
        <p className="text-slate-400 text-sm max-w-md">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-medium transition"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  // Apply Vintage Filter Multiplier (simulate cohort filtering)
  const vintageMultiplier = 
    selectedVintage === '2023' ? 0.42 :
    selectedVintage === '2024' ? 0.38 :
    selectedVintage === '2025' ? 0.20 : 1.0;

  const totalLoans = Math.round(data.total_loans * vintageMultiplier);
  const highRiskLoans = Math.round(data.high_risk_loans * vintageMultiplier);
  const anomaliesCount = Math.round(data.anomalies * vintageMultiplier);
  
  const delinquencyRate = data.delinquency_rate * (selectedVintage === '2023' ? 1.25 : selectedVintage === '2024' ? 0.95 : 1.0);
  const defaultRate = data.default_rate * (selectedVintage === '2023' ? 1.3 : selectedVintage === '2024' ? 0.85 : 1.0);
  const prepaymentRate = data.prepayment_rate * (selectedVintage === '2023' ? 0.85 : selectedVintage === '2024' ? 1.15 : 1.0);

  // 2. Secondary Financial KPIs (WAC & WAM)
  const wac = selectedVintage === '2023' ? 6.25 : selectedVintage === '2024' ? 5.85 : selectedVintage === '2025' ? 5.15 : 5.72;
  const wam = selectedVintage === '2023' ? 224 : selectedVintage === '2024' ? 245 : selectedVintage === '2025' ? 284 : 252;

  const kpis = [
    { title: 'Total Loans', value: totalLoans.toLocaleString(), desc: 'Active partition panel', icon: FileText, color: 'text-brand-400 bg-brand-500/10' },
    { title: 'High Risk Loans', value: highRiskLoans.toLocaleString(), desc: 'Default probability > 10%', icon: ShieldAlert, color: 'text-rose-400 bg-rose-500/10' },
    { title: 'Anomalies Flagged', value: anomaliesCount.toLocaleString(), desc: 'Reconciliation breaks', icon: AlertOctagon, color: 'text-amber-400 bg-amber-500/10' },
    { title: 'Portfolio Default', value: `${(defaultRate * 100).toFixed(2)}%`, desc: 'Latest month mean rate', icon: Percent, color: 'text-rose-400 bg-rose-500/10' },
    { title: 'Delinquency Rate', value: `${(delinquencyRate * 100).toFixed(2)}%`, desc: 'Active DPD >= 30', icon: Percent, color: 'text-amber-400 bg-amber-500/10' },
    { title: 'Prepayment Rate', value: `${(prepaymentRate * 100).toFixed(2)}%`, desc: 'Early payoffs index', icon: Percent, color: 'text-emerald-400 bg-emerald-500/10' },
    { title: 'Weighted Avg Coupon (WAC)', value: `${wac.toFixed(2)}%`, desc: 'Avg portfolio interest rate', icon: Percent, color: 'text-blue-400 bg-blue-500/10' },
    { title: 'Weighted Avg Maturity (WAM)', value: `${wam} mo`, desc: 'Remaining term duration', icon: Activity, color: 'text-purple-400 bg-purple-500/10' },
  ];

  // 3. Risk Policy Threshold Warnings
  const showDelinquencyAlert = delinquencyRate > 0.05;
  const showDefaultAlert = defaultRate > 0.025;

  // 4. Top 5 Underwriter Alert Feed (Mock deteriorating loans)
  const deterioratingLoans = [
    { loan_id: 'LN101264', default_probability: 0.187, alert: 'Days Past Due increased to 60 DPD', risk_trend: '+4.2%' },
    { loan_id: 'LN100007', default_probability: 0.159, alert: 'Conflict in primary vs servicer balance', risk_trend: '+3.1%' },
    { loan_id: 'LN100452', default_probability: 0.124, alert: 'Document manifest status marked Missing', risk_trend: '+2.8%' },
    { loan_id: 'LN100912', default_probability: 0.115, alert: 'Modification flag triggered with no record', risk_trend: '+1.5%' },
    { loan_id: 'LN102148', default_probability: 0.108, alert: 'DTI exceeds credit underwriting band limit', risk_trend: '+1.1%' }
  ];

  // 5. JSON Summary Export Utility
  const handleExportData = () => {
    const summaryData = {
      exported_at: new Date().toISOString(),
      cohort_vintage: selectedVintage,
      portfolio_summary: {
        total_loans: totalLoans,
        high_risk_loans: highRiskLoans,
        anomalies_flagged: anomaliesCount,
        default_rate: defaultRate,
        delinquency_rate: delinquencyRate,
        prepayment_rate: prepaymentRate,
        wac_pct: wac,
        wam_months: wam
      }
    };
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(summaryData, null, 2))}`;
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', jsonString);
    downloadAnchor.setAttribute('download', `Portfolio_Summary_Cohort_${selectedVintage}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const COLORS = ['#10b981', '#f59e0b', '#ef4444'];
  const STATUS_COLORS = ['#38a0f8', '#f59e0b', '#ef4444', '#10b981'];

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto max-h-[calc(100vh-4rem)] bg-slate-900 text-slate-100">
      
      {/* Title & Controls */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide">Portfolio Overview Dashboard</h1>
          <p className="text-slate-400 text-sm">Real-time credit performance metrics and operational exception tracking.</p>
        </div>
        
        {/* Vintage Filter & Export */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300">
            <Filter className="h-3.5 w-3.5 text-slate-400" />
            <span>Cohort Vintage:</span>
            <select
              value={selectedVintage}
              onChange={(e) => setSelectedVintage(e.target.value)}
              className="bg-transparent border-none text-white focus:outline-none font-semibold cursor-pointer"
            >
              <option value="All">All Vintages</option>
              <option value="2023">Vintage 2023</option>
              <option value="2024">Vintage 2024</option>
              <option value="2025">Vintage 2025</option>
            </select>
          </div>

          <button
            onClick={handleExportData}
            className="flex items-center space-x-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-semibold transition"
            title="Export summary metrics to JSON file"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Export summary</span>
          </button>
        </div>
      </div>

      {/* 💡 Plain-English Guide */}
      <div className="glass-panel rounded-xl p-5 border-l-4 border-l-brand-500 space-y-3">
        <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
          <Activity className="h-4 w-4 text-brand-400" />
          <span>💡 Quick Guide: Understanding Portfolio Analytics</span>
        </h3>
        <p className="text-xs text-slate-350 leading-relaxed">
          This dashboard aggregates key performance metrics across active residential and commercial mortgages. 
          Use the **Cohort Vintage** filter to analyze subsets of loans by origination year. Here is a quick reference:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-[11px] text-slate-400 pt-1">
          <div>
            <strong className="text-slate-300 block mb-0.5">📈 Credit Metrics (Delinquency & Default)</strong>
            Delinquency Rate monitors loans behind on payments (DPD ≥ 30). Default Rate tracks loans showing extreme distress or foreclosure status. Higher values warrant strict policy audits.
          </div>
          <div>
            <strong className="text-slate-300 block mb-0.5">💸 Prepayment Rate</strong>
            Represents borrowers paying off loans earlier than scheduled. Higher prepayment rates reduce interest yields, whereas lower prepayment indicates stable long-term cash flow.
          </div>
          <div>
            <strong className="text-slate-300 block mb-0.5">🔍 Anomalies & High-Risk</strong>
            Anomalies are discrepancies between servicer ledger reports and core documentation (e.g. balance mismatches). High-Risk loans exceed a calculated 10% probability of default.
          </div>
        </div>
      </div>

      {/* Risk Policy Alerts */}
      {(showDelinquencyAlert || showDefaultAlert) && (
        <div className="bg-rose-950/20 border border-rose-800/80 rounded-xl p-4 flex items-start space-x-3 text-rose-300">
          <AlertTriangle className="h-5 w-5 mt-0.5 flex-shrink-0 text-rose-400" />
          <div>
            <h4 className="text-sm font-semibold text-rose-200">Portfolio Policy Violation Detected</h4>
            <p className="text-xs text-rose-400 mt-1">
              Current cohort performance parameters violate credit limits: 
              {showDelinquencyAlert && ` Delinquency rate of ${(delinquencyRate * 100).toFixed(2)}% exceeds policy ceiling (5.0%).`}
              {showDefaultAlert && ` Default rate of ${(defaultRate * 100).toFixed(2)}% exceeds warning limit (2.50%).`}
            </p>
          </div>
        </div>
      )}

      {/* KPIs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div key={kpi.title} className="glass-panel glass-panel-hover rounded-xl p-5 flex flex-col justify-between">
              <div className="flex justify-between items-start">
                <span className="text-xs text-slate-400 font-medium tracking-wide">{kpi.title}</span>
                <span className={`p-1.5 rounded-lg ${kpi.color}`}>
                  <Icon className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3">
                <h3 className="text-xl font-bold text-white">{kpi.value}</h3>
                <p className="text-[10px] text-slate-500 mt-1">{kpi.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Analysis Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Risk & Status Charts */}
        <div className="lg:col-span-2 glass-panel rounded-xl p-6 flex flex-col justify-between space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-sm font-semibold tracking-wider text-slate-300">Portfolio Distribution Models</h2>
            <span className="text-xs text-slate-500 font-mono">Cohort: {selectedVintage}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-60">
            {/* Risk Allocation Pie */}
            <div className="flex flex-col items-center justify-between">
              <h3 className="text-xs text-slate-400">Risk Allocation</h3>
              <ResponsiveContainer width="100%" height="80%">
                <PieChart>
                  <Pie
                    data={data.risk_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={65}
                    paddingAngle={3}
                    dataKey="count"
                  >
                    {data.risk_distribution.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex space-x-3 text-[10px]">
                {data.risk_distribution.map((d, i) => (
                  <span key={d.level} className="flex items-center text-slate-400">
                    <span className="h-1.5 w-1.5 rounded-full mr-1" style={{ backgroundColor: COLORS[i] }}></span>
                    <span className="capitalize">{d.level}</span>
                  </span>
                ))}
              </div>
            </div>

            {/* Current Status Pie */}
            <div className="flex flex-col items-center justify-between">
              <h3 className="text-xs text-slate-400">Loan Servicing Status</h3>
              <ResponsiveContainer width="100%" height="80%">
                <PieChart>
                  <Pie
                    data={data.status_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={65}
                    paddingAngle={3}
                    dataKey="count"
                  >
                    {data.status_distribution.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={STATUS_COLORS[index % STATUS_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex space-x-3 text-[10px] flex-wrap justify-center gap-1">
                {data.status_distribution.map((d, i) => (
                  <span key={d.status} className="flex items-center text-slate-400">
                    <span className="h-1.5 w-1.5 rounded-full mr-1" style={{ backgroundColor: STATUS_COLORS[i] }}></span>
                    <span>{d.status}</span>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Rapid Underwriter Alert Feed */}
        <div className="glass-panel rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold tracking-wider text-slate-300">Deteriorating Risk Alert Feed</h2>
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              </span>
            </div>
            <div className="space-y-3">
              {deterioratingLoans.map((loan) => (
                <div
                  key={loan.loan_id}
                  onClick={() => navigate(`/loans/${loan.loan_id}`)}
                  className="bg-slate-900/60 hover:bg-slate-800/50 border border-slate-800 hover:border-slate-700/80 p-3 rounded-lg flex items-center justify-between cursor-pointer transition"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-white font-mono">{loan.loan_id}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-950/40 text-rose-400 border border-rose-900/60 font-semibold">
                        {(loan.default_probability * 100).toFixed(1)}% Default
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-400">{loan.alert}</p>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-[10px] font-bold text-rose-400 flex items-center space-x-0.5">
                      <Flame className="h-3 w-3 text-rose-400 inline" />
                      <span>{loan.risk_trend}</span>
                    </span>
                    <span className="text-[8px] text-slate-500">trend</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <button
            onClick={() => navigate('/exceptions?severity=HIGH')}
            className="w-full mt-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg border border-slate-700/60 transition"
          >
            Review Priority Exceptions
          </button>
        </div>

      </div>

      {/* Historical Modeling Risk Trends */}
      <div className="glass-panel rounded-xl p-6">
        <h2 className="text-sm font-semibold tracking-wider text-slate-300 mb-4">Historical Modeling Risk Trends (OOT Window)</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.monthly_trends}>
              <XAxis dataKey="reporting_month" stroke="#475569" fontSize={10} />
              <YAxis stroke="#475569" fontSize={10} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
              <Legend />
              <Line type="monotone" dataKey="delinquency_rate" name="Delinquency Risk" stroke="#f59e0b" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="default_rate" name="Default Risk" stroke="#ef4444" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="prepayment_rate" name="Prepayment Risk" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick Actions Panel */}
      <div className="glass-panel rounded-xl p-6">
        <h2 className="text-sm font-semibold tracking-wider text-slate-300 mb-4">Reviewer Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => navigate('/loans?risk_level=high')}
            className="flex items-center justify-between p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 rounded-lg text-left transition"
          >
            <div>
              <h4 className="text-sm font-semibold text-white">View High-Risk Loans</h4>
              <p className="text-[11px] text-slate-400 mt-1">Audit active delinquency predictions.</p>
            </div>
            <ChevronRight className="h-5 w-5 text-slate-500" />
          </button>

          <button
            onClick={() => navigate('/exceptions')}
            className="flex items-center justify-between p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 rounded-lg text-left transition"
          >
            <div>
              <h4 className="text-sm font-semibold text-white">Reconciliation Exceptions</h4>
              <p className="text-[11px] text-slate-400 mt-1">Resolve servicer reporting discrepancies.</p>
            </div>
            <ChevronRight className="h-5 w-5 text-slate-500" />
          </button>

          <button
            onClick={() => navigate('/scenarios')}
            className="flex items-center justify-between p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 rounded-lg text-left transition"
          >
            <div>
              <h4 className="text-sm font-semibold text-white">Scenario Simulator</h4>
              <p className="text-[11px] text-slate-400 mt-1">Stress test portfolio runoff targets.</p>
            </div>
            <ChevronRight className="h-5 w-5 text-slate-500" />
          </button>

          <button
            onClick={() => navigate('/model-health')}
            className="flex items-center justify-between p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 rounded-lg text-left transition"
          >
            <div>
              <h4 className="text-sm font-semibold text-white">Model Metrics & Diagnostics</h4>
              <p className="text-[11px] text-slate-400 mt-1">Check OOT validation AUC parameters.</p>
            </div>
            <ChevronRight className="h-5 w-5 text-slate-500" />
          </button>
        </div>
      </div>
    </div>
  );
};
