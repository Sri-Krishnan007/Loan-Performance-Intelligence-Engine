import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  AlertTriangle,
  Compass,
  FileSearch,
  TrendingUp,
  Sparkles
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/dashboard', label: 'Portfolio Overview', icon: LayoutDashboard },
    { to: '/loans', label: 'Loan Explorer', icon: Search },
    { to: '/exceptions', label: 'Exception Center', icon: AlertTriangle },
    { to: '/scenarios', label: 'Scenario Simulator', icon: Compass },
    { to: '/reviewer', label: 'AI Reviewer', icon: FileSearch },
    { to: '/predict', label: 'Live Predictor', icon: Sparkles },
    { to: '/model-health', label: 'Model & Data Health', icon: TrendingUp },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900 flex flex-col justify-between text-slate-300 min-h-screen">
      <div className="flex-1 py-6 flex flex-col space-y-1 px-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-md shadow-brand-950/40'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`
              }
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
        Reviewer Workstation v1.0.0
      </div>
    </aside>
  );
};
