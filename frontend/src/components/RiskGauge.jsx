import { motion } from "framer-motion";
import { getRiskLevel } from "@/lib/riskConfig";

// Semicircular risk gauge (0-100).
export default function RiskGauge({ value = 0, size = 260 }) {
  const v = Math.max(0, Math.min(100, value));
  const lvl = getRiskLevel(v);
  const radius = 80;
  const cy = 120;
  const x1 = 100 - radius;
  const x2 = 100 + radius;
  const d = `M ${x1} ${cy} A ${radius} ${radius} 0 0 1 ${x2} ${cy}`;

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 140" width={size} height={size * 0.7}>
        <path d={d} fill="none" stroke="#1a2536" strokeWidth={16} strokeLinecap="round" />
        <motion.path
          d={d}
          fill="none"
          stroke={lvl.hex}
          strokeWidth={16}
          strokeLinecap="round"
          pathLength={100}
          initial={{ strokeDashoffset: 100 }}
          animate={{ strokeDashoffset: 100 - v }}
          transition={{ duration: 1.1, ease: "easeOut" }}
          style={{ filter: `drop-shadow(0 0 10px ${lvl.hex}88)` }}
        />
        <text
          x="100"
          y="100"
          textAnchor="middle"
          style={{ fontSize: 40, fontWeight: 700, fontFamily: "Space Grotesk", fill: "#fff" }}
        >
          {Math.round(v)}
        </text>
        <text
          x="100"
          y="124"
          textAnchor="middle"
          style={{ fontSize: 11, letterSpacing: 2, fill: "#64748b", fontFamily: "Inter" }}
        >
          RISK SCORE
        </text>
      </svg>
      <span
        className="chip mt-1"
        style={{ background: lvl.bg, color: lvl.hex, borderColor: lvl.border }}
      >
        {lvl.label}
      </span>
    </div>
  );
}
