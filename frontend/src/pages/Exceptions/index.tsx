import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAnomalies } from '../../services/api';
import type { AnomalyListItem } from '../../types';
import { AlertTriangle, Eye } from 'lucide-react';

export const Exceptions: React.FC = () => {
  const navigate = useNavigate();
  const [anomalies, setAnomalies] = useState<AnomalyListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [severity, setSeverity] = useState('');
  const [type, setType] = useState('');

  const fetchExceptions = async () => {
    try {
      setLoading(true);
      const res = await getAnomalies({
        severity: severity || undefined,
        exception_type: type || undefined,
        limit: 20
      });
      setAnomalies(res.items);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to retrieve exceptions logs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExceptions();
  }, [severity, type]);

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto max-h-[calc(100vh-4rem)]">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-wide">Exception Center</h1>
        <p className="text-slate-400 text-sm">Review operational anomalies and secondary servicer update mismatches.</p>
      </div>

      {/* Filters Bar */}
      <div className="flex space-x-4 bg-slate-800/20 border border-slate-800 rounded-xl p-4">
        <div className="flex flex-col space-y-1">
          <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Severity</label>
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-xs text-white rounded-lg px-3 py-2 focus:outline-none transition"
          >
            <option value="">All Severities</option>
            <option value="HIGH">High Severity</option>
            <option value="MEDIUM">Medium Severity</option>
            <option value="LOW">Low Severity</option>
          </select>
        </div>

        <div className="flex flex-col space-y-1">
          <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Exception Type</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-xs text-white rounded-lg px-3 py-2 focus:outline-none transition"
          >
            <option value="">All Exceptions</option>
            <option value="Data Reconciliation Discrepancy">Discrepancies</option>
            <option value="Severe Delinquency">Severe Delinquency</option>
            <option value="Documentation Gap">Documentation Gaps</option>
          </select>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-14 bg-slate-800/30 rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-slate-800/10 p-12 border border-slate-800 text-center rounded-xl text-slate-400">
          <AlertTriangle className="h-12 w-12 text-rose-500 mx-auto mb-3" />
          {error}
        </div>
      ) : anomalies.length === 0 ? (
        <div className="bg-slate-800/5 p-12 border border-slate-800 text-center rounded-xl text-slate-500">
          No exceptions flagged matching query criteria.
        </div>
      ) : (
        <div className="bg-slate-800/20 border border-slate-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-800/50 border-b border-slate-700/50 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="p-4">Loan ID</th>
                  <th className="p-4">Month</th>
                  <th className="p-4">Anomaly Score</th>
                  <th className="p-4">Exception Type</th>
                  <th className="p-4">Severity</th>
                  <th className="p-4">Evidence</th>
                  <th className="p-4 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {anomalies.map((item) => (
                  <tr key={item.loan_id} className="hover:bg-slate-800/30 text-slate-300 transition">
                    <td className="p-4 font-semibold text-white font-mono">{item.loan_id}</td>
                    <td className="p-4 text-slate-400">{item.reporting_month}</td>
                    <td className="p-4 font-semibold text-amber-500">{(item.anomaly_score * 100).toFixed(0)}%</td>
                    <td className="p-4">{item.exception_type}</td>
                    <td className="p-4">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                          item.severity === 'HIGH'
                            ? 'bg-rose-950/40 text-rose-400'
                            : item.severity === 'MEDIUM'
                            ? 'bg-amber-950/40 text-amber-400'
                            : 'bg-emerald-950/40 text-emerald-400'
                        }`}
                      >
                        {item.severity}
                      </span>
                    </td>
                    <td className="p-4 max-w-xs truncate text-slate-400" title={item.evidence[0]}>
                      {item.evidence[0]}
                    </td>
                    <td className="p-4 text-center">
                      <button
                        onClick={() => navigate(`/loans/${item.loan_id}`)}
                        className="p-1 text-brand-400 hover:text-white rounded transition"
                        title="Investigate Loan Details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
