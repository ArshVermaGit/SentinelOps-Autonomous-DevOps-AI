"use client"
import Image from "next/image"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  LayoutDashboard, GitPullRequest, AlertTriangle, 
  BarChart3, GitBranch
} from "lucide-react"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/repositories", label: "Risk Heatmap", icon: GitBranch },
  { href: "/pull-requests", label: "PR Gatekeeper", icon: GitPullRequest },
  { href: "/incidents", label: "Incidents", icon: AlertTriangle },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
]

export default function Sidebar() {
  const pathname = usePathname()
  
  return (
    <aside className="w-64 bg-[#111827] border-r border-gray-800 flex flex-col shrink-0">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <Image 
            src="/logo.png" 
            alt="SentinelOps Logo" 
            width={36} 
            height={36} 
            className="w-9 h-9 rounded-lg object-contain" 
          />
          <div className="flex flex-col">
          <span className="font-bold text-white tracking-tight">SentinelOps</span>
          <span className="text-[10px] text-gray-500 font-medium">By Arsh Verma</span>
        </div>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                active
                  ? "bg-indigo-600/20 text-indigo-400 border border-indigo-600/30"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          )
        })}
      </nav>
      
      {/* Live status */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Monitoring 4 repositories</span>
        </div>
      </div>
    </aside>
  )
}
