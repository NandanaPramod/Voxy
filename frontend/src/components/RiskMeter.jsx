import { motion } from "framer-motion";
import { getRiskLevel } from "@/lib/riskConfig";

// Linear risk meter used for voice and scam sub-scores.
export default function RiskMeter({ label, value = 0, sub, icon: Icon }) {
  const lvl = getRiskLevel(value);
  const v = Math.max(0, Math.min(100, value));

  return (
    <div className="voxy-card p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="flex items-center gap-2 text-sm font-semibold text-slate-200">
          {Icon && <Icon className="w-4 h-4 text-slate-400" />}
          {label}
        </span>
        <span className="font-display font-bold" style={{ color: lvl.hex }}>
          {Math.round(v)}
          <span className="text-slate-500 text-xs font-normal">/100</span>
        </span>
      </div>
      <div className="h-2.5 rounded-full bg-[#1a2536] overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ background: lvl.hex, boxShadow: `0 0 12px ${lvl.hex}88` }}
          initial={{ width: 0 }}
          animate={{ width: `${v}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </div>
      {sub && <p className="text-xs text-slate-500 mt-2">{sub}</p>}
    </div>
  );
}
