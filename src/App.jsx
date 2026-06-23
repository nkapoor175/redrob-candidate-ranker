import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Rankings from './pages/Rankings';
import CandidateDetails from './pages/CandidateDetails';
import Analytics from './pages/Analytics';
import Documentation from './pages/Documentation';
import { candidates } from './data/mockCandidates';

function App() {
  const [candidatesList, setCandidatesList] = useState(candidates);
  const [jobDescriptionText, setJobDescriptionText] = useState("");

  return (
    <Router>
      <div className="flex h-screen bg-[#0F172A] text-slate-100 overflow-hidden">
        {/* Sidebar Navigation */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Top Header Navbar */}
          <Navbar />

          {/* Dynamic Page Routing Body */}
          <main className="flex-1 overflow-y-auto px-8 py-6">
            <Routes>
              <Route 
                path="/" 
                element={
                  <Dashboard 
                    candidatesList={candidatesList} 
                    setCandidatesList={setCandidatesList} 
                    jobDescriptionText={jobDescriptionText}
                    setJobDescriptionText={setJobDescriptionText}
                  />
                } 
              />
              <Route 
                path="/rankings" 
                element={<Rankings candidatesList={candidatesList} />} 
              />
              <Route 
                path="/candidate" 
                element={<CandidateDetails candidatesList={candidatesList} />} 
              />
              <Route 
                path="/candidate/:id" 
                element={<CandidateDetails candidatesList={candidatesList} />} 
              />
              <Route 
                path="/analytics" 
                element={<Analytics candidatesList={candidatesList} />} 
              />
              <Route path="/documentation" element={<Documentation />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
