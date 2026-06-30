import { useEffect, useState } from "react";
import api from "../api/client";
import SectionHeader from "./SectionHeader";

const STAGES = [
  { key: "LAST_32", label: "Round of 32", slots: 16 },
  { key: "LAST_16", label: "Round of 16", slots: 8 },
  { key: "QUARTER_FINALS", label: "Quarterfinals", slots: 4 },
  { key: "SEMI_FINALS", label: "Semifinals", slots: 2 },
  { key: "FINAL", label: "Final", slots: 1 },
];

const CARD_H = 52;
const CARD_GAP = 10;
const COL_W = 210;

function MatchCard({ match, style }) {
  const empty = !match;
  const isDecided = match?.winner != null;
  const homeWon = isDecided && match.winner === match.home_team;
  const awayWon = isDecided && match.winner === match.away_team;

  return (
    <div
      className={`absolute rounded overflow-hidden text-xs w-44 border ${
        empty
          ? "border-dashed border-[var(--color-gold-dim)]/30 bg-transparent"
          : "border-[var(--color-gold-dim)]/50 bg-[var(--color-pitch-navy-light)]"
      }`}
      style={style}
    >
      <div className={`flex justify-between px-2 py-1.5 ${homeWon ? "bg-[var(--color-gold)]/10" : ""}`}>
        <span className={`truncate ${homeWon ? "font-bold text-[var(--color-gold)]" : "text-white/90"}`}>
          {match?.home_team || (empty ? "" : "TBD")}
        </span>
        <span className="ml-1 text-[var(--color-slate)]" style={{ fontFamily: "var(--font-mono)" }}>
          {match?.home_score ?? ""}
        </span>
      </div>
      <div className="h-px bg-[var(--color-gold-dim)]/20" />
      <div className={`flex justify-between px-2 py-1.5 ${awayWon ? "bg-[var(--color-gold)]/10" : ""}`}>
        <span className={`truncate ${awayWon ? "font-bold text-[var(--color-gold)]" : "text-white/90"}`}>
          {match?.away_team || (empty ? "" : "TBD")}
        </span>
        <span className="ml-1 text-[var(--color-slate)]" style={{ fontFamily: "var(--font-mono)" }}>
          {match?.away_score ?? ""}
        </span>
      </div>
    </div>
  );
}

export default function KnockoutBracket({ tournamentId = "WC-2026" }) {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get(`/knockout-bracket/${tournamentId}`)
      .then((res) => setMatches(res.data))
      .catch(() => setError("Knockout stage hasn't started yet."))
      .finally(() => setLoading(false));
  }, [tournamentId]);

  const grouped = matches.reduce((acc, m) => {
    acc[m.stage] = acc[m.stage] || [];
    acc[m.stage].push(m);
    return acc;
  }, {});

  // Sort each stage's matches by match_date so slot order is stable and
  // consistent across renders, even before all fixtures are confirmed.
  Object.values(grouped).forEach((arr) => arr.sort((a, b) => (a.match_date || "").localeCompare(b.match_date || "")));

  // Only render stages up to the furthest one that actually has any data,
  // so the bracket grows automatically as the real tournament progresses
  // without needing any code changes.
 // Always render all stages -- the bracket structure itself (Round of 32
  // through Final) is fixed by the tournament format, regardless of
  // whether fixtures for later rounds have been confirmed by the source
  // yet. Empty slots render as placeholders and fill in automatically
  // once that round's matches sync through the pipeline.
  const visibleStages = STAGES;

  // Fixed-size slot array per stage: known matches fill in by date order,
  // remaining slots render as empty placeholders ("-- vs --") ready to be
  // filled automatically once the live pipeline syncs that fixture.
  const slotsByStage = {};
  visibleStages.forEach((s) => {
    const known = grouped[s.key] || [];
    slotsByStage[s.key] = Array.from({ length: s.slots }, (_, i) => known[i] || null);
  });

  const positions = {};
  const connectors = [];

  visibleStages.forEach((stage, roundIndex) => {
    const slots = slotsByStage[stage.key];

    if (roundIndex === 0) {
      slots.forEach((m, i) => {
        const top = i * (CARD_H + CARD_GAP);
        positions[`${stage.key}-${i}`] = { top, center: top + CARD_H / 2 };
      });
    } else {
      const prevKey = visibleStages[roundIndex - 1].key;
      slots.forEach((m, i) => {
        const centerA = positions[`${prevKey}-${i * 2}`]?.center;
        const centerB = positions[`${prevKey}-${i * 2 + 1}`]?.center;
        const center =
          centerA != null && centerB != null
            ? (centerA + centerB) / 2
            : centerA ?? centerB ?? i * (CARD_H + CARD_GAP) + CARD_H / 2;
        const top = center - CARD_H / 2;
        positions[`${stage.key}-${i}`] = { top, center };

        const x1 = roundIndex * COL_W - 10;
        if (centerA != null) connectors.push({ x1, y1: centerA, x2: x1 + 10, y2: center });
        if (centerB != null) connectors.push({ x1, y1: centerB, x2: x1 + 10, y2: center });
      });
    }
  });

  const maxHeight = Math.max(0, ...Object.values(positions).map((p) => p.top + CARD_H)) + 10;
  const totalWidth = visibleStages.length * COL_W;

  return (
    <section id="bracket" className="mt-16 scroll-mt-20">
      <SectionHeader eyebrow="ROAD TO THE FINAL" title="Knockout Bracket" />

      {loading && <p className="text-[var(--color-slate)]">Loading bracket...</p>}
      {error && <p className="text-[var(--color-slate)]">{error}</p>}

      {!loading && !error && visibleStages.length > 0 && (
        <div className="overflow-x-auto card-depth bg-[var(--color-pitch-navy-light)]/40 rounded-lg p-6">
          <div className="relative" style={{ width: totalWidth, height: maxHeight + 30 }}>
            {visibleStages.map((stage, i) => (
              <p
                key={stage.key}
                className="absolute text-xs tracking-widest text-[var(--color-gold)]"
                style={{ left: i * COL_W, top: 0, fontFamily: "var(--font-mono)" }}
              >
                {stage.label}
              </p>
            ))}

            <svg
              className="absolute pointer-events-none"
              style={{ left: 0, top: 30, width: totalWidth, height: maxHeight }}
            >
              {connectors.map((c, i) => (
                <path
                  key={i}
                  d={`M ${c.x1} ${c.y1} H ${(c.x1 + c.x2) / 2} V ${c.y2} H ${c.x2}`}
                  stroke="rgba(255,215,0,0.35)"
                  strokeWidth="1.5"
                  fill="none"
                />
              ))}
            </svg>

            <div className="absolute" style={{ left: 0, top: 30, width: totalWidth, height: maxHeight }}>
              {visibleStages.map((stage, roundIndex) =>
                slotsByStage[stage.key].map((m, i) => (
                  <MatchCard
                    key={`${stage.key}-${i}`}
                    match={m}
                    style={{ left: roundIndex * COL_W, top: positions[`${stage.key}-${i}`].top }}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}