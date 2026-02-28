import { getRiskEmoji, getRiskColor } from "@/lib/utils"

export default function RiskTrafficLight({ level }: { level: "safe" | "caution" | "high" }) {
  const colors = getRiskColor(level)
  return (
    <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg ${colors.bg} ${colors.border} border`}>
      {getRiskEmoji(level)}
    </div>
  )
}
