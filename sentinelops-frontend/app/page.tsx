"use client"
import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { Shield, Zap, ArrowRight, Github, Cpu, Network } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#030712] text-white flex flex-col items-center justify-center p-6 text-center relative overflow-hidden bg-grid">
      {/* Dynamic Background Orbs */}
      <motion.div 
        animate={{ 
          scale: [1, 1.2, 1],
          opacity: [0.15, 0.25, 0.15],
          x: [0, 50, 0],
          y: [0, -30, 0]
        }}
        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-600/30 blur-[120px] rounded-full" 
      />
      <motion.div 
        animate={{ 
          scale: [1.2, 1, 1.2],
          opacity: [0.1, 0.2, 0.1],
          x: [0, -40, 0],
          y: [0, 40, 0]
        }}
        transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
        className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-purple-600/20 blur-[120px] rounded-full" 
      />

      <main className="max-w-5xl z-10 w-full pt-20 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="relative mx-auto w-24 h-24 mb-10 flex justify-center items-center">
            <motion.div 
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="absolute -inset-4 bg-indigo-500/20 blur-2xl rounded-full opacity-50"
            />
            <Image 
              src="/logo.png" 
              alt="SentinelOps Logo" 
              width={120} 
              height={120} 
              className="w-24 h-24 relative drop-shadow-[0_0_25px_rgba(99,102,241,0.4)]"
              priority
            />
          </div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-bold uppercase tracking-[0.2em] mb-8"
          >
            <Zap className="w-3.5 h-3.5 fill-indigo-400/20" /> NEXT-GEN DEVOPS INTELLIGENCE
          </motion.div>

          <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-8 leading-[0.9] bg-clip-text text-transparent bg-linear-to-b from-white via-white to-white/40">
            ENGINEERING <br /> DECISION <span className="text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">INTELLIGENCE.</span>
          </h1>
          
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed font-medium">
            Predict failures before they happen. SentinelOps uses AI to analyze PR risk, explain CI failures, and automate your resolution workflow.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-5 mb-32">
            <Link href="/dashboard">
              <motion.button 
                whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(99, 102, 241, 0.4)" }}
                whileTap={{ scale: 0.98 }}
                className="px-10 py-4 bg-indigo-600 text-white rounded-2xl font-bold transition-all flex items-center gap-3 group text-lg shadow-xl shadow-indigo-600/20"
              >
                Enter Platform <ArrowRight className="w-5 h-5 group-hover:translate-x-1.5 transition-transform" />
              </motion.button>
            </Link>
            <a href="https://github.com/ArshVermaGit/SentinelOps-Autonomous-DevOps-AI" target="_blank" rel="noreferrer">
              <motion.button 
                whileHover={{ scale: 1.05, backgroundColor: "rgba(255,255,255,0.05)" }}
                whileTap={{ scale: 0.98 }}
                className="px-10 py-4 glass text-white rounded-2xl font-bold transition-all flex items-center gap-3 text-lg"
              >
                <Github className="w-5 h-5" /> View Source
              </motion.button>
            </a>
          </div>
        </motion.div>

        {/* Dynamic Feature Grid */}
        <div className="grid md:grid-cols-3 gap-8 text-left">
          {[
            {
              icon: <Shield className="w-6 h-6 text-emerald-400" />,
              title: "Predictive Risk Scoring",
              desc: "ML audits every PR against historical patterns to identify high-risk changes before merge.",
              glow: "group-hover:shadow-emerald-500/10"
            },
            {
              icon: <Cpu className="w-6 h-6 text-amber-400" />,
              title: "LLM Root Cause Analysis",
              desc: "Automated log extraction and AI-powered failure explanations with patch suggestions.",
              glow: "group-hover:shadow-amber-500/10"
            },
            {
              icon: <Network className="w-6 h-6 text-indigo-400" />,
              title: "Repo Manager & Sync",
              desc: "Link local repos, auto-detect changes, run health checks, and push to GitHub — all from one dashboard.",
              glow: "group-hover:shadow-indigo-500/10"
            }
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.4 + i * 0.1 }}
              className={`p-10 glass-card rounded-4xl group relative overflow-hidden ${feature.glow}`}
            >
              <div className="absolute -top-10 -right-10 w-32 h-32 bg-white/5 blur-3xl rounded-full group-hover:bg-white/10 transition-colors duration-500" />
              <div className="mb-6 w-14 h-14 bg-white/5 rounded-2xl flex items-center justify-center border border-white/5 group-hover:border-white/20 transition-all">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-4 tracking-tight">{feature.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed font-medium group-hover:text-gray-400 transition-colors">
                {feature.desc}
              </p>
            </motion.div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full max-w-5xl py-12 mt-20 border-t border-white/5 text-center">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8 mb-10">
          <div className="flex items-center gap-3">
             <Image src="/logo.png" alt="Logo" width={32} height={32} />
             <span className="font-bold text-lg tracking-tight">SentinelOps</span>
          </div>
          <div className="flex gap-8">
            {[
              { label: "GitHub", href: "https://github.com/ArshVermaGit", icon: <Github className="w-4 h-4" /> },
              { label: "LinkedIn", href: "https://www.linkedin.com/in/arshvermadev/" },
              { label: "Twitter", href: "https://x.com/TheArshVerma" },
              { label: "Contact", href: "mailto:arshverma.dev@gmail.com" }
            ].map((link, i) => (
              <a key={i} href={link.href} target="_blank" rel="noreferrer" className="text-gray-500 hover:text-white transition-colors text-sm font-semibold tracking-wide flex items-center gap-2 uppercase">
                {link.label}
              </a>
            ))}
          </div>
        </div>
        <p className="text-[10px] text-gray-600 font-bold uppercase tracking-[0.3em]">
          Handcrafted with precision by Arsh Verma &copy; 2026
        </p>
      </footer>
    </div>
  )
}
