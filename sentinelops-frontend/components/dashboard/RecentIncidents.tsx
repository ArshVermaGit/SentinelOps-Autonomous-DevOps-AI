"use client"
import { useEffect, useState } from "react"
import Link from "next/link"
import { apiClient } from "@/lib/api"
import { AlertTriangle, Brain } from "lucide-react"

interface Incident {
  id: number
  root_cause: string
  error_category: string
  status: string
  estimated_fix_time: string
}

export default function RecentIncidents() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  
  useEffect(() => {
    apiClient.get<Incident[]>("/incidents/?limit=5").then((r: { data: Incident[] }) => setIncidents(r.data)).catch(() => {})
  }, [])
  
  const categoryColors: Record<string, string> = {
    dependency: "text-orange-400 bg-orange-400/10",
    syntax: "text-red-400 bg-red-400/10",
    test: "text-yellow-400 bg-yellow-400/10",
    config: "text-blue-400 bg-blue-400/10",
    runtime: "text-purple-400 bg-purple-400/10",
    network: "text-cyan-400 bg-cyan-400/10",
  }
  
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-indigo-500/10 rounded-lg">
            <Brain className="w-4 h-4 text-indigo-400" />
          </div>
          <h3 className="font-semibold text-white tracking-tight">Recent AI Insights</h3>
        </div>
        <Link href="/incidents" className="text-[10px] uppercase font-bold tracking-wider text-indigo-400 hover:text-indigo-300 transition-colors">View All Explorer</Link>
      </div>
      
      <div className="space-y-2.5">
        {incidents.length === 0 && (
          <div className="py-8 text-center bg-gray-900/40 rounded-lg border border-dashed border-gray-800">
            <p className="text-sm text-gray-600">All systems operational ✅</p>
          </div>
        )}
        
        {incidents.map((inc) => (
          <Link
            key={inc.id}
            href={`/incidents/${inc.id}`}
            className="block p-3.5 bg-gray-900/60 border border-gray-800/50 rounded-xl hover:bg-gray-800 hover:border-indigo-500/30 transition-all group lg:hover:translate-x-1 duration-300"
          >
            <div className="flex items-start gap-3">
              <div className={`mt-0.5 p-1.5 rounded-lg shrink-0 ${inc.status === "open" ? "bg-red-400/10 text-red-400" : "bg-emerald-400/10 text-emerald-400"}`}>
                <AlertTriangle className="w-3.5 h-3.5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-200 line-clamp-1 group-hover:text-white transition-colors">{inc.root_cause}</p>
                <div className="flex items-center gap-3 mt-2">
                  <span className={`text-[9px] px-1.5 py-0.5 rounded-md font-bold uppercase tracking-wider ${categoryColors[inc.error_category] || "text-gray-500"}`}>
                    {inc.error_category}
                  </span>
                  <span className="text-[10px] text-gray-600 font-medium">{inc.estimated_fix_time}</span>
                  <span className={`text-[10px] font-bold uppercase ml-auto ${inc.status === "open" ? "text-red-400" : "text-emerald-400"}`}>
                    {inc.status}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
