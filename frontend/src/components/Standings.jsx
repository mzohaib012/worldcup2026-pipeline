import { useEffect, useState } from "react";
import api from "../api/client";
import SectionHeader from "./SectionHeader";

export default function Standings() {
  const [standings, setStandings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get("/standings/WC-2026")
      .then((res) => setStandings(res.data))
      .catch(() => setError("No 2026 standings available yet."))
      .finally(() => setLoading(false));
  }, []);

  const groups = [...new Set(standings.map((s) => s.group_name))].sort();
  const [activeGroup, setActiveGroup] = useState(null);

  useEffect(() => {
    if (groups.length && !activeGroup) setActiveGroup(groups[0]);
  }, [groups, activeGroup]);

  const rows = standings
    .filter((s) => s.group_name === activeGroup)
    .sort((a, b) => a.group_rank - b.group_rank);

  return (
    <section id="standings" className="mt-12 scroll-mt-20">
      <SectionHeader eyebrow="GROUP STAGE" title="Group Standings" />

      {loading && <p className="text-[var(--color-slate)]">Loading standings...</p>}
      {error && <p className="text-[var(--color-slate)]">{error}</p>}

      {!loading && !error && (
        <>
          <div className="flex gap-2 mb-4 flex-wrap">
            {groups.map((g) => (
              <button
                key={g}
                onClick={() => setActiveGroup(g)}
                className={`px-3 py-1 text-sm rounded border transition ${
                  activeGroup === g
                    ? "bg-[var(--color-gold)] text-[var(--color-pitch-navy)] border-[var(--color-gold)] font-bold"
                    : "border-[var(--color-gold-dim)] text-[var(--color-slate)] hover:border-[var(--color-gold)]"
                }`}
              >
                {g.replace("GROUP_", "Group ")}
              </button>
            ))}
          </div>

          <div className="overflow-x-auto card-depth rounded-lg bg-[var(--color-pitch-navy-light)] p-4">
            <table className="w-full text-sm" style={{ fontFamily: "var(--font-mono)" }}>
              <thead>
                <tr className="text-[var(--color-gold)] border-b border-[var(--color-gold-dim)] text-left">
                  <th className="py-2 pr-4">#</th>
                  <th className="py-2 pr-4">Team</th>
                  <th className="py-2 pr-3 text-center">P</th>
                  <th className="py-2 pr-3 text-center">W</th>
                  <th className="py-2 pr-3 text-center">D</th>
                  <th className="py-2 pr-3 text-center">L</th>
                  <th className="py-2 pr-3 text-center">GD</th>
                  <th className="py-2 pr-3 text-center">Pts</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.team_id} className="border-b border-white/10">
                    <td className="py-2 pr-4 text-[var(--color-slate)]">{r.group_rank}</td>
                    <td className="py-2 pr-4 font-semibold">{r.team_name}</td>
                    <td className="py-2 pr-3 text-center">{r.matches_played}</td>
                    <td className="py-2 pr-3 text-center">{r.wins}</td>
                    <td className="py-2 pr-3 text-center">{r.draws}</td>
                    <td className="py-2 pr-3 text-center">{r.losses}</td>
                    <td className="py-2 pr-3 text-center">{r.goal_difference}</td>
                    <td className="py-2 pr-3 text-center text-[var(--color-gold)] font-bold">{r.points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}