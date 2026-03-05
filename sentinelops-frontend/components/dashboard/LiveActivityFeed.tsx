"use client"
import { useState, useEffect } from "react"
import { useWebSocket } from "@/hooks/useWebSocket"
import { apiClient } from "@/lib/api"

interface Activity {
  id: string
  type: "failure" | "success" | "pr_risk" | "incident"
  message: string
  time: string
  repo?: string
}

export default function LiveActivityFeed() {
  const [activities, setActivities] = useState<Activity[]>([])
  
  useEffect(() => {
    // Fetch initial dynamic data, zero hardcoding
    apiClient.get("/dashboard/activities?limit=10").then(r => setActivities(r.data))
  }, [])
  
  useWebSocket((data) => {
    const newActivity: Activity = {
      id: Date.now().toString(),
      type: data.type === "ci_failure" ? "failure" : data.type === "new_incident" ? "incident" : "success",
      message: data.message as string,
      time: "just now",
      repo: data.repo_name as string,
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
        {activities.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/20 animate-pulse mb-3" />
            <p className="text-[10px] text-gray-600 font-medium leading-relaxed">
              No recent activity detected.<br/>Linked repositories are currently stable.
            </p>
          </div>
        )}
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
