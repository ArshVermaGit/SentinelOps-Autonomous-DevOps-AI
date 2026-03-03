"use client"
import PageHeader from "@/components/layout/PageHeader"
import MetricCard from "@/components/dashboard/MetricCard"
import CIHealthChart from "@/components/dashboard/CIHealthChart"
import RiskHeatmap from "@/components/dashboard/RiskHeatmap"
import LiveActivityFeed from "@/components/dashboard/LiveActivityFeed"
import RiskExplainer from "@/components/dashboard/RiskExplainer"
import LocalSandbox from "@/components/dashboard/LocalSandbox"
import { useDashboard } from "@/hooks/useDashboard"
import { AlertTriangle, CheckCircle, GitPullRequest, Zap, Activity, ShieldCheck, Cpu } from "lucide-react"
import { motion } from "framer-motion"

export default function DashboardPage() {
  const { data } = useDashboard()
  
  return (
    <div className="space-y-6">
      <PageHeader
        title="Engineering Overview"
        subtitle="Real-time health monitoring across my repos and pipelines"
        badge="LIVE"
      />

      {/* Resilience Score Hero */}
      <div className="relative group">
        <div className="absolute inset-0 bg-linear-to-r from-indigo-500/10 via-emerald-500/10 to-indigo-500/10 blur-3xl opacity-50 transition-opacity group-hover:opacity-70" />
        <div className="glass shadow-2xl rounded-3xl p-8 border border-white/10 relative overflow-hidden">
          <div className="absolute -top-24 -right-24 w-64 h-64 bg-emerald-500/10 blur-[100px] rounded-full" />
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-4 max-w-lg">
              <div className="flex items-center gap-2">
                <div className="px-2 py-1 bg-emerald-500/20 rounded border border-emerald-500/30 text-[10px] font-bold text-emerald-400 tracking-widest uppercase">
                  Excellent Stability
                </div>
                <div className="text-[10px] text-gray-500 font-medium">Updated 30s ago</div>
              </div>
              <h2 className="text-3xl font-bold text-white tracking-tight">System Health Score</h2>
              <p className="text-sm text-gray-400 leading-relaxed">
                The infra looks <span className="text-emerald-400 font-bold">solid</span> right now. 
                Everything is stable even with the recent spike in PR activity.
              </p>
              <div className="flex items-center gap-6 pt-2">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs text-gray-300">Security: Stable</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-indigo-400" />
                  <span className="text-xs text-gray-300">Throughput: High</span>
                </div>
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-amber-400" />
                  <span className="text-xs text-gray-300">AI Trust: 98%</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <svg className="w-40 h-40 transform -rotate-90">
                <circle cx="80" cy="80" r="70" className="stroke-white/5" strokeWidth="12" fill="none" />
                <motion.circle 
                  cx="80" cy="80" r="70" 
                  className="stroke-emerald-500" 
                  strokeWidth="12" 
                  fill="none" 
                  strokeDasharray="440"
                  initial={{ strokeDashoffset: 440 }}
                  animate={{ strokeDashoffset: 440 - (440 * (data?.pulse?.pulse_score ?? 92) / 100) }}
                  transition={{ duration: 2, ease: "circOut" }}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-bold text-white tracking-tighter">{data?.pulse?.pulse_score ?? 92}</span>
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Score</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="CI Success Rate"
          value={`${data?.ci.success_rate ?? "—"}%`}
          change="+2.3% vs last week"
          changeType="positive"
          icon={CheckCircle}
          color="emerald"
        />
        <MetricCard
          label="Open Incidents"
          value={data?.incidents.open ?? "—"}
          change="3 high severity"
          changeType="negative"
          icon={AlertTriangle}
          color="red"
        />
        <MetricCard
          label="Risky PRs"
          value={data?.repos.high_risk ?? "—"}
          change="Awaiting review"
          changeType="neutral"
          icon={GitPullRequest}
          color="amber"
        />
        <MetricCard
          label="Avg Build Time"
          value={data ? `${Math.round((data.ci.avg_build_time_ms / 1000) / 60)}m` : "—"}
          change="+18s anomaly detected"
          changeType="negative"
          icon={Zap}
          color="indigo"
        />
      </div>
      
      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* CI Health Chart - wide */}
        <div className="lg:col-span-2">
          <CIHealthChart />
        </div>
        {/* Live Activity Feed */}
        <div className="col-span-1">
          <LiveActivityFeed />
        </div>
      </div>
      
      {/* Bottom row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-white text-sm">
        <RiskHeatmap repos={data?.repos_list ?? []} />
        <RiskExplainer drivers={data?.repos_list?.[0]?.risk_drivers ?? [
          { feature: "Lines Changed (+)", impact: 0.25 },
          { feature: "Author History (+)", impact: 0.18 },
          { feature: "Complexity (+)", impact: 0.12 },
          { feature: "Dependencies (+)", impact: 0.08 },
          { feature: "Test Coverage (-)", impact: -0.10 }
        ]} />
        <LocalSandbox />
      </div>
    </div>
  )
}
