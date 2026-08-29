import React, { useState } from 'react';
import { runScenario } from '../../services/api';
import type { ScenarioResponse } from '../../types';
import { Compass, AlertCircle } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend
} from 'recharts';

export const Scenarios: React.FC = () => {
  const [selectedScen, setSelectedScen] = useState('adverse_credit');
  const [selectedSegs, setSelectedSegs] = useState<string[]>(['credit_band']);
  
  const [result, setResult] = useState<ScenarioResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await runScenario(selectedScen, selectedSegs);
      setResult(res);
    } catch (err) {
      console.error(err);
      setError("Scenario simulation execution failed.");
    } finally {
      setLoading(false);
    }
  };

  const toggleSegment = (seg: string) => {
    if (selectedSegs.includes(seg)) {
      setSelectedSegs(selectedSegs.filter(s => s !== seg));
    } else {
      setSelectedSegs([...selectedSegs, seg]);
    }
  };

  const scenarioOptions = [
    { id: 'base', label: 'Base Case (Neutral)', desc: 'Standard macroeconomic conditions, baseline predicted probabilities.' },
    { id: 'adverse_credit', label: 'Adverse Credit Stress', desc: 'Simulates rising delinquency rates (1.75x) and default shocks (2.25x).' },
    { id: 'high_prepayment', label: 'High Prepayment Rally', desc: 'Simulates refinancing spikes (3x) and interest rate regressions.' },
  ];

  const segmentOptions = [
    { id: 'credit_band', label: 'Credit Score Band' },
    { id: 'state', label: 'Property State' },
    { id: 'servicer', label: 'Servicer Name' },
    { id: 'vintage', label: 'Vintage Year' },
  ];

  const baselineRates = {
    delinquency: 0.0843,
    default: 0.0241,
    prepayment: 0.0169
  };

  const chartData = result ? [
    { name: 'Delinquency', Baseline: (baselineRates.delinquency * 100).toFixed(2), Stressed: (result.portfolio.delinquency_rate * 100).toFixed(2) },
    { name: 'Default', Baseline: (baselineRates.default * 100).toFixed(2), Stressed: (result.portfolio.default_rate * 100).toFixed(2) },
    { name: 'Prepayment', Baseline: (baselineRates.prepayment * 100).toFixed(2), Stressed: (result.portfolio.prepayment_rate * 100).toFixed(2) },
  ] : [];

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto max-h-[calc(100vh-4rem)]">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-wide flex items-center">
          <Compass className="h-6 w-6 text-brand-500 mr-2" />
          Scenario Simulator
        </h1>
        <p className="text-slate-400 text-sm">Stress-test the servicing portfolio against custom macroeconomic credit curves.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-5 space-y-6 h-fit">
          {/* Select Scenario */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">1. Stress Scenario</h3>
            <div className="space-y-2">
              {scenarioOptions.map((opt) => (
                <label
                  key={opt.id}
                  onClick={() => setSelectedScen(opt.id)}
                  className={`flex flex-col p-3 rounded-lg border text-left cursor-pointer transition ${
                    selectedScen === opt.id
                      ? 'bg-brand-950/20 border-brand-700 text-white'
                      : 'border-slate-800 hover:border-slate-700 text-slate-400'
                  }`}
                >
                  <span className="text-xs font-bold">{opt.label}</span>
                  <span className="text-[10px] text-slate-500 mt-1">{opt.desc}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Select Segments */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">2. Grouping Dimensions</h3>
            <div className="grid grid-cols-2 gap-2">
              {segmentOptions.map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => toggleSegment(opt.id)}
                  className={`py-2 px-3 rounded-lg text-xs font-semibold border text-center transition ${
                    selectedSegs.includes(opt.id)
                      ? 'bg-slate-800 border-slate-700 text-white'
                      : 'border-slate-800/80 bg-slate-900/30 text-slate-500 hover:border-slate-700'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Run Button */}
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-40 text-white rounded-lg py-3 text-sm font-semibold shadow-md transition"
          >
            {loading ? 'Running Projections...' : 'Simulate Portfolio Stress'}
          </button>
        </div>

        {/* Results Column */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="bg-rose-950/20 border border-rose-900 p-4 rounded-lg flex space-x-3 text-rose-400 text-xs">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!result ? (
            <div className="h-full border border-dashed border-slate-800 rounded-xl flex flex-col items-center justify-center text-center p-12 text-slate-500 space-y-3 min-h-[400px]">
              <Compass className="h-10 w-10 text-slate-700" />
              <h3 className="text-sm font-bold text-slate-400">Projections Pending</h3>
              <p className="text-xs text-slate-500 max-w-xs">Configure your scenario multipliers and click simulate to plotstressed performance indicators.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Macro Impact Charts */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { label: 'Stressed Delinquency', baseline: baselineRates.delinquency, stressed: result.portfolio.delinquency_rate, color: 'text-amber-400' },
                  { label: 'Stressed Default', baseline: baselineRates.default, stressed: result.portfolio.default_rate, color: 'text-rose-400' },
                  { label: 'Stressed Prepayment', baseline: baselineRates.prepayment, stressed: result.portfolio.prepayment_rate, color: 'text-emerald-400' }
                ].map((item, idx) => (
                  <div key={idx} className="bg-slate-800/20 border border-slate-800 rounded-xl p-5">
                    <span className="text-[10px] text-slate-500 font-semibold uppercase">{item.label}</span>
                    <div className="flex items-baseline space-x-2 mt-2">
                      <span className={`text-xl font-bold ${item.color}`}>{(item.stressed * 100).toFixed(2)}%</span>
                      <span className="text-[10px] text-slate-500">vs {(item.baseline * 100).toFixed(2)}%</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Stress Chart */}
              <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-6">
                <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase mb-4">Baseline vs. Stressed Comparison</h3>
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <XAxis dataKey="name" stroke="#475569" fontSize={10} />
                      <YAxis stroke="#475569" fontSize={10} unit="%" />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                      <Legend />
                      <Bar dataKey="Baseline" fill="#1e293b" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Stressed" fill="#38a0f8" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Segments table */}
              {result.segments.length > 0 && (
                <div className="bg-slate-800/20 border border-slate-800 rounded-xl overflow-hidden">
                  <div className="px-5 py-4 bg-slate-800/40 border-b border-slate-800">
                    <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">Segment Level Impacts</h3>
                  </div>
                  <div className="overflow-x-auto text-xs">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="bg-slate-800/10 text-slate-400 border-b border-slate-800/60 font-semibold uppercase">
                          {selectedSegs.map(s => (
                            <th key={s} className="p-3 capitalize">{s.replace('_', ' ')}</th>
                          ))}
                          <th className="p-3 text-right">Delinquency</th>
                          <th className="p-3 text-right">Default</th>
                          <th className="p-3 text-right">Prepayment</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/40 text-slate-300">
                        {result.segments.map((seg, i) => (
                          <tr key={i} className="hover:bg-slate-800/10">
                            {selectedSegs.map(s => (
                              <td key={s} className="p-3 font-semibold text-white">{seg[s]}</td>
                            ))}
                            <td className="p-3 text-right">{(seg.delinquency_rate * 100).toFixed(2)}%</td>
                            <td className="p-3 text-right">{(seg.default_rate * 100).toFixed(2)}%</td>
                            <td className="p-3 text-right">{(seg.prepayment_rate * 100).toFixed(2)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
