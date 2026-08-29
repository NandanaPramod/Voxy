const STEPS = [
  { key: "home", label: "Home" },
  { key: "upload", label: "Upload" },
  { key: "analyzing", label: "Analyze" },
  { key: "results", label: "Results" },
];

export default function StepIndicator({ current }) {
  const activeIndex = STEPS.findIndex((s) => s.key === current);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 pt-6">
      <ol className="flex items-center gap-2 sm:gap-3">
        {STEPS.map((step, i) => {
          const done = i < activeIndex;
          const active = i === activeIndex;
          return (
            <li key={step.key} className="flex items-center gap-2 sm:gap-3">
              <div
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors ${
                  active
                    ? "border-brand text-ink bg-brand shadow-glow"
                    : done
                    ? "border-line text-slate-300 bg-panel2"
                    : "border-line/60 text-slate-500"
                }`}
              >
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] ${
                    active ? "bg-ink text-brand" : "bg-panel2 text-slate-400"
                  }`}
                >
                  {i + 1}
                </span>
                <span className="hidden sm:inline">{step.label}</span>
              </div>
              {i < STEPS.length - 1 && (
                <span className={`h-px w-6 sm:w-10 ${done ? "bg-brand/60" : "bg-line"}`} />
              )}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
