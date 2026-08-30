import { ShieldAlert } from "lucide-react";

export default function Logo({ compact = false }) {
  return (
    <div className="flex items-center gap-2.5 select-none">
      <div className="relative">
        <div className="absolute inset-0 rounded-xl bg-brand/30 blur-md" />
        <div className="relative w-9 h-9 rounded-xl bg-gradient-to-br from-brand to-brand2 flex items-center justify-center shadow-glow">
          <ShieldAlert className="w-5 h-5 text-ink" strokeWidth={2.4} />
        </div>
      </div>
      {!compact && (
        <div className="leading-none">
          <span className="font-display font-bold text-xl tracking-tight text-white">
            Vox<span className="text-brand">y</span>
          </span>
        </div>
      )}
    </div>
  );
}
