import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"

interface DashboardData {
  repos: {
    total: number
    high_risk: number
    avg_risk_score: number
  }
  ci: {
    total_runs_30d: number
    failed_runs_30d: number
    success_rate: number
    avg_build_time_ms: number
  }
  incidents: {
    open: number
    total_30d: number
  }
  repos_list: Array<{
    id: number
    name: string
    risk_score: number
    failure_rate: number
  }>
}

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const r = await apiClient.get("/dashboard/summary")
        setData(r.data)
      } catch {
        setError("Failed to load dashboard data")
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])
  
  return { data, loading, error }
}
