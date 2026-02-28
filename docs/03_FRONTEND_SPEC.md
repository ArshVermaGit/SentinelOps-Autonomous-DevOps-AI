# SentinelOps — Frontend Specification

## Project Structure

```
sentinelops-frontend/
├── app/
│   ├── layout.tsx                    # Root layout with sidebar
│   ├── page.tsx                      # Redirect to /dashboard
│   ├── dashboard/
│   │   └── page.tsx                  # Main dashboard
│   ├── incidents/
│   │   ├── page.tsx                  # Incidents list
│   │   └── [id]/
│   │       └── page.tsx              # Incident detail with LLM analysis
│   ├── repositories/
│   │   └── page.tsx                  # Repository risk heatmap
│   ├── pull-requests/
│   │   └── page.tsx                  # PR risk gatekeeper
│   └── analytics/
│       └── page.tsx                  # Engineering performance insights
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx               # Navigation sidebar
│   │   ├── TopBar.tsx                # Top status bar
│   │   └── PageHeader.tsx            # Page title + subtitle
│   ├── dashboard/
│   │   ├── MetricCard.tsx            # KPI metric card
│   │   ├── CIHealthChart.tsx         # Build success/failure trend
│   │   ├── RiskHeatmap.tsx           # Repository risk heatmap
│   │   ├── RecentIncidents.tsx       # Last 5 incidents feed
│   │   └── LiveActivityFeed.tsx      # Real-time event stream
│   ├── incidents/
│   │   ├── IncidentCard.tsx          # Incident list item
│   │   ├── RootCausePanel.tsx        # LLM analysis display
│   │   ├── DiffViewer.tsx            # Syntax-highlighted diff
│   │   ├── SimulationModal.tsx       # Self-healing simulation
│   │   └── SimilarityBadge.tsx       # "95% similar to #234"
│   ├── pull-requests/
│   │   ├── PRRiskCard.tsx            # PR with risk score
│   │   ├── RiskTrafficLight.tsx      # 🟢🟡🔴 component
│   │   └── RiskFactorList.tsx        # Contributing risk factors
│   ├── graph/
│   │   └── IncidentMemoryGraph.tsx   # React Flow incident graph
│   └── ui/
│       ├── Badge.tsx                 # Status badge
│       ├── ProgressBar.tsx           # Animated progress bar
│       ├── LoadingSpinner.tsx
│       ├── EmptyState.tsx
│       └── RealTimeDot.tsx           # Pulsing live indicator
├── hooks/
│   ├── useWebSocket.ts               # WebSocket connection hook
│   ├── useDashboard.ts               # Dashboard data fetching
│   ├── useIncidents.ts
│   └── useRiskHeatmap.ts
├── lib/
│   ├── api.ts                        # API client
│   ├── utils.ts                      # Helpers (risk color, format, etc.)
│   └── constants.ts                  # App-wide constants
├── types/
│   └── index.ts                      # All TypeScript types
├── styles/
│   └── globals.css                   # Tailwind + custom CSS
├── tailwind.config.ts
├── next.config.js
└── package.json
```

---

## Design System

### Color Palette
```css
/* globals.css */
:root {
  --bg-primary: #0a0f1e;        /* Deep navy — main background */
  --bg-secondary: #111827;      /* Card background */
  --bg-tertiary: #1f2937;       /* Input / hover */
  --accent-primary: #6366f1;    /* Indigo — primary actions */
  --accent-secondary: #8b5cf6;  /* Purple — secondary */
  --accent-cyan: #06b6d4;       /* Cyan — live indicators */
  --risk-safe: #10b981;         /* Green */
  --risk-caution: #f59e0b;      /* Amber */
  --risk-high: #ef4444;         /* Red */
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --border: #1f2937;
}
```

### Typography
- Font: Inter (Google Fonts)
- Headings: font-bold tracking-tight
- Mono: `font-mono` for code, diffs, scores

