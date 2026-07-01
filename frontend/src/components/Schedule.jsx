import { useEffect, useState } from "react";
import api from "../api/client";
import SectionHeader from "./SectionHeader";

const STAGE_LABELS = {
  GROUP_STAGE: "Group Stage",
  LAST_32: "Round of 32",
  LAST_16: "Round of 16",
  QUARTER_FINALS: "Quarterfinals",
  SEMI_FINALS: "Semifinals",
  THIRD_PLACE: "Third Place",
  FINAL: "Final",
};

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" });
}

export default function Schedule({ tournamentId = "WC-2026" }) {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("upcoming");

  useEffect(() => {
    api
      .get(`/schedule/${tournamentId}`)
      .then((res) => setMatches(res.data))
      .catch((err) => console.error("Failed to fetch schedule:", err))
      .finally(() => setLoading(false));
  }, [tournamentId]);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const played = matches.filter((m) => {
    const matchDate = new Date(m.match_date);
    return matchDate < today || (m.home_score !== null && m.away_score !== null);
  });

  const upcoming = matches.filter((m) => {
    const matchDate = new Date(m.match_date);
    return matchDate >= today && (m.home_score === null || m.away_score === null);
  });
  const list = tab === "upcoming" ? upcoming : [...played].reverse();

  return (
    <section id="schedule" className="mt-16 scroll-mt-20">
      <SectionHeader eyebrow="MATCH CALENDAR" title="Schedule" />
      {loading && <p className="text-[var(--color-slate)]">Loading schedule...</p>}
      {!loading && (
        <>
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setTab("upcoming")}
              className={`px-3 py-1 text-sm rounded border transition ${
                tab === "upcoming"
                  ? "bg-[var(--color-gold)] text-[var(--color-pitch-navy)] border-[var(--color-gold)] font-bold"
                  : "border-[var(--color-gold-dim)] text-[var(--color-slate)] hover:border-[var(--color-gold)]"
              }`}
            >
              Upcoming ({upcoming.length})
            </button>
            <button
              onClick={() => setTab("results")}
              className={`px-3 py-1 text-sm rounded border transition ${
                tab === "results"
                  ? "bg-[var(--color-gold)] text-[var(--color-pitch-navy)] border-[var(--color-gold)] font-bold"
                  : "border-[var(--color-gold-dim)] text-[var(--color-slate)] hover:border-[var(--color-gold)]"
              }`}
            >
              Results ({played.length})
            </button>
          </div>

          <div className="card-depth bg-[var(--color-pitch-navy-light)] rounded-lg divide-y divide-white/10 max-h-[420px] overflow-y-auto">
            {list.length === 0 && (
              <p className="text-[var(--color-slate)] text-sm p-4">No matches in this view.</p>
            )}
            {list.map((m) => (
              <div key={m.match_id} className="flex items-center justify-between px-4 py-3 text-sm">
                <div className="flex flex-col gap-0.5 w-28 shrink-0">
                  <span
                    className="text-[var(--color-slate)] text-xs"
                    style={{ fontFamily: "var(--font-mono)" }}
                  >
                    {formatDate(m.match_date)}
                  </span>
                  <span className="text-[10px] text-[var(--color-gold)] tracking-wide">
                    {(STAGE_LABELS[m.stage] || m.stage || "").toUpperCase()}
                    {m.group_name ? ` \u2022 ${m.group_name.replace("GROUP_", "GRP ")}` : ""}
                  </span>
                </div>
                <div className="flex-1 flex items-center justify-center gap-3">
                  <span className="w-32 text-right truncate">{m.home_team || "TBD"}</span>
                  <span
                    className="px-2 font-bold text-[var(--color-gold)] tabular-nums"
                    style={{ fontFamily: "var(--font-mono)" }}
                  >
                    {m.home_score !== null && m.away_score !== null
                      ? `${m.home_score} - ${m.away_score}`
                      : "vs"}
                  </span>
                  <span className="w-32 text-left truncate">{m.away_team || "TBD"}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}