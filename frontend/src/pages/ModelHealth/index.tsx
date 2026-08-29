import React, { useEffect, useState } from 'react';
import { getDataQuality, getModelHealth } from '../../services/api';
import type { DataQualityResponse, ModelHealthResponse } from '../../types';
import { ShieldCheck, Activity, AlertTriangle } from 'lucide-react';

export const ModelHealth: React.FC = () => {
  const [dq, setDq] = useState<DataQualityResponse | null>(null);
  const [mh, setMh] = useState<ModelHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        setLoading(true);
        const [dqRes, mhRes] = await Promise.all([
          getDataQuality(),
          getModelHealth()
        ]);
        setDq(dqRes);
        setMh(mhRes);
        setError(null);
      } catch (err) {
        console.error(err);
        setError("Failed to retrieve diagnostics parameters.");
      } finally {
        setLoading(false);
      }
    };
    fetchHealth();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 p-8 space-y-6 animate-pulse">
        <div className="h-8 w-64 bg-slate-800 rounded"></div>
        <div className="grid grid-cols-2 gap-6">
          <div className="h-80 bg-slate-800 rounded-xl"></div>
          <div className="h-80 bg-slate-800 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (error || !dq || !mh) {
    return (
      <div className="flex-1 p-8 flex flex-col items-center justify-center text-center space-y-4">
        <AlertTriangle className="h-16 w-16 text-rose-500" />
        <h2 className="text-xl font-bold text-white">Diagnostics Offline</h2>
        <p className="text-slate-400 text-sm max-w-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex-1 p-8 space-y-8 overflow-y-auto max-h-[calc(100vh-4rem)]">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-wide">Model & Data Health</h1>
        <p className="text-slate-400 text-sm">Review data-quality profiling matrices and out-of-time model validation diagnostics.</p>
      </div>

      {/* Overview Diagnostics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Batch Score Card */}
        <div className="bg-slate-800/30 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Batch Data Quality Score</span>
            <h2 className="text-3xl font-extrabold text-white">{dq.batch_quality_score.toFixed(2)}%</h2>
            <p className="text-[10px] text-slate-500 mt-1">Deducted for warning/error violations on 71,142 train records.</p>
          </div>
          <ShieldCheck className="h-10 w-10 text-emerald-500" />
        </div>

        {/* Validation Split Card */}
        <div className="bg-slate-800/30 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
          <div className="space-y-1 text-xs">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Validation Split Parameters</span>
            <div className="flex justify-between border-b border-slate-800/60 pb-1 mt-1 text-[11px]">
              <span className="text-slate-400">Method:</span>
              <span className="font-semibold text-white">{mh.validation.method}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1 text-[11px]">
              <span className="text-slate-400">Train Period:</span>
              <span className="font-semibold text-white">{mh.validation.train_period}</span>
            </div>
            <div className="flex justify-between text-[11px]">
              <span className="text-slate-400">Validation Period:</span>
              <span className="font-semibold text-white">{mh.validation.validation_period}</span>
            </div>
          </div>
          <Activity className="h-10 w-10 text-brand-500" />
        </div>
      </div>

      {/* Model Performance Table */}
      <div className="bg-slate-800/20 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="px-5 py-4 bg-slate-800/40 border-b border-slate-800">
          <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">Trained Model Performance (Calibrated Validation Set)</h3>
        </div>
        <div className="overflow-x-auto text-xs">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-slate-800/10 text-slate-400 border-b border-slate-800/60 font-semibold uppercase">
                <th className="p-3">Model Name</th>
                <th className="p-3">ROC-AUC</th>
                <th className="p-3">PR-AUC</th>
                <th className="p-3">F1-Score</th>
                <th className="p-3">Brier Score</th>
                <th className="p-3">Calibration Status</th>
                <th className="p-3">Artifact Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40 text-slate-300">
              {mh.models.map((m) => (
                <tr key={m.name} className="hover:bg-slate-800/10">
                  <td className="p-3 font-semibold text-white capitalize">{m.name.replace('_', ' ')}</td>
                  <td className="p-3">{m.roc_auc > 0 ? m.roc_auc.toFixed(4) : 'N/A (Multiclass)'}</td>
                  <td className="p-3">{m.pr_auc > 0 ? m.pr_auc.toFixed(4) : 'N/A'}</td>
                  <td className="p-3">{m.f1.toFixed(4)}</td>
                  <td className="p-3">{m.brier_score > 0 ? m.brier_score.toFixed(4) : 'N/A'}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] ${m.calibrated ? 'bg-emerald-950/40 text-emerald-400' : 'bg-slate-800 text-slate-500'}`}>
                      {m.calibrated ? 'CALIBRATED' : 'RAW'}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] ${m.artifact_available ? 'bg-brand-950/40 text-brand-400' : 'bg-rose-950/40 text-rose-400'}`}>
                      {m.artifact_available ? 'AVAILABLE' : 'OFFLINE'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Profiling and Drift Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Outliers Profile */}
        <div className="bg-slate-800/20 border border-slate-800 rounded-xl overflow-hidden">
          <div className="px-5 py-3 bg-slate-800/40 border-b border-slate-800">
            <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">Outliers Profile (IQR Method)</h3>
          </div>
          <div className="overflow-x-auto text-xs">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-800/10 text-slate-400 border-b border-slate-800/60 font-semibold uppercase">
                  <th className="p-3">Feature Column</th>
                  <th className="p-3">Lower Bound</th>
                  <th className="p-3">Upper Bound</th>
                  <th className="p-3 text-right">Outliers Count</th>
                  <th className="p-3 text-right">Outliers %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40 text-slate-300">
                {dq.outliers.map((o) => (
                  <tr key={o.column} className="hover:bg-slate-800/10">
                    <td className="p-3 font-semibold text-white capitalize">{o.column.replace('_', ' ')}</td>
                    <td className="p-3">{o.lower_bound.toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
                    <td className="p-3">{o.upper_bound.toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
                    <td className="p-3 text-right">{o.outlier_count.toLocaleString()}</td>
                    <td className="p-3 text-right font-medium text-amber-500">{(o.outlier_pct * 100).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Drift Report */}
        <div className="bg-slate-800/20 border border-slate-800 rounded-xl overflow-hidden">
          <div className="px-5 py-3 bg-slate-800/40 border-b border-slate-800">
            <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">Train vs. Test Population Drift (PSI)</h3>
          </div>
          <div className="overflow-x-auto text-xs">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-800/10 text-slate-400 border-b border-slate-800/60 font-semibold uppercase">
                  <th className="p-3">Feature Column</th>
                  <th className="p-3">Population Stability Index (PSI)</th>
                  <th className="p-3">Stability Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40 text-slate-300">
                {dq.drift.map((d) => (
                  <tr key={d.column} className="hover:bg-slate-800/10">
                    <td className="p-3 font-semibold text-white capitalize">{d.column.replace('_', ' ')}</td>
                    <td className="p-3 font-mono">{d.psi.toFixed(5)}</td>
                    <td className="p-3 font-semibold">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${d.status === 'Stable' ? 'bg-emerald-950/40 text-emerald-400' : 'bg-amber-950/40 text-amber-400'}`}>
                        {d.status.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