### Risk Color Helper
```typescript
// lib/utils.ts
export function getRiskColor(level: "safe" | "caution" | "high" | string) {
  switch (level) {
    case "safe": return { text: "text-emerald-400", bg: "bg-emerald-400/10", border: "border-emerald-400/30" }
    case "caution": return { text: "text-amber-400", bg: "bg-amber-400/10", border: "border-amber-400/30" }
    case "high": return { text: "text-red-400", bg: "bg-red-400/10", border: "border-red-400/30" }
    default: return { text: "text-gray-400", bg: "bg-gray-400/10", border: "border-gray-400/30" }
  }
}

export function getRiskEmoji(level: string) {
  return level === "safe" ? "🟢" : level === "caution" ? "🟡" : "🔴"
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`
}
```

---

## app/layout.tsx

```tsx
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import Sidebar from "@/components/layout/Sidebar"
import TopBar from "@/components/layout/TopBar"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "SentinelOps — Autonomous DevOps AI Co-Pilot",
  description: "Engineering decision intelligence. Predict failures before they happen.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0a0f1e] text-white min-h-screen`}>
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <TopBar />
            <main className="flex-1 overflow-y-auto p-6">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}
```

---

## components/layout/Sidebar.tsx

```tsx
"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  LayoutDashboard, GitPullRequest, AlertTriangle, 
  BarChart3, GitBranch, Shield, Zap
} from "lucide-react"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/repositories", label: "Risk Heatmap", icon: GitBranch },
  { href: "/pull-requests", label: "PR Gatekeeper", icon: GitPullRequest },
  { href: "/incidents", label: "Incidents", icon: AlertTriangle },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
]

export default function Sidebar() {
  const pathname = usePathname()
  
  return (
    <aside className="w-64 bg-[#111827] border-r border-gray-800 flex flex-col shrink-0">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-white text-sm">SentinelOps</div>
            <div className="text-xs text-gray-500">DevOps AI Co-Pilot</div>
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                active
                  ? "bg-indigo-600/20 text-indigo-400 border border-indigo-600/30"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          )
        })}
      </nav>
      
      {/* Live status */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Monitoring 4 repositories</span>
        </div>
      </div>
    </aside>
  )
}
```

---

## app/dashboard/page.tsx

```tsx
"use client"
import { useEffect, useState } from "react"
import PageHeader from "@/components/layout/PageHeader"
import MetricCard from "@/components/dashboard/MetricCard"
import CIHealthChart from "@/components/dashboard/CIHealthChart"
import RiskHeatmap from "@/components/dashboard/RiskHeatmap"
import RecentIncidents from "@/components/dashboard/RecentIncidents"
import LiveActivityFeed from "@/components/dashboard/LiveActivityFeed"
import { useDashboard } from "@/hooks/useDashboard"
import { AlertTriangle, CheckCircle, GitPullRequest, Zap } from "lucide-react"

export default function DashboardPage() {
  const { data, loading } = useDashboard()
  
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
```

---

## components/dashboard/MetricCard.tsx

```tsx
import { LucideIcon } from "lucide-react"

interface MetricCardProps {
  label: string
  value: string | number
  change: string
  changeType: "positive" | "negative" | "neutral"
  icon: LucideIcon
  color: "emerald" | "red" | "amber" | "indigo"
}

const colorMap = {
  emerald: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20" },
  red: { bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/20" },
  amber: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20" },
  indigo: { bg: "bg-indigo-500/10", text: "text-indigo-400", border: "border-indigo-500/20" },
}

export default function MetricCard({ label, value, change, changeType, icon: Icon, color }: MetricCardProps) {
  const colors = colorMap[color]
  const changeColor = changeType === "positive" ? "text-emerald-400" : changeType === "negative" ? "text-red-400" : "text-gray-400"
  
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          <p className={`text-xs mt-1 ${changeColor}`}>{change}</p>
        </div>
        <div className={`w-10 h-10 rounded-lg ${colors.bg} ${colors.border} border flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${colors.text}`} />
        </div>
      </div>
    </div>
  )
}
```

---

## components/dashboard/CIHealthChart.tsx

```tsx
"use client"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"

export default function CIHealthChart() {
  const [data, setData] = useState([])
  const [view, setView] = useState<"trend" | "duration">("trend")
  
  useEffect(() => {
    apiClient.get("/dashboard/ci-health").then(r => setData(r.data.data))
  }, [])
  
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="font-semibold text-white">CI Pipeline Health</h3>
          <p className="text-xs text-gray-500 mt-0.5">Build outcomes over last 30 days</p>
        </div>
        <div className="flex gap-2">
          {["trend", "duration"].map(v => (
            <button
              key={v}
              onClick={() => setView(v as any)}
              className={`px-3 py-1 text-xs rounded-md transition-all ${
                view === v ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-400 hover:text-white"
              }`}
            >
              {v === "trend" ? "Success Rate" : "Build Time"}
            </button>
          ))}
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={220}>
        {view === "trend" ? (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#6b7280" }} />
            <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: "8px" }}
              labelStyle={{ color: "#f9fafb" }}
            />
            <Legend />
            <Bar dataKey="success" fill="#10b981" radius={[4,4,0,0]} name="Success" />
            <Bar dataKey="failure" fill="#ef4444" radius={[4,4,0,0]} name="Failure" />
          </BarChart>
        ) : (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#6b7280" }} />
            <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: "8px" }}
              formatter={(v: number) => [`${Math.round(v/1000)}s`, "Avg Duration"]}
            />
            <Line type="monotone" dataKey="avg_duration" stroke="#6366f1" strokeWidth={2} dot={false} />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}
