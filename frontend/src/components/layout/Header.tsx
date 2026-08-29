import React, { useEffect, useState } from 'react';
import { getHealth, isMockModeActive, setMockMode } from '../../services/api';
import { ShieldCheck, Activity, ToggleLeft, ToggleRight } from 'lucide-react';

export const Header: React.FC = () => {
  const [health, setHealth] = useState<{ status: string; service: string } | null>(null);
  const isMock = isMockModeActive();

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await getHealth();
        setHealth({ status: res.status, service: res.service });
      } catch (err) {
        setHealth({ status: 'offline', service: 'Offline Mode' });
      }
    };
    fetchHealth();
  }, []);

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900 px-6 flex items-center justify-between text-slate-100 sticky top-0 z-40">
      <div className="flex items-center space-x-3">
        <ShieldCheck className="h-6 w-6 text-brand-500" />
        <span className="text-lg font-semibold tracking-wide text-white">
          Intain Loan Intelligence
        </span>
      </div>

      <div className="flex items-center space-x-6">
        {/* Mock Mode Toggle */}
        <button
          onClick={() => setMockMode(!isMock)}
          className={`flex items-center space-x-2 text-xs px-3 py-1.5 rounded-full border transition-all ${
            isMock
              ? 'bg-amber-950/40 text-amber-400 border-amber-800/80 hover:bg-amber-950/60'
              : 'bg-slate-800/60 text-slate-400 border-slate-700 hover:bg-slate-800 hover:text-slate-200'
          }`}
          title="Toggle between live backend APIs and static mockup data fallbacks."
        >
          {isMock ? (
            <>
              <ToggleRight className="h-4 w-4 text-amber-400" />
              <span>Mock Mode Active</span>
            </>
          ) : (
            <>
              <ToggleLeft className="h-4 w-4 text-slate-400" />
              <span>Live API Mode</span>
            </>
          )}
        </button>

        {/* Health indicator */}
        <div className="flex items-center space-x-2 text-xs">
          <Activity className="h-4 w-4 text-slate-500" />
          <span className="text-slate-400">System:</span>
          {health ? (
            <span
              className={`font-semibold px-2 py-0.5 rounded-md ${
                health.status === 'ok'
                  ? 'bg-emerald-950/50 text-emerald-400'
                  : health.status === 'warning'
                  ? 'bg-amber-950/50 text-amber-400'
                  : 'bg-rose-950/50 text-rose-400'
              }`}
            >
              {health.status.toUpperCase()}
            </span>
          ) : (
            <span className="text-slate-500">Checking...</span>
          )}
        </div>
      </div>
    </header>
  );
};
