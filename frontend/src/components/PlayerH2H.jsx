import { useEffect, useState } from "react";
import api from "../api/client";
import SectionHeader from "./SectionHeader";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Legend,
} from "recharts";

function PlayerSearch({ label, players, value, onChange }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!value) setQuery("");
  }, [value]);

  const filtered = players
    .filter((p) => p.full_name.toLowerCase().includes(query.toLowerCase()))
    .slice(0, 20);

  const select = (name) => {
    onChange(name);
    setQuery(name);
    setOpen(false);
  };

  return (
    <div className="flex flex-col gap-1 relative">
      <label className="text-xs text-[var(--color-slate)]">{label}</label>
      <input
        type="text"
        value={query}
        placeholder="Type player name..."
        onChange={(e) => { setQuery(e.target.value); setOpen(true); onChange(""); }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        className="bg-[var(--color-pitch-navy-light)] border border-[var(--color-gold-dim)] rounded px-3 py-2 text-sm text-white min-w-[200px] focus:outline-none focus:border-[var(--color-gold)]"
        style={{ fontFamily: "var(--font-mono)" }}
      />
      {open && filtered.length > 0 && (
        <div className="absolute top-full mt-1 left-0 w-full max-h-48 overflow-y-auto bg-[var(--color-pitch-navy)] border border-[var(--color-gold-dim)] rounded z-50 shadow-xl">
          {filtered.map((p) => (
            <div
              key={p.player_id}
              onMouseDown={() => select(p.full_name)}
              className="px-3 py-2 text-sm cursor-pointer hover:bg-[var(--color-gold)]/10 hover:text-[var(--color-gold)]"
            >
              {p.full_name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PlayerH2H() {
  const [players, setPlayers] = useState([]);
  const [playerA, setPlayerA] = useState("");
  const [playerB, setPlayerB] = useState("");
  const [statsA, setStatsA] = useState(null);
  const [statsB, setStatsB] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/players").then((res) => setPlayers(res.data));
  }, []);

  const fetchStats = async () => {
    if (!playerA || !playerB) return;
    setLoading(true);
    try {
      const [a, b] = await Promise.all([
        api.get(`/player-stats/${encodeURIComponent(playerA)}`),
        api.get(`/player-stats/${encodeURIComponent(playerB)}`),
      ]);
      setStatsA(a.data);
      setStatsB(b.data);
    } catch (e) {
      console.error("Failed to fetch player stats:", e);
    } finally {
      setLoading(false);
    }
  };

  const radarData = statsA && statsB
    ? [
        { stat: "Goals", A: statsA.total_goals, B: statsB.total_goals },
        { stat: "Tournaments", A: statsA.tournaments, B: statsB.tournaments },
        { stat: "Goals/Tourney", A: statsA.goals_per_tournament, B: statsB.goals_per_tournament },
        { stat: "Penalties", A: statsA.penalties, B: statsB.penalties },
      ]
    : [];

  const StatRow = ({ label, a, b }) => {
    const aWins = a > b;
    const bWins = b > a;
    return (
      <div className="flex items-center justify-between py-2 border-b border-white/10 text-sm">
        <span className={`w-16 text-right font-bold tabular-nums ${aWins ? "text-[var(--color-gold)]" : "text-white/70"}`}
          style={{ fontFamily: "var(--font-mono)" }}>
          {a ?? "-"}
        </span>
        <span className="text-[var(--color-slate)] text-xs tracking-wide mx-4">{label}</span>
        <span className={`w-16 text-left font-bold tabular-nums ${bWins ? "text-[var(--color-gold)]" : "text-white/70"}`}
          style={{ fontFamily: "var(--font-mono)" }}>
          {b ?? "-"}
        </span>
      </div>
    );
  };

  return (
    <section id="h2h" className="mt-16 scroll-mt-20">
      <SectionHeader eyebrow="PLAYER COMPARISON" title="Head to Head" />

      <div className="card-depth bg-[var(--color-pitch-navy-light)] rounded-lg p-6">
        <div className="flex flex-wrap items-end gap-4 mb-8">
          <PlayerSearch label="Player A" players={players} value={playerA} onChange={setPlayerA} />
          <span className="text-[var(--color-gold)] font-bold pb-2"
            style={{ fontFamily: "var(--font-display)" }}>VS</span>
          <PlayerSearch label="Player B" players={players} value={playerB} onChange={setPlayerB} />
          <button
            onClick={fetchStats}
            disabled={!playerA || !playerB || loading}
            className="bg-[var(--color-gold)] text-[var(--color-pitch-navy)] font-bold px-5 py-2 rounded disabled:opacity-40 hover:brightness-110 transition"
          >
            {loading ? "Loading..." : "Compare"}
          </button>
        </div>

        {statsA && statsB && (
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <div className="flex justify-between mb-4">
                <span className="font-bold text-[var(--color-gold)]"
                  style={{ fontFamily: "var(--font-display)" }}>
                  {statsA.full_name}
                </span>
                <span className="font-bold text-white/60"
                  style={{ fontFamily: "var(--font-display)" }}>
                  {statsB.full_name}
                </span>
              </div>
              <StatRow label="Total Goals" a={statsA.total_goals} b={statsB.total_goals} />
              <StatRow label="Tournaments" a={statsA.tournaments} b={statsB.tournaments} />
              <StatRow label="Goals / Tourney" a={statsA.goals_per_tournament} b={statsB.goals_per_tournament} />
              <StatRow label="Penalties" a={statsA.penalties} b={statsB.penalties} />
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.15)" />
                  <PolarAngleAxis dataKey="stat" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <Radar name={statsA.full_name} dataKey="A"
                    stroke="#ffd700" fill="#ffd700" fillOpacity={0.25} />
                  <Radar name={statsB.full_name} dataKey="B"
                    stroke="#00c853" fill="#00c853" fillOpacity={0.25} />
                  <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}