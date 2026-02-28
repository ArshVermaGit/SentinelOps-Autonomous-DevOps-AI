"use client"
import { useState } from "react"

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
  const [activities] = useState<Activity[]>(MOCK_ACTIVITIES)
  
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
