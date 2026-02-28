import Link from "next/link"
import { getRiskColor } from "@/lib/utils"

interface Repo {
  id: number
  name: string
  risk_score: number
}

export default function RiskHeatmap({ repos }: { repos: Repo[] }) {
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white">Repository Risk Heatmap</h3>
        <Link href="/repositories" className="text-xs text-indigo-400 hover:text-indigo-300">View all →</Link>
      </div>
      
      <div className="space-y-3">
        {repos.map((repo) => {
          const riskLevel = repo.risk_score > 0.65 ? "high" : repo.risk_score > 0.35 ? "caution" : "safe"
          const colors = getRiskColor(riskLevel)
          
          return (
            <div key={repo.id} className="flex items-center gap-3">
              <div className="w-32 text-sm text-gray-400 truncate">{repo.name}</div>
              <div className="flex-1 bg-gray-800 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    riskLevel === "high" ? "bg-red-500" :
                    riskLevel === "caution" ? "bg-amber-500" : "bg-emerald-500"
                  }`}
                  style={{ width: `${repo.risk_score * 100}%` }}
                />
              </div>
              <span className={`text-xs font-mono w-8 text-right ${colors.text}`}>
                {Math.round(repo.risk_score * 100)}%
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
