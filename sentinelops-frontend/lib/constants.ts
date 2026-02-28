export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws"

export const RISK_LEVELS = ["safe", "caution", "high"] as const
export type RiskLevel = (typeof RISK_LEVELS)[number]

export const REFRESH_INTERVAL = 30000 // 30 seconds

export const ERROR_CATEGORIES = [
  "dependency",
  "syntax",
  "test",
  "config",
  "runtime",
  "network"
] as const
