"use client"
import { useEffect, useState, useRef, useCallback } from "react"
import { apiClient } from "@/lib/api"
import { Bell, AlertTriangle, GitPullRequest, Zap, Check, Info } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import Link from "next/link"

interface NotificationItem {
  id: number
  type: string
  severity: string
  title: string
  message: string
  is_read: string
  incident_id: number | null
  ci_run_id: number | null
  pr_id: number | null
  created_at: string
}

const typeIcons: Record<string, typeof AlertTriangle> = {
  incident: AlertTriangle,
  ci_failure: Zap,
  pr_risk: GitPullRequest,
  system: Info,
}

const severityColors: Record<string, string> = {
  critical: "text-red-400",
  warning: "text-amber-400",
  info: "text-indigo-400",
}

export default function NotificationDropdown() {
  const [open, setOpen] = useState(false)
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    apiClient.get("/settings/notifications?limit=10")
      .then(r => setNotifications(r.data))
      .catch(() => {})
  }, [])

  const unreadCount = notifications.filter(n => n.is_read === "unread").length

  const markAllRead = async () => {
    try {
      await apiClient.post("/settings/notifications/read", { mark_all: true })
      setNotifications(prev => prev.map(n => ({ ...n, is_read: "read" })))
    } catch {
      // Silently fail
    }
  }

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const formatTime = useCallback((dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return "just now"
    if (mins < 60) return `${mins}m ago`
    if (mins < 1440) return `${Math.floor(mins / 60)}h ago`
    return `${Math.floor(mins / 1440)}d ago`
  }, [])

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-all"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        )}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -5, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -5, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-12 w-96 bg-[#111827] border border-gray-700 rounded-xl shadow-2xl z-50 overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-800">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-white text-sm">Notifications</h3>
                {unreadCount > 0 && (
                  <span className="text-xs bg-red-500/10 text-red-400 border border-red-500/20 px-1.5 py-0.5 rounded-full font-bold">
                    {unreadCount}
                  </span>
                )}
              </div>
              {unreadCount > 0 && (
                <button
                  onClick={markAllRead}
                  className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                >
                  <Check className="w-3 h-3" /> Mark all read
                </button>
              )}
            </div>

            {/* Notification List */}
            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <p className="text-sm text-gray-600 text-center py-8">No notifications</p>
              ) : (
                notifications.map(n => {
                  const Icon = typeIcons[n.type] || Info
                  const color = severityColors[n.severity] || "text-gray-400"

                  return (
                    <Link
                      key={n.id}
                      href={n.incident_id ? `/incidents/${n.incident_id}` : "/dashboard"}
                      onClick={() => setOpen(false)}
                      className={`block px-4 py-3 hover:bg-gray-800/50 transition-all border-b border-gray-800/50 last:border-0 ${
                        n.is_read === "unread" ? "bg-indigo-500/5" : ""
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${color}`} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-xs font-medium text-white truncate">{n.title}</p>
                            {n.is_read === "unread" && (
                              <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full shrink-0" />
                            )}
                          </div>
                          <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{n.message}</p>
                          <p className="text-[10px] text-gray-600 mt-1">{formatTime(n.created_at)}</p>
                        </div>
                      </div>
                    </Link>
                  )
                })
              )}
            </div>

            {/* Footer */}
            <div className="border-t border-gray-800 p-3 text-center">
              <Link
                href="/settings"
                onClick={() => setOpen(false)}
                className="text-xs text-indigo-400 hover:text-indigo-300"
              >
                View all notifications →
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
