export default function Header() {
  return (
    <header className="sticky top-0 z-20 bg-[var(--color-pitch-black)]/90 backdrop-blur border-b border-[var(--color-gold-dim)]/40">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[var(--color-gold)]" />
          <span
            className="text-sm font-bold tracking-[0.2em] text-white"
            style={{ fontFamily: "var(--font-display)" }}
          >
            WORLD CUP <span className="text-[var(--color-gold)]">2026</span>
          </span>
        </div>
        <div
          className="flex items-center gap-2 text-xs text-[var(--color-slate)]"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-live-green)] animate-pulse" />
          LIVE DATA PIPELINE
        </div>
      </div>
    </header>
  );
}