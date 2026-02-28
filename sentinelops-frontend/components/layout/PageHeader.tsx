interface PageHeaderProps {
  title: string
  subtitle: string
  badge?: string
  badgeColor?: "red" | "emerald" | "amber" | "indigo"
}

const badgeColors = {
  red: "bg-red-500/10 text-red-400 border-red-500/30",
  emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
  amber: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  indigo: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30",
}

export default function PageHeader({ title, subtitle, badge, badgeColor = "indigo" }: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-white">{title}</h1>
          {badge && (
            <span className={`text-xs px-2 py-0.5 rounded-full border font-mono font-bold ${badgeColors[badgeColor]}`}>
              {badge}
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
      </div>
    </div>
  )
}
