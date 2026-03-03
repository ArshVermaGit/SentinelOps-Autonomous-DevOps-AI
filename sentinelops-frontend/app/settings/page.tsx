"use client"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import { ToggleRight, ToggleLeft, Bell, Brain, Database, ExternalLink } from "lucide-react"
import { useToastStore } from "@/components/ui/Toast"
import { motion, AnimatePresence } from "framer-motion"

interface RepoSetting {
  id: number
  name: string
  full_name: string
  url: string
  is_active: boolean
  risk_score: number
  failure_rate: number
  last_analyzed: string | null
}

interface SettingsData {
  repositories: RepoSetting[]
  notifications: {
    email_enabled: boolean
    slack_enabled: boolean
    webhook_url: string | null
    notify_on_high_risk_pr: boolean
    notify_on_ci_failure: boolean
    notify_on_incident: boolean
  }
  ai: {
    openai_model: string
    ml_model_trained: boolean
    embedding_model: string
  }
}

export default function SettingsPage() {
  const [data, setData] = useState<SettingsData | null>(null)
  const [activeTab, setActiveTab] = useState<"repos" | "notifications" | "ai">("repos")
  const addToast = useToastStore(state => state.addToast)

  useEffect(() => {
    apiClient.get("/settings/")
      .then(r => setData(r.data))
      .catch(() => addToast("Failed to fetch settings", "error"))
  }, [addToast])

  const toggleRepo = async (repoId: number) => {
    try {
      const r = await apiClient.put(`/settings/repositories/${repoId}/toggle`)
      setData(prev => prev ? {
        ...prev,
        repositories: prev.repositories.map(repo =>
          repo.id === repoId ? { ...repo, is_active: r.data.is_active } : repo
        )
      } : prev)
      addToast(`Repository ${r.data.is_active ? "enabled" : "disabled"}`, "success")
    } catch {
      addToast("Failed to toggle repository", "error")
    }
  }

  const tabs = [
    { key: "repos" as const, label: "Repositories", icon: Database },
    { key: "notifications" as const, label: "Notifications", icon: Bell },
    { key: "ai" as const, label: "AI / ML", icon: Brain },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Platform Settings"
        subtitle="Configure repositories, notifications, and AI/ML preferences"
      />

      {/* Tab Navigation */}
      <div className="flex gap-2">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-all ${
              activeTab === tab.key
                ? "bg-indigo-600 text-white"
                : "bg-gray-800 text-gray-400 hover:text-white"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {activeTab === "repos" && (
          <motion.div
            key="repos"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-3"
          >
            {data?.repositories.map(repo => (
              <div
                key={repo.id}
                className="bg-[#111827] border border-gray-800 rounded-xl p-5 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <Database className={`w-5 h-5 ${repo.is_active ? "text-emerald-400" : "text-gray-600"}`} />
                  <div>
                    <div className="font-medium text-white">{repo.name}</div>
                    <div className="text-xs text-gray-500">{repo.full_name}</div>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="text-xs text-gray-500">Risk Score</div>
                    <div className={`text-sm font-mono font-bold ${
                      repo.risk_score > 0.65 ? "text-red-400" :
                      repo.risk_score > 0.35 ? "text-amber-400" : "text-emerald-400"
                    }`}>{Math.round(repo.risk_score * 100)}%</div>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-gray-500">Failure Rate</div>
                    <div className="text-sm font-mono text-gray-300">{Math.round(repo.failure_rate * 100)}%</div>
                  </div>

                  <a href={repo.url} target="_blank" rel="noreferrer" className="text-gray-500 hover:text-white transition-colors">
                    <ExternalLink className="w-4 h-4" />
                  </a>

                  <button onClick={() => toggleRepo(repo.id)} className="text-gray-400 hover:text-white transition-colors">
                    {repo.is_active ? (
                      <ToggleRight className="w-7 h-7 text-emerald-400" />
                    ) : (
                      <ToggleLeft className="w-7 h-7 text-gray-600" />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </motion.div>
        )}

        {activeTab === "notifications" && (
          <motion.div
            key="notifications"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-[#111827] border border-gray-800 rounded-xl p-6 space-y-5"
          >
            <h3 className="font-semibold text-white mb-4">Notification Preferences</h3>

            {[
              { label: "High-Risk PR Alerts", desc: "Get notified when a PR scores above 65% failure risk", enabled: data?.notifications.notify_on_high_risk_pr },
              { label: "CI Failure Alerts", desc: "Instant notifications on CI pipeline failures", enabled: data?.notifications.notify_on_ci_failure },
              { label: "Incident Alerts", desc: "Alerts when new incidents are detected by AI", enabled: data?.notifications.notify_on_incident },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between py-3 border-b border-gray-800 last:border-0">
                <div>
                  <div className="text-sm text-white font-medium">{item.label}</div>
                  <div className="text-xs text-gray-500 mt-0.5">{item.desc}</div>
                </div>
                <div className={`px-3 py-1 rounded-lg text-xs font-bold ${
                  item.enabled ? "bg-emerald-400/10 text-emerald-400" : "bg-gray-800 text-gray-500"
                }`}>
                  {item.enabled ? "Enabled" : "Disabled"}
                </div>
              </div>
            ))}

            <div className="pt-4 border-t border-gray-800">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-3">Channels</div>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: "Email", enabled: data?.notifications.email_enabled },
                  { label: "Slack", enabled: data?.notifications.slack_enabled },
                  { label: "Webhook", enabled: !!data?.notifications.webhook_url },
                ].map((ch, i) => (
                  <div key={i} className={`text-center p-3 rounded-xl border ${
                    ch.enabled ? "bg-indigo-400/10 border-indigo-400/30 text-indigo-400" : "bg-gray-800/50 border-gray-700 text-gray-500"
                  }`}>
                    <div className="text-sm font-medium">{ch.label}</div>
                    <div className="text-xs mt-1">{ch.enabled ? "Connected" : "Not configured"}</div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === "ai" && (
          <motion.div
            key="ai"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-[#111827] border border-gray-800 rounded-xl p-6 space-y-5"
          >
            <h3 className="font-semibold text-white mb-4">AI & ML Configuration</h3>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">LLM Model</p>
                <p className="text-lg font-bold font-mono text-indigo-400">{data?.ai.openai_model}</p>
                <p className="text-xs text-gray-500 mt-1">Root cause analysis engine</p>
              </div>
              <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">ML Predictor</p>
                <p className="text-lg font-bold font-mono text-emerald-400">
                  {data?.ai.ml_model_trained ? "Trained ✓" : "Not Trained"}
                </p>
                <p className="text-xs text-gray-500 mt-1">CI failure probability model</p>
              </div>
              <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Embedding Model</p>
                <p className="text-lg font-bold font-mono text-amber-400">{data?.ai.embedding_model}</p>
                <p className="text-xs text-gray-500 mt-1">Incident similarity search</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
