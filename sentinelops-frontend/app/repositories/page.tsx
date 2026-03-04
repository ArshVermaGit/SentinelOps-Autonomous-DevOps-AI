"use client"
import { useState } from "react"
import PageHeader from "@/components/layout/PageHeader"
import { useRepoManager, LinkedRepo } from "@/hooks/useRepoManager"
import { useToastStore } from "@/components/ui/Toast"
import { motion, AnimatePresence } from "framer-motion"
import {
  GitBranch, GitCommit, FolderGit2, CheckCircle2, XCircle,
  AlertTriangle, ChevronDown, ChevronUp, Rocket, Plus, Unlink, RefreshCw,
  ArrowUpCircle, ArrowDownCircle, Loader2
} from "lucide-react"

export default function RepositoriesPage() {
  const { repos, loading, linkRepo, unlinkRepo, commitRepo, refresh } = useRepoManager()
  const addToast = useToastStore(state => state.addToast)

  // Link form state
  const [showLinkForm, setShowLinkForm] = useState(false)
  const [linkName, setLinkName] = useState("")
  const [linkPath, setLinkPath] = useState("")
  const [linkUrl, setLinkUrl] = useState("")

  // Per-repo expanded state and commit messages
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})
  const [commitMsgs, setCommitMsgs] = useState<Record<string, string>>({})
  const [committing, setCommitting] = useState<Record<string, boolean>>({})

  const toggleExpand = (path: string) => {
    setExpanded(prev => ({ ...prev, [path]: !prev[path] }))
  }

  const handleLink = async () => {
    if (!linkName.trim() || !linkPath.trim()) {
      addToast("Please fill in repo name and local path", "error")
      return
    }
    try {
      await linkRepo(linkName, linkPath, linkUrl)
      addToast(`Linked ${linkName} successfully`, "success")
      setShowLinkForm(false)
      setLinkName("")
      setLinkPath("")
      setLinkUrl("")
    } catch {
      addToast("Failed to link repo. Make sure the path contains a .git folder.", "error")
    }
  }

  const handleCommit = async (repo: LinkedRepo) => {
    const msg = commitMsgs[repo.local_path]
    if (!msg?.trim()) {
      addToast("Enter a commit message first", "error")
      return
    }
    setCommitting(prev => ({ ...prev, [repo.local_path]: true }))
    try {
      await commitRepo(repo.local_path, msg)
      addToast(`Pushed ${repo.name} to GitHub!`, "success")
      setCommitMsgs(prev => ({ ...prev, [repo.local_path]: "" }))
    } catch {
      addToast("Commit/push failed — check your repo state", "error")
    } finally {
      setCommitting(prev => ({ ...prev, [repo.local_path]: false }))
    }
  }

  const totalChanges = (repo: LinkedRepo) => {
    const cf = repo.changed_files
    return (cf?.staged?.length || 0) + (cf?.modified?.length || 0) + (cf?.untracked?.length || 0)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Repository Manager"
        subtitle="Manage, monitor, and sync all your repos from one place"
        badge="SYNC"
      />

      {/* Action Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowLinkForm(f => !f)}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition-all"
          >
            <Plus className="w-4 h-4" />
            Link Repository
          </button>
          <button
            onClick={refresh}
            className="flex items-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white text-xs font-medium rounded-xl border border-white/10 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
        </div>
        <div className="text-xs text-gray-500">
          {repos.length} repo{repos.length !== 1 ? "s" : ""} linked &middot; Auto-syncing every 5s
        </div>
      </div>

      {/* Link Form */}
      <AnimatePresence>
        {showLinkForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="glass border border-white/10 rounded-2xl p-5 space-y-4">
              <h3 className="text-sm font-bold text-white">Link a Local Repository</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input
                  value={linkName}
                  onChange={e => setLinkName(e.target.value)}
                  placeholder="Repo name (e.g. SentinelOps)"
                  className="bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/50"
                />
                <input
                  value={linkPath}
                  onChange={e => setLinkPath(e.target.value)}
                  placeholder="Local path (e.g. ~/GitHub/SentinelOps)"
                  className="bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/50"
                />
                <input
                  value={linkUrl}
                  onChange={e => setLinkUrl(e.target.value)}
                  placeholder="GitHub URL (optional)"
                  className="bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/50"
                />
              </div>
              <button
                onClick={handleLink}
                className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl transition-all"
              >
                Connect Repository
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Repo Cards */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
        </div>
      ) : repos.length === 0 ? (
        <div className="text-center py-20 glass border border-white/10 rounded-2xl">
          <FolderGit2 className="w-10 h-10 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">No repositories linked yet.</p>
          <p className="text-gray-600 text-xs mt-1">Click &quot;Link Repository&quot; to connect your first repo.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {repos.map((repo) => {
            const isExpanded = expanded[repo.local_path]
            const changes = totalChanges(repo)
            const healthOk = repo.health?.passing
            const riskLevel = repo.risk?.risk_level || "safe"
            const syncState = repo.sync?.state || "synced"

            return (
              <motion.div
                key={repo.local_path}
                layout
                className="glass border border-white/10 rounded-2xl overflow-hidden"
              >
                {/* Header */}
                <div
                  className="p-5 flex items-center justify-between cursor-pointer hover:bg-white/2 transition-colors"
                  onClick={() => toggleExpand(repo.local_path)}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${
                      healthOk ? "bg-emerald-500/10 border-emerald-500/30" : "bg-red-500/10 border-red-500/30"
                    }`}>
                      {healthOk
                        ? <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                        : <XCircle className="w-5 h-5 text-red-400" />
                      }
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white">{repo.name}</div>
                      <div className="text-[10px] text-gray-500 mt-0.5 flex items-center gap-2">
                        <GitBranch className="w-3 h-3" />
                        {repo.branch || "main"}
                        <span className="text-gray-700">&middot;</span>
                        <span className="text-gray-500">{repo.local_path}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {/* Sync Badge */}
                    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider ${
                      syncState === "synced" ? "bg-emerald-500/10 text-emerald-400" :
                      syncState === "ahead" ? "bg-indigo-500/10 text-indigo-400" :
                      syncState === "behind" ? "bg-amber-500/10 text-amber-400" :
                      "bg-red-500/10 text-red-400"
                    }`}>
                      {syncState === "ahead" && <ArrowUpCircle className="w-3 h-3" />}
                      {syncState === "behind" && <ArrowDownCircle className="w-3 h-3" />}
                      {syncState} {repo.sync?.ahead > 0 && `+${repo.sync.ahead}`} {repo.sync?.behind > 0 && `-${repo.sync.behind}`}
                    </div>

                    {/* Changes Badge */}
                    {changes > 0 && (
                      <div className="px-2.5 py-1 bg-amber-500/10 text-amber-400 rounded-lg text-[10px] font-bold">
                        {changes} change{changes !== 1 ? "s" : ""}
                      </div>
                    )}

                    {/* Health Badge */}
                    <div className={`px-2.5 py-1 rounded-lg text-[10px] font-bold ${
                      healthOk ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"
                    }`}>
                      {healthOk ? "Healthy" : `${repo.health?.error_count || 0} Error${(repo.health?.error_count || 0) !== 1 ? "s" : ""}`}
                    </div>

                    {/* Risk Badge */}
                    <div className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase ${
                      riskLevel === "safe" ? "bg-emerald-500/10 text-emerald-400" :
                      riskLevel === "caution" ? "bg-amber-500/10 text-amber-400" :
                      "bg-red-500/10 text-red-400"
                    }`}>
                      {riskLevel}
                    </div>

                    {isExpanded
                      ? <ChevronUp className="w-4 h-4 text-gray-500" />
                      : <ChevronDown className="w-4 h-4 text-gray-500" />
                    }
                  </div>
                </div>

                {/* Expandable Detail */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-5 pb-5 space-y-4 border-t border-white/5 pt-4">

                        {/* Changed Files */}
                        {changes > 0 && (
                          <div className="space-y-2">
                            <h4 className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Changed Files</h4>
                            <div className="grid grid-cols-1 gap-1 max-h-40 overflow-y-auto">
                              {repo.changed_files?.staged?.map(f => (
                                <div key={`s-${f}`} className="flex items-center gap-2 text-xs px-3 py-1.5 bg-emerald-500/5 rounded-lg">
                                  <span className="text-[10px] font-bold text-emerald-400 w-14">STAGED</span>
                                  <span className="text-gray-300 font-mono text-[11px]">{f}</span>
                                </div>
                              ))}
                              {repo.changed_files?.modified?.map(f => (
                                <div key={`m-${f}`} className="flex items-center gap-2 text-xs px-3 py-1.5 bg-amber-500/5 rounded-lg">
                                  <span className="text-[10px] font-bold text-amber-400 w-14">MODIFIED</span>
                                  <span className="text-gray-300 font-mono text-[11px]">{f}</span>
                                </div>
                              ))}
                              {repo.changed_files?.untracked?.map(f => (
                                <div key={`u-${f}`} className="flex items-center gap-2 text-xs px-3 py-1.5 bg-gray-500/5 rounded-lg">
                                  <span className="text-[10px] font-bold text-gray-500 w-14">NEW</span>
                                  <span className="text-gray-400 font-mono text-[11px]">{f}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Errors */}
                        {!healthOk && repo.health?.errors && repo.health.errors.length > 0 && (
                          <div className="space-y-2">
                            <h4 className="text-[10px] text-red-400 font-bold uppercase tracking-widest flex items-center gap-1.5">
                              <AlertTriangle className="w-3 h-3" />
                              Errors ({repo.health.error_count})
                            </h4>
                            <div className="space-y-1 max-h-40 overflow-y-auto">
                              {repo.health.errors.map((err, i) => (
                                <div key={i} className="text-[11px] font-mono text-red-300/80 bg-red-500/5 px-3 py-2 rounded-lg border border-red-500/10">
                                  {err}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Commit Section */}
                        <div className="flex items-center gap-3 pt-2">
                          <div className="relative flex-1">
                            <input
                              value={commitMsgs[repo.local_path] || ""}
                              onChange={e => setCommitMsgs(prev => ({ ...prev, [repo.local_path]: e.target.value }))}
                              placeholder="Commit message..."
                              className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                            />
                            <GitCommit className="absolute left-3.5 top-3.5 w-4 h-4 text-gray-500" />
                          </div>

                          <button
                            onClick={() => handleCommit(repo)}
                            disabled={!repo.ready_to_commit || committing[repo.local_path]}
                            className={`flex items-center gap-2 px-5 py-3 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                              repo.ready_to_commit
                                ? "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/25"
                                : "bg-gray-800 text-gray-500 cursor-not-allowed"
                            }`}
                          >
                            {committing[repo.local_path] ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Rocket className="w-4 h-4" />
                            )}
                            Push to GitHub
                          </button>

                          <button
                            onClick={() => { unlinkRepo(repo.local_path); addToast(`Unlinked ${repo.name}`, "info") }}
                            className="p-3 bg-white/5 hover:bg-red-500/10 text-gray-500 hover:text-red-400 rounded-xl border border-white/10 transition-all"
                            title="Unlink this repo"
                          >
                            <Unlink className="w-4 h-4" />
                          </button>
                        </div>

                        {!repo.ready_to_commit && changes > 0 && (
                          <p className="text-[10px] text-amber-400/80 flex items-center gap-1.5">
                            <AlertTriangle className="w-3 h-3" />
                            {!healthOk
                              ? "Fix errors before pushing. Resolve them one by one above."
                              : "Stage your changes (git add) to unlock the push button."
                            }
                          </p>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </div>
      )}
    </div>
  )
}
