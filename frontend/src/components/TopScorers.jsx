import { useEffect, useState } from "react";
import api, { API_BASE_URL } from "../api/client";
import SectionHeader from "./SectionHeader";

export default function TopScorers({ limit = 12 }) {
  const [scorers, setScorers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get(`/top-scorers?limit=${limit}`)
      .then((res) => setScorers(res.data))
      .catch((err) => console.error("Failed to fetch top scorers:", err))
      .finally(() => setLoading(false));
  }, [limit]);

  return (
    <section className="mt-16">
      <SectionHeader eyebrow="ALL-TIME LEADERS" title="Top Scorers" />

      {loading && <p className="text-[var(--color-slate)]">Loading top scorers...</p>}

      {!loading && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {scorers.map((s, i) => (
            <div
              key={s.player_id}
              className="group relative rounded-lg overflow-hidden border border-[var(--color-gold-dim)] bg-[var(--color-pitch-navy-light)] card-depth hover:border-[var(--color-gold)] hover:shadow-[0_8px_30px_rgba(255,215,0,0.25)] transition duration-300"
            >
              <span
                className="absolute top-1 left-1 z-10 text-xs font-bold bg-[var(--color-gold)] text-[var(--color-pitch-navy)] rounded px-1.5 py-0.5"
                style={{ fontFamily: "var(--font-mono)" }}
              >
                #{i + 1}
              </span>
              <img
                src={`${API_BASE_URL}/player-card/${encodeURIComponent(s.full_name)}`}
                alt={s.full_name}
                loading="lazy"
                className="w-full h-auto group-hover:scale-105 transition duration-300"
              />
              <div className="p-2 text-center">
                <p className="text-sm font-semibold truncate">{s.full_name}</p>
                <p className="text-xs text-[var(--color-gold)]" style={{ fontFamily: "var(--font-mono)" }}>
                  {s.total_goals} goals
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}