import React from 'react';
import { ShieldAlert, LogOut } from 'lucide-react';

function Navbar({ token, username, role, cases, selectedCaseId, onCaseChange, onLogout, onNavigate }) {
  return (
    <header className="bg-slate-900/60 backdrop-blur border-b border-slate-800 px-6 py-4 flex justify-between items-center z-10">
      <div 
        className="flex items-center space-x-3 cursor-pointer" 
        onClick={() => onNavigate(token ? 'dashboard' : 'landing')}
      >
        <div className="w-10 h-10 rounded-lg bg-cyan-950 border border-cyan-500 flex items-center justify-center text-cyan-400">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-wider text-slate-100 flex items-center">
            CRIMEINTEL AI
            <span className="ml-2 text-[10px] bg-cyan-950 border border-cyan-500/30 text-cyan-400 px-1.5 py-0.5 rounded uppercase font-semibold tracking-normal">
              Support Node
            </span>
          </h1>
          <p className="text-[9px] text-slate-400 uppercase tracking-widest leading-none mt-0.5">
            Evidence Analysis & Investigation Support
          </p>
        </div>
      </div>

      {token && (
        <div className="flex items-center space-x-4">
          {/* Active Case Context Selector */}
          <div className="flex items-center space-x-2">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              Active Case Context:
            </span>
            <select
              className="bg-slate-900 border border-slate-700 text-slate-100 text-xs rounded px-3 py-1.5 outline-none focus:border-cyan-500"
              value={selectedCaseId || ''}
              onChange={(e) => onCaseChange(Number(e.target.value))}
            >
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.case_number} - {c.title}
                </option>
              ))}
            </select>
          </div>

          {/* User Account Info */}
          <div className="flex items-center space-x-3 border-l border-slate-855 pl-4">
            <div className="text-right font-sans">
              <p className="text-xs font-semibold text-slate-200">{username}</p>
              <p className="text-[9px] text-cyan-400 uppercase tracking-wider">{role}</p>
            </div>
            <button
              onClick={onLogout}
              className="bg-slate-900 hover:bg-red-950/30 border border-slate-800 hover:border-red-900/50 text-slate-400 hover:text-red-400 p-2 rounded transition-all"
              title="Logout Securely"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </header>
  );
}

export default Navbar;
