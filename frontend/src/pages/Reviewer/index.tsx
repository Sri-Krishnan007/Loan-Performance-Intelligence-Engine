import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getLoans, generateReviewer, submitReviewerDecision } from '../../services/api';
import type { LoanItem, ReviewerResponse } from '../../types';
import { AlertCircle, AlertTriangle, FileText, CheckCircle, HelpCircle } from 'lucide-react';

export const Reviewer: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [loans, setLoans] = useState<LoanItem[]>([]);
  const [selectedId, setSelectedId] = useState(searchParams.get('loan_id') || '');
  
  const [review, setReview] = useState<ReviewerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Human Decision states
  const [decision, setDecision] = useState<'accepted' | 'rejected'>('accepted');
  const [note, setNote] = useState('');
  const [submitStatus, setSubmitStatus] = useState<string | null>(null);

  useEffect(() => {
    const fetchHighRisk = async () => {
      try {
        const res = await getLoans({ risk_level: 'high', limit: 20 });
        setLoans(res.items);
        if (res.items.length > 0 && !selectedId) {
          setSelectedId(res.items[0].loan_id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchHighRisk();
  }, []);

  const handleGenerate = async () => {
    if (!selectedId) return;
    try {
      setLoading(true);
      setError(null);
      setSubmitStatus(null);
      const res = await generateReviewer(selectedId);
      setReview(res);
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
        <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-5 space-y-6 h-fit">
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

          <button
            onClick={handleGenerate}
            disabled={loading || !selectedId}
            className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-40 text-white rounded-lg py-3 text-sm font-semibold shadow-md transition"
          >
            {loading ? 'Analyzing portfolio...' : 'Generate Reviewer Notes'}
          </button>
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
              <div className="bg-amber-950/20 border border-amber-800/80 p-4 rounded-lg flex space-x-3 text-amber-400 text-xs">
                <AlertTriangle className="h-5 w-5 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-white uppercase tracking-wider">{review.disclaimer}</h4>
                  <p className="mt-1">This report is an automated recommendation helper grounded on primary and secondary database parameters. Final lending status changes require manual reviewer decisions.</p>
                </div>
              </div>

              {/* Summary details */}
              <div className="bg-slate-800/20 border border-slate-800 rounded-xl p-5 space-y-4">
                <div>
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wide">AI Risk Summary</h3>
                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg mt-2 text-xs text-slate-300 leading-relaxed font-sans whitespace-pre-line">
                    {review.summary}
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
              <div className="bg-slate-800/30 border border-slate-800 rounded-xl p-5">
                <h3 className="text-xs font-bold text-slate-300 tracking-wider uppercase mb-4">Underwriter Action Panel</h3>
                <form onSubmit={handleSubmitDecision} className="space-y-4 text-xs">
                  {/* Buttons selection */}
                  <div className="flex space-x-4">
                    <button
                      type="button"
                      onClick={() => setDecision('accepted')}
                      className={`flex-1 py-2.5 rounded-lg border font-semibold transition ${
                        decision === 'accepted'
                          ? 'bg-emerald-950/40 border-emerald-700 text-emerald-400'
                          : 'border-slate-800 bg-slate-900/40 text-slate-500 hover:border-slate-700'
                      }`}
                    >
                      Accept AI Recommendation
                    </button>
                    <button
                      type="button"
                      onClick={() => setDecision('rejected')}
                      className={`flex-1 py-2.5 rounded-lg border font-semibold transition ${
                        decision === 'rejected'
                          ? 'bg-rose-950/40 border-rose-700 text-rose-400'
                          : 'border-slate-800 bg-slate-900/40 text-slate-500 hover:border-slate-700'
                      }`}
                    >
                      Reject AI Recommendation
                    </button>
                  </div>

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
