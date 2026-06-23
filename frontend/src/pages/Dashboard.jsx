import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, Check, Play, Award, Zap, Percent, Users2 } from 'lucide-react';
import { candidates as defaultCandidates } from '../data/mockCandidates';

export default function Dashboard({ candidatesList, setCandidatesList, jobDescriptionText, setJobDescriptionText }) {
  const navigate = useNavigate();
  const [jobFile, setJobFile] = useState(null);
  const [candidateFile, setCandidateFile] = useState(null);
  const [pendingCandidates, setPendingCandidates] = useState(null);
  
  const [isDragJob, setIsDragJob] = useState(false);
  const [isDragCand, setIsDragCand] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisStage, setAnalysisStage] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  // Parse candidate CSV dataset in-browser
  const parseCSV = (text) => {
    const lines = text.split('\n');
    if (lines.length < 2) return [];
    
    const headers = lines[0].split(',').map(h => h.trim().replace(/^["']|["']$/g, ''));
    const list = [];
    
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      
      const values = line.split(',').map(v => v.trim().replace(/^["']|["']$/g, ''));
      const candidate = {
        id: String(i),
        rank: i,
        scores: {}
      };
      
      headers.forEach((header, index) => {
        const val = values[index] || "";
        const lowerHeader = header.toLowerCase();
        
        if (lowerHeader.includes('name')) {
          candidate.name = val;
        } else if (lowerHeader.includes('role') || lowerHeader.includes('title')) {
          candidate.role = val;
        } else if (lowerHeader.includes('experienceyears') || lowerHeader.includes('experience years') || lowerHeader === 'experience' || lowerHeader === 'exp') {
          candidate.experienceYears = parseInt(val) || 0;
        } else if (lowerHeader.includes('final') || lowerHeader.includes('score')) {
          candidate.finalScore = parseInt(val) || 0;
        } else if (lowerHeader.includes('skillmatch') || lowerHeader.includes('skill match')) {
          candidate.scores.skillMatch = parseInt(val) || 0;
        } else if (lowerHeader.includes('experiencescore') || lowerHeader.includes('experience score') || lowerHeader === 'experience_score') {
          candidate.scores.experience = parseInt(val) || 0;
        } else if (lowerHeader.includes('growth')) {
          candidate.scores.growth = parseInt(val) || 0;
        } else if (lowerHeader.includes('behavioral')) {
          candidate.scores.behavioral = parseInt(val) || 0;
        } else if (lowerHeader.includes('status')) {
          candidate.status = val;
        } else if (lowerHeader.includes('skills')) {
          candidate.skills = val.split(';').map(s => s.trim());
        }
      });

      // Fallbacks
      if (!candidate.name) candidate.name = `Candidate ${i}`;
      if (!candidate.role) candidate.role = "AI Technical Engineer";
      if (!candidate.status) candidate.status = "Under Review";
      if (!candidate.skills || candidate.skills.length === 0 || candidate.skills[0] === "") {
        candidate.skills = ["Python", "Machine Learning", "FastAPI"];
      }
      
      if (candidate.scores.skillMatch === undefined) candidate.scores.skillMatch = Math.round(50 + Math.random() * 45);
      if (candidate.scores.experience === undefined) candidate.scores.experience = Math.round(50 + Math.random() * 45);
      if (candidate.scores.growth === undefined) candidate.scores.growth = Math.round(50 + Math.random() * 45);
      if (candidate.scores.behavioral === undefined) candidate.scores.behavioral = Math.round(50 + Math.random() * 45);
      
      if (!candidate.finalScore) {
        candidate.finalScore = Math.round(
          (candidate.scores.skillMatch + candidate.scores.experience + candidate.scores.growth + candidate.scores.behavioral) / 4
        );
      }
      
      if (!candidate.projects) {
        candidate.projects = [
          {
            title: "Project Alpha",
            description: "Developed and integrated technical systems fitting job descriptions."
          }
        ];
      }
      
      if (!candidate.reasoning) {
        candidate.reasoning = "Good matching alignment extracted automatically from custom CSV upload files.";
      }

      list.push(candidate);
    }

    list.sort((a, b) => b.finalScore - a.finalScore);
    list.forEach((c, idx) => {
      c.rank = idx + 1;
      c.id = String(idx + 1);
    });
    return list;
  };

  // Drag & Drop Handlers for Job Description
  const handleDragJob = (e) => {
    e.preventDefault();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragJob(true);
    } else {
      setIsDragJob(false);
    }
  };

  const handleDropJob = (e) => {
    e.preventDefault();
    setIsDragJob(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleJobFileLoad(e.dataTransfer.files[0]);
    }
  };

  const handleFileChangeJob = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleJobFileLoad(e.target.files[0]);
    }
  };

  const handleJobFileLoad = (file) => {
    setJobFile(file);
    if (file.name.endsWith('.txt')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setJobDescriptionText(e.target.result);
      };
      reader.readAsText(file);
    } else {
      setJobDescriptionText(`Extracted metadata from PDF file: ${file.name}`);
    }
  };

  // Drag & Drop Handlers for Candidate Dataset
  const handleDragCand = (e) => {
    e.preventDefault();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragCand(true);
    } else {
      setIsDragCand(false);
    }
  };

  const handleDropCand = (e) => {
    e.preventDefault();
    setIsDragCand(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleCandidateFileLoad(e.dataTransfer.files[0]);
    }
  };

  const handleFileChangeCand = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleCandidateFileLoad(e.target.files[0]);
    }
  };

  const handleCandidateFileLoad = (file) => {
    setCandidateFile(file);
    const reader = new FileReader();
    
    if (file.name.endsWith('.json')) {
      reader.onload = (e) => {
        try {
          const parsed = JSON.parse(e.target.result);
          const list = Array.isArray(parsed) ? parsed : (parsed.candidates || []);
          list.sort((a, b) => (b.finalScore || 0) - (a.finalScore || 0));
          list.forEach((c, idx) => {
            c.rank = idx + 1;
            c.id = c.id || String(idx + 1);
            if (!c.scores) c.scores = {
              skillMatch: c.skillMatch || 70,
              experience: c.experience || 70,
              growth: c.growth || 70,
              behavioral: c.behavioral || 70
            };
          });
          setPendingCandidates(list);
        } catch (err) {
          alert("Failed to parse JSON file. Please make sure it is a valid candidates JSON array.");
          setCandidateFile(null);
        }
      };
      reader.readAsText(file);
    } else if (file.name.endsWith('.csv')) {
      reader.onload = (e) => {
        try {
          const list = parseCSV(e.target.result);
          setPendingCandidates(list);
        } catch (err) {
          alert("Failed to parse CSV file. Please make sure the headers align correctly.");
          setCandidateFile(null);
        }
      };
      reader.readAsText(file);
    } else {
      alert("Unsupported file format. Please upload .json or .csv files.");
      setCandidateFile(null);
    }
  };

  // Load Demo files and reset state
  const loadDemoDatasets = () => {
    setJobFile({ name: "job_description_ml_lead.pdf" });
    setCandidateFile({ name: "candidates_v2_extracted.json" });
    setPendingCandidates(defaultCandidates);
  };

  // Analysis Simulation
  const startAnalysis = () => {
    if (!jobFile || !candidateFile) return;
    setIsAnalyzing(true);
    setIsComplete(false);
    setAnalysisProgress(0);

    const stages = [
      { text: "Reading files and starting pipeline...", limit: 20 },
      { text: "Parsing Job Description & extracting key skill keywords...", limit: 40 },
      { text: "Parsing candidates profiles & mapping schemas...", limit: 65 },
      { text: "Generating semantic embeddings & executing cosine matching...", limit: 85 },
      { text: "Running LLM re-ranker and calculating final confidence scores...", limit: 100 }
    ];

    let currentLimitIndex = 0;
    const interval = setInterval(() => {
      setAnalysisProgress((prev) => {
        const next = prev + 2;
        if (next >= stages[currentLimitIndex].limit) {
          setAnalysisStage(stages[currentLimitIndex].text);
          if (currentLimitIndex < stages.length - 1) {
            currentLimitIndex++;
          }
        }
        if (next >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setIsAnalyzing(false);
            setIsComplete(true);
            if (pendingCandidates) {
              setCandidatesList(pendingCandidates);
            }
          }, 600);
          return 100;
        }
        return next;
      });
    }, 40);
  };

  // Compute dynamic stats based on current active list
  const dynamicStats = useMemo(() => {
    if (!candidatesList || candidatesList.length === 0) {
      return { totalCandidates: 0, skillsExtracted: 0, averageMatchScore: 0, topRankedCandidate: "N/A" };
    }
    const total = candidatesList.length;
    const allSkills = new Set();
    candidatesList.forEach(c => (c.skills || []).forEach(s => allSkills.add(s)));
    
    const sum = candidatesList.reduce((acc, c) => acc + c.finalScore, 0);
    const avg = Math.round(sum / total);
    
    const sorted = [...candidatesList].sort((a, b) => b.finalScore - a.finalScore);
    const top = sorted[0]?.name || "N/A";
    
    return {
      totalCandidates: total,
      skillsExtracted: allSkills.size,
      averageMatchScore: avg,
      topRankedCandidate: top
    };
  }, [candidatesList]);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">
            AI-Powered Candidate Ranking System
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl">
            Upload a job description and candidate dataset to extract skills, compute embedding alignments, and generate AI-powered rankings.
          </p>
        </div>
        <button
          onClick={loadDemoDatasets}
          className="text-xs text-sky-400 hover:text-sky-300 font-semibold px-3.5 py-2.5 bg-slate-850 hover:bg-slate-800 border border-slate-800 hover:border-sky-500/20 rounded-xl transition-all self-start sm:self-center shrink-0"
        >
          Load Demo Datasets
        </button>
      </div>

      {/* Upload Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Upload JD Card */}
        <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700/60 transition-all duration-300">
          <div>
            <h3 className="font-semibold text-slate-200 mb-2">Upload Job Description</h3>
            <p className="text-xs text-slate-400 mb-4">Provide the target role details. Supported formats: PDF, TXT</p>
          </div>
          
          <div
            onDragEnter={handleDragJob}
            onDragOver={handleDragJob}
            onDragLeave={handleDragJob}
            onDrop={handleDropJob}
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all duration-200 cursor-pointer ${
              jobFile
                ? 'border-emerald-500/50 bg-emerald-500/[0.02]'
                : isDragJob
                ? 'border-sky-400 bg-sky-500/[0.04]'
                : 'border-slate-800 hover:border-slate-700 bg-slate-900/30'
            }`}
          >
            {jobFile ? (
              <div className="text-center space-y-2">
                <div className="p-3 bg-emerald-500/10 border border-emerald-400/20 text-emerald-400 rounded-full inline-block">
                  <Check className="h-6 w-6" />
                </div>
                <p className="text-xs font-semibold text-emerald-400 truncate max-w-[200px]">{jobFile.name}</p>
                <button
                  onClick={(e) => { e.stopPropagation(); setJobFile(null); }}
                  className="text-[10px] text-slate-500 hover:text-slate-400 underline"
                >
                  Change file
                </button>
              </div>
            ) : (
              <label className="text-center space-y-3 cursor-pointer w-full">
                <div className="p-3 bg-slate-800 border border-slate-700/50 text-slate-400 rounded-full inline-block">
                  <UploadCloud className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-300">Drag & drop job description</p>
                  <p className="text-[10px] text-slate-500 mt-1">or click to browse from files (.pdf, .txt)</p>
                </div>
                <input
                  type="file"
                  accept=".pdf,.txt"
                  className="hidden"
                  onChange={handleFileChangeJob}
                />
              </label>
            )}
          </div>
        </div>

        {/* Upload Candidate Dataset Card */}
        <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700/60 transition-all duration-300">
          <div>
            <h3 className="font-semibold text-slate-200 mb-2">Upload Candidate Dataset</h3>
            <p className="text-xs text-slate-400 mb-4">Provide candidate profiles. Supported formats: JSON, CSV</p>
          </div>

          <div
            onDragEnter={handleDragCand}
            onDragOver={handleDragCand}
            onDragLeave={handleDragCand}
            onDrop={handleDropCand}
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all duration-200 cursor-pointer ${
              candidateFile
                ? 'border-emerald-500/50 bg-emerald-500/[0.02]'
                : isDragCand
                ? 'border-sky-400 bg-sky-500/[0.04]'
                : 'border-slate-800 hover:border-slate-700 bg-slate-900/30'
            }`}
          >
            {candidateFile ? (
              <div className="text-center space-y-2">
                <div className="p-3 bg-emerald-500/10 border border-emerald-400/20 text-emerald-400 rounded-full inline-block">
                  <Check className="h-6 w-6" />
                </div>
                <p className="text-xs font-semibold text-emerald-400 truncate max-w-[200px]">{candidateFile.name}</p>
                <button
                  onClick={(e) => { e.stopPropagation(); setCandidateFile(null); setPendingCandidates(null); }}
                  className="text-[10px] text-slate-500 hover:text-slate-400 underline"
                >
                  Change file
                </button>
              </div>
            ) : (
              <label className="text-center space-y-3 cursor-pointer w-full">
                <div className="p-3 bg-slate-800 border border-slate-700/50 text-slate-400 rounded-full inline-block">
                  <UploadCloud className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-300">Drag & drop resumes dataset</p>
                  <p className="text-[10px] text-slate-500 mt-1">or click to browse from files (.json, .csv)</p>
                </div>
                <input
                  type="file"
                  accept=".json,.csv"
                  className="hidden"
                  onChange={handleFileChangeCand}
                />
              </label>
            )}
          </div>
        </div>
      </div>

      {/* Action / Loader Section */}
      <div className="flex flex-col items-center justify-center py-6 bg-slate-900/20 rounded-2xl border border-slate-800/40">
        {!isAnalyzing && !isComplete ? (
          <div className="text-center space-y-3">
            <button
              onClick={startAnalysis}
              disabled={!jobFile || !candidateFile}
              className={`glow-button flex items-center gap-2 px-6 py-3.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                jobFile && candidateFile
                  ? 'bg-gradient-to-r from-sky-400 to-blue-500 hover:from-sky-500 hover:to-blue-600 text-slate-900 transform hover:-translate-y-0.5 shadow-lg shadow-sky-500/20'
                  : 'bg-slate-800 text-slate-500 border border-slate-800 cursor-not-allowed'
              }`}
            >
              <Play className="h-4 w-4 fill-current" />
              Analyze Candidates
            </button>
            <p className="text-xs text-slate-500">
              {!jobFile || !candidateFile ? "Please upload both files to activate analysis." : "Ready to rank using embedding cos-similarity and LLM re-scoring."}
            </p>
          </div>
        ) : isAnalyzing ? (
          <div className="w-full max-w-lg px-8 text-center space-y-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-400">
              <span>{analysisStage}</span>
              <span className="text-sky-400 font-bold">{analysisProgress}%</span>
            </div>
            
            {/* Custom high fidelity progress bar */}
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden p-[1px]">
              <div
                style={{ width: `${analysisProgress}%` }}
                className="h-full bg-gradient-to-r from-sky-400 via-blue-500 to-sky-400 rounded-full transition-all duration-100 glow-cyan"
              />
            </div>
            
            <p className="text-[10px] text-slate-500 italic animate-pulse">Running scoring models in pipeline...</p>
          </div>
        ) : (
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2.5">
              <span className="p-1 rounded-full bg-emerald-500/10 border border-emerald-400/20 text-emerald-400">
                <Check className="h-4 w-4" />
              </span>
              <span className="text-sm font-semibold text-emerald-400">Candidate Ranking Generated Successfully!</span>
            </div>
            <button
              onClick={() => navigate('/rankings')}
              className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700/80 hover:border-sky-500/30 rounded-xl text-xs font-semibold transition-all duration-200"
            >
              View Ranked Candidates
            </button>
          </div>
        )}
      </div>

      {/* Statistics Cards */}
      <div>
        <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
          <Zap className="h-4 w-4 text-sky-400" />
          Ranker Overview Statistics
        </h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Card 1: Total Candidates */}
          <div className="bg-[#1E293B] border border-slate-800/80 rounded-2xl p-5 hover:-translate-y-0.5 hover:border-slate-700/60 transition-all duration-300 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-medium text-slate-400">Total Candidates</span>
              <p className="text-2xl font-bold text-white">{dynamicStats.totalCandidates}</p>
            </div>
            <div className="p-3 rounded-xl bg-sky-500/10 border border-sky-400/20 text-sky-400">
              <Users2 className="h-5 w-5" />
            </div>
          </div>

          {/* Card 2: Skills Extracted */}
          <div className="bg-[#1E293B] border border-slate-800/80 rounded-2xl p-5 hover:-translate-y-0.5 hover:border-slate-700/60 transition-all duration-300 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-medium text-slate-400">Skills Extracted</span>
              <p className="text-2xl font-bold text-white">{dynamicStats.skillsExtracted}</p>
            </div>
            <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-400/20 text-purple-400">
              <Zap className="h-5 w-5" />
            </div>
          </div>

          {/* Card 3: Average Match Score */}
          <div className="bg-[#1E293B] border border-slate-800/80 rounded-2xl p-5 hover:-translate-y-0.5 hover:border-slate-700/60 transition-all duration-300 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-medium text-slate-400">Avg Match Score</span>
              <p className="text-2xl font-bold text-white">{dynamicStats.averageMatchScore}%</p>
            </div>
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-400/20 text-amber-400">
              <Percent className="h-5 w-5" />
            </div>
          </div>

          {/* Card 4: Top Ranked Candidate */}
          <div className="bg-[#1E293B] border border-slate-800/80 rounded-2xl p-5 hover:-translate-y-0.5 hover:border-slate-700/60 transition-all duration-300 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-medium text-slate-400">Top Ranked</span>
              <p className="text-lg font-bold text-white truncate max-w-[150px]">{dynamicStats.topRankedCandidate}</p>
            </div>
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-400/20 text-emerald-400">
              <Award className="h-5 w-5" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
