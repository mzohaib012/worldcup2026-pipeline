export default function SectionHeader({ eyebrow, title }) {
  return (
    <div className="mb-6">
      {eyebrow && (
        <p
          className="text-xs tracking-[0.3em] text-[var(--color-slate)] mb-2"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          {eyebrow}
        </p>
      )}
      <div className="broadcast-bar">
        <span
          className="text-[var(--color-pitch-navy)] font-bold uppercase text-lg tracking-wide"
          style={{ fontFamily: "var(--font-display)" }}
        >
          {title}
        </span>
      </div>
    </div>
  );
}