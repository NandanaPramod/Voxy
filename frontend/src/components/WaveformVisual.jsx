// Animated audio-equalizer style bars, like a live waveform.
// Bars animate with staggered delays so the pattern keeps moving.
const BARS = [
  0.18, 0.32, 0.5, 0.72, 0.55, 0.88, 0.64, 1, 0.78, 0.92, 0.6, 0.84,
  0.46, 0.68, 0.36, 0.54, 0.28, 0.42, 0.22, 0.34,
];

export default function WaveformVisual() {
  return (
    <div
      aria-hidden="true"
      className="relative flex items-center justify-center gap-[7px] h-64 sm:h-80 lg:h-96 select-none"
    >
      {/* Soft radial glow so it melts into the background */}
      <div className="absolute inset-0 bg-[radial-gradient(closest-side,rgba(139,232,203,0.10),transparent_70%)] pointer-events-none" />

      {BARS.map((h, i) => (
        <span
          key={i}
          className="w-2.5 sm:w-3 rounded-full bg-gradient-to-t from-lavender/70 via-steel/80 to-brand origin-center animate-wave"
          style={{
            height: `${h * 100}%`,
            animationDelay: `${(i % 10) * 0.13}s`,
            animationDuration: `${1.1 + (i % 5) * 0.18}s`,
            opacity: 0.45 + h * 0.55,
          }}
        />
      ))}
    </div>
  );
}
