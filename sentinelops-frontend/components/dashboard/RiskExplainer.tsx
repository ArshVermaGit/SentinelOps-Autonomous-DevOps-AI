"use client"
import { motion } from "framer-motion"
import { Info, ArrowUpRight, ArrowDownRight } from "lucide-react"

interface RiskDriver {
  feature: string
  impact: number
}

export default function RiskExplainer({ drivers }: { drivers: RiskDriver[] }) {
  const maxImpact = Math.max(...drivers.map(d => d.impact), 0.1)

  return (
    <div className="glass-card rounded-2xl p-5 border border-white/5 relative overflow-hidden h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            What&apos;s driving the risk?
            <Info className="w-3.5 h-3.5 text-gray-500" />
          </h3>
          <p className="text-[10px] text-gray-500 font-medium">Breakdown of the AI&apos;s scoring logic</p>
        </div>
      </div>

      <div className="space-y-4">
        {drivers.map((driver, i) => (
          <div key={i}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-medium text-gray-400 capitalize">{driver.feature.replace('_', ' ')}</span>
              <span className={`text-[11px] font-bold flex items-center gap-0.5 ${driver.impact > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                {driver.impact > 0 ? <ArrowUpRight className="w-2.5 h-2.5" /> : <ArrowDownRight className="w-2.5 h-2.5" />}
                +{Math.round(driver.impact * 100)}%
              </span>
            </div>
            <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(driver.impact / maxImpact) * 100}%` }}
                transition={{ duration: 1, delay: i * 0.1, ease: "circOut" }}
                className={`h-full rounded-full ${driver.impact > 0.15 ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]' : 'bg-indigo-400'}`}
              />
            </div>
          </div>
        ))}
      </div>

      {drivers.length > 0 && (
        <div className="mt-6 pt-4 border-t border-white/5">
          <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-3">
            <p className="text-[10px] text-indigo-300 leading-relaxed italic">
              AI Analysis: High impact drivers indicate potential regression risk in the largest {drivers[0].feature.replace('_', ' ')} changes.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
