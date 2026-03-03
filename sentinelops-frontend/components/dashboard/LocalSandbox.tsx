"use client"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { GitBranch, GitCommit, Rocket, AlertCircle, Terminal } from "lucide-react"
import { apiClient } from "@/lib/api"
import { useToastStore } from "@/components/ui/Toast"

interface LocalStatus {
  has_changes: boolean
  diff_summary?: {
    files_count: number
    max_complexity: number
  }
  risk?: {
    risk_level: string
    risk_probability: number
  }
}

type ToastState = { addToast: (msg: string, type: "success" | "error" | "info") => void }

export default function LocalSandbox() {
  const [status, setStatus] = useState<LocalStatus | null>(null)
  const [message, setMessage] = useState("")
  const [isSyncing, setIsSyncing] = useState(false)
  const addToast = useToastStore((state: ToastState) => state.addToast)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const r = await apiClient.get("/local/status")
        setStatus(r.data)
      } catch {
        // Silently fail — backend may not be running yet
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const handlePush = async () => {
    if (!message.trim()) {
      addToast("Please enter a commit message", "error")
      return
    }

    setIsSyncing(true)
    try {
      await apiClient.post("/local/commit", { message })
      addToast("Successfully pushed to GitHub!", "success")
      setMessage("")
    } catch {
      addToast("Failed to sync changes. Check your repository state.", "error")
    } finally {
      setIsSyncing(false)
    }
  }

  if (!status?.has_changes) return null

  const riskLevel = status.risk?.risk_level || "safe"
  const riskColor = riskLevel === "high" ? "text-red-400" : riskLevel === "caution" ? "text-amber-400" : "text-emerald-400"
  const riskBg = riskLevel === "high" ? "bg-red-500/10 border-red-500/30" : riskLevel === "caution" ? "bg-amber-500/10 border-amber-500/30" : "bg-emerald-500/10 border-emerald-500/30"

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass overflow-hidden rounded-3xl border border-white/10 flex flex-col h-full"
    >
      <div className="p-5 border-b border-white/5 bg-white/5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
            <Terminal className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white leading-none">Local Sandbox</h3>
            <p className="text-[10px] text-gray-500 mt-1">Real-time local risk detector</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Watching Changes</span>
        </div>
      </div>

      <div className="p-5 space-y-4 flex-1">
        {/* Risk Meter */}
        <div className={`p-4 rounded-2xl border ${riskBg} flex items-center justify-between`}>
          <div className="space-y-1">
            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Uncommitted Risk</p>
            <p className={`text-sm font-bold ${riskColor} capitalize`}>{riskLevel} Profile</p>
          </div>
          <div className="text-right">
            <p className="text-[10px] text-gray-500 font-medium">Staged Files</p>
            <p className="text-sm font-bold text-white">{status.diff_summary?.files_count ?? 0}</p>
          </div>
        </div>

        {/* Action Center */}
        <div className="space-y-3">
          <div className="relative">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Commit message..."
              className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
            />
            <GitCommit className="absolute left-3.5 top-3.5 w-4 h-4 text-gray-500" />
          </div>

          <button 
            onClick={handlePush}
            disabled={isSyncing || riskLevel === 'high'}
            className={`w-full py-3 rounded-xl flex items-center justify-center gap-2 text-xs font-bold transition-all ${
              riskLevel === 'high' 
                ? 'bg-red-500/20 text-red-300 cursor-not-allowed grayscale' 
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/25'
            }`}
          >
            {isSyncing ? (
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <Rocket className="w-4 h-4" />
                Push to GitHub
              </>
            )}
          </button>
          
          {riskLevel === 'high' && (
            <p className="text-[10px] text-red-400/80 text-center flex items-center justify-center gap-1.5 font-medium">
              <AlertCircle className="w-3 h-3" />
              Push blocked: Review critical risks before syncing.
            </p>
          )}
        </div>
      </div>

      <div className="p-4 bg-white/5 border-t border-white/5 mt-auto">
        <div className="flex items-center gap-2 text-[10px] text-gray-500">
          <GitBranch className="w-3 h-3" />
          <span>Local branch synchronized with origin/main</span>
        </div>
      </div>
    </motion.div>
  )
}
