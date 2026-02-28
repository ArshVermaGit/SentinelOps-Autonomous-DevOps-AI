"use client"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

export default function AnalyticsPage() {
  const [ciHealth, setCiHealth] = useState([])
  const [summary, setSummary] = useState<{ ci: { success_rate: number; total_runs_30d: number; failed_runs_30d: number; avg_build_time_ms: number } } | null>(null)
  
  useEffect(() => {
    apiClient.get("/dashboard/ci-health?days=30").then(r => setCiHealth(r.data.data)).catch(() => {})
    apiClient.get<{ ci: { success_rate: number; total_runs_30d: number; failed_runs_30d: number; avg_build_time_ms: number } }>("/dashboard/summary").then((r: { data: { ci: { success_rate: number; total_runs_30d: number; failed_runs_30d: number; avg_build_time_ms: number } } }) => setSummary(r.data)).catch(() => {})
  }, [])
  
  return (
    <div className="space-y-6">
      <PageHeader
        title="Engineering Analytics"
        subtitle="CI/CD performance insights and trend analysis"
      />
      
      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: "Success Rate", value: `${summary.ci.success_rate}%`, color: "text-emerald-400" },
            { label: "Total Runs (30d)", value: summary.ci.total_runs_30d, color: "text-indigo-400" },
            { label: "Failed Runs (30d)", value: summary.ci.failed_runs_30d, color: "text-red-400" },
            { label: "Avg Build Time", value: `${Math.round(summary.ci.avg_build_time_ms / 1000)}s`, color: "text-amber-400" },
          ].map(({ label, value, color }) => (
            <div key={label} className="bg-[#111827] border border-gray-800 rounded-xl p-5">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
              <p className={`text-2xl font-bold ${color}`}>{value}</p>
            </div>
          ))}
        </div>
      )}
      
      {/* Build outcome trend */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold text-white mb-4">Build Outcome Trend (30 days)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={ciHealth}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} angle={-45} textAnchor="end" height={60} />
            <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} />
            <Tooltip contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: "8px" }} />
            <Bar dataKey="success" stackId="a" fill="#10b981" radius={[2,2,0,0]} name="Success" />
            <Bar dataKey="failure" stackId="a" fill="#ef4444" radius={[2,2,0,0]} name="Failure" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Build duration trend */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold text-white mb-4">Average Build Duration (30 days)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={ciHealth}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} angle={-45} textAnchor="end" height={60} />
            <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} tickFormatter={(v) => `${Math.round(v/1000)}s`} />
            <Tooltip
              contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: "8px" }}
              formatter={(v: number | string | undefined) => [`${(Number(v ?? 0)/1000).toFixed(1)}s`, "Duration"]}
            />
            <Line type="monotone" dataKey="avg_duration" stroke="#6366f1" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
