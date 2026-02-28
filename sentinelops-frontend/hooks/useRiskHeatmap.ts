import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"

interface HeatmapData {
  repos: Array<{
    name: string
    risk_score: number
    failure_rate: number
    last_analyzed: string
  }>
}

export function useRiskHeatmap() {
  const [data, setData] = useState<HeatmapData | null>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    apiClient.get("/dashboard/risk-heatmap")
      .then(r => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])
  
  return { data, loading }
}
