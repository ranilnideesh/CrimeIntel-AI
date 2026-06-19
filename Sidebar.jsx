import React from 'react';
import { 
  LayoutDashboard, FilePlus, UploadCloud, Cpu, 
  Split, Sparkles, CheckSquare, Map, GitFork, 
  TrendingUp, MessageSquare, FileText, PhoneCall, 
  Activity 
} from 'lucide-react';

function Sidebar({ activePage, onNavigate, userRole }) {
  const links = [
    {
      group: "Workspace",
      items: [
        { id: 'dashboard', label: 'Officer Dashboard', icon: LayoutDashboard },
        { id: 'new-case', label: 'New Case Entry', icon: FilePlus },
        { id: 'evidence-upload', label: 'Evidence Vault', icon: UploadCloud }
      ]
    },
    {
      group: "Forensic Intelligence",
      items: [
        { id: 'ai-analysis', label: 'AI Evidence Analyzer', icon: Cpu },
        { id: 'historical-compare', label: 'MO Similarity Compare', icon: Split },
        { id: 'lead-generation', label: 'Actionable Leads', icon: Sparkles },
        { id: 'case-timeline', label: 'Case Milestones', icon: CheckSquare }
      ]
    },
    {
      group: "Spatial & Link Graphs",
      items: [
        { id: 'crime-map', label: 'Crime Hotspots Map', icon: Map },
        { id: 'evidence-graph', label: 'Entity Relation Graph', icon: GitFork },
        { id: 'outcome-prediction', label: 'Case Outcome Predictor', icon: TrendingUp }
      ]
    },
    {
      group: "Dossier & Help",
      items: [
        { id: 'chatbot', label: 'AI Chatbot Copilot', icon: MessageSquare },
        { id: 'report-download', label: 'Dossier Generator', icon: FileText },
        { id: 'emergency-help', label: 'Emergency Help Desk', icon: PhoneCall }
      ]
    }
  ];

  return (
    <aside className="w-64 bg-slate-900/60 border-r border-slate-800 flex flex-col justify-between overflow-y-auto">
      <div className="py-4 px-3 space-y-6">
        {links.map((g, gi) => (
          <div key={gi}>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-3 mb-2">{g.group}</p>
            <div className="space-y-1">
              {g.items.map(item => {
                const Icon = item.icon;
                const isActive = activePage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onNavigate(item.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded text-xs transition-all font-medium ${
                      isActive
                        ? 'bg-cyan-950/60 border border-cyan-800/40 text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.06)]'
                        : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-200'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
        
        {/* Admin Section */}
        {userRole === 'Admin' && (
          <div>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-3 mb-2">Administration</p>
            <button
              onClick={() => onNavigate('admin-panel')}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded text-xs transition-all font-medium ${
                activePage === 'admin-panel'
                  ? 'bg-cyan-950/60 border border-cyan-800/40 text-cyan-400'
                  : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-200'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>System Audit Log</span>
            </button>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-900 bg-slate-950/50">
        <div className="flex items-center space-x-2 text-[10px] text-slate-500 font-semibold tracking-wider">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>SECURE POLICE ENCRYPTED CHANNEL</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
