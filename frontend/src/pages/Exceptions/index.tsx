import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAnomalies } from '../../services/api';
import type { AnomalyListItem } from '../../types';
import { AlertTriangle, Eye, Clock, User, CheckCircle2, ChevronDown, ChevronUp, Sliders } from 'lucide-react';

export const Exceptions: React.FC = () => {
  const navigate = useNavigate();
  const [anomalies, setAnomalies] = useState<AnomalyListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [severity, setSeverity] = useState('');
  const [type, setType] = useState('');
  
  // 1. Variance Score Threshold State
  const [scoreThreshold, setScoreThreshold] = useState<number>(30);

  // 2. Expandable Compare Row State
  const [expandedLoan, setExpandedLoan] = useState<string | null>(null);

  // 3. Reviewer Assignment State
  const [assignments, setAssignments] = useState<Record<string, string>>({});

  // 4. Selected Exceptions for Bulk Action
  const [selectedExceptions, setSelectedExceptions] = useState<string[]>([]);
  const [resolvedIds, setResolvedIds] = useState<string[]>([]);

  const fetchExceptions = async () => {
    try {
      setLoading(true);
      const res = await getAnomalies({
        severity: severity || undefined,
        exception_type: type || undefined,
        limit: 20
      });
      // Filter list locally based on score threshold
      const filtered = res.items.filter(item => (item.anomaly_score * 100) >= scoreThreshold);
      setAnomalies(filtered);
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
  }, [severity, type, scoreThreshold]);

  // 5. Bulk resolve exception handler
  const handleBulkResolve = () => {
    if (selectedExceptions.length === 0) return;
    setResolvedIds([...resolvedIds, ...selectedExceptions]);
    setSelectedExceptions([]);
  };

  const handleToggleSelect = (loanId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (selectedExceptions.includes(loanId)) {
      setSelectedExceptions(selectedExceptions.filter(id => id !== loanId));
    } else {
      setSelectedExceptions([...selectedExceptions, loanId]);
    }
  };

  // Mock assignment options
  const reviewers = ['Operator_A', 'Reviewer_B', 'Risk_Manager'];

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto max-h-[calc(100vh-4rem)] bg-slate-900 text-slate-100">
      
      {/* Title */}
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide">Exception Center</h1>
          <p className="text-slate-400 text-sm">Review operational anomalies and secondary servicer update mismatches.</p>
        </div>
        {selectedExceptions.length > 0 && (
          <button
            onClick={handleBulkResolve}
            className="flex items-center space-x-2 px-3 py-1.5 bg-emerald-950/40 text-emerald-400 border border-emerald-900 rounded-lg text-xs font-semibold hover:bg-emerald-900/40 transition"
          >
            <CheckCircle2 className="h-4 w-4" />
            <span>Resolve {selectedExceptions.length} Exceptions</span>
          </button>
        )}
      </div>

      {/* Filters Bar */}
      <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex flex-wrap gap-4">
          <div className="flex flex-col space-y-1">
            <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Severity</label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="bg-slate-900 border border-slate-850 text-xs text-white rounded-lg px-3 py-2 focus:outline-none transition"
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
              className="bg-slate-900 border border-slate-850 text-xs text-white rounded-lg px-3 py-2 focus:outline-none transition"
            >
              <option value="">All Exceptions</option>
              <option value="Data Reconciliation Discrepancy">Discrepancies</option>
              <option value="Severe Delinquency">Severe Delinquency</option>
              <option value="Documentation Gap">Documentation Gaps</option>
            </select>
          </div>
        </div>

        {/* 1. Score Threshold Slider */}
        <div className="flex flex-col space-y-1 w-full md:w-64">
          <div className="flex justify-between items-center text-[10px] text-slate-500 font-semibold uppercase tracking-wider">
            <span>Score Threshold</span>
            <span className="text-amber-400 font-mono font-bold">{scoreThreshold}%+</span>
          </div>
          <div className="flex items-center space-x-2">
            <Sliders className="h-3.5 w-3.5 text-slate-500" />
            <input
              type="range"
              min="0"
              max="100"
              value={scoreThreshold}
              onChange={(e) => setScoreThreshold(parseInt(e.target.value))}
              className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-500"
            />
          </div>
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
      ) : anomalies.filter(item => !resolvedIds.includes(item.loan_id)).length === 0 ? (
        <div className="bg-slate-800/5 p-12 border border-slate-800 text-center rounded-xl text-slate-500">
          No exceptions flagged matching query criteria.
        </div>
      ) : (
        <div className="bg-slate-800/20 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-800/50 border-b border-slate-700/50 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="p-4 w-12 text-center">Select</th>
                  <th className="p-4 w-10">Compare</th>
                  <th className="p-4">Loan ID</th>
                  <th className="p-4">Anomaly Score</th>
                  <th className="p-4">Exception Type</th>
                  <th className="p-4">Severity</th>
                  <th className="p-4">Owner Assignment</th>
                  <th className="p-4"><Clock className="h-3.5 w-3.5 inline mr-1 text-slate-500" />SLA Age</th>
                  <th className="p-4 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {anomalies
                  .filter(item => !resolvedIds.includes(item.loan_id))
                  .map((item) => {
                    const isExpanded = expandedLoan === item.loan_id;
                    const isSelected = selectedExceptions.includes(item.loan_id);
                    const currentOwner = assignments[item.loan_id] || 'Unassigned';
                    
                    // SLA Age mock based on ID
                    const slaAge = item.loan_id === 'LN101264' ? '4 hours ago' : item.loan_id === 'LN100007' ? '12 hours ago' : '2 days ago';

                    return (
                      <React.Fragment key={item.loan_id}>
                        <tr className={`hover:bg-slate-800/30 text-slate-300 transition ${isSelected ? 'bg-brand-950/10' : ''}`}>
                          <td className="p-4 text-center" onClick={(e) => handleToggleSelect(item.loan_id, e)}>
                            <input
                              type="checkbox"
                              checked={isSelected}
                              readOnly
                              className="rounded bg-slate-900 border-slate-700 text-brand-650 focus:ring-0 focus:ring-offset-0 cursor-pointer"
                            />
                          </td>
                          <td className="p-4 text-center">
                            <button
                              onClick={() => setExpandedLoan(isExpanded ? null : item.loan_id)}
                              className="text-slate-500 hover:text-white transition"
                            >
                              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                            </button>
                          </td>
                          <td className="p-4 font-semibold text-white font-mono">{item.loan_id}</td>
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
                          <td className="p-4 text-slate-400">
                            {/* 3. Owner assignment selector */}
                            <div className="flex items-center space-x-1.5">
                              <User className="h-3 w-3 text-slate-500" />
                              <select
                                value={currentOwner}
                                onChange={(e) => setAssignments({ ...assignments, [item.loan_id]: e.target.value })}
                                className="bg-transparent border-none text-[11px] text-slate-300 focus:outline-none cursor-pointer font-medium hover:text-white"
                              >
                                <option value="Unassigned" className="bg-slate-900 text-slate-400">Unassigned</option>
                                {reviewers.map(r => (
                                  <option key={r} value={r} className="bg-slate-900 text-white">{r.replace('_', ' ')}</option>
                                ))}
                              </select>
                            </div>
                          </td>
                          <td className="p-4 text-slate-400 font-medium">{slaAge}</td>
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
                        
                        {/* 4. Side-by-Side Discrepancy Comparison Row */}
                        {isExpanded && (
                          <tr className="bg-slate-950/40">
                            <td colSpan={9} className="p-4 border-l-2 border-brand-500">
                              <div className="space-y-3">
                                <h4 className="text-xs font-bold text-white flex items-center space-x-2">
                                  <span>Reconciliation Comparison Details</span>
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-950/40 text-brand-400 border border-brand-900/60 font-mono">
                                    Conflict Detected
                                  </span>
                                </h4>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-[11px] text-slate-300">
                                  <div className="bg-slate-900/50 p-3 rounded border border-slate-800">
                                    <span className="text-[10px] text-slate-500 font-semibold block mb-1">PRIMARY SYSTEM TAPE</span>
                                    <span className="block font-medium">Unadjusted Balance: $148,254.21</span>
                                    <span className="block mt-0.5 text-slate-400">Payment Status: Active Current</span>
                                    <span className="block mt-0.5 text-slate-400">Doc Code: Completed</span>
                                  </div>
                                  <div className="bg-slate-900/50 p-3 rounded border border-slate-800">
                                    <span className="text-[10px] text-slate-500 font-semibold block mb-1">SERVICER DATA LOGS</span>
                                    <span className="block font-medium text-amber-400">Servicer Balance: $147,105.12</span>
                                    <span className="block mt-0.5 text-slate-400">Serviced Status: 30 DPD Delinquent</span>
                                    <span className="block mt-0.5 text-slate-400">Payment Log ID: Servicer_C_912</span>
                                  </div>
                                  <div className="bg-slate-900/50 p-3 rounded border border-slate-800">
                                    <span className="text-[10px] text-slate-500 font-semibold block mb-1">AUDIT EVIDENCE VARIANCE</span>
                                    <span className="block font-mono font-bold text-rose-400">Variance Delta: $1,149.09</span>
                                    <span className="block mt-0.5 text-slate-400">Days Out of Sync: 12 days</span>
                                    <p className="mt-1 text-[10px] text-slate-400 italic">"Discrepancy likely due to late-processing fee delay."</p>
                                  </div>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
