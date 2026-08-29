import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { LoanExplorer } from './pages/LoanExplorer';
import { LoanIntelligence } from './pages/LoanIntelligence';
import { Exceptions } from './pages/Exceptions';
import { Scenarios } from './pages/Scenarios';
import { Reviewer } from './pages/Reviewer';
import { ModelHealth } from './pages/ModelHealth';

function App() {
  return (
    <BrowserRouter>
      <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <main className="flex-1 bg-slate-900 overflow-hidden flex flex-col">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/loans" element={<LoanExplorer />} />
              <Route path="/loans/:loanId" element={<LoanIntelligence />} />
              <Route path="/exceptions" element={<Exceptions />} />
              <Route path="/scenarios" element={<Scenarios />} />
              <Route path="/reviewer" element={<Reviewer />} />
              <Route path="/model-health" element={<ModelHealth />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
