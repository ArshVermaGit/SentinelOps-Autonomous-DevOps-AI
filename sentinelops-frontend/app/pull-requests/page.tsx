"use client"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import { getRiskColor, getRiskEmoji } from "@/lib/utils"
import { User, FileCode, Package } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { PullRequest } from "@/types"
import { useSearchStore } from "@/hooks/useSearchStore"
import { useToastStore } from "@/components/ui/Toast"

export default function PullRequestsPage() {
  const [prs, setPrs] = useState<PullRequest[]>([])
  const [filter, setFilter] = useState<string>("all")
  const [loading, setLoading] = useState(true)
  const query = useSearchStore(state => state.query)
  const addToast = useToastStore(state => state.addToast)
  
  useEffect(() => {
    apiClient.get("/pull-requests/")
      .then(r => {
        setPrs(r.data)
        setLoading(false)
      })
      .catch(() => {
        addToast("Failed to fetch pull requests", "error")
        setLoading(false)
      })
  }, [addToast])
  
  const filtered = (filter === "all" ? prs : prs.filter(pr => pr.risk_level === filter))
    .filter(pr => 
      pr.title.toLowerCase().includes(query.toLowerCase()) ||
      pr.author.toLowerCase().includes(query.toLowerCase())
    )
  
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
        {loading ? (
          [1,2,3].map(i => <div key={i} className="h-24 bg-gray-800/50 animate-pulse rounded-xl" />)
        ) : filtered.length > 0 ? (
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
                      <div className={`mt-0.5 w-8 h-8 rounded-lg flex items-center justify-center text-lg ${colors.bg}`}>
                        {getRiskEmoji(pr.risk_level)}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <div className="font-medium text-white">{pr.title}</div>
                          {pr.github_pr_number === 0 && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 tracking-tight uppercase">
                              Local
                            </span>
                          )}
                        </div>
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
        ) : (
          <div className="text-center py-20 bg-[#111827] border border-gray-800 rounded-2xl">
            <p className="text-gray-500">
              {query 
                ? `No pull requests matching "${query}"` 
                : filter !== "all" 
                  ? `No ${filter} risk PRs found.` 
                  : "No pull requests detected yet."}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
