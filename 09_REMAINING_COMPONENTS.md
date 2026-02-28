# SentinelOps — Remaining Frontend Components

## app/repositories/page.tsx

```tsx
"use client"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import { getRiskColor, getRiskEmoji } from "@/lib/utils"
import { GitBranch, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react"

export default function RepositoriesPage() {
  const [data, setData] = useState<any>(null)
  
  useEffect(() => {
    apiClient.get("/dashboard/risk-heatmap").then(r => setData(r.data))
  }, [])
  
  return (
    <div className="space-y-6">
      <PageHeader
        title="Repository Risk Heatmap"
        subtitle="All monitored repositories ranked by CI failure risk"
      />
      
      <div className="grid gap-4">
        {data?.repositories?.map((repo: any) => {
          const colors = getRiskColor(repo.risk_level)
          return (
            <div
              key={repo.id}
              className="bg-[#111827] border border-gray-800 rounded-xl p-5 flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colors.bg} ${colors.border} border`}>
                  <GitBranch className={`w-5 h-5 ${colors.text}`} />
                </div>
                <div>
                  <div className="font-semibold text-white">{repo.name}</div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {getRiskEmoji(repo.risk_level)} {repo.risk_level.toUpperCase()} RISK
                  </div>
                </div>
              </div>
              
              {/* Risk Progress Bar */}
              <div className="flex items-center gap-4 flex-1 mx-8">
                <div className="flex-1 bg-gray-800 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      repo.risk_level === "high" ? "bg-red-500" :
                      repo.risk_level === "caution" ? "bg-amber-500" : "bg-emerald-500"
                    }`}
                    style={{ width: `${repo.risk_score * 100}%` }}
                  />
                </div>
                <span className={`text-sm font-mono font-bold ${colors.text} w-12 text-right`}>
                  {Math.round(repo.risk_score * 100)}%
                </span>
              </div>
              
              <div className="flex gap-6 text-right">
                <div>
                  <div className="text-xs text-gray-500">Failure Rate</div>
                  <div className="text-sm font-medium text-white">
                    {Math.round((repo.failure_rate || 0) * 100)}%
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

---

## app/pull-requests/page.tsx

```tsx
"use client"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import { getRiskColor, getRiskEmoji } from "@/lib/utils"
import { GitPullRequest, User, FileCode, Package } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export default function PullRequestsPage() {
  const [prs, setPrs] = useState<any[]>([])
  const [filter, setFilter] = useState<string>("all")
  
  useEffect(() => {
    apiClient.get("/pull-requests/").then(r => setPrs(r.data))
  }, [])
  
  const filtered = filter === "all" ? prs : prs.filter(pr => pr.risk_level === filter)
  
  return (
    <div className="space-y-6">
      <PageHeader
        title="PR Risk Gatekeeper"
        subtitle="Every open pull request scored by AI before merge"
        badge="LIVE"
      />
      
      {/* Filter tabs */}
      <div className="flex gap-2">
        {["all", "high", "caution", "safe"].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 text-sm rounded-lg transition-all ${
              filter === f
                ? "bg-indigo-600 text-white"
                : "bg-gray-800 text-gray-400 hover:text-white"
            }`}
          >
            {f === "all" ? "All PRs" : `${getRiskEmoji(f)} ${f.charAt(0).toUpperCase() + f.slice(1)}`}
            <span className="ml-2 text-xs opacity-60">
              ({f === "all" ? prs.length : prs.filter(p => p.risk_level === f).length})
            </span>
          </button>
        ))}
      </div>
      
      {/* PR Cards */}
      <div className="space-y-3">
        <AnimatePresence>
          {filtered.map((pr, i) => {
            const colors = getRiskColor(pr.risk_level)
            return (
              <motion.div
                key={pr.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ delay: i * 0.05 }}
                className={`bg-[#111827] border rounded-xl p-5 ${colors.border}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    {/* Traffic Light */}
                    <div className={`mt-0.5 w-8 h-8 rounded-lg flex items-center justify-center text-lg ${colors.bg}`}>
                      {getRiskEmoji(pr.risk_level)}
                    </div>
                    
                    <div className="flex-1">
                      <div className="font-medium text-white">{pr.title}</div>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="flex items-center gap-1 text-xs text-gray-500">
                          <User className="w-3 h-3" /> {pr.author}
                        </span>
                        <span className="text-xs text-gray-600">
                          +{pr.lines_added} / -{pr.lines_deleted} lines
                        </span>
                        <span className="flex items-center gap-1 text-xs text-gray-500">
                          <FileCode className="w-3 h-3" /> {pr.files_changed} files
                        </span>
                        {pr.has_dependency_changes && (
                          <span className="flex items-center gap-1 text-xs text-orange-400">
                            <Package className="w-3 h-3" /> deps changed
                          </span>
                        )}
                      </div>
                      
                      {/* Risk Factors */}
                      {pr.risk_factors?.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {pr.risk_factors.map((factor: string, j: number) => (
                            <span key={j} className={`text-xs px-2 py-0.5 rounded-full ${colors.bg} ${colors.text}`}>
                              {factor}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Risk Score */}
                  <div className="text-right ml-4">
                    <div className={`text-2xl font-bold font-mono ${colors.text}`}>
                      {Math.round(pr.risk_probability * 100)}%
                    </div>
                    <div className="text-xs text-gray-500">failure risk</div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </div>
  )
}
```

---

## components/layout/TopBar.tsx

```tsx
"use client"
import { Bell, Search, Wifi } from "lucide-react"
import { useWebSocket } from "@/hooks/useWebSocket"
import { useState } from "react"

export default function TopBar() {
  const [connected, setConnected] = useState(false)
  const [notifications, setNotifications] = useState<string[]>([])
  
  useWebSocket((data) => {
    if (data.type === "new_incident") {
      setNotifications(prev => [data.message, ...prev.slice(0, 4)])
    }
    setConnected(true)
  })
  
  return (
    <header className="h-14 bg-[#111827] border-b border-gray-800 flex items-center px-6 justify-between shrink-0">
      {/* Search */}
      <div className="flex items-center gap-2 bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 w-72">
        <Search className="w-4 h-4 text-gray-500" />
        <input
          className="bg-transparent text-sm text-gray-400 placeholder-gray-600 outline-none flex-1"
          placeholder="Search incidents, repos, PRs..."
        />
        <kbd className="text-xs text-gray-600 border border-gray-700 rounded px-1">⌘K</kbd>
      </div>
      
      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Live indicator */}
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${connected ? "bg-emerald-400 animate-pulse" : "bg-gray-600"}`} />
          <span className="text-xs text-gray-500">{connected ? "Live monitoring" : "Connecting..."}</span>
        </div>
        
        {/* Notifications */}
        <div className="relative">
          <button className="relative p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-all">
            <Bell className="w-4 h-4" />
            {notifications.length > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            )}
          </button>
        </div>
      </div>
    </header>
  )
}
```

---

## components/layout/PageHeader.tsx

```tsx
interface PageHeaderProps {
  title: string
  subtitle: string
  badge?: string
  badgeColor?: "red" | "emerald" | "amber" | "indigo"
}

const badgeColors = {
  red: "bg-red-500/10 text-red-400 border-red-500/30",
  emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
  amber: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  indigo: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30",
}

export default function PageHeader({ title, subtitle, badge, badgeColor = "indigo" }: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-white">{title}</h1>
          {badge && (
            <span className={`text-xs px-2 py-0.5 rounded-full border font-mono font-bold ${badgeColors[badgeColor]}`}>
              {badge}
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
      </div>
    </div>
  )
}
```

---

## components/dashboard/LiveActivityFeed.tsx

```tsx
"use client"
import { useEffect, useState } from "react"
import { useWebSocket } from "@/hooks/useWebSocket"

interface Activity {
  id: string
  type: "failure" | "success" | "pr_risk" | "incident"
  message: string
  time: string
  repo?: string
}

const MOCK_ACTIVITIES: Activity[] = [
  { id: "1", type: "failure", message: "CI failed: api-gateway / Build & Test", time: "2m ago", repo: "api-gateway" },
  { id: "2", type: "incident", message: "AI analysis complete: root cause identified", time: "2m ago" },
  { id: "3", type: "pr_risk", message: "🔴 High-risk PR detected: auth migration", time: "8m ago" },
  { id: "4", type: "success", message: "CI passed: frontend-app / Deploy Staging", time: "12m ago" },
  { id: "5", type: "success", message: "CI passed: payment-service / Unit Tests", time: "23m ago" },
  { id: "6", type: "pr_risk", message: "🟡 Caution: rate-limiter PR (54% risk)", time: "34m ago" },
  { id: "7", type: "failure", message: "CI failed: data-pipeline / Integration", time: "41m ago" },
]

export default function LiveActivityFeed() {
  const [activities, setActivities] = useState<Activity[]>(MOCK_ACTIVITIES)
  
  useWebSocket((data) => {
    const newActivity: Activity = {
      id: Date.now().toString(),
      type: data.type === "ci_failure" ? "failure" : data.type === "new_incident" ? "incident" : "success",
      message: data.message,
      time: "just now",
      repo: data.repo_name,
    }
    setActivities(prev => [newActivity, ...prev.slice(0, 9)])
  })
  
  const typeConfig = {
    failure: { dot: "bg-red-500", text: "text-red-400" },
    success: { dot: "bg-emerald-500", text: "text-gray-400" },
    pr_risk: { dot: "bg-amber-500", text: "text-amber-400" },
    incident: { dot: "bg-indigo-500", text: "text-indigo-400" },
  }
  
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white">Live Activity</h3>
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-gray-500">real-time</span>
        </div>
      </div>
      
      <div className="space-y-3 overflow-y-auto max-h-[280px]">
        {activities.map((activity) => {
          const config = typeConfig[activity.type]
          return (
            <div key={activity.id} className="flex items-start gap-3">
              <div className={`w-1.5 h-1.5 rounded-full mt-2 shrink-0 ${config.dot}`} />
              <div className="flex-1 min-w-0">
                <p className={`text-xs ${config.text} leading-relaxed`}>{activity.message}</p>
                <p className="text-xs text-gray-600 mt-0.5">{activity.time}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

---

## components/dashboard/RiskHeatmap.tsx

```tsx
import Link from "next/link"
import { getRiskColor } from "@/lib/utils"

interface Repo {
  id: number
  name: string
  risk_score: number
}

export default function RiskHeatmap({ repos }: { repos: Repo[] }) {
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white">Repository Risk Heatmap</h3>
        <Link href="/repositories" className="text-xs text-indigo-400 hover:text-indigo-300">View all →</Link>
      </div>
      
      <div className="space-y-3">
        {repos.map((repo) => {
          const riskLevel = repo.risk_score > 0.65 ? "high" : repo.risk_score > 0.35 ? "caution" : "safe"
          const colors = getRiskColor(riskLevel)
          
          return (
            <div key={repo.id} className="flex items-center gap-3">
              <div className="w-32 text-sm text-gray-400 truncate">{repo.name}</div>
              <div className="flex-1 bg-gray-800 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    riskLevel === "high" ? "bg-red-500" :
                    riskLevel === "caution" ? "bg-amber-500" : "bg-emerald-500"
                  }`}
                  style={{ width: `${repo.risk_score * 100}%` }}
                />
              </div>
              <span className={`text-xs font-mono w-8 text-right ${colors.text}`}>
                {Math.round(repo.risk_score * 100)}%
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

---

## components/dashboard/RecentIncidents.tsx

```tsx
"use client"
import { useEffect, useState } from "react"
import Link from "next/link"
import { apiClient } from "@/lib/api"
import { AlertTriangle, Brain } from "lucide-react"

export default function RecentIncidents() {
  const [incidents, setIncidents] = useState<any[]>([])
  
  useEffect(() => {
    apiClient.get("/incidents/?limit=5").then(r => setIncidents(r.data))
  }, [])
  
  const categoryColors: Record<string, string> = {
    dependency: "text-orange-400",
    syntax: "text-red-400",
    test: "text-yellow-400",
    config: "text-blue-400",
    runtime: "text-purple-400",
    network: "text-cyan-400",
  }
  
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-indigo-400" />
          <h3 className="font-semibold text-white">Recent AI-Analyzed Incidents</h3>
        </div>
        <Link href="/incidents" className="text-xs text-indigo-400 hover:text-indigo-300">View all →</Link>
      </div>
      
      <div className="space-y-3">
        {incidents.length === 0 && (
          <p className="text-sm text-gray-600 py-4 text-center">No incidents detected — all systems healthy ✅</p>
        )}
        
        {incidents.map((inc) => (
          <Link
            key={inc.id}
            href={`/incidents/${inc.id}`}
            className="block p-3 bg-gray-900 rounded-lg hover:bg-gray-800 transition-all group"
          >
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-200 truncate">{inc.root_cause}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-xs ${categoryColors[inc.error_category] || "text-gray-500"}`}>
                    {inc.error_category}
                  </span>
                  <span className="text-xs text-gray-600">·</span>
                  <span className="text-xs text-gray-600">{inc.estimated_fix_time}</span>
                  <span className="text-xs text-gray-600">·</span>
                  <span className={`text-xs ${inc.status === "open" ? "text-red-400" : "text-emerald-400"}`}>
                    {inc.status}
                  </span>
                </div>
              </div>
              <span className="text-xs text-gray-600 shrink-0 group-hover:text-indigo-400">→</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
```

---

## components/incidents/DiffViewer.tsx

```tsx
"use client"

interface DiffViewerProps {
  diff: string
}

export default function DiffViewer({ diff }: DiffViewerProps) {
  const lines = diff.split("\n")
  
  return (
    <div className="font-mono text-xs bg-gray-950 rounded-lg overflow-auto max-h-64 border border-gray-800">
      <table className="w-full border-collapse">
        <tbody>
          {lines.map((line, i) => {
            let bg = ""
            let text = "text-gray-400"
            
            if (line.startsWith("+") && !line.startsWith("+++")) {
              bg = "bg-emerald-900/30"
              text = "text-emerald-400"
            } else if (line.startsWith("-") && !line.startsWith("---")) {
              bg = "bg-red-900/30"
              text = "text-red-400"
            } else if (line.startsWith("@@")) {
              bg = "bg-indigo-900/20"
              text = "text-indigo-400"
            } else if (line.startsWith("---") || line.startsWith("+++")) {
              text = "text-gray-500"
            }
            
            return (
              <tr key={i} className={bg}>
                <td className="w-8 text-gray-700 text-right pr-3 py-0.5 select-none border-r border-gray-800 pl-2">
                  {i + 1}
                </td>
                <td className={`pl-4 py-0.5 ${text} whitespace-pre`}>
                  {line || " "}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
```

---

## components/incidents/SimilarityBadge.tsx

```tsx
import Link from "next/link"
import { GitMerge } from "lucide-react"

export default function SimilarityBadge({ similarId, score }: { similarId: number; score: number }) {
  return (
    <div className="flex items-center gap-2 bg-amber-400/10 border border-amber-400/30 rounded-lg px-4 py-2.5">
      <GitMerge className="w-4 h-4 text-amber-400" />
      <span className="text-sm text-amber-300">
        <strong>{Math.round(score * 100)}% similar</strong> to{" "}
        <Link href={`/incidents/${similarId}`} className="underline underline-offset-2 hover:text-amber-200">
          Incident #{similarId}
        </Link>
        {" "}— same root cause pattern detected previously
      </span>
    </div>
  )
}
```

---

## hooks/useDashboard.ts

```typescript
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"

interface DashboardData {
  repos: {
    total: number
    high_risk: number
    avg_risk_score: number
  }
  ci: {
    total_runs_30d: number
    failed_runs_30d: number
    success_rate: number
    avg_build_time_ms: number
  }
  incidents: {
    open: number
    total_30d: number
  }
  repos_list: Array<{
    id: number
    name: string
    risk_score: number
    failure_rate: number
  }>
}

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const fetch = async () => {
      try {
        const r = await apiClient.get("/dashboard/summary")
        setData(r.data)
      } catch (e) {
        setError("Failed to load dashboard data")
      } finally {
        setLoading(false)
      }
    }
    
    fetch()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetch, 30000)
    return () => clearInterval(interval)
  }, [])
  
  return { data, loading, error }
}
```

---

## lib/utils.ts (complete)

```typescript
export function getRiskColor(level: "safe" | "caution" | "high" | string) {
  switch (level) {
    case "safe":
      return {
        text: "text-emerald-400",
        bg: "bg-emerald-400/10",
        border: "border-emerald-400/30",
        hex: "#10b981"
      }
    case "caution":
      return {
        text: "text-amber-400",
        bg: "bg-amber-400/10",
        border: "border-amber-400/30",
        hex: "#f59e0b"
      }
    case "high":
      return {
        text: "text-red-400",
        bg: "bg-red-400/10",
        border: "border-red-400/30",
        hex: "#ef4444"
      }
    default:
      return {
        text: "text-gray-400",
        bg: "bg-gray-400/10",
        border: "border-gray-400/30",
        hex: "#9ca3af"
      }
  }
}

export function getRiskEmoji(level: string) {
  return level === "safe" ? "🟢" : level === "caution" ? "🟡" : "🔴"
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  const mins = Math.floor(ms / 60000)
  const secs = Math.floor((ms % 60000) / 1000)
  return `${mins}m ${secs}s`
}

export function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return "just now"
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
  return `${Math.floor(diffMins / 1440)}d ago`
}

export function getRiskProbabilityLabel(prob: number): string {
  if (prob < 0.35) return "LOW"
  if (prob < 0.65) return "MEDIUM"
  return "HIGH"
}
```

---

## types/index.ts

```typescript
export interface Repository {
  id: number
  name: string
  full_name: string
  url: string
  risk_score: number
  failure_rate: number
  deployment_stability: number
  last_analyzed: string
}

export interface PullRequest {
  id: number
  github_pr_number: number
  title: string
  author: string
  lines_added: number
  lines_deleted: number
  files_changed: number
  has_config_changes: boolean
  has_test_changes: boolean
  has_dependency_changes: boolean
  risk_probability: number
  risk_level: "safe" | "caution" | "high"
  risk_factors: string[]
  status: "open" | "merged" | "closed"
  created_at: string
}

export interface CIRun {
  id: number
  workflow_name: string
  status: "success" | "failure" | "running" | "cancelled"
  duration_ms: number
  started_at: string
  finished_at: string
  is_anomalous_duration: boolean
  error_block?: string
  failure_step?: string
}

export interface Incident {
  id: number
  root_cause: string
  responsible_files: string[]
  error_category: string
  llm_confidence: number
  suggested_fix: string
  fix_diff: string
  estimated_fix_time: string
  risk_if_unresolved: string
  status: "open" | "simulated" | "resolved"
  similar_incident_id?: number
  similarity_score: number
  simulation_result?: SimulationResult
  ci_run?: CIRun
  created_at: string
}

export interface SimulationResult {
  success: boolean
  steps: SimulationStep[]
  predicted_outcome: string
  confidence: string
  tests_passed: number
  tests_failed: number
}

export interface SimulationStep {
  step: string
  status: "success" | "failure" | "skipped" | "running"
  duration_ms: number
}

export interface DashboardSummary {
  repos: {
    total: number
    high_risk: number
    avg_risk_score: number
  }
  ci: {
    total_runs_30d: number
    failed_runs_30d: number
    success_rate: number
    avg_build_time_ms: number
  }
  incidents: {
    open: number
    total_30d: number
  }
  repos_list: Repository[]
}
```
