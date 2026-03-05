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
  const { data, loading } = useDashboard()
  
  return (
    <div className="space-y-6">
      <PageHeader
        title="Engineering Overview"
        subtitle="Real-time health monitoring across my repos and pipelines"
        badge="LIVE"
      />
      
      {loading && (
        <div className="flex items-center justify-center p-20 glass rounded-3xl animate-pulse">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
            <p className="text-gray-500 font-medium tracking-widest text-[10px] uppercase">Integrating Real-World Data...</p>
          </div>
        </div>
      )}

      {/* Resilience Score Hero */}
      <div className="relative group">
        <div className="absolute inset-0 bg-linear-to-r from-indigo-500/10 via-emerald-500/10 to-indigo-500/10 blur-3xl opacity-50 transition-opacity group-hover:opacity-70" />
        <div className="glass shadow-2xl rounded-3xl p-8 border border-white/10 relative overflow-hidden">
          <div className="absolute -top-24 -right-24 w-64 h-64 bg-emerald-500/10 blur-[100px] rounded-full" />
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-4 max-w-lg">
              <div className="flex items-center gap-2">
                <div className={`px-2 py-1 ${data?.pulse?.status === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'} rounded border text-[10px] font-bold tracking-widest uppercase`}>
                  {data?.pulse?.status ?? "Initializing Sync..."}
                </div>
                {data?.pulse?.last_updated && (
                  <div className="text-[10px] text-gray-500 font-medium whitespace-nowrap">Updated just now</div>
                )}
              </div>
              <h2 className="text-3xl font-bold text-white tracking-tight">System Health Pulse</h2>
              <p className="text-sm text-gray-400 leading-relaxed">
                {!data?.pulse ? (
                  "Scanning your linked repositories for real-world risk and stability metrics..."
                ) : data.pulse.pulse_score > 85 ? (
                  <>The infrastructure is <span className="text-emerald-400 font-bold">solid</span>. Stability metrics exceed targets with current PR activity.</>
                ) : data.pulse.pulse_score > 65 ? (
                  <>System is <span className="text-indigo-400 font-bold">stable</span>. Some cautious patterns detected in recent local code changes.</>
                ) : (
                  <>System at <span className="text-red-400 font-bold">risk</span>. Critical health issues detected in recent CI runs or PR analysis.</>
                )}
              </p>
              <div className="flex items-center gap-6 pt-2">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs text-gray-300">Stability: {data?.pulse?.metrics.stability ?? "—"}%</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-indigo-400" />
                  <span className="text-xs text-gray-300">Recovery: {data?.pulse?.metrics.recovery ?? "—"}%</span>
                </div>
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-amber-400" />
                  <span className="text-xs text-gray-300">Risk Control: {data?.pulse?.metrics.risk_control ?? "—"}%</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <svg className="w-40 h-40 transform -rotate-90">
                <circle cx="80" cy="80" r="70" className="stroke-white/5" strokeWidth="12" fill="none" />
                <motion.circle 
                  cx="80" cy="80" r="70" 
                  className={data?.pulse?.pulse_score && data.pulse.pulse_score < 65 ? "stroke-red-500" : "stroke-emerald-500"} 
                  strokeWidth="12" 
                  fill="none" 
                  strokeDasharray="440"
                  initial={{ strokeDashoffset: 440 }}
                  animate={{ strokeDashoffset: 440 - (440 * (data?.pulse?.pulse_score ?? 0) / 100) }}
                  transition={{ duration: 2, ease: "circOut" }}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-bold text-white tracking-tighter">{data?.pulse?.pulse_score ?? "—"}</span>
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
          value={data ? `${data.ci.success_rate}%` : "—"}
          change={data ? "Real-time sync" : "Calculating..."}
          changeType="neutral"
          icon={CheckCircle}
          color="emerald"
        />
        <MetricCard
          label="Open Incidents"
          value={data ? data.incidents.open : "—"}
          change={data?.incidents.open === 0 ? "System healthy" : "Requires attention"}
          changeType={data?.incidents.open === 0 ? "positive" : "negative"}
          icon={AlertTriangle}
          color="red"
        />
        <MetricCard
          label="Local Risk"
          value={data ? Math.round(data.repos.avg_risk_score * 100) + "%" : "—"}
          change="Aggregated risk"
          changeType="neutral"
          icon={GitPullRequest}
          color="amber"
        />
        <MetricCard
          label="Avg Build Time"
          value={data ? (data.ci.avg_build_time_ms > 0 ? `${Math.round(data.ci.avg_build_time_ms / 1000)}s` : "0s") : "—"}
          change="Local execution"
          changeType="neutral"
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
        <RiskExplainer drivers={data?.repos_list?.[0]?.risk_drivers ?? []} />
        <LocalSandbox />
      </div>
    </div>
  )
}
