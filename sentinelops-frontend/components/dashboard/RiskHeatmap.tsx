import { motion } from "framer-motion"
import { Shield, AlertTriangle, CheckCircle2 } from "lucide-react"

interface Repo {
  id: number
  name: string
  risk_score: number
}

export default function RiskHeatmap({ repos }: { repos: Repo[] }) {
  return (
    <div className="glass-card rounded-2xl p-6 h-full relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 blur-[50px] rounded-full" />
      
      <div className="flex items-center justify-between mb-6 relative z-10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center">
            <Shield className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <h3 className="font-bold text-white text-sm">Cluster Risk Heatmap</h3>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest font-medium">Real-time repository health</p>
          </div>
        </div>
        <div className="text-[10px] py-1 px-2 rounded-full bg-white/5 border border-white/5 text-gray-400">
          {repos.length} Repositories
        </div>
      </div>
      
      <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-4 lg:grid-cols-6 gap-2 relative z-10">
        {repos.map((repo, i) => {
          const intensity = repo.risk_score
          const bgColor = intensity > 0.7 
            ? "bg-red-500" 
            : intensity > 0.4 
            ? "bg-amber-500" 
            : "bg-emerald-500"
          
          return (
            <motion.div
              key={repo.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.02 }}
              whileHover={{ scale: 1.1, zIndex: 20 }}
              className="relative aspect-square group/tile"
            >
              <div 
                className={`w-full h-full rounded-md transition-all duration-500 cursor-pointer shadow-lg shadow-black/20 ${bgColor}`}
                style={{ 
                  opacity: 0.3 + (intensity * 0.7),
                  boxShadow: intensity > 0.7 ? "0 0 12px rgba(239, 68, 68, 0.4)" : "none"
                }}
              />
              
              {/* Premium Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-40 p-3 glass rounded-xl opacity-0 group-hover/tile:opacity-100 transition-opacity pointer-events-none z-30 shadow-2xl border border-white/10">
                <p className="text-xs font-bold text-white mb-1 truncate">{repo.name}</p>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-gray-400 font-medium">Risk Score</span>
                  <span className={`text-[10px] font-bold ${
                    intensity > 0.7 ? "text-red-400" : intensity > 0.4 ? "text-amber-400" : "text-emerald-400"
                  }`}>
                    {Math.round(intensity * 100)}%
                  </span>
                </div>
                <div className="mt-2 flex items-center gap-1.5">
                  {intensity > 0.7 ? (
                    <AlertTriangle className="w-3 h-3 text-red-400" />
                  ) : (
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  )}
                  <span className="text-[9px] text-gray-300">
                    {intensity > 0.7 ? "Immediate Audit Needed" : "Operational Stable"}
                  </span>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
      
      <div className="mt-6 pt-6 border-t border-white/5 flex items-center justify-between text-[10px]">
        <div className="flex items-center gap-4 text-gray-500">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Safe
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-amber-500" /> Warning
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]" /> High Risk
          </div>
        </div>
      </div>
    </div>
  )
}
