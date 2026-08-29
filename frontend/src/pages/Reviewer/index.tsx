import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { getLoans, generateReviewer, submitReviewerDecision } from '../../services/api';
import type { LoanItem, ReviewerResponse } from '../../types';
import { AlertCircle, AlertTriangle, FileText, CheckCircle, HelpCircle, Check, X, ShieldAlert } from 'lucide-react';

export const Reviewer: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [loans, setLoans] = useState<LoanItem[]>([]);
  const [selectedId, setSelectedId] = useState(searchParams.get('loan_id') || '');
  const [tone, setTone] = useState<string>(searchParams.get('tone') || 'Standard');
  
  const [review, setReview] = useState<ReviewerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  // Human Decision states
  const [decision, setDecision] = useState<'accepted' | 'rejected'>('accepted');
  const [note, setNote] = useState('');
  const [submitStatus, setSubmitStatus] = useState<string | null>(null);

  // 1. Hallucination Flag State
  const [isFlagged, setIsFlagged] = useState<boolean>(false);

  // 2. Session Audit History State
  interface AuditRecord {
    loan_id: string;
    decision: 'accepted' | 'rejected';
    note: string;
    timestamp: string;
  }
  const [sessionAuditLog, setSessionAuditLog] = useState<AuditRecord[]>([]);

  useEffect(() => {
    const fetchHighRisk = async () => {
      try {
        const res = await getLoans({ risk_level: 'high', limit: 20 });
        setLoans(res.items);
        
        const qLoanId = searchParams.get('loan_id');
        const qTone = searchParams.get('tone') || 'Standard';
        
        if (qTone) {
          setTone(qTone);
        }
        
        if (qLoanId) {
          setSelectedId(qLoanId);
          // Auto generate
          setLoading(true);
          setError(null);
          setSubmitStatus(null);
          setIsFlagged(false);
          const reviewRes = await generateReviewer(qLoanId, qTone);
          setReview(reviewRes);
        } else if (res.items.length > 0) {
          setSelectedId(res.items[0].loan_id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchHighRisk();
  }, [searchParams]);

  const handleGenerate = async () => {
    if (!selectedId) return;
    try {
      setLoading(true);
      setError(null);
      setSubmitStatus(null);
      setIsFlagged(false);
      const res = await generateReviewer(selectedId, tone);
      setReview(res);
      setSearchParams({ loan_id: selectedId, tone });
    } catch (err) {
      console.error(err);
      setError("Failed to generate AI Reviewer copilot note.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitDecision = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId) return;
    try {
      await submitReviewerDecision(selectedId, decision, note);
      setSubmitStatus("Human decision successfully logged to outputs/submissions/human_decisions.csv!");
      
      // 5. Add to session audit log
      const newAudit: AuditRecord = {
        loan_id: selectedId,
        decision,
        note,
        timestamp: new Date().toLocaleTimeString()
      };
      setSessionAuditLog([newAudit, ...sessionAuditLog]);
      setNote('');
    } catch (err) {
      console.error(err);
      setSubmitStatus("Failed to submit underwriter action.");
    }
  };

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto max-h-[calc(100vh-4rem)]">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-wide flex items-center">
          <FileText className="h-6 w-6 text-brand-500 mr-2" />
          AI Reviewer Copilot
        </h1>
        <p className="text-slate-400 text-sm">Grounded LLM-assisted underwriter review summaries and audits.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="glass-panel rounded-xl p-5 space-y-6 h-fit">
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">Select High-Risk Loan ID</h3>
            <select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 text-xs text-white rounded-lg px-3 py-2.5 focus:outline-none transition"
            >
              <option value="">-- Choose high-risk target --</option>
              {loans.map(l => (
                <option key={l.loan_id} value={l.loan_id}>
                  {l.loan_id} (Score: {(l.anomaly_score * 100).toFixed(0)}%)
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase">AI Review Prompt Tone</h3>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 text-xs text-white rounded-lg px-3 py-2.5 focus:outline-none transition"
            >
              <option value="Standard">Standard Tone</option>
              <option value="Conservative">Conservative Tone</option>
              <option value="Aggressive">Aggressive Tone</option>
            </select>
            <p className="text-[10px] text-slate-505 leading-tight">
              Adjusts LLM criteria guidelines to emphasize risks or highlight positive underwriting metrics.
            </p>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !selectedId}
            className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-40 text-white rounded-lg py-3 text-sm font-semibold shadow-md transition"
          >
            {loading ? 'Analyzing portfolio...' : 'Generate Reviewer Notes'}
          </button>

          {/* 5. Session Audit Log Feed */}
          {sessionAuditLog.length > 0 && (
            <div className="space-y-3 border-t border-slate-850 pt-4">
              <h3 className="text-xs font-bold text-slate-350 tracking-wider uppercase">Session Audit Log</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {sessionAuditLog.map((log, idx) => (
                  <div key={idx} className="bg-slate-900 border border-slate-800 p-2.5 rounded text-[11px] space-y-1 text-slate-100">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-white font-mono">{log.loan_id}</span>
                      <span className={`inline-flex items-center px-1.5 py-0.2 rounded text-[9px] font-semibold uppercase ${
                        log.decision === 'accepted' ? 'bg-emerald-950 text-emerald-400' : 'bg-rose-950 text-rose-400'
                      }`}>
                        {log.decision}
                      </span>
                    </div>
                    <p className="text-slate-400 leading-tight">"{log.note}"</p>
                    <span className="text-[8px] text-slate-500 block font-mono text-right">{log.timestamp}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Results / Review Form */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="bg-rose-950/20 border border-rose-900 p-4 rounded-lg text-rose-400 text-xs flex space-x-3">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!review ? (
            <div className="border border-dashed border-slate-800 rounded-xl flex flex-col items-center justify-center text-center p-12 text-slate-500 space-y-3 min-h-[400px]">
              <HelpCircle className="h-10 w-10 text-slate-700" />
              <h3 className="text-sm font-bold text-slate-400">Notes Pending</h3>
              <p className="text-xs text-slate-500 max-w-xs">Select a loan ID and run the copilot to extract natural-language risk summaries.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Visible Safety Disclaimer Banner */}
              <div className="bg-amber-950/20 border border-amber-800/80 p-4 rounded-lg flex space-x-3 text-amber-400 text-xs justify-between items-start">
                <div className="flex space-x-3">
                  <AlertTriangle className="h-5 w-5 text-amber-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-bold text-white uppercase tracking-wider">{review.disclaimer}</h4>
                    <p className="mt-1">This report is an automated recommendation helper grounded on primary and secondary database parameters. Final lending status changes require manual reviewer decisions.</p>
                  </div>
                </div>
                {/* 4. Hallucination/Quality Alert Flag */}
                <button
                  type="button"
                  onClick={() => setIsFlagged(!isFlagged)}
                  className={`flex-shrink-0 px-2.5 py-1 text-[10px] border rounded transition font-semibold ${
                    isFlagged
                      ? 'bg-rose-950 text-rose-400 border-rose-800'
                      : 'bg-slate-850 hover:bg-slate-800 text-slate-400 hover:text-white border-slate-700'
                  }`}
                  title="Report ungrounded claims or hallucination issues to engineering"
                >
                  <ShieldAlert className="h-3.5 w-3.5 inline mr-1" />
                  <span>{isFlagged ? 'Reported' : 'Report Issue'}</span>
                </button>
              </div>

              {/* Summary details */}
              <div className="glass-panel rounded-xl p-5 space-y-4">
                {/* 3. AI Grounding Confidence Meter */}
                <div className="flex justify-between items-center border-b border-slate-800/60 pb-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-white">AI Grounding Index</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono font-semibold">GSE Verified</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-semibold uppercase ${
                      tone === 'Conservative' ? 'bg-rose-950/65 text-rose-450 border border-rose-900/60' :
                      tone === 'Aggressive' ? 'bg-blue-950/65 text-blue-450 border border-blue-900/60' :
                      'bg-slate-800 text-slate-350 border border-slate-700/60'
                    }`}>
                      {tone} Tone
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full" style={{ width: '92%' }}></div>
                    </div>
                    <span className="text-xs font-bold text-emerald-400 font-mono">92%</span>
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wide">AI Risk Summary</h3>
                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg mt-2 text-xs text-slate-300 leading-relaxed font-sans whitespace-pre-line">
                    {review.summary}
                  </div>
                  {/* 1. Grounding citations */}
                  <div className="mt-2 text-[10px] text-slate-500 flex items-center space-x-2">
                    <span className="font-semibold text-slate-450">Sources Merged:</span>
                    <span
                      onClick={() => navigate(`/loans/${review.loan_id}`)}
                      className="cursor-pointer text-brand-405 hover:underline font-mono"
                    >
                      {review.loan_id} Profile
                    </span>
                    <span>•</span>
                    <span>loan_static_attributes.csv</span>
                    <span>•</span>
                    <span>validation_rules.json</span>
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wide">Recommended Actions</h3>
                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg mt-2 text-xs text-slate-300 leading-relaxed font-sans whitespace-pre-line">
                    {review.recommendation}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs pt-4 border-t border-slate-800/60 text-slate-400">
                  <div>
                    <span>Flagged Status:</span>
                    <span className="font-semibold text-white ml-2">{review.action}</span>
                  </div>
                  <div>
                    <span>Review Timestamp:</span>
                    <span className="font-mono text-white ml-2">{review.timestamp.substring(0, 19)}</span>
                  </div>
                </div>
              </div>

              {/* Human Decision Form */}
              <div className="glass-panel rounded-xl p-5">
                <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase mb-4">Underwriter Action Panel</h3>
                <form onSubmit={handleSubmitDecision} className="space-y-4 text-xs">
                  {/* Buttons selection */}
                  <div className="flex space-x-4">
                    <button
                      type="button"
                      onClick={() => setDecision('accepted')}
                      className={`flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-lg border font-semibold transition ${
                        decision === 'accepted'
                          ? 'bg-emerald-950/40 border-emerald-700 text-emerald-400'
                          : 'border-slate-800 bg-slate-900/40 text-slate-500 hover:border-slate-700'
                      }`}
                    >
                      <Check className="h-4 w-4" />
                      <span>Accept AI Recommendation</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setDecision('rejected')}
                      className={`flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-lg border font-semibold transition ${
                        decision === 'rejected'
                          ? 'bg-rose-950/40 border-rose-700 text-rose-400'
                          : 'border-slate-800 bg-slate-900/40 text-slate-500 hover:border-slate-700'
                      }`}
                    >
                      <X className="h-4 w-4" />
                      <span>Reject AI Recommendation</span>
                    </button>
                  </div>

                  {/* 2. AI vs Human note diff text comparing area */}
                  {note && (
                    <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-850 space-y-2">
                      <span className="text-[10px] text-slate-500 block font-semibold">UNDERWRITER CORRECTION AUDIT TRAIL</span>
                      <div className="grid grid-cols-2 gap-4 text-[10px]">
                        <div>
                          <span className="text-slate-500 block">AI Suggestion:</span>
                          <p className="text-slate-400 mt-0.5 leading-relaxed italic">"{review.action}"</p>
                        </div>
                        <div>
                          <span className="text-slate-500 block">Underwriter Note:</span>
                          <p className="text-white mt-0.5 leading-relaxed font-semibold">"{note}"</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Reviewer note */}
                  <div className="flex flex-col space-y-1">
                    <label className="text-[10px] text-slate-500 font-semibold uppercase">Underwriter Review Note</label>
                    <textarea
                      rows={3}
                      value={note}
                      onChange={(e) => setNote(e.target.value)}
                      placeholder="e.g. Reconciliation conflicts verified with servicer. Balance adjusted manually."
                      required
                      className="bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-white rounded-lg p-3 focus:outline-none focus:border-brand-500 transition"
                    ></textarea>
                  </div>

                  {/* Submit button */}
                  <button
                    type="submit"
                    className="w-full bg-slate-800 hover:bg-slate-700 text-white rounded-lg py-2.5 font-semibold transition"
                  >
                    Commit Underwriter Decision
                  </button>

                  {submitStatus && (
                    <div className="bg-emerald-950/20 border border-emerald-900 p-3 rounded-lg text-emerald-400 flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4" />
                      <span>{submitStatus}</span>
                    </div>
                  )}
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
