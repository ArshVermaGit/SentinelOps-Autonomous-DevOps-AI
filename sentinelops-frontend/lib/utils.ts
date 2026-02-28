export function getRiskColor(level: "safe" | "caution" | "high" | string) {
  switch (level) {
    case "safe":
      return {
        text: "text-emerald-400",
        bg: "bg-emerald-400/10",
        border: "border-emerald-400/30",
        hex: "#10b981"
      }
    case "caution":
      return {
        text: "text-amber-400",
        bg: "bg-amber-400/10",
        border: "border-amber-400/30",
        hex: "#f59e0b"
      }
    case "high":
      return {
        text: "text-red-400",
        bg: "bg-red-400/10",
        border: "border-red-400/30",
        hex: "#ef4444"
      }
    default:
      return {
        text: "text-gray-400",
        bg: "bg-gray-400/10",
        border: "border-gray-400/30",
        hex: "#9ca3af"
      }
  }
}

export function getRiskEmoji(level: string) {
  return level === "safe" ? "🟢" : level === "caution" ? "🟡" : "🔴"
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  const mins = Math.floor(ms / 60000)
  const secs = Math.floor((ms % 60000) / 1000)
  return `${mins}m ${secs}s`
}

export function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return "just now"
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
  return `${Math.floor(diffMins / 1440)}d ago`
}

export function getRiskProbabilityLabel(prob: number): string {
  if (prob < 0.35) return "LOW"
  if (prob < 0.65) return "MEDIUM"
  return "HIGH"
}
