interface BadgeProps {
  text: string
  variant?: "default" | "success" | "danger" | "warning" | "info"
}

const variants = {
  default: "bg-gray-400/10 text-gray-400 border-gray-400/30",
  success: "bg-emerald-400/10 text-emerald-400 border-emerald-400/30",
  danger: "bg-red-400/10 text-red-400 border-red-400/30",
  warning: "bg-amber-400/10 text-amber-400 border-amber-400/30",
  info: "bg-indigo-400/10 text-indigo-400 border-indigo-400/30",
}

export default function Badge({ text, variant = "default" }: BadgeProps) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${variants[variant]}`}>
      {text}
    </span>
  )
}
