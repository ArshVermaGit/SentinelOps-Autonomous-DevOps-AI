"use client"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import { getRiskEmoji } from "@/lib/utils"
import { AnimatePresence } from "framer-motion"
import PRRiskCard from "@/components/pull-requests/PRRiskCard"

interface PR {
  id: number
  title: string
  author: string
  lines_added: number
  lines_deleted: number
  files_changed: number
  risk_level: string
  risk_probability: number
  risk_factors: string[]
  has_dependency_changes?: boolean
}

export default function PullRequestsPage() {
  const [prs, setPrs] = useState<PR[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>("all")
  
  useEffect(() => {
    apiClient.get<PR[]>("/pull-requests/").then((r: { data: PR[] }) => {
      setPrs(r.data)
      setLoading(false)
    }).catch(() => setLoading(false))
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
      <div className="flex flex-wrap gap-2">
        {["all", "high", "caution", "safe"].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 text-sm rounded-lg transition-all border ${
              filter === f
                ? "bg-indigo-600 text-white border-indigo-500 shadow-lg shadow-indigo-600/20"
                : "bg-gray-800/50 text-gray-400 border-gray-700 hover:text-white hover:bg-gray-800"
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
      {loading ? (
        <div className="space-y-3">
          {[1,2,3].map(i => (
            <div key={i} className="h-24 bg-gray-800/40 animate-pulse rounded-xl border border-gray-800" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {filtered.map((pr, i) => (
              <PRRiskCard key={pr.id} pr={pr} index={i} />
            ))}
          </AnimatePresence>
          
          {filtered.length === 0 && (
            <div className="text-center py-20 bg-[#111827] border border-gray-800 rounded-2xl">
              <p className="text-gray-500">No pull requests match the selected filter.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
