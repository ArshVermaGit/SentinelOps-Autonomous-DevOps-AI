"use client"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import RootCausePanel from "@/components/incidents/RootCausePanel"
import DiffViewer from "@/components/incidents/DiffViewer"
import SimulationModal from "@/components/incidents/SimulationModal"
import SimilarityBadge from "@/components/incidents/SimilarityBadge"
import IncidentMemoryGraph from "@/components/graph/IncidentMemoryGraph"

interface GraphData {
  pr_id: string;
  pr_title: string;
  author: string;
  author_failure_rate: number;
  commits: Array<{
    sha: string;
    message: string;
  }>;
  files: string[];
  ci_run_id: string;
  ci_status: string;
  incident_title: string;
}

interface Incident {
  id: number
  status: string
  error_category: string
  root_cause: string
  llm_confidence: number
  estimated_fix_time: string
  risk_if_unresolved: string
  suggested_fix: string
  fix_diff: string
  similar_incident_id?: number
  similarity_score?: number
  ci_run?: {
    id: string
    workflow_name: string
    repository?: {
      name: string
    }
  }
  relationship_data?: GraphData
}

export default function IncidentDetailPage() {
  const { id } = useParams()
  const [incident, setIncident] = useState<Incident | null>(null)
  const [loading, setLoading] = useState(true)
  const [showSim, setShowSim] = useState(false)
  
  useEffect(() => {
    apiClient.get<Incident>(`/incidents/${id}`).then((r: { data: Incident }) => {
      setIncident(r.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])
  
  if (loading) return <div className="text-gray-400 p-8 flex items-center gap-3">
    <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
    Analyzing incident...
  </div>
  if (!incident) return <div className="text-red-400 p-8">Incident not found</div>
  
  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader
        title={`Incident #${id}`}
        subtitle={`Detected in: ${incident.ci_run?.workflow_name} — ${incident.ci_run?.repository?.name || "Unknown"}`}
        badge={incident.status === "open" ? "OPEN" : incident.status.toUpperCase()}
        badgeColor={incident.status === "open" ? "red" : "emerald"}
      />
      
      {/* Similarity badge */}
      {incident.similar_incident_id && incident.similarity_score && (
        <SimilarityBadge
          similarId={incident.similar_incident_id}
          score={incident.similarity_score}
        />
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Root Cause Panel */}
        <RootCausePanel incident={incident} />
        
        {/* Memory Graph */}
        <IncidentMemoryGraph data={incident.relationship_data} />
      </div>
      
      {/* Suggested Fix Diff */}
      {incident.fix_diff && (
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white">Suggested Fix</h3>
            <button
              onClick={() => setShowSim(true)}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm rounded-lg transition-all flex items-center gap-2"
            >
              ⚡ Simulate Fix
            </button>
          </div>
          <DiffViewer diff={incident.fix_diff} />
        </div>
      )}
      
      {/* Simulation Modal */}
      {showSim && (
        <SimulationModal
          incidentId={id as string}
          onClose={() => setShowSim(false)}
        />
      )}
    </div>
  )
}
