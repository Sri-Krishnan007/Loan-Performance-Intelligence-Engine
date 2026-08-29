import React, { useState } from 'react';
import { predictLive } from '../../services/api';
import type { LivePredictionPayload, LivePredictionResult } from '../../services/api';
import { Sparkles, AlertTriangle, BarChart, RefreshCw } from 'lucide-react';

export const LivePredictor: React.FC = () => {
  const [formData, setFormData] = useState<LivePredictionPayload>({
    fico_score: 720,
    ltv: 80,
    dti: 36,
    original_balance: 300000,
    current_balance: 290000,
    interest_rate: 6.25,
    days_past_due: 0,
    document_status: 'Complete',
    state: 'CA',
    loan_purpose: 'Purchase',
    occupancy_type: 'Primary Residence',
    property_type: 'Single Family',
    servicer_name: 'Servicer_A',
    current_status: 'Current',
    modification_flag: 0,
    prepayment_flag: 0,
    
    // Optional reconciliation fields
    servicer_current_balance: undefined,
    servicer_days_past_due: undefined,
    servicer_document_status: undefined,
    servicer_status: undefined
  });

  const [includeServicer, setIncludeServicer] = useState(false);
  const [result, setResult] = useState<LivePredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      
      const payload: LivePredictionPayload = { ...formData };
      if (!includeServicer) {
        delete payload.servicer_current_balance;
        delete payload.servicer_days_past_due;
        delete payload.servicer_document_status;
        delete payload.servicer_status;
      } else {
        payload.servicer_current_balance = payload.servicer_current_balance ?? formData.current_balance;
        payload.servicer_days_past_due = payload.servicer_days_past_due ?? formData.days_past_due;
        payload.servicer_document_status = payload.servicer_document_status ?? formData.document_status;
        payload.servicer_status = payload.servicer_status ?? formData.current_status;
      }

      const res = await predictLive(payload);
      setResult(res);
    } catch (err) {
      console.error(err);
      setError('Live prediction inference failed. Ensure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      fico_score: 720,
      ltv: 80,
      dti: 36,
      original_balance: 300000,
      current_balance: 290000,
      interest_rate: 6.25,
      days_past_due: 0,
      document_status: 'Complete',
      state: 'CA',
      loan_purpose: 'Purchase',
      occupancy_type: 'Primary Residence',
      property_type: 'Single Family',
      servicer_name: 'Servicer_A',
      current_status: 'Current',
      modification_flag: 0,
      prepayment_flag: 0
    });
    setIncludeServicer(false);
    setResult(null);
    setError(null);
  };

  const states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'];
  const propertyTypes = ['Condominium', 'Multi Unit', 'Single Family', 'Townhouse'];
  const servicers = ['Servicer_A', 'Servicer_B', 'Servicer_C', 'Servicer_D', 'Servicer_E'];

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto max-h-[calc(100vh-4rem)] bg-slate-900 text-slate-100 font-sans">
      {/* Title */}
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-brand-400" />
            Live Credit Risk Predictor
          </h1>
          <p className="text-slate-400 text-sm">Enter raw underwriting parameters to calculate default risk probabilities and anomaly indices.</p>
        </div>
        <button
          onClick={handleReset}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-350 hover:text-white rounded-lg text-xs font-semibold transition"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Reset Form</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form panel */}
        <form onSubmit={handleSubmit} className="lg:col-span-2 glass-panel rounded-xl p-6 space-y-6">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-355 border-b border-slate-800/80 pb-2">Loan Parameters Profile</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            {/* FICO */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Credit Score (FICO)</label>
              <input
                type="number"
                min="300"
                max="850"
                value={formData.fico_score}
                onChange={(e) => setFormData({ ...formData, fico_score: parseInt(e.target.value) || 0 })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition"
                required
              />
            </div>

            {/* LTV */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Loan-to-Value (LTV %)</label>
              <input
                type="number"
                min="0"
                max="200"
                step="0.1"
                value={formData.ltv}
                onChange={(e) => setFormData({ ...formData, ltv: parseFloat(e.target.value) || 0 })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition"
                required
              />
            </div>

            {/* DTI */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Debt-to-Income (DTI %)</label>
              <input
                type="number"
                min="0"
                max="100"
                step="0.1"
                value={formData.dti}
                onChange={(e) => setFormData({ ...formData, dti: parseFloat(e.target.value) || 0 })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition"
                required
              />
            </div>

            {/* Original Balance */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Original Balance ($)</label>
              <input
                type="number"
                min="0"
                value={formData.original_balance}
                onChange={(e) => setFormData({ ...formData, original_balance: parseFloat(e.target.value) || 0 })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition"
                required
              />
            </div>

            {/* Current Balance */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Current Balance ($)</label>
              <input
                type="number"
                min="0"
                value={formData.current_balance}
                onChange={(e) => setFormData({ ...formData, current_balance: parseFloat(e.target.value) || 0 })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition"
                required
              />
            </div>

            {/* Interest Rate */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Interest Rate (%)</label>
              <input
                type="number"
                min="0"
                max="30"
                step="0.01"
                value={formData.interest_rate}
                onChange={(e) => setFormData({ ...formData, interest_rate: parseFloat(e.target.value) || 0 })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition"
                required
              />
            </div>

            {/* Days Past Due */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Days Past Due (DPD)</label>
              <input
                type="number"
                min="0"
                value={formData.days_past_due}
                onChange={(e) => setFormData({ ...formData, days_past_due: parseInt(e.target.value) || 0 })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition"
                required
              />
            </div>

            {/* Property State */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Property State</label>
              <select
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition cursor-pointer"
              >
                {states.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            {/* Loan Purpose */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Loan Purpose</label>
              <select
                value={formData.loan_purpose}
                onChange={(e) => setFormData({ ...formData, loan_purpose: e.target.value })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition cursor-pointer"
              >
                <option value="Purchase">Purchase</option>
                <option value="Refinance">Refinance</option>
              </select>
            </div>

            {/* Occupancy Type */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Occupancy Type</label>
              <select
                value={formData.occupancy_type}
                onChange={(e) => setFormData({ ...formData, occupancy_type: e.target.value })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition cursor-pointer"
              >
                <option value="Primary Residence">Primary Residence</option>
                <option value="Second Home">Second Home</option>
                <option value="Investment">Investment</option>
              </select>
            </div>

            {/* Property Type */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Property Type</label>
              <select
                value={formData.property_type}
                onChange={(e) => setFormData({ ...formData, property_type: e.target.value })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition cursor-pointer"
              >
                {propertyTypes.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            {/* Servicer */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Servicer Name</label>
              <select
                value={formData.servicer_name}
                onChange={(e) => setFormData({ ...formData, servicer_name: e.target.value })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition cursor-pointer"
              >
                {servicers.map(srv => <option key={srv} value={srv}>{srv.replace('_', ' ')}</option>)}
              </select>
            </div>

            {/* Current Status */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Current Status</label>
              <select
                value={formData.current_status}
                onChange={(e) => setFormData({ ...formData, current_status: e.target.value })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition cursor-pointer"
              >
                <option value="Current">Current</option>
                <option value="Delinquent">Delinquent</option>
                <option value="Default">Default</option>
                <option value="Prepaid">Prepaid</option>
              </select>
            </div>

            {/* Document Status */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Document Status</label>
              <select
                value={formData.document_status}
                onChange={(e) => setFormData({ ...formData, document_status: e.target.value })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition cursor-pointer"
              >
                <option value="Complete">Complete</option>
                <option value="Missing">Missing</option>
                <option value="Pending">Pending</option>
              </select>
            </div>

            {/* Modification and Prepayment options */}
            <div className="flex flex-col space-y-1">
              <label className="text-slate-400 font-semibold font-sans">Modified Terms?</label>
              <select
                value={formData.modification_flag}
                onChange={(e) => setFormData({ ...formData, modification_flag: parseInt(e.target.value) || 0 })}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 transition cursor-pointer"
              >
                <option value="0">No Modification</option>
                <option value="1">Terms Modified</option>
              </select>
            </div>
          </div>

          {/* Servicer updates checkbox */}
          <div className="border-t border-slate-800/80 pt-4 space-y-4">
            <div className="flex items-center space-x-2.5">
              <input
                type="checkbox"
                id="includeServicer"
                checked={includeServicer}
                onChange={(e) => setIncludeServicer(e.target.checked)}
                className="rounded bg-slate-950 border-slate-800 text-brand-600 focus:ring-0 focus:ring-offset-0 cursor-pointer"
              />
              <label htmlFor="includeServicer" className="text-xs text-slate-350 font-bold select-none cursor-pointer font-sans">
                Include Servicer Ledger Data (Enable Source Reconciliation Checks)
              </label>
            </div>

            {includeServicer && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs bg-slate-950/40 p-4 rounded-xl border border-slate-800">
                {/* Servicer Balance */}
                <div className="flex flex-col space-y-1">
                  <label className="text-slate-500 font-sans">Servicer Balance ($)</label>
                  <input
                    type="number"
                    min="0"
                    placeholder={formData.current_balance.toString()}
                    value={formData.servicer_current_balance ?? ''}
                    onChange={(e) => setFormData({ ...formData, servicer_current_balance: parseFloat(e.target.value) || undefined })}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-brand-500 transition"
                  />
                </div>

                {/* Servicer DPD */}
                <div className="flex flex-col space-y-1">
                  <label className="text-slate-500 font-sans">Servicer DPD</label>
                  <input
                    type="number"
                    min="0"
                    placeholder={formData.days_past_due.toString()}
                    value={formData.servicer_days_past_due ?? ''}
                    onChange={(e) => setFormData({ ...formData, servicer_days_past_due: parseInt(e.target.value) || undefined })}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-brand-500 transition"
                  />
                </div>

                {/* Servicer Status */}
                <div className="flex flex-col space-y-1">
                  <label className="text-slate-500 font-sans">Servicer Status</label>
                  <select
                    value={formData.servicer_status ?? ''}
                    onChange={(e) => setFormData({ ...formData, servicer_status: e.target.value || undefined })}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-brand-500 transition cursor-pointer"
                  >
                    <option value="">Matches Profile ({formData.current_status})</option>
                    <option value="Current">Current</option>
                    <option value="Delinquent">Delinquent</option>
                    <option value="Default">Default</option>
                    <option value="Prepaid">Prepaid</option>
                  </select>
                </div>

                {/* Servicer Doc Status */}
                <div className="flex flex-col space-y-1">
                  <label className="text-slate-500 font-sans">Servicer Doc Status</label>
                  <select
                    value={formData.servicer_document_status ?? ''}
                    onChange={(e) => setFormData({ ...formData, servicer_document_status: e.target.value || undefined })}
                    className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-brand-500 transition cursor-pointer"
                  >
                    <option value="">Matches Profile ({formData.document_status})</option>
                    <option value="Complete">Complete</option>
                    <option value="Missing">Missing</option>
                    <option value="Pending">Pending</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Action button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-bold shadow-md shadow-brand-950/20 transition disabled:opacity-40 font-sans cursor-pointer"
          >
            {loading ? 'Evaluating Model Inference...' : 'Calculate Live Inference'}
          </button>
        </form>

        {/* Results panel */}
        <div className="space-y-6">
          {error && (
            <div className="bg-rose-950/20 border border-rose-900 p-4 rounded-xl text-rose-455 text-xs flex items-start gap-2.5">
              <AlertTriangle className="h-5 w-5 text-rose-400 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!result ? (
            <div className="glass-panel border-dashed border-slate-800 rounded-xl p-12 text-center text-slate-500 flex flex-col items-center justify-center min-h-[450px]">
              <Sparkles className="h-10 w-10 text-slate-700 mb-3" />
              <h4 className="text-sm font-bold text-slate-400 font-sans">Waiting for Inference</h4>
              <p className="text-xs text-slate-550 max-w-xs mt-1.5 font-sans leading-relaxed">Modify the loan parameters on the left and run the predictor to get live probabilities.</p>
            </div>
          ) : (
            <div className="glass-panel rounded-xl p-6 space-y-6">
              <h3 className="text-xs font-bold text-slate-350 uppercase tracking-wider border-b border-slate-800/80 pb-2 flex items-center gap-1.5">
                <BarChart className="h-4 w-4 text-brand-400" />
                <span>Prediction Results</span>
              </h3>

              {/* Probabilities list */}
              <div className="space-y-4">
                {[
                  { label: 'Delinquency Prob (3m)', value: result.delinquency_probability, color: 'text-amber-450', barBg: 'bg-amber-500', glow: 'glow-amber-sm' },
                  { label: 'Default Prob (12m)', value: result.default_probability, color: 'text-rose-455', barBg: 'bg-rose-500', glow: 'glow-rose-sm' },
                  { label: 'Prepayment Prob (12m)', value: result.prepayment_probability, color: 'text-emerald-450', barBg: 'bg-emerald-500', glow: 'glow-emerald-sm' }
                ].map((prob, i) => (
                  <div key={i} className="space-y-1.5">
                    <div className="flex justify-between text-[11px] font-sans">
                      <span className="text-slate-400 font-medium">{prob.label}</span>
                      <span className={`font-mono font-bold ${prob.color}`}>{(prob.value * 100).toFixed(2)}%</span>
                    </div>
                    <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${prob.barBg} ${prob.glow}`}
                        style={{ width: `${Math.min(100, Math.max(2, prob.value * 100))}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>

              {/* State & Confidence info */}
              <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800 text-xs space-y-3 font-sans">
                <div className="flex justify-between border-b border-slate-800/60 pb-2">
                  <span className="text-slate-500">Predicted Next State:</span>
                  <span className="font-bold text-white uppercase">{result.next_state}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Inference Confidence:</span>
                  <span className="font-mono font-bold text-slate-355">{(result.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>

              {/* Anomaly & Verification info */}
              <div className="space-y-4 pt-4 border-t border-slate-800/80 font-sans">
                <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wide">Verification & Anomaly Checks</h4>
                
                {/* Score */}
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500">Combined Anomaly Score:</span>
                  <span className={`font-mono font-bold ${
                    result.anomaly_score >= 0.7 ? 'text-rose-455' :
                    result.anomaly_score >= 0.4 ? 'text-amber-455' :
                    'text-emerald-455'
                  }`}>
                    {(result.anomaly_score * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Exception type */}
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500">Exception Category:</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    result.exception_type === 'None'
                      ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-900/60'
                      : 'bg-rose-950/40 text-rose-400 border border-rose-900/60'
                  }`}>
                    {result.exception_type}
                  </span>
                </div>

                {/* Underwriter action */}
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500">Recommended Action:</span>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                    result.action === 'Priority Review' ? 'bg-rose-900 text-white' :
                    result.action === 'Investigate Data' ? 'bg-amber-900 text-white' :
                    'bg-emerald-900 text-white'
                  }`}>
                    {result.action}
                  </span>
                </div>

                {/* Variance Drivers */}
                {result.top_drivers !== 'None' && (
                  <div className="bg-rose-950/20 border border-rose-900/50 p-3 rounded-lg text-[10px] text-rose-350 space-y-1">
                    <span className="font-bold uppercase tracking-wider block">RECONCILIATION DRIVERS</span>
                    <p className="leading-tight font-mono">{result.top_drivers.replace(/;/g, ', ')}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
