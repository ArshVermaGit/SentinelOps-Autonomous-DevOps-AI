export default function RealTimeDot({ active = true }: { active?: boolean }) {
  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-2 h-2 rounded-full ${active ? "bg-emerald-400 animate-pulse" : "bg-gray-600"}`} />
      <span className="text-xs text-gray-500">{active ? "Live" : "Offline"}</span>
    </div>
  )
}
