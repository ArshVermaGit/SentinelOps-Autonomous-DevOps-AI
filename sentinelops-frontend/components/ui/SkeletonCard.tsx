export default function SkeletonCard({ lines = 3, className = "" }: { lines?: number; className?: string }) {
  const widths = ["65%", "80%", "72%", "58%", "85%"]
  return (
    <div className={`bg-[#111827] border border-gray-800 rounded-xl p-5 animate-pulse ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-3">
          <div className="h-4 bg-gray-800 rounded-lg w-3/4" />
          {Array.from({ length: lines - 1 }).map((_, i) => (
            <div key={i} className="h-3 bg-gray-800/60 rounded-lg" style={{ width: widths[i % widths.length] }} />
          ))}
        </div>
        <div className="w-10 h-10 bg-gray-800 rounded-lg ml-4 shrink-0" />
      </div>
    </div>
  )
}
