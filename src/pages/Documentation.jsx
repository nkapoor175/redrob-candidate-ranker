import React from 'react';
import { BookOpen, Cpu, Settings, ArrowDown, HelpCircle, Code2, Database } from 'lucide-react';

export default function Documentation() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto animate-fade-in pb-12">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">System Documentation</h2>
        <p className="text-slate-400 text-sm">
          Technical specifications, architecture details, and data-flow pipeline pipelines for the ranking system.
        </p>
      </div>

      {/* Project Overview */}
      <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6 space-y-3">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-sky-400" />
          Project Overview
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          The <strong>AI-Powered Candidate Ranking System</strong> is designed to solve the resume review bottleneck in high-volume recruiting.
          By using Semantic Text Similarity (via Sentence-Transformers) and Generative Large Language Models, the engine parses unstructured resumes
          and aligns them with candidate experience curves, skill weights, and growth directories, outputting normalized scores for rapid screening.
        </p>
      </div>

      {/* Visual System Architecture Diagram */}
      <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6 space-y-6">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Cpu className="h-4 w-4 text-sky-400" />
          System Architecture Flow
        </h3>

        {/* Diagram Area */}
        <div className="p-6 bg-slate-900/40 border border-slate-800/80 rounded-xl space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative">
            {/* Input Left: Job Description */}
            <div className="flex flex-col items-center space-y-3">
              <div className="w-full max-w-xs bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 text-center hover:border-sky-500/20 transition-all duration-200">
                <span className="text-[10px] uppercase font-bold text-sky-400">Input Source 1</span>
                <p className="text-xs font-bold text-slate-200 mt-1">Job Description (PDF/TXT)</p>
              </div>
              <ArrowDown className="h-4 w-4 text-slate-600" />
              <div className="w-full max-w-xs bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 text-center hover:border-sky-500/20 transition-all duration-200">
                <span className="text-[10px] uppercase font-bold text-slate-500">Pipeline Step</span>
                <p className="text-xs font-bold text-slate-200 mt-1">JD Parser & Keywords Extractor</p>
              </div>
            </div>

            {/* Input Right: Candidates Dataset */}
            <div className="flex flex-col items-center space-y-3">
              <div className="w-full max-w-xs bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 text-center hover:border-indigo-500/20 transition-all duration-200">
                <span className="text-[10px] uppercase font-bold text-indigo-400">Input Source 2</span>
                <p className="text-xs font-bold text-slate-200 mt-1">Candidate Resumes (JSON/CSV)</p>
              </div>
              <ArrowDown className="h-4 w-4 text-slate-600" />
              <div className="w-full max-w-xs bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 text-center hover:border-indigo-500/20 transition-all duration-200">
                <span className="text-[10px] uppercase font-bold text-slate-500">Pipeline Step</span>
                <p className="text-xs font-bold text-slate-200 mt-1">Resume Parser & Embeddings Mapper</p>
              </div>
            </div>
          </div>

          {/* Integration Bridge */}
          <div className="flex flex-col items-center py-2">
            <div className="h-8 w-px bg-slate-700" />
            <div className="w-full max-w-md bg-gradient-to-r from-sky-500/20 to-indigo-500/20 border border-sky-400/25 rounded-xl p-4.5 text-center glow-cyan">
              <span className="text-[10px] uppercase font-bold text-sky-300 tracking-wider">Matching Engine</span>
              <h4 className="text-xs font-bold text-slate-100 mt-1">Hybrid Semantic scoring Engine</h4>
              <p className="text-[10px] text-slate-400 mt-1 leading-normal">
                Aligns resume skills vectors and calculates Cosine-similarity scores based on experience relevance levels.
              </p>
            </div>
            <ArrowDown className="h-4 w-4 text-sky-500 mt-3" />
            <div className="w-full max-w-md bg-slate-800/80 border border-slate-700 rounded-xl p-4 text-center">
              <span className="text-[10px] uppercase font-bold text-amber-400">Contextual Refinement</span>
              <p className="text-xs font-bold text-slate-200 mt-1">LLM Zero-Shot Re-Ranker</p>
            </div>
            <ArrowDown className="h-4 w-4 text-slate-600 mt-3" />
            <div className="w-full max-w-md bg-emerald-500/10 border border-emerald-400/30 rounded-xl p-4 text-center">
              <span className="text-[10px] uppercase font-bold text-emerald-400">Output Stream</span>
              <p className="text-xs font-bold text-slate-200 mt-1">Recruiter Dashboard Ranked Queue</p>
            </div>
          </div>
        </div>
      </div>

      {/* Technical Workflow Details */}
      <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Settings className="h-4 w-4 text-sky-400" />
          Technical Execution Stages
        </h3>

        <div className="space-y-4 text-xs">
          {/* Stage 1 */}
          <div className="flex gap-4 items-start">
            <div className="px-2 py-1 bg-slate-900 border border-slate-800 text-sky-400 rounded-md font-bold shrink-0">
              01
            </div>
            <div className="space-y-1">
              <h4 className="font-semibold text-slate-200">Requirements Extraction</h4>
              <p className="text-slate-400 leading-relaxed">
                Extracts absolute criteria (e.g., degree requirements, core programming languages, years of senior experience) from the job description to form the evaluation weights.
              </p>
            </div>
          </div>

          {/* Stage 2 */}
          <div className="flex gap-4 items-start">
            <div className="px-2 py-1 bg-slate-900 border border-slate-800 text-sky-400 rounded-md font-bold shrink-0">
              02
            </div>
            <div className="space-y-1">
              <h4 className="font-semibold text-slate-200">Semantic Embeddings & Indexing</h4>
              <p className="text-slate-400 leading-relaxed">
                Resumes are parsed and sentence embeddings are generated using pre-trained semantic transformers. This allows the system to recognize synonyms (e.g., matching "Deep Learning" to "Neural Networks").
              </p>
            </div>
          </div>

          {/* Stage 3 */}
          <div className="flex gap-4 items-start">
            <div className="px-2 py-1 bg-slate-900 border border-slate-800 text-sky-400 rounded-md font-bold shrink-0">
              03
            </div>
            <div className="space-y-1">
              <h4 className="font-semibold text-slate-200">LLM Reranking Verification</h4>
              <p className="text-slate-400 leading-relaxed">
                Top matching profiles are sent to a Large Language Model to evaluate subtle context, project quality, and career progression trends to formulate final qualitative scores.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
