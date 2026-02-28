"use client"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import IncidentCard from "@/components/incidents/IncidentCard"

interface Incident {
  id: number
  root_cause: string
  error_category: string
  status: string
  llm_confidence: number
  estimated_fix_time: string
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    apiClient.get<Incident[]>("/incidents/").then((r: { data: Incident[] }) => {
      setIncidents(r.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])
  
  return (
    <div className="space-y-6">
      <PageHeader
        title="Incident Explorer"
        subtitle="AI-analyzed CI failures with root cause and suggested fixes"
      />
      
      {loading ? (
        <div className="flex flex-col gap-4">
          {[1,2,3].map(i => (
            <div key={i} className="h-32 bg-gray-800/50 animate-pulse rounded-xl" />
          ))}
        </div>
      ) : incidents.length > 0 ? (
        <div className="grid gap-4">
          {incidents.map((inc) => (
            <IncidentCard key={inc.id} incident={inc} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20 bg-[#111827] border border-gray-800 rounded-2xl">
          <p className="text-gray-500">No incidents detected yet.</p>
        </div>
      )}
    </div>
  )
}
