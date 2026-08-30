import { motion } from "framer-motion";
import {
  PhoneOff,
  Brain,
  Fingerprint,
  AlertTriangle,
  MessageSquare,
  ShieldCheck,
  RefreshCw,
  ArrowLeft,
} from "lucide-react";
import RiskGauge from "@/components/RiskGauge";
import RiskMeter from "@/components/RiskMeter";
import ThreatList from "@/components/ThreatList";
import { getRiskLevel } from "@/lib/riskConfig";

export default function ResultsPage({ result, file, onAgain, onHome }) {
  const lvl = getRiskLevel(result.overall_risk);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-8 pb-6">
      <button
        onClick={onHome}
        className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors mb-5"
      >
        <ArrowLeft className="w-4 h-4" /> Home
      </button>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="font-display font-bold text-3xl sm:text-4xl text-white">
          Analysis Report
        </h1>
        {file && (
          <p className="text-slate-400 text-sm mt-1 truncate">
            {file.name}
          </p>
        )}
      </motion.div>

      {/* Top: gauge + recommended action */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-6">
        <div className="voxy-card p-6 flex flex-col items-center justify-center">
          <RiskGauge value={result.overall_risk} />
          <p className="text-xs text-slate-500 mt-3">
            Overall risk level:{" "}
            <span className="font-semibold" style={{ color: lvl.hex }}>
              {result.risk_level}
            </span>
          </p>
        </div>

        <div
          className="voxy-card p-6 flex flex-col"
          style={{ borderColor: lvl.border, background: lvl.bg }}
        >
          <div className="flex items-center gap-2 mb-3">
            <PhoneOff className="w-5 h-5" style={{ color: lvl.hex }} />
            <h2 className="font-display font-bold text-lg text-white">
              Recommended Action
            </h2>
          </div>
          <p className="text-slate-200 text-sm leading-relaxed flex-1">
            {result.recommended_action}
          </p>
          <div className="flex flex-wrap gap-3 mt-5">
            <button onClick={onAgain} className="voxy-btn-primary">
              <RefreshCw className="w-4 h-4" /> Analyze another call
            </button>
          </div>
        </div>
      </div>

      {/* Sub-scores */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
        <RiskMeter
          label="Scam Conversation Risk"
          value={result.scam_risk}
          icon={Brain}
          sub="Based on the transcript content."
        />
        <RiskMeter
          label="Voice Authenticity Risk"
          value={result.voice_risk}
          icon={Fingerprint}
          sub="Higher means the voice may be synthetic."
        />
      </div>

      {/* Threats */}
      <div className="voxy-card p-6 mt-4">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-danger" />
          <h2 className="font-display font-bold text-lg text-white">
            Detected Threats
          </h2>
        </div>
        <ThreatList threats={result.threats} />
      </div>

      {/* Transcript */}
      <div className="voxy-card p-6 mt-4">
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare className="w-5 h-5 text-brand" />
          <h2 className="font-display font-bold text-lg text-white">Transcript</h2>
        </div>
        <div className="border-l-2 border-danger/50 pl-4">
          <p className="font-mono text-sm text-slate-300 leading-relaxed">
            {result.transcript}
          </p>
        </div>
      </div>

      {/* Ledger */}
      <div className="voxy-card p-6 mt-4 flex flex-col sm:flex-row items-start sm:items-center gap-4 justify-between">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-safe/10 border border-safe/30 flex items-center justify-center">
            <ShieldCheck className="w-6 h-6 text-safe" />
          </div>
          <div>
            <p className="font-display font-semibold text-white">
              Ledger Status: {result.ledger_status}
            </p>
            <p className="text-sm text-slate-400">
              Result recorded tamper-evidently. Raw audio is never stored.
            </p>
          </div>
        </div>
        <span className="chip border-safe/40 bg-safe/10 text-safe">
          <span className="w-1.5 h-1.5 rounded-full bg-safe" />
          Verified
        </span>
      </div>
    </div>
  );
}
