import Link from "next/link"
import { AlertTriangle, ChevronRight } from "lucide-react"

interface Incident {
  id: number
  root_cause: string
  error_category: string
  status: string
  llm_confidence: number
  estimated_fix_time: string
}

const categoryColors: Record<string, string> = {
  dependency: "text-orange-400 bg-orange-400/10",
  syntax: "text-red-400 bg-red-400/10",
  test: "text-yellow-400 bg-yellow-400/10",
  config: "text-blue-400 bg-blue-400/10",
  runtime: "text-purple-400 bg-purple-400/10",
  network: "text-cyan-400 bg-cyan-400/10",
}

export default function IncidentCard({ incident }: { incident: Incident }) {
  const catStyle = categoryColors[incident.error_category] || "text-gray-400 bg-gray-400/10"
  
  return (
    <Link
      href={`/incidents/${incident.id}`}
      className="block bg-[#111827] border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-all group"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <div className={`mt-0.5 p-2 rounded-lg shrink-0 ${incident.status === "open" ? "bg-red-400/10 text-red-400" : "bg-emerald-400/10 text-emerald-400"}`}>
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-gray-200 line-clamp-2 leading-relaxed mb-3">
              {incident.root_cause}
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <span className={`text-[10px] sm:text-xs px-2 py-0.5 rounded-full font-medium ${catStyle}`}>
                {incident.error_category.toUpperCase()}
              </span>
              <span className="text-xs text-gray-500 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                {Math.round((incident.llm_confidence ?? 0) * 100)}% confidence
              </span>
              <span className="text-xs text-gray-500">{incident.estimated_fix_time}</span>
              <span className={`text-xs font-bold uppercase ${incident.status === "open" ? "text-red-400" : "text-emerald-400"}`}>
                {incident.status}
              </span>
            </div>
          </div>
        </div>
        <div className="ml-4 flex items-center justify-center h-full self-center">
          <ChevronRight className="text-gray-600 group-hover:text-white transition-colors" />
        </div>
      </div>
    </Link>
  )
}
