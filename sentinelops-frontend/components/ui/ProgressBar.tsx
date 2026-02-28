interface ProgressBarProps {
  value: number  // 0-100
  color?: "emerald" | "red" | "amber" | "indigo"
}

const colors = {
  emerald: "bg-emerald-500",
  red: "bg-red-500",
  amber: "bg-amber-500",
  indigo: "bg-indigo-500",
}

export default function ProgressBar({ value, color = "indigo" }: ProgressBarProps) {
  return (
    <div className="w-full bg-gray-800 rounded-full h-2">
      <div
        className={`h-2 rounded-full transition-all ${colors[color]}`}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  )
}
