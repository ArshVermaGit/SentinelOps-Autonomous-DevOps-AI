export interface Repository {
  id: number
  name: string
  full_name: string
  url: string
  risk_score: number
  failure_rate: number
  deployment_stability: number
  last_analyzed: string
}

export interface PullRequest {
  id: number
  github_pr_number: number
  title: string
  author: string
  lines_added: number
  lines_deleted: number
  files_changed: number
  has_config_changes: boolean
  has_test_changes: boolean
  has_dependency_changes: boolean
  risk_probability: number
  risk_level: "safe" | "caution" | "high"
  risk_factors: string[]
  status: "open" | "merged" | "closed"
  created_at: string
}

export interface CIRun {
  id: number
  workflow_name: string
  status: "success" | "failure" | "running" | "cancelled"
  duration_ms: number
  started_at: string
  finished_at: string
  is_anomalous_duration: boolean
  error_block?: string
  failure_step?: string
}

export interface Incident {
  id: number
  root_cause: string
  responsible_files: string[]
  error_category: string
  llm_confidence: number
  suggested_fix: string
  fix_diff: string
  estimated_fix_time: string
  risk_if_unresolved: string
  status: "open" | "simulated" | "resolved"
  similar_incident_id?: number
  similarity_score: number
  simulation_result?: SimulationResult
  ci_run?: CIRun
  created_at: string
}

export interface SimulationResult {
  success: boolean
  steps: SimulationStep[]
  predicted_outcome: string
  confidence: string
  tests_passed: number
  tests_failed: number
}

export interface SimulationStep {
  step: string
  status: "success" | "failure" | "skipped" | "running"
  duration_ms: number
}

export interface DashboardSummary {
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
  repos_list: Repository[]
}