```

---

## app/incidents/[id]/page.tsx

```tsx
"use client"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import RootCausePanel from "@/components/incidents/RootCausePanel"
import DiffViewer from "@/components/incidents/DiffViewer"
import SimulationModal from "@/components/incidents/SimulationModal"
import SimilarityBadge from "@/components/incidents/SimilarityBadge"

export default function IncidentDetailPage() {
  const { id } = useParams()
  const [incident, setIncident] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [showSim, setShowSim] = useState(false)
  
  useEffect(() => {
    apiClient.get(`/incidents/${id}`).then(r => {
      setIncident(r.data)
      setLoading(false)
    })
  }, [id])
  
  if (loading) return <div className="text-gray-400 p-8">Analyzing incident...</div>
  if (!incident) return <div className="text-red-400 p-8">Incident not found</div>
  
  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader
        title={`Incident #${id}`}
        subtitle={`Detected in: ${incident.ci_run?.workflow_name} — ${incident.ci_run?.repository?.name}`}
        badge={incident.status === "open" ? "OPEN" : incident.status.toUpperCase()}
        badgeColor={incident.status === "open" ? "red" : "emerald"}
      />
      
      {/* Similarity badge */}
      {incident.similar_incident_id && (
        <SimilarityBadge
          similarId={incident.similar_incident_id}
          score={incident.similarity_score}
        />
      )}
      
      {/* Root Cause Panel */}
      <RootCausePanel incident={incident} />
      
      {/* Suggested Fix Diff */}
      {incident.fix_diff && (
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white">Suggested Fix</h3>
            <button
              onClick={() => setShowSim(true)}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm rounded-lg transition-all flex items-center gap-2"
            >
              ⚡ Simulate Fix
            </button>
          </div>
          <DiffViewer diff={incident.fix_diff} />
        </div>
      )}
      
      {/* Simulation Modal */}
      {showSim && (
        <SimulationModal
          incidentId={id as string}
          onClose={() => setShowSim(false)}
        />
      )}
    </div>
  )
}
```

---

## components/incidents/RootCausePanel.tsx

```tsx
import { Brain, Clock, FileCode, AlertCircle } from "lucide-react"

export default function RootCausePanel({ incident }: { incident: any }) {
  const categoryColors: Record<string, string> = {
    dependency: "text-orange-400 bg-orange-400/10",
    syntax: "text-red-400 bg-red-400/10",
    test: "text-yellow-400 bg-yellow-400/10",
    config: "text-blue-400 bg-blue-400/10",
    runtime: "text-purple-400 bg-purple-400/10",
    network: "text-cyan-400 bg-cyan-400/10",
  }
  
  const catStyle = categoryColors[incident.error_category] || "text-gray-400 bg-gray-400/10"
  
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold text-white">AI Root Cause Analysis</h3>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-xs px-2 py-1 rounded-full font-mono ${catStyle}`}>
            {incident.error_category}
          </span>
          <span className="text-xs text-gray-500">
            {Math.round((incident.llm_confidence ?? 0) * 100)}% confidence
          </span>
        </div>
      </div>
      
      {/* Root cause explanation */}
      <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
        <p className="text-gray-200 text-sm leading-relaxed">{incident.root_cause}</p>
      </div>
      
      {/* Metadata grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* Responsible files */}
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <FileCode className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-xs text-gray-500 uppercase tracking-wider">Files</span>
          </div>
          <div className="space-y-1">
            {incident.responsible_files?.map((f: string) => (
              <div key={f} className="text-xs font-mono text-indigo-400 bg-indigo-400/10 px-2 py-1 rounded">
                {f}
              </div>
            ))}
          </div>
        </div>
        
        {/* Fix time */}
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <Clock className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-xs text-gray-500 uppercase tracking-wider">Est. Fix Time</span>
          </div>
          <span className="text-sm text-emerald-400 font-medium">{incident.estimated_fix_time}</span>
        </div>
        
        {/* Risk if unresolved */}
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <AlertCircle className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-xs text-gray-500 uppercase tracking-wider">Risk</span>
          </div>
          <p className="text-xs text-red-400">{incident.risk_if_unresolved}</p>
        </div>
      </div>
      
      {/* Suggested fix */}
      <div>
        <span className="text-xs text-gray-500 uppercase tracking-wider block mb-2">Suggested Fix</span>
        <div className="bg-emerald-400/5 border border-emerald-400/20 rounded-lg p-3">
          <p className="text-sm text-emerald-300">{incident.suggested_fix}</p>
        </div>
      </div>
    </div>
  )
}
```

---

## components/incidents/SimulationModal.tsx

```tsx
"use client"
import { useState } from "react"
import { apiClient } from "@/lib/api"
import { CheckCircle, XCircle, Loader, X } from "lucide-react"

