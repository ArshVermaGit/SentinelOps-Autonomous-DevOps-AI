"use client"
import { useState, useEffect } from "react"
import { Search } from "lucide-react"
import { useWebSocket } from "@/hooks/useWebSocket"
import { useSearchStore } from "@/hooks/useSearchStore"
import NotificationDropdown from "@/components/layout/NotificationDropdown"

export default function TopBar() {
  const [connected, setConnected] = useState(false)
  const { query, setQuery } = useSearchStore()
  
  useWebSocket((data) => {
    if (data.type) {
      setConnected(true)
    }
  })

  // ⌘K keyboard shortcut for search focus
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        const input = document.getElementById("sentinel-search") as HTMLInputElement
        input?.focus()
      }
      if (e.key === "Escape") {
        const input = document.getElementById("sentinel-search") as HTMLInputElement
        if (document.activeElement === input) {
          input.blur()
          setQuery("")
        }
      }
    }
    document.addEventListener("keydown", handler)
    return () => document.removeEventListener("keydown", handler)
  }, [setQuery])
  
  return (
    <header className="h-14 bg-[#111827] border-b border-gray-800 flex items-center px-6 justify-between shrink-0">
      {/* Search */}
      <div className="flex items-center gap-2 bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 w-72 focus-within:border-indigo-500 transition-colors">
        <Search className="w-4 h-4 text-gray-500" />
        <input
          id="sentinel-search"
          className="bg-transparent text-sm text-gray-400 placeholder-gray-600 outline-none flex-1"
          placeholder="Search incidents, repos, PRs..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <kbd className="text-xs text-gray-600 border border-gray-700 rounded px-1">⌘K</kbd>
      </div>
      
      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Live indicator */}
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${connected ? "bg-emerald-400 animate-pulse" : "bg-gray-600"}`} />
          <span className="text-xs text-gray-500">{connected ? "Live monitoring" : "Connecting..."}</span>
        </div>
        
        {/* Notification Dropdown */}
        <NotificationDropdown />
      </div>
    </header>
  )
}
