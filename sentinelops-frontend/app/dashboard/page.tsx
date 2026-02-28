"use client"
import PageHeader from "@/components/layout/PageHeader"
import MetricCard from "@/components/dashboard/MetricCard"
import CIHealthChart from "@/components/dashboard/CIHealthChart"
import RiskHeatmap from "@/components/dashboard/RiskHeatmap"
import RecentIncidents from "@/components/dashboard/RecentIncidents"
import LiveActivityFeed from "@/components/dashboard/LiveActivityFeed"
import { useDashboard } from "@/hooks/useDashboard"
import { AlertTriangle, CheckCircle, GitPullRequest, Zap } from "lucide-react"

export default function DashboardPage() {
  const { data } = useDashboard()
  
  return (
    <div className="space-y-6">
      <PageHeader
        title="Engineering Intelligence Dashboard"
        subtitle="Real-time AI monitoring across all repositories and CI pipelines"
        badge="LIVE"
      />
      
      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
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
      <div className="grid grid-cols-3 gap-6">
        {/* CI Health Chart - wide */}
        <div className="col-span-2">
          <CIHealthChart />
        </div>
        {/* Live Activity Feed */}
        <div className="col-span-1">
          <LiveActivityFeed />
        </div>
      </div>
      
      {/* Bottom row */}
      <div className="grid grid-cols-2 gap-6">
        <RiskHeatmap repos={data?.repos_list ?? []} />
        <RecentIncidents />
      </div>
    </div>
  )
}
