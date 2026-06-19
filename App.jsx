import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

// Page Imports
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import NewCasePage from './pages/NewCasePage';
import EvidenceUploadPage from './pages/EvidenceUploadPage';
import AIAnalysisPage from './pages/AIAnalysisPage';
import CrimeComparisonPage from './pages/CrimeComparisonPage';
import LeadGenerationPage from './pages/LeadGenerationPage';
import CaseTimelinePage from './pages/CaseTimelinePage';
import CrimeMapPage from './pages/CrimeMapPage';
import EvidenceGraphPage from './pages/EvidenceGraphPage';
import OutcomePredictionPage from './pages/OutcomePredictionPage';
import ChatbotAssistantPage from './pages/ChatbotAssistantPage';
import ReportDownloadPage from './pages/ReportDownloadPage';
import EmergencyHelpPage from './pages/EmergencyHelpPage';
import AdminPanelPage from './pages/AdminPanelPage';

function App() {
  const { token, role, username, logout } = useAuth();
  const [activePage, setActivePage] = useState('landing');
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [stats, setStats] = useState(null);

  const selectedCase = cases.find(c => c.id === selectedCaseId) || null;

  useEffect(() => {
    if (token) {
      fetchCases();
      fetchStats();
      setActivePage('dashboard');
    } else {
      setActivePage('landing');
    }
  }, [token]);

  const fetchCases = async () => {
    try {
      const res = await axios.get('/api/v1/cases/');
      setCases(res.data);
      if (res.data.length > 0 && !selectedCaseId) {
        setSelectedCaseId(res.data[0].id);
      }
    } catch (e) {
      console.error("Error loading cases", e);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get('/api/v1/dashboard/stats');
      setStats(res.data);
    } catch (e) {
      console.error("Error loading dashboard metrics", e);
    }
  };

  const renderPage = () => {
    switch (activePage) {
      case 'landing':
        return <LandingPage onNavigate={setActivePage} />;
      case 'login':
        return <LoginPage onNavigate={setActivePage} />;
      case 'dashboard':
        return <Dashboard stats={stats} currentCase={selectedCase} userRole={role} />;
      case 'new-case':
        return <NewCasePage onCaseCreated={fetchCases} />;
      case 'evidence-upload':
        return <EvidenceUploadPage currentCase={selectedCase} onUpload={fetchStats} />;
      case 'ai-analysis':
        return <AIAnalysisPage currentCase={selectedCase} />;
      case 'historical-compare':
        return <CrimeComparisonPage currentCase={selectedCase} />;
      case 'lead-generation':
        return <LeadGenerationPage currentCase={selectedCase} />;
      case 'case-timeline':
        return <CaseTimelinePage currentCase={selectedCase} />;
      case 'crime-map':
        return <CrimeMapPage />;
      case 'evidence-graph':
        return <EvidenceGraphPage currentCase={selectedCase} />;
      case 'outcome-prediction':
        return <OutcomePredictionPage currentCase={selectedCase} />;
      case 'chatbot':
        return <ChatbotAssistantPage currentCase={selectedCase} />;
      case 'report-download':
        return <ReportDownloadPage currentCase={selectedCase} />;
      case 'emergency-help':
        return <EmergencyHelpPage />;
      case 'admin-panel':
        return role === 'Admin' ? <AdminPanelPage /> : <Dashboard stats={stats} currentCase={selectedCase} userRole={role} />;
      default:
        return <Dashboard stats={stats} currentCase={selectedCase} userRole={role} />;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Navbar */}
      <Navbar 
        token={token} 
        username={username} 
        role={role} 
        cases={cases} 
        selectedCaseId={selectedCaseId} 
        onCaseChange={setSelectedCaseId} 
        onLogout={logout} 
        onNavigate={setActivePage} 
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        {token && (
          <Sidebar 
            activePage={activePage} 
            onNavigate={setActivePage} 
            userRole={role} 
          />
        )}

        {/* Content Panel */}
        <main className="flex-1 p-6 overflow-y-auto bg-slate-950/20">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

export default App;
