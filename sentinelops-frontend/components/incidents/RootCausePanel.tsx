import { Brain, Clock, FileCode, AlertCircle } from "lucide-react"

interface Incident {
  error_category: string
  root_cause: string
  llm_confidence: number
  estimated_fix_time: string
  risk_if_unresolved: string
  responsible_files?: string[]
  suggested_fix?: string
}

export default function RootCausePanel({ incident }: { incident: Incident }) {
  const categoryColors: Record<string, string> = {
    dependency: "text-orange-400 bg-orange-400/10",
    syntax: "text-red-400 bg-red-400/10",
    test: "text-yellow-400 bg-yellow-400/10",
    config: "text-blue-400 bg-blue-400/10",
    runtime: "text-purple-400 bg-purple-400/10",
    network: "text-cyan-400 bg-cyan-400/10",
  }
  
  const catStyle = categoryColors[incident.error_category] || "text-gray-400 bg-gray-400/10"
  
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold text-white">AI Root Cause Analysis</h3>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-xs px-2 py-1 rounded-full font-mono ${catStyle}`}>
            {incident.error_category}
          </span>
          <span className="text-xs text-gray-500">
            {Math.round((incident.llm_confidence ?? 0) * 100)}% confidence
          </span>
        </div>
      </div>
      
      <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
        <p className="text-gray-200 text-sm leading-relaxed">{incident.root_cause}</p>
      </div>
      
      <div className="grid grid-cols-3 gap-4">
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <FileCode className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-xs text-gray-500 uppercase tracking-wider">Files</span>
          </div>
          <div className="space-y-1">
            {incident.responsible_files?.map((f: string) => (
              <div key={f} className="text-xs font-mono text-indigo-400 bg-indigo-400/10 px-2 py-1 rounded">
                {f}
              </div>
            ))}
          </div>
        </div>
        
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <Clock className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-xs text-gray-500 uppercase tracking-wider">Est. Fix Time</span>
          </div>
          <span className="text-sm text-emerald-400 font-medium">{incident.estimated_fix_time}</span>
        </div>
        
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <AlertCircle className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-xs text-gray-500 uppercase tracking-wider">Risk</span>
          </div>
          <p className="text-xs text-red-400">{incident.risk_if_unresolved}</p>
        </div>
      </div>
      
      <div>
        <span className="text-xs text-gray-500 uppercase tracking-wider block mb-2">Suggested Fix</span>
        <div className="bg-emerald-400/5 border border-emerald-400/20 rounded-lg p-3">
          <p className="text-sm text-emerald-300">{incident.suggested_fix}</p>
        </div>
      </div>
    </div>
  )
}
