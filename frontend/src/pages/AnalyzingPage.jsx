import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AudioLines, Mic, Brain, Fingerprint, ShieldAlert } from "lucide-react";

const STAGES = [
  { icon: AudioLines, label: "Reading audio…" },
  { icon: Mic, label: "Transcribing speech…" },
  { icon: Brain, label: "Detecting scam patterns…" },
  { icon: Fingerprint, label: "Checking voice authenticity…" },
  { icon: ShieldAlert, label: "Computing overall risk…" },
];

export default function AnalyzingPage({ fileName }) {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setStage((s) => (s < STAGES.length - 1 ? s + 1 : s));
    }, 520);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 pt-12 pb-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="voxy-card p-8 sm:p-10 text-center relative overflow-hidden"
      >
        {/* Scanning line */}
        <div className="absolute inset-x-0 top-0 h-px bg-brand/60 animate-scan" />

        {/* Animated waveform */}
        <div className="flex items-end justify-center gap-1.5 h-20 mb-6">
          {Array.from({ length: 17 }).map((_, i) => (
            <span
              key={i}
              className="w-1.5 rounded-full bg-gradient-to-t from-brand2 to-brand animate-wave"
              style={{
                height: "100%",
                animationDelay: `${(i % 9) * 0.09}s`,
                opacity: 0.35 + 0.65 * Math.abs(Math.sin(i)),
              }}
            />
          ))}
        </div>

        <h1 className="font-display font-bold text-2xl text-white">
          Analyzing call…
        </h1>
        <p className="text-slate-400 text-sm mt-1.5 truncate">
          {fileName ?? "Processing audio"}
        </p>

        {/* Stage list */}
        <div className="mt-7 space-y-2 text-left">
          {STAGES.map((s, i) => {
            const done = i < stage;
            const active = i === stage;
            const Icon = s.icon;
            return (
              <div
                key={s.label}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors ${
                  active ? "bg-brand/10 border border-brand/30" : "border border-transparent"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    done
                      ? "bg-safe/15 text-safe"
                      : active
                      ? "bg-brand/15 text-brand"
                      : "bg-panel2 text-slate-500"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? "animate-pulse" : ""}`} />
                </div>
                <span
                  className={`text-sm ${
                    done ? "text-slate-300" : active ? "text-white font-medium" : "text-slate-500"
                  }`}
                >
                  {s.label}
                </span>
              </div>
            );
          })}
        </div>
      </motion.div>

      <p className="text-center text-xs text-slate-600 mt-5">
        This is a demo with mock data — connect the backend later to analyze real calls.
      </p>
    </div>
  );
}
