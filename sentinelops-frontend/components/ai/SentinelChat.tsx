"use client"
import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { MessageSquare, Send, X, Bot, Sparkles, Terminal } from "lucide-react"
import { apiClient } from "@/lib/api"

export default function SentinelChat() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<{role: 'user' | 'bot', text: string}[]>([
    { role: 'bot', text: "Hey! I'm Sentinel AI. Need a hand analyzing these pipelines or checking repo health?" }
  ])
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return
    const userMsg = input
    setInput("")
    setMessages(prev => [...prev, { role: 'user', text: userMsg }])
    setIsTyping(true)

    try {
      const response = await apiClient.post("/dashboard/ai-chat", { query: userMsg })
      setMessages(prev => [...prev, { role: 'bot', text: response.data.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: "Gah, lost connection to the server. Check your API key or network?" }])
    } finally {
      setIsTyping(false)
    }
  }

  return (
    <div className="fixed bottom-8 right-8 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="mb-4 w-[400px] h-[550px] glass overflow-hidden rounded-3xl shadow-2xl border border-white/10 flex flex-col"
          >
            {/* Header */}
            <div className="p-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
                  <Bot className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white leading-none">Sentinel AI</h3>
                  <p className="text-[10px] text-emerald-400 mt-1 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    AI Core Online
                  </p>
                </div>
              </div>
              <button 
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/5 rounded-lg transition-colors text-gray-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Messages */}
            <div 
              ref={scrollRef}
              className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide"
            >
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-3 rounded-2xl text-xs leading-relaxed ${
                    m.role === 'user' 
                      ? 'bg-indigo-600 text-white rounded-tr-none' 
                      : 'bg-white/5 text-gray-200 border border-white/10 rounded-tl-none'
                  }`}>
                    {m.text}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white/5 border border-white/10 p-3 rounded-2xl rounded-tl-none flex gap-1 items-center">
                    <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" />
                    <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce delay-75" />
                    <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce delay-150" />
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/5 bg-white/5">
              <div className="relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask for an impact analysis..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                />
                <button 
                  onClick={handleSend}
                  disabled={!input.trim() || isTyping}
                  className="absolute right-2 top-1.5 bottom-1.5 px-3 rounded-lg bg-indigo-500 hover:bg-indigo-400 disabled:opacity-50 transition-colors flex items-center justify-center"
                >
                  <Send className="w-3.5 h-3.5 text-white" />
                </button>
              </div>
              <p className="text-[9px] text-gray-600 mt-3 text-center uppercase tracking-widest font-bold flex items-center justify-center gap-1.5">
                <Terminal className="w-2.5 h-2.5" />
                SentinelOps Core v1.4
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toggle Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        className="w-16 h-16 rounded-full bg-indigo-600 shadow-2xl shadow-indigo-600/40 flex items-center justify-center group relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-linear-to-tr from-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity" />
        {isOpen ? (
          <X className="w-7 h-7 text-white relative z-10" />
        ) : (
          <div className="relative">
            <MessageSquare className="w-7 h-7 text-white relative z-10" />
            <Sparkles className="absolute -top-1 -right-1.5 w-4 h-4 text-emerald-300 animate-pulse" />
          </div>
        )}
      </motion.button>
    </div>
  )
}
