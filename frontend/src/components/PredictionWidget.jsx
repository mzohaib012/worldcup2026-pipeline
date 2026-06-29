import { useEffect, useState } from "react";
import api from "../api/client";
import SectionHeader from "./SectionHeader";

export default function PredictionWidget() {
  const [teams, setTeams] = useState([]);
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get("/teams")
      .then((res) => setTeams(res.data))
      .catch((err) => console.error("Failed to fetch teams:", err));
  }, []);

  const handlePredict = () => {
    if (!homeTeam || !awayTeam) return;
    setLoading(true);
    setError(null);
    setResult(null);
    api
      .get(`/predict/${encodeURIComponent(homeTeam)}/${encodeURIComponent(awayTeam)}`)
      .then((res) => setResult(res.data))
      .catch(() => setError("Could not generate a prediction for these teams."))
      .finally(() => setLoading(false));
  };

  const barColor = (label) => {
    if (label === "HOME_WIN") return "var(--color-gold)";
    if (label === "AWAY_WIN") return "var(--color-live-green)";
    return "var(--color-slate)";
  };

  const labelText = (label) => {
    if (label === "HOME_WIN") return homeTeam || "Home";
    if (label === "AWAY_WIN") return awayTeam || "Away";
    return "Draw";
  };

  return (
    <section className="mt-16">
      <SectionHeader eyebrow="MACHINE LEARNING" title="Win Probability Predictor" />

      <div className="card-depth bg-[var(--color-pitch-navy-light)] rounded-lg p-6">
      <div className="flex flex-wrap items-end gap-4 mb-6">
        <div className="flex flex-col">
          <label className="text-xs text-[var(--color-slate)] mb-1">Home Team</label>
          <select
            value={homeTeam}
            onChange={(e) => setHomeTeam(e.target.value)}
            className="bg-[var(--color-pitch-navy-light)] border border-[var(--color-gold-dim)] rounded px-3 py-2 text-sm min-w-[180px]"
          >
            <option value="">Select team...</option>
            {teams.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <span className="text-[var(--color-gold)] font-bold pb-2">VS</span>

        <div className="flex flex-col">
          <label className="text-xs text-[var(--color-slate)] mb-1">Away Team</label>
          <select
            value={awayTeam}
            onChange={(e) => setAwayTeam(e.target.value)}
            className="broadcast-select min-w-[180px]"
          >
            <option value="">Select team...</option>
            {teams.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <button
          onClick={handlePredict}
          disabled={!homeTeam || !awayTeam || loading}
          className="bg-[var(--color-gold)] text-[var(--color-pitch-navy)] font-bold px-5 py-2 rounded disabled:opacity-40 hover:brightness-110 hover:shadow-[0_0_20px_rgba(255,215,0,0.5)] transition"
        >
          {loading ? "Predicting..." : "Predict"}
        </button>
      </div>

      {error && <p className="text-[var(--color-slate)]">{error}</p>}

      {result && (
        <div className="space-y-3 max-w-md">
          {Object.entries(result.probabilities).map(([label, value]) => {
            const pct = parseFloat(value);
            return (
              <div key={label}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{labelText(label)}</span>
                  <span style={{ fontFamily: "var(--font-mono)" }}>{value}</span>
                </div>
                <div className="h-2 bg-white/10 rounded overflow-hidden">
                  <div
                    className="h-full rounded transition-all duration-500"
                    style={{ width: `${pct}%`, backgroundColor: barColor(label) }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
      </div>
    </section>
  );
}