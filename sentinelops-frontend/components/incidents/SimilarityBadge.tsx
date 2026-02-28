import Link from "next/link"
import { GitMerge } from "lucide-react"

export default function SimilarityBadge({ similarId, score }: { similarId: number; score: number }) {
  return (
    <div className="flex items-center gap-2 bg-amber-400/10 border border-amber-400/30 rounded-lg px-4 py-2.5">
      <GitMerge className="w-4 h-4 text-amber-400" />
      <span className="text-sm text-amber-300">
        <strong>{Math.round(score * 100)}% similar</strong> to{" "}
        <Link href={`/incidents/${similarId}`} className="underline underline-offset-2 hover:text-amber-200">
          Incident #{similarId}
        </Link>
        {" "}— same root cause pattern detected previously
      </span>
    </div>
  )
}
