import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getLoans } from '../../services/api';
import type { LoanItem } from '../../types';
import {
  Search,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  FileText
} from 'lucide-react';

export const LoanExplorer: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [loans, setLoans] = useState<LoanItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [searchId, setSearchId] = useState(searchParams.get('loan_id') || '');
  const [riskFilter, setRiskFilter] = useState(searchParams.get('risk_level') || '');
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '');
  const [anomalyFilter, setAnomalyFilter] = useState(searchParams.get('anomaly') || '');
  const [vintageFilter, setVintageFilter] = useState(searchParams.get('vintage') || '');
  
  // Pagination
  const limit = 15;
  const page = parseInt(searchParams.get('page') || '1');
  const offset = (page - 1) * limit;

  const fetchLoans = async () => {
    try {
      setLoading(true);
      
      const queryParams: any = {
        limit,
        offset
      };
      
      if (searchParams.get('loan_id')) queryParams.loan_id = searchParams.get('loan_id');
      if (searchParams.get('risk_level')) queryParams.risk_level = searchParams.get('risk_level');
      if (searchParams.get('status')) queryParams.status = searchParams.get('status');
      if (searchParams.get('anomaly')) queryParams.anomaly = searchParams.get('anomaly') === 'true';
      if (searchParams.get('vintage')) queryParams.vintage = parseInt(searchParams.get('vintage')!);

      const res = await getLoans(queryParams);
      setLoans(res.items);
      setTotal(res.total);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load portfolio loan records.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLoans();
  }, [searchParams]);

  const handleApplyFilters = (e: React.FormEvent) => {
    e.preventDefault();
    const params: Record<string, string> = { page: '1' };
    if (searchId) params.loan_id = searchId;
    if (riskFilter) params.risk_level = riskFilter;
    if (statusFilter) params.status = statusFilter;
    if (anomalyFilter) params.anomaly = anomalyFilter;
    if (vintageFilter) params.vintage = vintageFilter;
    setSearchParams(params);
  };

  const handleClearFilters = () => {
    setSearchId('');
    setRiskFilter('');
    setStatusFilter('');
    setAnomalyFilter('');
    setVintageFilter('');
    setSearchParams({ page: '1' });
  };

  const handlePageChange = (newSpec: number) => {
    const currentParams = Object.fromEntries(searchParams.entries());
    currentParams.page = newSpec.toString();
    setSearchParams(currentParams);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="flex-1 p-8 space-y-6 overflow-y-auto max-h-[calc(100vh-4rem)]">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide">Loan Explorer</h1>
          <p className="text-slate-400 text-sm">Query and profile individual loan delinquency risks and audit flags.</p>
        </div>
        <button
          onClick={fetchLoans}
          className="p-2 border border-slate-700 bg-slate-800/40 text-slate-400 rounded-lg hover:text-white transition"
          title="Refresh panel data"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {/* Filter Bar */}
      <form onSubmit={handleApplyFilters} className="bg-slate-800/20 border border-slate-800 rounded-xl p-5 grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* Loan ID Search */}
        <div className="flex flex-col space-y-1">
          <label className="text-[10px] text-slate-500 font-semibold tracking-wider uppercase">Loan ID</label>
          <div className="relative">
            <input
              type="text"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              placeholder="e.g. LN1002"
              className="w-full bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-white rounded-lg pl-8 pr-3 py-2.5 focus:outline-none focus:border-brand-500 transition"
            />
            <Search className="absolute left-2.5 top-3 h-4 w-4 text-slate-500" />
          </div>
        </div>

        {/* Risk Level Filter */}
        <div className="flex flex-col space-y-1">
          <label className="text-[10px] text-slate-500 font-semibold tracking-wider uppercase">Risk Level</label>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2.5 focus:outline-none focus:border-brand-500 transition"
          >
            <option value="">All Risks</option>
            <option value="low">Low Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="high">High Risk</option>
          </select>
        </div>

        {/* Servicing Status */}
        <div className="flex flex-col space-y-1">
          <label className="text-[10px] text-slate-500 font-semibold tracking-wider uppercase">Current Status</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2.5 focus:outline-none focus:border-brand-500 transition"
          >
            <option value="">All Statuses</option>
            <option value="current">Current</option>
            <option value="delinquent">Delinquent</option>
            <option value="default">Default</option>
            <option value="prepaid">Prepaid</option>
          </select>
        </div>

        {/* Anomaly state */}
        <div className="flex flex-col space-y-1">
          <label className="text-[10px] text-slate-500 font-semibold tracking-wider uppercase">Discrepancy</label>
          <select
            value={anomalyFilter}
            onChange={(e) => setAnomalyFilter(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2.5 focus:outline-none focus:border-brand-500 transition"
          >
            <option value="">All Records</option>
            <option value="true">Anomalous Only</option>
            <option value="false">Normal Only</option>
          </select>
        </div>

        {/* Vintage filter */}
        <div className="flex flex-col space-y-1">
          <label className="text-[10px] text-slate-500 font-semibold tracking-wider uppercase">Vintage</label>
          <input
            type="number"
            value={vintageFilter}
            onChange={(e) => setVintageFilter(e.target.value)}
            placeholder="e.g. 2022"
            className="w-full bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-white rounded-lg px-3 py-2.5 focus:outline-none focus:border-brand-500 transition"
          />
        </div>

        {/* Action buttons */}
        <div className="flex items-end space-x-2">
          <button
            type="submit"
            className="flex-1 bg-brand-600 hover:bg-brand-700 text-white rounded-lg py-2 text-xs font-semibold shadow-md transition"
          >
            Apply
          </button>
          <button
            type="button"
            onClick={handleClearFilters}
            className="flex-1 border border-slate-700 bg-slate-800/40 hover:bg-slate-800 text-slate-300 rounded-lg py-2 text-xs font-semibold transition"
          >
            Clear
          </button>
        </div>
      </form>

      {/* Main Table */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-12 bg-slate-800/40 rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-slate-800/20 border border-slate-800 p-8 text-center rounded-xl flex flex-col items-center space-y-3">
          <AlertTriangle className="h-10 w-10 text-rose-500" />
          <h3 className="text-sm font-semibold text-white">Error Loading Data</h3>
          <p className="text-xs text-slate-400 max-w-sm">{error}</p>
        </div>
      ) : loans.length === 0 ? (
        <div className="bg-slate-800/10 border border-slate-800 p-12 text-center rounded-xl flex flex-col items-center space-y-3">
          <FileText className="h-12 w-12 text-slate-600" />
          <h3 className="text-sm font-semibold text-slate-400">No Loans Match Filters</h3>
          <p className="text-xs text-slate-500 max-w-sm">Try clearing your filters or testing other query substrings.</p>
        </div>
      ) : (
        <div className="bg-slate-800/20 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-800/50 border-b border-slate-700/50 text-slate-400 font-semibold tracking-wider">
                  <th className="p-4 uppercase">Loan ID</th>
                  <th className="p-4 uppercase">Risk Category</th>
                  <th className="p-4 uppercase">Status</th>
                  <th className="p-4 uppercase text-right">Outstanding Balance</th>
                  <th className="p-4 uppercase text-right">Origination Balance</th>
                  <th className="p-4 uppercase text-right">Days Past Due</th>
                  <th className="p-4 uppercase text-center">FICO Band</th>
                  <th className="p-4 uppercase text-center">State</th>
                  <th className="p-4 uppercase text-right">Anomaly Index</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {loans.map((loan) => (
                  <tr
                    key={loan.loan_id}
                    onClick={() => navigate(`/loans/${loan.loan_id}`)}
                    className="hover:bg-slate-800/40 cursor-pointer text-slate-300 transition"
                  >
                    <td className="p-4 font-semibold text-white">{loan.loan_id}</td>
                    <td className="p-4">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                          loan.risk_level === 'high'
                            ? 'bg-rose-950/40 text-rose-400'
                            : loan.risk_level === 'medium'
                            ? 'bg-amber-950/40 text-amber-400'
                            : 'bg-emerald-950/40 text-emerald-400'
                        }`}
                      >
                        {loan.risk_level}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className="flex items-center">
                        <span
                          className={`h-1.5 w-1.5 rounded-full mr-2 ${
                            loan.current_status === 'Default'
                              ? 'bg-rose-500'
                              : loan.current_status === 'Delinquent'
                              ? 'bg-amber-500'
                              : loan.current_status === 'Prepaid'
                              ? 'bg-emerald-500'
                              : 'bg-brand-500'
                          }`}
                        ></span>
                        {loan.current_status}
                      </span>
                    </td>
                    <td className="p-4 text-right font-medium">${loan.current_balance.toLocaleString()}</td>
                    <td className="p-4 text-right">${loan.original_balance.toLocaleString()}</td>
                    <td className="p-4 text-right">{loan.days_past_due} DPD</td>
                    <td className="p-4 text-center text-slate-400">{loan.credit_score_band}</td>
                    <td className="p-4 text-center text-slate-400">{loan.state}</td>
                    <td className="p-4 text-right font-medium text-amber-500">{(loan.anomaly_score * 100).toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="bg-slate-800/40 px-6 py-4 flex items-center justify-between border-t border-slate-800 text-xs">
              <span className="text-slate-400">
                Showing <span className="font-semibold text-white">{offset + 1}</span> to{' '}
                <span className="font-semibold text-white">{Math.min(offset + limit, total)}</span> of{' '}
                <span className="font-semibold text-white">{total}</span> records
              </span>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handlePageChange(page - 1)}
                  disabled={page === 1}
                  className="p-1.5 border border-slate-700 bg-slate-800/40 text-slate-400 rounded hover:text-white disabled:opacity-30 disabled:pointer-events-none transition"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <span className="text-slate-400">
                  Page <span className="font-semibold text-white">{page}</span> of{' '}
                  <span className="font-semibold text-white">{totalPages}</span>
                </span>
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page === totalPages}
                  className="p-1.5 border border-slate-700 bg-slate-800/40 text-slate-400 rounded hover:text-white disabled:opacity-30 disabled:pointer-events-none transition"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
