import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"

interface Incident {
  id: number
  root_cause: string
  error_category: string
  status: string
  estimated_fix_time: string
}

export function useIncidents(limit: number = 20) {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    apiClient.get(`/incidents/?limit=${limit}`)
      .then(r => setIncidents(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [limit])
  
  return { incidents, loading }
}
