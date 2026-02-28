"use client"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"

export default function CIHealthChart() {
  const [data, setData] = useState([])
  const [view, setView] = useState<"trend" | "duration">("trend")
  
  useEffect(() => {
    apiClient.get("/dashboard/ci-health").then(r => setData(r.data.data)).catch(() => {})
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
              onClick={() => setView(v as "trend" | "duration")}
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
              formatter={(v: number | string | undefined) => [`${Math.round(Number(v ?? 0)/1000)}s`, "Avg Duration"]}
            />
            <Line type="monotone" dataKey="avg_duration" stroke="#6366f1" strokeWidth={2} dot={false} />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}
