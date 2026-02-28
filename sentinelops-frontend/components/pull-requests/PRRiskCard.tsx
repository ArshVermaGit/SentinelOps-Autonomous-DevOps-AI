import { motion } from "framer-motion"
import { User, FileCode, Package } from "lucide-react"
import { getRiskColor, getRiskEmoji } from "@/lib/utils"
import RiskFactorList from "./RiskFactorList"

interface PR {
  id: number
  title: string
  author: string
  lines_added: number
  lines_deleted: number
  files_changed: number
  risk_level: string
  risk_probability: number
  risk_factors: string[]
  has_dependency_changes?: boolean
}

export default function PRRiskCard({ pr, index }: { pr: PR; index: number }) {
  const colors = getRiskColor(pr.risk_level)
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ delay: index * 0.05 }}
      className={`bg-[#111827] border rounded-xl p-5 ${colors.border} transition-all hover:bg-gray-800/40`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <div className={`mt-0.5 w-10 h-10 rounded-xl flex items-center justify-center text-xl ${colors.bg}`}>
            {getRiskEmoji(pr.risk_level)}
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-white truncate">{pr.title}</h3>
            <div className="flex flex-wrap items-center gap-4 mt-2">
              <span className="flex items-center gap-1.5 text-xs text-gray-500">
                <User className="w-3.5 h-3.5" /> {pr.author}
              </span>
              <span className="text-xs text-gray-600 font-mono">
                <span className="text-emerald-500">+{pr.lines_added}</span>
                <span className="mx-1">/</span>
                <span className="text-red-500">-{pr.lines_deleted}</span>
              </span>
              <span className="flex items-center gap-1.5 text-xs text-gray-500">
                <FileCode className="w-3.5 h-3.5" /> {pr.files_changed} files
              </span>
              {pr.has_dependency_changes && (
                <span className="flex items-center gap-1.5 text-xs text-amber-500 font-medium">
                  <Package className="w-3.5 h-3.5" /> DEPS CHANGED
                </span>
              )}
            </div>
            
            <div className="mt-4">
              <RiskFactorList factors={pr.risk_factors} riskLevel={pr.risk_level} />
            </div>
          </div>
        </div>
        
        <div className="text-right ml-6 shrink-0">
          <div className={`text-3xl font-bold font-mono ${colors.text}`}>
            {Math.round(pr.risk_probability * 100)}%
          </div>
          <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mt-1">
            failure risk
          </div>
        </div>
      </div>
    </motion.div>
  )
}
