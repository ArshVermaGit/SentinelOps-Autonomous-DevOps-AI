"use client"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"
import { motion } from "framer-motion"

const CustomTooltip = ({ active, payload, label, formatter }: { 
  active?: boolean, 
  payload?: Array<{ value: number, name: string, color: string }>, 
  label?: string, 
  formatter?: (v: number) => string 
}) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass p-3 rounded-xl shadow-2xl border border-white/10">
        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">{label}</p>
        <div className="space-y-1">
          {payload.map((item, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="text-xs font-semibold text-white">
                {formatter ? formatter(item.value) : item.value}
                <span className="text-gray-500 ml-1 font-normal">{item.name}</span>
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }
  return null
}

export default function CIHealthChart() {
  const [data, setData] = useState<Array<{ date: string, success: number, failure: number, avg_duration: number }>>([])
  const [view, setView] = useState<"trend" | "duration">("trend")
  
  useEffect(() => {
    apiClient.get("/dashboard/ci-health").then(r => setData(r.data.data)).catch(() => {})
  }, [])
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-2xl p-6 relative overflow-hidden"
    >
      <div className="flex items-center justify-between mb-8">
        <div>
          <h3 className="text-lg font-bold text-white tracking-tight">CI Pipeline Health</h3>
          <p className="text-xs text-gray-500 mt-1">Real-time build stability and performance metrics</p>
        </div>
        <div className="flex bg-gray-950/50 p-1 rounded-lg border border-white/5">
          {["trend", "duration"].map(v => (
            <button
              key={v}
              onClick={() => setView(v as "trend" | "duration")}
              className={`px-4 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded-md transition-all ${
                view === v ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20" : "text-gray-500 hover:text-white"
              }`}
            >
              {v === "trend" ? "Success Rate" : "Build Time"}
            </button>
          ))}
        </div>
      </div>
      
      <div className="h-[250px] w-full">
        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
          {view === "trend" ? (
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorSuccess" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorFailure" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
              <XAxis 
                dataKey="date" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10, fill: "#4b5563", fontWeight: 500 }} 
                dy={10}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10, fill: "#4b5563", fontWeight: 500 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area 
                type="monotone" 
                dataKey="success" 
                stroke="#10b981" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorSuccess)" 
                name="Success"
              />
              <Area 
                type="monotone" 
                dataKey="failure" 
                stroke="#ef4444" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorFailure)" 
                name="Failure"
              />
            </AreaChart>
          ) : (
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorDuration" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
              <XAxis 
                dataKey="date" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10, fill: "#4b5563", fontWeight: 500 }}
                dy={10}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10, fill: "#4b5563", fontWeight: 500 }}
              />
              <Tooltip 
                content={<CustomTooltip formatter={(v: number) => `${Math.round(v/1000)}s`} />} 
              />
              <Area 
                type="monotone" 
                dataKey="avg_duration" 
                stroke="#6366f1" 
                strokeWidth={4}
                fillOpacity={1} 
                fill="url(#colorDuration)" 
                name="Avg Duration"
                dot={{ r: 4, fill: "#6366f1", strokeWidth: 2, stroke: "#030712" }}
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
    </motion.div>
  )
}
