import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, UserCheck, BarChart3, BookOpen, BrainCircuit } from 'lucide-react';

export default function Sidebar() {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Rankings', path: '/rankings', icon: UserCheck },
    { name: 'Candidate Details', path: '/candidate', icon: Users },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Documentation', path: '/documentation', icon: BookOpen },
  ];

  return (
    <aside className="w-64 bg-[#1E293B] border-r border-slate-800 flex flex-col h-screen shrink-0 transition-all duration-300">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="p-1.5 rounded-lg bg-sky-500/10 border border-sky-400/20 text-sky-400">
          <BrainCircuit className="h-6 w-6 animate-pulse-slow" />
        </div>
        <span className="font-bold text-lg bg-gradient-to-r from-white via-slate-100 to-sky-400 bg-clip-text text-transparent">
          AI Candidate Ranker
        </span>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            // If candidate, match subpaths like /candidate/1
            end={item.path === '/'}
            className={({ isActive }) => {
              // Custom matching for candidates to highlight sidebar item
              const isCandidatePath = item.path === '/candidate' && window.location.pathname.startsWith('/candidate');
              const active = isActive || isCandidatePath;

              return `flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
                active
                  ? 'bg-sky-500/10 border border-sky-500/20 text-sky-400 shadow-md shadow-sky-500/5'
                  : 'border border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`;
            }}
          >
            <item.icon className="h-4 w-4" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer Details */}
      <div className="p-4 border-t border-slate-800">
        <div className="p-3 bg-slate-800/40 border border-slate-800 rounded-xl">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span>System Status</span>
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
          </div>
          <p className="text-xs font-semibold text-slate-300">Model: Gemini 3.5 Flash</p>
        </div>
      </div>
    </aside>
  );
}
