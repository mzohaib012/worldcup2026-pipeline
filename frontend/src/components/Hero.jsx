export default function Hero() {
  return (
    <div className="stadium-glow relative overflow-hidden">
      <div className="pitch-stripes" />
      <div className="relative max-w-6xl mx-auto px-4 py-20 text-center">
        <p
          className="text-xs tracking-[0.35em] text-[var(--color-gold)] mb-4"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          USA &middot; CANADA &middot; MEXICO &mdash; 48 NATIONS
        </p>
        <h1
          className="text-5xl md:text-7xl font-bold leading-none text-white"
          style={{
            fontFamily: "var(--font-display)",
            textShadow: "0 0 28px rgba(255,215,0,0.35), 0 0 4px rgba(255,255,255,0.4)",
          }}
        >
          WORLD CUP <span className="text-[var(--color-gold)]">2026</span>
        </h1>
        <p
          className="text-[var(--color-slate)] mt-4 max-w-xl mx-auto"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          Live tournament data, all-time records, and machine-learning predictions
          &mdash; streamed straight from the pitch into this dashboard.
        </p>
      </div>
    </div>
  );
}