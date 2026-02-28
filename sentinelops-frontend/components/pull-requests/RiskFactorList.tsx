import { getRiskColor } from "@/lib/utils"

export default function RiskFactorList({ factors, riskLevel }: { factors: string[]; riskLevel: string }) {
  const colors = getRiskColor(riskLevel)
  
  if (!factors?.length) return null
  
  return (
    <div className="flex flex-wrap gap-1.5">
      {factors.map((factor, i) => (
        <span key={i} className={`text-xs px-2 py-0.5 rounded-full ${colors.bg} ${colors.text}`}>
          {factor}
        </span>
      ))}
    </div>
  )
}
