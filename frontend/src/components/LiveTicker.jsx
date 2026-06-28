import { useEffect, useState } from "react";
import api from "../api/client";

export default function LiveTicker() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatches = () => {
      api
        .get("/catch-me-up")
        .then((res) => setMatches(res.data.catch_me_up || []))
        .catch((err) => console.error("Failed to fetch catch-me-up:", err))
        .finally(() => setLoading(false));
    };

    fetchMatches();
    const interval = setInterval(fetchMatches, 60000);
    return () => clearInterval(interval);
  }, []);

  // Roughly 6 seconds per item keeps the scroll speed consistent
  // regardless of how many matches are currently in the feed.
  const duration = Math.max(matches.length * 6, 15);

  return (
    <div className="bg-[var(--color-pitch-navy-light)] border-b border-[var(--color-gold-dim)] py-3 px-4">
      <div className="flex items-center gap-3 mb-2">
        <span className="w-2 h-2 rounded-full bg-[var(--color-live-green)] animate-pulse"></span>
        <span
          className="text-xs font-bold uppercase tracking-widest text-[var(--color-gold)]"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Catch Me Up
        </span>
      </div>

      {loading ? (
        <p className="text-sm text-[var(--color-slate)]">Loading latest matches...</p>
      ) : matches.length === 0 ? (
        <p className="text-sm text-[var(--color-slate)]">No recent match activity.</p>
      ) : (
        <div className="overflow-hidden">
          <div
            className="marquee-track flex gap-10 whitespace-nowrap w-max"
            style={{ animationDuration: `${duration}s` }}
          >
            {[...matches, ...matches].map((m, i) => (
              <span
                key={i}
                className="text-sm flex-shrink-0"
                style={{ fontFamily: "var(--font-mono)" }}
              >
                {m}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}