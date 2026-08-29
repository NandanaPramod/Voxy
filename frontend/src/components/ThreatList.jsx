import { AlertTriangle } from "lucide-react";

export default function ThreatList({ threats = [] }) {
  if (!threats.length) {
    return (
      <div className="voxy-card p-4 flex items-center gap-3 text-slate-400">
        <AlertTriangle className="w-5 h-5 text-safe" />
        <span className="text-sm">No scam threats detected in this call.</span>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {threats.map((t, i) => (
        <span
          key={t + i}
          className="chip border-danger/40 bg-danger/10 text-danger"
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          {t}
        </span>
      ))}
    </div>
  );
}
