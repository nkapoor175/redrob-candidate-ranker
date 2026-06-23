import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Award, Brain, Briefcase, Code, ChevronLeft, MessageSquareQuote } from 'lucide-react';

export default function CandidateDetails({ candidatesList }) {
  const { id } = useParams();
  const navigate = useNavigate();

  // Find candidate by ID. Default to the top candidate (id "1") if no ID or invalid ID is provided.
  const activeCandidate = (candidatesList || []).find(c => c.id === id) || (candidatesList || [])[0];

  if (!activeCandidate) {
    return (
      <div className="text-center py-12 text-slate-500 bg-[#1E293B] border border-slate-800 rounded-2xl">
        No candidate profiles loaded. Please upload a candidates dataset first.
      </div>
    );
  }

  const handleCandidateChange = (newId) => {
    navigate(`/candidate/${newId}`);
  };

  // Helper for progress bar color mapping
  const getProgressBarColor = (key) => {
    switch (key) {
      case 'skillMatch': return 'bg-sky-400';
      case 'experience': return 'bg-indigo-400';
      case 'growth': return 'bg-purple-400';
      case 'behavioral': return 'bg-pink-400';
      default: return 'bg-slate-400';
    }
  };

  // Helper to map score keys to human readable labels
  const getScoreLabel = (key) => {
    switch (key) {
      case 'skillMatch': return 'Skill Match';
      case 'experience': return 'Experience Relevance';
      case 'growth': return 'Growth Index';
      case 'behavioral': return 'Behavioral Score';
      default: return key;
    }
  };

  // Score badge styling color
  const getScoreColor = (score) => {
    if (score >= 90) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (score >= 80) return 'text-sky-400 border-sky-500/30 bg-sky-500/10';
    if (score >= 70) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top back & switcher navigation row */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <button
          onClick={() => navigate('/rankings')}
          className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to Rankings
        </button>

        {/* Quick Profile Switcher */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500 font-medium">Select Candidate:</span>
          <select
            value={activeCandidate?.id || ""}
            onChange={(e) => handleCandidateChange(e.target.value)}
            className="bg-[#1E293B] border border-slate-800 focus:border-sky-500/50 rounded-xl px-3 py-1.5 text-xs text-slate-300 outline-none cursor-pointer transition-all duration-200"
          >
            {(candidatesList || []).map((c) => (
              <option key={c.id} value={c.id}>
                Rank {c.rank}: {c.name} ({c.finalScore}%)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Grid: Left is Profile / Right is Evaluation details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Profile Card & Skills */}
        <div className="lg:col-span-1 space-y-6">
          {/* Candidate Profile Summary */}
          <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
            {/* Top background accent */}
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-sky-400 to-indigo-500" />
            
            <div className="flex flex-col items-center text-center space-y-4 pt-2">
              {/* Avatar circle */}
              <div className="h-20 w-20 rounded-full bg-slate-800 border border-slate-700/60 flex items-center justify-center text-3xl font-bold text-sky-400">
                {activeCandidate.name.split(' ').map(n => n[0]).join('')}
              </div>

              {/* Text metadata */}
              <div>
                <h3 className="text-lg font-bold text-white flex items-center justify-center gap-1.5">
                  {activeCandidate.name}
                </h3>
                <p className="text-xs text-slate-400 font-medium mt-1">{activeCandidate.role}</p>
                <div className="flex justify-center gap-4 mt-3 text-[11px] text-slate-500 font-semibold">
                  <span className="px-2 py-0.5 bg-slate-800 border border-slate-800 rounded-md">
                    {activeCandidate.experienceYears} Years Exp
                  </span>
                  <span className="px-2 py-0.5 bg-slate-800 border border-slate-800 rounded-md">
                    Rank #{activeCandidate.rank}
                  </span>
                </div>
              </div>

              {/* Overall Score Meter */}
              <div className="w-full pt-4 border-t border-slate-800/80">
                <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                  <span>Match Confidence</span>
                  <span className="font-semibold text-slate-200">{activeCandidate.finalScore}%</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden p-[1px]">
                  <div
                    style={{ width: `${activeCandidate.finalScore}%` }}
                    className="h-full bg-gradient-to-r from-sky-400 to-indigo-500 rounded-full"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Skills Tag Section */}
          <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Code className="h-4 w-4 text-sky-400" />
              Extracted Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {activeCandidate.skills.map((skill) => (
                <span
                  key={skill}
                  className="px-2.5 py-1 rounded-xl bg-slate-900/60 border border-slate-800/80 text-[11px] font-semibold text-slate-300 hover:text-sky-400 hover:border-sky-500/20 transition-all duration-200"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Breakdown Scores, Reasoning, Projects */}
        <div className="lg:col-span-2 space-y-6">
          {/* Evaluator Reasoning Explanation */}
          <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-5">
              <MessageSquareQuote className="h-32 w-32" />
            </div>
            
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Brain className="h-4 w-4 text-sky-400" />
              AI Evaluation & Reasoning
            </h4>
            
            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4.5">
              <p className="text-sm font-medium text-slate-200 leading-relaxed italic">
                "{activeCandidate.reasoning}"
              </p>
            </div>
          </div>

          {/* Score breakdowns progress bars */}
          <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-5 flex items-center gap-2">
              <Award className="h-4 w-4 text-sky-400" />
              Detailed Criteria Breakdown
            </h4>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {Object.entries(activeCandidate.scores).map(([key, score]) => (
                <div key={key} className="space-y-2">
                  <div className="flex justify-between items-baseline text-xs">
                    <span className="font-semibold text-slate-300">{getScoreLabel(key)}</span>
                    <span className={`font-bold ${getScoreColor(score)}`}>{score}%</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden p-[0.5px]">
                    <div
                      style={{ width: `${score}%` }}
                      className={`h-full rounded-full ${getProgressBarColor(key)}`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Candidate Projects */}
          <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Briefcase className="h-4 w-4 text-sky-400" />
              Key Project Portfolio
            </h4>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {activeCandidate.projects.map((proj, idx) => (
                <div
                  key={idx}
                  className="bg-slate-900/30 hover:bg-slate-900/60 border border-slate-800/80 hover:border-slate-800 rounded-xl p-4.5 transition-all duration-200"
                >
                  <h5 className="font-semibold text-slate-200 text-xs mb-2 flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-sky-400"></span>
                    {proj.title}
                  </h5>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    {proj.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
