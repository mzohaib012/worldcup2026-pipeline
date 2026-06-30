export default function Hero() {
  return (
    <div className="stadium-glow relative overflow-hidden border-b border-[var(--color-gold-dim)]/30">
      <div className="pitch-stripes" />
     <div className="relative max-w-5xl mx-auto px-4 py-4 flex items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div
            className="leading-[0.75] text-white font-bold"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <div className="text-3xl md:text-4xl">26</div>
          </div>
          <div className="h-10 w-px bg-[var(--color-gold-dim)]/50" />
          <div>
            <p
              className="text-xs tracking-[0.35em] text-[var(--color-gold)]"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              WE ARE 26
            </p>
            <p className="text-[11px] text-[var(--color-slate)] mt-0.5" style={{ fontFamily: "var(--font-mono)" }}>
              USA &middot; CANADA &middot; MEXICO
            </p>
          </div>
        </div>

        <p
          className="hidden md:block text-sm text-[var(--color-slate)] text-right max-w-xs"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          Live data, all-time records & ML predictions for the 48-nation tournament.
        </p>
      </div>
    </div>
  );
}