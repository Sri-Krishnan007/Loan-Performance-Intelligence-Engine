import React, { useState, useEffect } from 'react';
import { runScenario, getMonteCarlo, getStressSensitivity } from '../../services/api';
import type { MonteCarloMetrics, StressSensitivityItem } from '../../services/api';
import type { ScenarioResponse } from '../../types';
import { Compass, AlertCircle, Sliders, Download, Sparkles, DollarSign, Activity } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ScatterChart,
  Scatter,
  ZAxis,
  Cell
} from 'recharts';

export const Scenarios: React.FC = () => {
  const [selectedScen, setSelectedScen] = useState('adverse_credit');
  const [selectedSegs, setSelectedSegs] = useState<string[]>(['credit_band']);
  
  // 1. Custom Stress Multipliers Sliders
  const [customDelinquencyStress, setCustomDelinquencyStress] = useState<number>(1.75);
  const [customDefaultStress, setCustomDefaultStress] = useState<number>(2.25);
  const [customPrepaymentStress, setCustomPrepaymentStress] = useState<number>(1.5);

  const [result, setResult] = useState<ScenarioResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Advanced simulation states
  const [mcData, setMcData] = useState<MonteCarloMetrics | null>(null);
  const [sensitivityData, setSensitivityData] = useState<StressSensitivityItem[]>([]);

  useEffect(() => {
    const loadSimulationMetrics = async () => {
      try {
        const mc = await getMonteCarlo();
        setMcData(mc);
        const sens = await getStressSensitivity();
        setSensitivityData(sens);
      } catch (err) {
        console.error("Error loading simulation indicators:", err);
      }
    };
    loadSimulationMetrics();
  }, []);

  const handleSimulate = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await runScenario(selectedScen, selectedSegs);
      
      // Inject custom stress inputs into result
      const modifiedRes: ScenarioResponse = {
        ...res,
        portfolio: {
          delinquency_rate: res.portfolio.delinquency_rate * (customDelinquencyStress / 1.75),
          default_rate: res.portfolio.default_rate * (customDefaultStress / 2.25),
          prepayment_rate: res.portfolio.prepayment_rate * (customPrepaymentStress / 1.5)
        },
        segments: res.segments.map(seg => ({
          ...seg,
          delinquency_rate: seg.delinquency_rate * (customDelinquencyStress / 1.75),
          default_rate: seg.default_rate * (customDefaultStress / 2.25),
          prepayment_rate: seg.prepayment_rate * (customPrepaymentStress / 1.5)
        }))
      };
      
      setResult(modifiedRes);
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

  // 2. Expected Loss and LGD projections calculation
  const lgd = 0.40; // Loss Given Default estimate: 40%
  const outstandingPortfolioBal = 45280000; // Mock outstanding portfolio balance ($45.28M)
  const expectedBaselineLoss = outstandingPortfolioBal * baselineRates.default * lgd;
  const expectedStressedLoss = result ? (outstandingPortfolioBal * result.portfolio.default_rate * lgd) : 0;
  const lossVariance = expectedStressedLoss - expectedBaselineLoss;

  // 3. Segment CSV Download
  const handleDownloadCsv = () => {
    if (!result) return;
    const headers = selectedSegs.join(',') + ',Delinquency Rate,Default Rate,Prepayment Rate\n';
    const csvContent = headers + result.segments.map((seg: any) => 
      selectedSegs.map(s => seg[s]).join(',') + `,${seg.delinquency_rate},${seg.default_rate},${seg.prepayment_rate}`
    ).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `Scenario_Stressed_Segments_${selectedScen}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 4. Prepayment vs Default Risk Frontier coordinates
  const COLORS = ['#38a0f8', '#f59e0b', '#ef4444', '#10b981', '#a855f7', '#ec4899'];

  const scatterData = result ? result.segments.map((seg: any) => ({
    name: selectedSegs.map(s => seg[s]).join(' - '),
    x: parseFloat((seg.default_rate * 100).toFixed(2)),
    y: parseFloat((seg.prepayment_rate * 100).toFixed(2)),
    z: 100
  })) : [];

  const renderAdvancedSimulators = () => {
    return (
      <div className="space-y-6">
        {/* Monte Carlo VaR Summary Card */}
        {mcData && (
          <div className="glass-panel rounded-xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-slate-350 uppercase tracking-wider flex items-center gap-1.5 border-b border-slate-800 pb-2">
              <Sparkles className="h-4 w-4 text-brand-400" />
              <span>Monte Carlo Portfolio VaR Analysis</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
              <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-850">
                <span className="text-[10px] text-slate-500 font-bold block uppercase">Expected Loss</span>
                <span className="text-sm font-bold text-white mt-1 block">{(mcData.metrics.mean_loss_rate * 100).toFixed(2)}%</span>
                <span className="text-[9px] text-slate-450 font-mono">${Math.round(mcData.metrics.expected_losses).toLocaleString()}</span>
              </div>
              <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-850">
                <span className="text-[10px] text-rose-500 font-bold block uppercase">95% Value-at-Risk</span>
                <span className="text-sm font-bold text-rose-455 mt-1 block">{(mcData.metrics.value_at_risk_95 * 100).toFixed(2)}%</span>
                <span className="text-[9px] text-rose-355 font-mono">${Math.round(mcData.metrics.value_at_risk_95_amount).toLocaleString()}</span>
              </div>
              <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-850">
                <span className="text-[10px] text-rose-600 font-bold block uppercase">99% Value-at-Risk</span>
                <span className="text-sm font-bold text-rose-500 mt-1 block">{(mcData.metrics.value_at_risk_99 * 100).toFixed(2)}%</span>
                <span className="text-[9px] text-rose-400 font-mono">${Math.round(mcData.metrics.value_at_risk_99_amount).toLocaleString()}</span>
              </div>
              <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-850">
                <span className="text-[10px] text-emerald-500 font-bold block uppercase">Expected Yield</span>
                <span className="text-sm font-bold text-emerald-400 mt-1 block">{(mcData.metrics.mean_interest_yield_rate * 100).toFixed(2)}%</span>
                <span className="text-[9px] text-emerald-355 font-mono">${Math.round(mcData.metrics.expected_interest_earnings).toLocaleString()}</span>
              </div>
            </div>
            <p className="text-[10px] text-slate-500 leading-normal">
              Value-at-Risk (VaR) measures statistical credit losses over a 12-month horizon. 95% VaR indicates that portfolio write-offs will remain below this rate with 95% probability. 99% VaR represents extreme tail stress.
            </p>
          </div>
        )}

        {/* Stress Sensitivity Grid */}
        {sensitivityData.length > 0 && (
          <div className="glass-panel rounded-xl overflow-hidden shadow-xl animate-fadeIn">
            <div className="px-5 py-3.5 bg-slate-800/40 border-b border-slate-850 flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-350 tracking-wider uppercase flex items-center gap-1.5">
                <Activity className="h-4 w-4 text-brand-400" />
                <span>Borrower Leverage vs Property Equity Stress Sensitivity Matrix</span>
              </h3>
            </div>
            <div className="overflow-x-auto text-[11px] text-slate-350">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-900 border-b border-slate-800/80 font-bold text-slate-400">
                    <th className="p-3">Borrower Leverage \ Equity</th>
                    <th className="p-3 text-center">Base Equity</th>
                    <th className="p-3 text-center">Moderate LTV (+10%)</th>
                    <th className="p-3 text-center">Severe LTV (+20%)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850/60">
                  {["Base Leverage", "Moderate DTI (+5%)", "Severe DTI (+12%)"].map((lev, idx) => {
                    const baseVal = sensitivityData.find(d => d.leverage_stress === lev && d.equity_stress === "Base Equity")?.average_default_probability ?? 0;
                    const modVal = sensitivityData.find(d => d.leverage_stress === lev && d.equity_stress === "Moderate LTV (+10%)")?.average_default_probability ?? 0;
                    const sevVal = sensitivityData.find(d => d.leverage_stress === lev && d.equity_stress === "Severe LTV (+20%)")?.average_default_probability ?? 0;
                    return (
                      <tr key={idx} className="hover:bg-slate-850/5">
                        <td className="p-3 font-semibold text-slate-200">{lev}</td>
                        <td className="p-3 text-center font-mono">{(baseVal * 100).toFixed(2)}%</td>
                        <td className="p-3 text-center font-mono text-amber-450">{(modVal * 100).toFixed(2)}%</td>
                        <td className="p-3 text-center font-mono text-rose-455">{(sevVal * 100).toFixed(2)}%</td>
                      </tr>
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
                  onClick={() => {
                    setSelectedScen(opt.id);
                    if (opt.id === 'base') {
                      setCustomDelinquencyStress(1.0);
                      setCustomDefaultStress(1.0);
                      setCustomPrepaymentStress(1.0);
                    } else if (opt.id === 'adverse_credit') {
                      setCustomDelinquencyStress(1.75);
                      setCustomDefaultStress(2.25);
                      setCustomPrepaymentStress(1.2);
                    } else {
                      setCustomDelinquencyStress(1.1);
                      setCustomDefaultStress(1.3);
                      setCustomPrepaymentStress(3.0);
                    }
                  }}
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

          {/* 1. Custom Stress Sliders */}
          <div className="space-y-3 border-t border-slate-800/60 pt-4">
            <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase flex items-center space-x-1.5">
              <Sliders className="h-3.5 w-3.5 text-brand-400" />
              <span>Custom Stress Tuning</span>
            </h3>
            
            <div className="space-y-3 text-xs">
              {/* Delinquency Stress */}
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-400">Delinquency Multiplier</span>
                  <span className="font-mono text-amber-400 font-bold">{customDelinquencyStress.toFixed(2)}x</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="4.0"
                  step="0.05"
                  value={customDelinquencyStress}
                  onChange={(e) => setCustomDelinquencyStress(parseFloat(e.target.value))}
                  className="w-full h-1 bg-slate-800 rounded-lg appearance-none accent-amber-500 cursor-pointer"
                />
              </div>

              {/* Default Stress */}
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-400">Default Multiplier</span>
                  <span className="font-mono text-rose-400 font-bold">{customDefaultStress.toFixed(2)}x</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="4.0"
                  step="0.05"
                  value={customDefaultStress}
                  onChange={(e) => setCustomDefaultStress(parseFloat(e.target.value))}
                  className="w-full h-1 bg-slate-800 rounded-lg appearance-none accent-rose-500 cursor-pointer"
                />
              </div>

              {/* Prepayment Stress */}
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-400">Prepayment Multiplier</span>
                  <span className="font-mono text-emerald-400 font-bold">{customPrepaymentStress.toFixed(2)}x</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="4.0"
                  step="0.05"
                  value={customPrepaymentStress}
                  onChange={(e) => setCustomPrepaymentStress(parseFloat(e.target.value))}
                  className="w-full h-1 bg-slate-800 rounded-lg appearance-none accent-emerald-500 cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Select Segments */}
          <div className="space-y-3 border-t border-slate-800/60 pt-4">
            <h3 className="text-xs font-bold text-slate-350 tracking-wider uppercase">2. Grouping Dimensions</h3>
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
            <div className="space-y-6 animate-fadeIn">
              <div className="border border-dashed border-slate-800 rounded-xl flex flex-col items-center justify-center text-center p-12 text-slate-500 space-y-3 min-h-[220px]">
                <Compass className="h-10 w-10 text-slate-700 animate-spin-slow" />
                <h3 className="text-sm font-bold text-slate-400 font-sans">Projections Pending</h3>
                <p className="text-xs text-slate-500 max-w-xs leading-relaxed font-sans">Configure your scenario multipliers and click simulate to plot stressed performance indicators.</p>
              </div>
              {renderAdvancedSimulators()}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Macro Impact Charts & Expected Loss */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  { label: 'Stressed Delinquency', baseline: baselineRates.delinquency, stressed: result.portfolio.delinquency_rate, color: 'text-amber-400' },
                  { label: 'Stressed Default', baseline: baselineRates.default, stressed: result.portfolio.default_rate, color: 'text-rose-400' },
                  { label: 'Stressed Prepay', baseline: baselineRates.prepayment, stressed: result.portfolio.prepayment_rate, color: 'text-emerald-400' }
                ].map((item, idx) => (
                  <div key={idx} className="bg-slate-800/20 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
                    <span className="text-[10px] text-slate-500 font-semibold uppercase">{item.label}</span>
                    <div className="flex items-baseline space-x-2 mt-2">
                      <span className={`text-lg font-bold ${item.color}`}>{(item.stressed * 100).toFixed(2)}%</span>
                      <span className="text-[9px] text-slate-500">vs {(item.baseline * 100).toFixed(2)}%</span>
                    </div>
                  </div>
                ))}

                {/* Portfolio Expected Loss Stress Delta Card */}
                <div className="bg-rose-950/20 border border-rose-900/40 rounded-xl p-4 flex flex-col justify-between">
                  <span className="text-[10px] text-rose-355 font-semibold uppercase flex items-center">
                    <DollarSign className="h-3.5 w-3.5 mr-0.5 inline animate-pulse text-rose-455" />
                    <span>Expected Stress Loss</span>
                  </span>
                  <div className="mt-2">
                    <h3 className="text-md font-bold text-white">${(expectedStressedLoss / 1000000).toFixed(2)}M</h3>
                    <span className="text-[8px] font-bold text-rose-400">Delta: +${(lossVariance / 1000).toFixed(0)}k</span>
                  </div>
                </div>
              </div>

              {/* Stress Projections Chart */}
              <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-5">
                <h3 className="text-xs font-bold text-slate-350 tracking-wider uppercase mb-4">Cumulative State Projections (%)</h3>
                <div className="h-64 text-xs">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <XAxis dataKey="name" stroke="#64748b" />
                      <YAxis stroke="#64748b" />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                      <Legend />
                      <Bar dataKey="Delinquency" fill="#f59e0b" />
                      <Bar dataKey="Default" fill="#ef4444" />
                      <Bar dataKey="Prepayment" fill="#10b981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Prepayment vs Default Risk Frontier Chart */}
              <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-5">
                <h3 className="text-xs font-bold text-slate-350 tracking-wider uppercase mb-4">Segment Risk Frontier: Prepayment vs Default</h3>
                <div className="h-64 text-xs">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                      <XAxis type="number" dataKey="x" name="Default" unit="%" label={{ value: 'Default Rate (%)', position: 'bottom', offset: 0, fill: '#64748b' }} stroke="#64748b" />
                      <YAxis type="number" dataKey="y" name="Prepayment" unit="%" label={{ value: 'Prepayment Rate (%)', angle: -90, position: 'left', offset: 0, fill: '#64748b' }} stroke="#64748b" />
                      <ZAxis type="number" dataKey="z" range={[60, 60]} />
                      <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                      <Scatter name="Segments" data={scatterData} fill="#38a0f8">
                        {scatterData.map((_entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Segments table */}
              {result.segments.length > 0 && (
                <div className="bg-slate-800/20 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
                  <div className="px-5 py-4 bg-slate-800/40 border-b border-slate-800 flex justify-between items-center">
                    <h3 className="text-xs font-bold text-slate-350 tracking-wider uppercase">Segment Level Impacts</h3>
                    <button
                      onClick={handleDownloadCsv}
                      className="flex items-center space-x-1 px-2.5 py-1 bg-slate-900 border border-slate-705 text-slate-400 hover:text-white rounded text-[10px] font-semibold transition"
                    >
                      <Download className="h-3 w-3" />
                      <span>Download Segments</span>
                    </button>
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
                        {result.segments.map((seg: any, i: number) => {
                          const delinquencyDelta = seg.delinquency_rate - baselineRates.delinquency;
                          return (
                            <tr key={i} className="hover:bg-slate-800/10">
                              {selectedSegs.map(s => (
                                <td key={s} className="p-3 font-semibold text-white">{seg[s]}</td>
                              ))}
                              <td className="p-3 text-right">
                                <span>{(seg.delinquency_rate * 100).toFixed(2)}%</span>
                                <span className={`text-[9px] font-bold ml-1.5 ${delinquencyDelta >= 0 ? 'text-rose-450 font-bold' : 'text-emerald-450'}`}>
                                  ({delinquencyDelta >= 0 ? '+' : ''}{(delinquencyDelta * 100).toFixed(1)}%)
                                </span>
                              </td>
                              <td className="p-3 text-right">{(seg.default_rate * 100).toFixed(2)}%</td>
                              <td className="p-3 text-right">{(seg.prepayment_rate * 100).toFixed(2)}%</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Monte Carlo & Sensitivity widgets (Stressed status) */}
              {renderAdvancedSimulators()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
