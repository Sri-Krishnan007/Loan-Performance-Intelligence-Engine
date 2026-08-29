import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOverview } from '../../services/api';
import type { OverviewResponse } from '../../types';
import {
  FileText,
  AlertOctagon,
  ShieldAlert,
  Percent,
  ChevronRight
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

  const COLORS = ['#10b981', '#f59e0b', '#ef4444'];
  const STATUS_COLORS = ['#38a0f8', '#f59e0b', '#ef4444', '#10b981'];

  const kpis = [
    { title: 'Total Loans', value: data.total_loans.toLocaleString(), desc: 'Active test partition panel', icon: FileText, color: 'text-brand-400 bg-brand-500/10' },
    { title: 'High Risk Loans', value: data.high_risk_loans.toLocaleString(), desc: 'Default probability > 10%', icon: ShieldAlert, color: 'text-rose-400 bg-rose-500/10' },
    { title: 'Anomalies Flagged', value: data.anomalies.toLocaleString(), desc: 'Reconciliation breaks', icon: AlertOctagon, color: 'text-amber-400 bg-amber-500/10' },
    { title: 'Portfolio Default', value: `${(data.default_rate * 100).toFixed(2)}%`, desc: 'Latest month mean rate', icon: Percent, color: 'text-rose-400 bg-rose-500/10' },
    { title: 'Delinquency Rate', value: `${(data.delinquency_rate * 100).toFixed(2)}%`, desc: 'Active DPD >= 30', icon: Percent, color: 'text-amber-400 bg-amber-500/10' },
    { title: 'Prepayment Rate', value: `${(data.prepayment_rate * 100).toFixed(2)}%`, desc: 'Early payoffs index', icon: Percent, color: 'text-emerald-400 bg-emerald-500/10' },
  ];

  return (
    <div className="flex-1 p-8 space-y-8 overflow-y-auto max-h-[calc(100vh-4rem)]">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-wide">Portfolio Dashboard</h1>
        <p className="text-slate-400 text-sm">Real-time credit performance metrics and operational exception tracking.</p>
      </div>

      {/* KPIs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div key={kpi.title} className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-5 flex flex-col justify-between hover:border-slate-600 transition">
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

      {/* Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Level and Status Distributions */}
        <div className="bg-slate-800/30 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
          <h2 className="text-sm font-semibold tracking-wider text-slate-300 mb-4">Risk & Status Distributions</h2>
          <div className="grid grid-cols-2 gap-4 h-64">
            {/* Risk Levels Pie */}
            <div className="flex flex-col items-center">
              <h3 className="text-xs text-slate-400 mb-2">Risk Allocation</h3>
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
              <div className="flex space-x-3 text-[10px] mt-1">
                {data.risk_distribution.map((d, i) => (
                  <span key={d.level} className="flex items-center">
                    <span className="h-1.5 w-1.5 rounded-full mr-1" style={{ backgroundColor: COLORS[i] }}></span>
                    <span className="capitalize">{d.level} ({d.count})</span>
                  </span>
                ))}
              </div>
            </div>

            {/* Current Status Pie */}
            <div className="flex flex-col items-center">
              <h3 className="text-xs text-slate-400 mb-2">Loan Servicing Status</h3>
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
              <div className="flex space-x-3 text-[10px] mt-1 flex-wrap justify-center gap-y-1">
                {data.status_distribution.map((d, i) => (
                  <span key={d.status} className="flex items-center">
                    <span className="h-1.5 w-1.5 rounded-full mr-1" style={{ backgroundColor: STATUS_COLORS[i] }}></span>
                    <span>{d.status} ({d.count})</span>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Portfolio Trends Line Chart */}
        <div className="bg-slate-800/30 border border-slate-800 rounded-xl p-6">
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
      </div>

      {/* Quick Actions Panel */}
      <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-6">
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
