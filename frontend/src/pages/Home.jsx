import { motion } from "framer-motion";
import {
  AudioLines,
  ScanLine,
  ShieldCheck,
  Fingerprint,
  ArrowRight,
  Mic,
  Brain,
  Lock,
} from "lucide-react";
import WaveformVisual from "@/components/WaveformVisual";

const FEATURES = [
  {
    icon: AudioLines,
    title: "Speech-to-Text",
    desc: "Turns the call audio into a clean transcript for analysis.",
  },
  {
    icon: Brain,
    title: "Scam Detection",
    desc: "Spots impersonation, OTP requests, urgency and other scam patterns.",
  },
  {
    icon: Fingerprint,
    title: "Voice Authenticity",
    desc: "Estimates whether the caller's voice may be synthetic or spoofed.",
  },
  {
    icon: Lock,
    title: "Tamper-Evident Ledger",
    desc: "Every analysis result is recorded so findings can't be silently changed.",
  },
];

const FLOW = [
  { icon: Mic, title: "1. Upload", desc: "Drop a call recording." },
  { icon: ScanLine, title: "2. Analyze", desc: "Voxy scans the call." },
  { icon: ShieldCheck, title: "3. Report", desc: "Get a risk report." },
];

export default function Home({ onStart }) {
  return (
    <div className="relative">
      <div className="absolute inset-0 voxy-grid pointer-events-none" />

      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 pt-12 sm:pt-20 pb-10">
        <div className="flex flex-col lg:flex-row lg:items-center gap-10 lg:gap-6">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl flex-1"
        >
          <span className="chip border-brand/40 bg-brand/10 text-brand">
            <span className="w-1.5 h-1.5 rounded-full bg-brand animate-pulse" />
            AI-Powered Scam Call Detection
          </span>
          <h1 className="font-display font-bold text-4xl sm:text-6xl leading-[1.05] tracking-tight mt-5 text-white">
            Hear a suspicious call?
            <br />
            <span className="text-gradient">Know the risk in seconds.</span>
          </h1>
          <p className="text-slate-400 text-base sm:text-lg mt-5 max-w-xl">
            Voxy transcribes the call, detects scam tactics, checks voice
            authenticity, and gives you a clear risk score with a recommended
            action.
          </p>

          <div className="flex flex-wrap items-center gap-3 mt-8">
            <button onClick={onStart} className="voxy-btn-primary text-base px-6 py-3.5">
              Analyze a Call
              <ArrowRight className="w-5 h-5" />
            </button>
            <span className="text-sm text-slate-500">
              Demo uses sample data — no backend needed yet.
            </span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="flex-1 hidden md:block"
        >
          <WaveformVisual />
        </motion.div>
        </div>

        {/* Flow */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-14">
          {FLOW.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 + i * 0.08 }}
              className="voxy-card p-5 flex items-center gap-4"
            >
              <div className="w-11 h-11 rounded-xl bg-panel2 border border-line flex items-center justify-center shrink-0">
                <f.icon className="w-5 h-5 text-brand" />
              </div>
              <div>
                <p className="font-display font-semibold text-white">{f.title}</p>
                <p className="text-sm text-slate-400">{f.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Features */}
        <div className="mt-14">
          <h2 className="font-display font-bold text-2xl text-white mb-5">
            What Voxy checks
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {FEATURES.map((feat, i) => (
              <motion.div
                key={feat.title}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.05 * i }}
                className="voxy-card p-5 hover:border-brand/50 transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-brand/10 border border-brand/20 flex items-center justify-center mb-3">
                  <feat.icon className="w-5 h-5 text-brand" />
                </div>
                <h3 className="font-display font-semibold text-white text-sm">
                  {feat.title}
                </h3>
                <p className="text-sm text-slate-400 mt-1.5">{feat.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
