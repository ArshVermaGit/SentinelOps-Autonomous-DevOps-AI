"use client"
import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { Shield, Zap, BarChart3, ArrowRight, Github } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0a0f1e] text-white flex flex-col items-center justify-center p-6 text-center relative overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 blur-[120px] rounded-full" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[120px] rounded-full" />

      <main className="max-w-4xl z-10 w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
            <Image 
              src="/logo.png" 
              alt="SentinelOps Logo" 
              width={100} 
              height={100} 
              className="w-20 h-20 mb-6 drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]"
              priority
            />
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-bold">
              <Zap className="w-3 h-3" /> DEV-OPS AI CO-PILOT
            </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-linear-to-b from-white to-gray-400 bg-clip-text text-transparent">
            Engineering Decision <br /> Intelligence.
          </h1>
          <p className="text-lg text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            SentinelOps predicts CI failures, analyzes root causes with AI, and suggests fixes before you even merge. Stop reacting. Start preventing.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 mb-20">
            <Link href="/dashboard">
              <button className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold transition-all shadow-lg shadow-indigo-600/20 flex items-center gap-2 group">
                Enter Dashboard <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
            </Link>
            <a href="https://github.com/ArshVermaGit/SentinelOps-Autonomous-DevOps-AI" target="_blank" rel="noreferrer">
              <button className="px-8 py-3 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-white rounded-xl font-semibold transition-all flex items-center gap-2">
                <Github className="w-4 h-4" /> View Source
              </button>
            </a>
          </div>
        </motion.div>

        {/* Feature Grid */}
        <div className="grid md:grid-cols-3 gap-6 text-left">
          {[
            {
              icon: <Shield className="w-5 h-5 text-emerald-400" />,
              title: "PR Gatekeeper",
              desc: "Predictive risk scoring for every pull request before it hits main."
            },
            {
              icon: <Zap className="w-5 h-5 text-amber-400" />,
              title: "AI Analysis",
              desc: "LLM-powered root cause extraction and automated patch suggestions."
            },
            {
              icon: <BarChart3 className="w-5 h-5 text-indigo-400" />,
              title: "Health Metrics",
              desc: "Real-time visibility into your pipeline stability and deployment health."
            }
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 + i * 0.1 }}
              className="p-6 bg-gray-900/40 border border-gray-800 rounded-2xl backdrop-blur-sm"
            >
              <div className="mb-4">{feature.icon}</div>
              <h3 className="font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-12 border-t border-white/5 text-center text-gray-500 text-sm">
        <p className="mb-4">© 2026 SentinelOps. Created by Arsh Verma.</p>
        <div className="flex justify-center gap-6">
          <a href="https://github.com/ArshVermaGit" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">GitHub</a>
          <a href="https://www.linkedin.com/in/arshvermadev/" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">LinkedIn</a>
          <a href="https://x.com/TheArshVerma" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">X (Twitter)</a>
          <a href="mailto:arshverma.dev@gmail.com" className="hover:text-white transition-colors">Email</a>
        </div>
      </footer>
    </div>
  )
}
