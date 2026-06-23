import React, { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  LineChart, Line
} from 'recharts';
import { Award, TrendingUp, TrendingDown, Users } from 'lucide-react';

export default function Analytics({ candidatesList }) {
  // Theme colors matching dark navy / cyan/blue accents
  const colors = {
    cyan: '#38BDF8',
    indigo: '#818CF8',
    purple: '#A78BFA',
    fuchsia: '#E879F9',
    blue: '#60A5FA',
    rose: '#FB7185'
  };

  const pieColors = [colors.cyan, colors.indigo, colors.purple, colors.fuchsia, colors.blue, colors.rose];

  // Calculate summary metrics dynamically
  const metrics = useMemo(() => {
    if (!candidatesList || candidatesList.length === 0) {
      return { total: 0, highest: 0, lowest: 0, average: 0 };
    }
    const scores = candidatesList.map(c => c.finalScore);
    const total = candidatesList.length;
    const highest = Math.max(...scores);
    const lowest = Math.min(...scores);
    const average = Math.round(scores.reduce((a, b) => a + b, 0) / total);

    return { total, highest, lowest, average };
  }, [candidatesList]);

  // Compute Score Distribution count (Bar Chart)
  const scoreDistribution = useMemo(() => {
    const counts = { "50-60": 0, "60-70": 0, "70-80": 0, "80-90": 0, "90-100": 0 };
    (candidatesList || []).forEach(c => {
      const score = c.finalScore;
      if (score >= 90) counts["90-100"]++;
      else if (score >= 80) counts["80-90"]++;
      else if (score >= 70) counts["70-80"]++;
      else if (score >= 60) counts["60-70"]++;
      else counts["50-60"]++;
    });
    return Object.entries(counts).map(([range, count]) => ({ range, count }));
  }, [candidatesList]);

  // Compute Top 6 Skills counts (Pie Chart)
  const topSkills = useMemo(() => {
    const counts = {};
    (candidatesList || []).forEach(c => {
      (c.skills || []).forEach(s => {
        counts[s] = (counts[s] || 0) + 1;
      });
    });
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6);
  }, [candidatesList]);

  // Top 3 Candidates names and criteria scores comparison (Radar Chart)
  const top3Names = useMemo(() => {
    const sorted = [...(candidatesList || [])].sort((a, b) => b.finalScore - a.finalScore);
    return sorted.slice(0, 3).map(c => c.name);
  }, [candidatesList]);

  const radarComparison = useMemo(() => {
    const sorted = [...(candidatesList || [])].sort((a, b) => b.finalScore - a.finalScore);
    const top3 = sorted.slice(0, 3);
    const criteriaKeys = ["skillMatch", "experience", "growth", "behavioral"];
    const criteriaLabels = {
      skillMatch: "Skill Match",
      experience: "Experience",
      growth: "Growth",
      behavioral: "Behavioral"
    };

    return criteriaKeys.map(crit => {
      const obj = { subject: criteriaLabels[crit] };
      top3.forEach(c => {
        obj[c.name] = c.scores?.[crit] || 0;
      });
      return obj;
    });
  }, [candidatesList]);

  // Ranking Trend score curve (Line Chart)
  const rankingTrend = useMemo(() => {
    const sorted = [...(candidatesList || [])].sort((a, b) => b.finalScore - a.finalScore);
    return sorted.map((c, idx) => ({
      rank: `R${idx + 1}`,
      name: c.name,
      score: c.finalScore
    }));
  }, [candidatesList]);

  // Custom tooltips matching dark SaaS styling
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#1E293B] border border-slate-700/80 p-3 rounded-xl shadow-xl">
          <p className="text-xs font-semibold text-slate-200 mb-1">{label || payload[0].name}</p>
          <div className="space-y-1">
            {payload.map((p, idx) => (
              <p key={idx} className="text-[11px] font-medium flex items-center gap-2" style={{ color: p.color || p.fill }}>
                <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: p.color || p.fill }}></span>
                {p.name}: {p.value}%
              </p>
            ))}
          </div>
        </div>
      );
    }
    return null;
  };

  const CustomPieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#1E293B] border border-slate-700/80 p-3 rounded-xl shadow-xl">
          <p className="text-xs font-semibold text-slate-200 mb-1">{data.name}</p>
          <p className="text-[11px] font-medium text-sky-400">
            Count: {data.value} Candidates
          </p>
        </div>
      );
    }
    return null;
  };

  if (!candidatesList || candidatesList.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500 bg-[#1E293B] border border-slate-800 rounded-2xl">
        No candidate analytics available. Please upload a candidates dataset first.
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Recruitment Analytics</h2>
        <p className="text-slate-400 text-sm">
          Visual insights of candidate pool distributions, skill breakdowns, and matcher engine trends.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Candidates */}
        <div className="bg-[#1E293B] border border-slate-800/85 rounded-2xl p-5 hover:border-slate-700/60 transition-all duration-300 flex items-center justify-between">
          <div>
            <span className="text-xs font-medium text-slate-400">Total Evaluated</span>
            <p className="text-2xl font-bold text-white mt-1">{metrics.total}</p>
          </div>
          <div className="p-3 bg-sky-500/10 border border-sky-400/20 text-sky-400 rounded-xl">
            <Users className="h-5 w-5" />
          </div>
        </div>

        {/* Average Match Score */}
        <div className="bg-[#1E293B] border border-slate-800/85 rounded-2xl p-5 hover:border-slate-700/60 transition-all duration-300 flex items-center justify-between">
          <div>
            <span className="text-xs font-medium text-slate-400">Average Match Score</span>
            <p className="text-2xl font-bold text-white mt-1">{metrics.average}%</p>
          </div>
          <div className="p-3 bg-indigo-500/10 border border-indigo-400/20 text-indigo-400 rounded-xl">
            <Award className="h-5 w-5" />
          </div>
        </div>

        {/* Highest Score */}
        <div className="bg-[#1E293B] border border-slate-800/85 rounded-2xl p-5 hover:border-slate-700/60 transition-all duration-300 flex items-center justify-between">
          <div>
            <span className="text-xs font-medium text-slate-400">Highest Score</span>
            <p className="text-2xl font-bold text-white mt-1">{metrics.highest}%</p>
          </div>
          <div className="p-3 bg-emerald-500/10 border border-emerald-400/20 text-emerald-400 rounded-xl">
            <TrendingUp className="h-5 w-5" />
          </div>
        </div>

        {/* Lowest Score */}
        <div className="bg-[#1E293B] border border-slate-800/85 rounded-2xl p-5 hover:border-slate-700/60 transition-all duration-300 flex items-center justify-between">
          <div>
            <span className="text-xs font-medium text-slate-400">Lowest Score</span>
            <p className="text-2xl font-bold text-white mt-1">{metrics.lowest}%</p>
          </div>
          <div className="p-3 bg-rose-500/10 border border-rose-400/20 text-rose-400 rounded-xl">
            <TrendingDown className="h-5 w-5" />
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart 1: Candidate Score Distribution (Bar Chart) */}
        <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-5 hover:border-slate-700/40 transition-all duration-300">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-5">
            Candidate Score Distribution
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={scoreDistribution} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis dataKey="range" stroke="#64748B" fontSize={10} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255, 255, 255, 0.03)' }} />
              <Bar name="Candidates Count" dataKey="count" fill={colors.cyan} radius={[4, 4, 0, 0]} barSize={25} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Chart 2: Top Skills Distribution (Pie Chart) */}
        <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-5 hover:border-slate-700/40 transition-all duration-300">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-5">
            Top Skills Distribution
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={topSkills}
                cx="50%"
                cy="45%"
                innerRadius={60}
                outerRadius={85}
                paddingAngle={4}
                dataKey="value"
              >
                {topSkills.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomPieTooltip />} />
              <Legend
                verticalAlign="bottom"
                height={36}
                iconSize={8}
                iconType="circle"
                wrapperStyle={{ fontSize: '10px', color: '#94A3B8' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Chart 3: Score Breakdown Comparison (Radar Chart) */}
        <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-5 hover:border-slate-700/40 transition-all duration-300">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-5">
            Top Candidates Criteria Comparison
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarComparison}>
              <PolarGrid stroke="#334155" opacity={0.4} />
              <PolarAngleAxis dataKey="subject" stroke="#94A3B8" fontSize={9} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#64748B" fontSize={8} />
              
              {/* Dynamically draw radar for top 3 candidates */}
              {top3Names.map((name, index) => {
                const radarColors = [colors.cyan, colors.indigo, colors.purple];
                return (
                  <Radar
                    key={name}
                    name={name}
                    dataKey={name}
                    stroke={radarColors[index % radarColors.length]}
                    fill={radarColors[index % radarColors.length]}
                    fillOpacity={0.12}
                  />
                );
              })}
              
              <Tooltip content={<CustomTooltip />} />
              <Legend iconSize={8} iconType="circle" wrapperStyle={{ fontSize: '10px' }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Chart 4: Candidate Ranking Trend (Line Chart) */}
        <div className="bg-[#1E293B] border border-slate-800 rounded-2xl p-5 hover:border-slate-700/40 transition-all duration-300">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-5">
            Score Curve (By Rank Position)
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={rankingTrend} margin={{ top: 10, right: 20, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis dataKey="rank" stroke="#64748B" fontSize={10} tickLine={false} />
              <YAxis domain={[50, 100]} stroke="#64748B" fontSize={10} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Line
                name="Final Score"
                type="monotone"
                dataKey="score"
                stroke={colors.cyan}
                strokeWidth={2}
                dot={{ fill: '#0F172A', stroke: colors.cyan, strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