interface SimStep {
  step: string
  status: "success" | "failure" | "skipped" | "running"
  duration_ms: number
}

export default function SimulationModal({ incidentId, onClose }: { incidentId: string; onClose: () => void }) {
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [steps, setSteps] = useState<SimStep[]>([])
  
  const runSimulation = async () => {
    setRunning(true)
    setSteps([])
    
    // Animate steps appearing
    const mockSteps = [
      "Apply patch",
      "Install dependencies", 
      "Run unit tests",
      "Run integration tests",
      "Build Docker image"
    ]
    
    for (let i = 0; i < mockSteps.length; i++) {
      setSteps(prev => [...prev, { step: mockSteps[i], status: "running", duration_ms: 0 }])
      await new Promise(r => setTimeout(r, 600))
    }
    
    const response = await apiClient.post(`/simulation/${incidentId}/apply-fix`)
    setResult(response.data)
    setSteps(response.data.steps)
    setRunning(false)
  }
  
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-[#111827] border border-gray-700 rounded-2xl p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="font-bold text-white">⚡ Self-Healing Simulation</h3>
            <p className="text-xs text-gray-500 mt-0.5">Apply AI patch in sandbox environment</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {!running && !result && (
          <button
            onClick={runSimulation}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium transition-all"
          >
            Run Simulation
          </button>
        )}
        
        {(running || result) && (
          <div className="space-y-3">
            {steps.map((step, i) => (
              <div key={i} className="flex items-center gap-3">
                {step.status === "running" ? (
                  <Loader className="w-4 h-4 text-indigo-400 animate-spin" />
                ) : step.status === "success" ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : step.status === "failure" ? (
                  <XCircle className="w-4 h-4 text-red-400" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-gray-600" />
                )}
                <span className="text-sm text-gray-300">{step.step}</span>
                {step.duration_ms > 0 && (
                  <span className="ml-auto text-xs text-gray-600 font-mono">
                    {(step.duration_ms / 1000).toFixed(1)}s
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
        
        {result && (
          <div className={`mt-5 p-4 rounded-xl border ${
            result.success
              ? "bg-emerald-400/10 border-emerald-400/30"
              : "bg-red-400/10 border-red-400/30"
          }`}>
            <p className={`font-semibold text-sm ${result.success ? "text-emerald-400" : "text-red-400"}`}>
              {result.predicted_outcome}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {result.tests_passed} tests passed · {result.tests_failed} failed · {result.confidence} confidence
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
```

---

## components/graph/IncidentMemoryGraph.tsx

```tsx
"use client"
import { useEffect, useState, useCallback } from "react"
import ReactFlow, {
  Node, Edge, Background, Controls, MiniMap,
  useNodesState, useEdgesState, addEdge
} from "reactflow"
import "reactflow/dist/style.css"

// Node types for the incident memory graph
// PR → Commit → Author → Failure → Log Pattern

const nodeDefaults = {
  pr: { style: { background: "#6366f1", color: "white", border: "none", borderRadius: "8px", padding: "8px 12px", fontSize: "12px" } },
  commit: { style: { background: "#1f2937", color: "#9ca3af", border: "1px solid #374151", borderRadius: "6px", fontSize: "11px" } },
  failure: { style: { background: "#ef4444", color: "white", border: "none", borderRadius: "8px", padding: "6px 10px", fontSize: "11px" } },
  pattern: { style: { background: "#f59e0b", color: "black", border: "none", borderRadius: "20px", padding: "4px 10px", fontSize: "10px" } },
}

export default function IncidentMemoryGraph({ data }: { data: any }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  
  useEffect(() => {
    if (!data) return
    
    // Build nodes and edges from incident data
    const newNodes: Node[] = []
    const newEdges: Edge[] = []
    
    data.incidents?.forEach((incident: any, i: number) => {
      const x = (i % 3) * 300
      const y = Math.floor(i / 3) * 200
      
      newNodes.push({
        id: `pr-${incident.pr_id}`,
        type: "default",
        position: { x, y },
        data: { label: `PR #${incident.pr_id}` },
        ...nodeDefaults.pr
      })
      
      newNodes.push({
        id: `failure-${incident.id}`,
        type: "default",
        position: { x: x + 150, y: y + 80 },
        data: { label: `Failure: ${incident.error_category}` },
        ...nodeDefaults.failure
      })
      
      newEdges.push({
        id: `e-${incident.pr_id}-${incident.id}`,
        source: `pr-${incident.pr_id}`,
        target: `failure-${incident.id}`,
        animated: true,
        style: { stroke: "#ef4444", strokeWidth: 1.5 }
      })
      
      if (incident.similar_incident_id) {
        newEdges.push({
          id: `sim-${incident.id}-${incident.similar_incident_id}`,
          source: `failure-${incident.id}`,
          target: `failure-${incident.similar_incident_id}`,
          animated: false,
          style: { stroke: "#f59e0b", strokeDasharray: "5,5" },
          label: `${Math.round(incident.similarity_score * 100)}% similar`
        })
      }
    })
    
    setNodes(newNodes)
    setEdges(newEdges)
  }, [data])
  
  return (
    <div className="h-[450px] bg-[#0a0f1e] rounded-xl border border-gray-800">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background color="#1f2937" gap={20} />
        <Controls />
        <MiniMap
          nodeColor={(n) => {
            if (n.id.startsWith("pr")) return "#6366f1"
            if (n.id.startsWith("failure")) return "#ef4444"
            return "#f59e0b"
          }}
          style={{ background: "#111827" }}
        />
      </ReactFlow>
    </div>
  )
}
```

---

## hooks/useWebSocket.ts

```typescript
import { useEffect, useRef, useCallback } from "react"

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws"

export function useWebSocket(onMessage: (data: any) => void) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeout = useRef<NodeJS.Timeout>()
  
  const connect = useCallback(() => {
    wsRef.current = new WebSocket(WS_URL)
    
    wsRef.current.onopen = () => {
      console.log("SentinelOps WebSocket connected")
    }
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (e) {
        console.error("WS parse error", e)
      }
    }
    
    wsRef.current.onclose = () => {
      // Reconnect after 3 seconds
      reconnectTimeout.current = setTimeout(connect, 3000)
    }
    
    wsRef.current.onerror = (err) => {
      console.error("WebSocket error", err)
      wsRef.current?.close()
    }
  }, [onMessage])
  
  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimeout.current)
      wsRef.current?.close()
    }
  }, [connect])
  
  return wsRef
}
```

---

## lib/api.ts

```typescript
import axios from "axios"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" }
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("API Error:", err.response?.data || err.message)
    return Promise.reject(err)
  }
)
```

---

## package.json

```json
{
  "name": "sentinelops-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.1.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "recharts": "2.12.3",
    "reactflow": "11.11.3",
    "framer-motion": "11.0.22",
    "lucide-react": "0.368.0",
    "axios": "1.6.8",
    "clsx": "2.1.1",
    "tailwind-merge": "2.2.2"
  },
  "devDependencies": {
    "typescript": "5.4.3",
    "@types/react": "18.2.74",
    "@types/node": "20.12.5",
    "tailwindcss": "3.4.3",
    "autoprefixer": "10.4.19",
    "postcss": "8.4.38"
  }
}
```

---

## tailwind.config.ts

```typescript
import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0a0f1e",
          secondary: "#111827",
          tertiary: "#1f2937",
        },
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      }
    },
  },
  plugins: [],
}

export default config
```
