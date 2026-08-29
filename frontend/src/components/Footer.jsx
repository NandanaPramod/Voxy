import Logo from "./Logo";

export default function Footer() {
  return (
    <footer className="border-t border-line/80 mt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <Logo compact />
        <p className="text-xs text-slate-500 text-center sm:text-right">
          Voxy — AI-Powered Scam Call Detection. Demo data, not legal or
          security advice.
        </p>
      </div>
    </footer>
  );
}
