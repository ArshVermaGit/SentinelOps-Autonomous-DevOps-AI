import { LucideIcon } from "lucide-react"

interface MetricCardProps {
  label: string
  value: string | number
  change: string
  changeType: "positive" | "negative" | "neutral"
  icon: LucideIcon
  color: "emerald" | "red" | "amber" | "indigo"
}

const colorMap = {
  emerald: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20" },
  red: { bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/20" },
  amber: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20" },
  indigo: { bg: "bg-indigo-500/10", text: "text-indigo-400", border: "border-indigo-500/20" },
}

export default function MetricCard({ label, value, change, changeType, icon: Icon, color }: MetricCardProps) {
  const colors = colorMap[color]
  const changeColor = changeType === "positive" ? "text-emerald-400" : changeType === "negative" ? "text-red-400" : "text-gray-400"
  
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          <p className={`text-xs mt-1 ${changeColor}`}>{change}</p>
        </div>
        <div className={`w-10 h-10 rounded-lg ${colors.bg} ${colors.border} border flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${colors.text}`} />
        </div>
      </div>
    </div>
  )
}
