import { useEffect, useState, useRef } from "react";
import api from "../api/client";
import { GoalAnimation, WinnerAnimation } from "./CelebrationOverlay";

function useCountdown(targetIso) {
  const [timeLeft, setTimeLeft] = useState(null);

  useEffect(() => {
    if (!targetIso) return;
    const target = new Date(targetIso).getTime();

    const tick = () => {
      const diff = target - Date.now();
      if (diff <= 0) {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
        return;
      }
      setTimeLeft({
        days: Math.floor(diff / 86400000),
        hours: Math.floor((diff % 86400000) / 3600000),
        minutes: Math.floor((diff % 3600000) / 60000),
        seconds: Math.floor((diff % 60000) / 1000),
      });
    };

    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [targetIso]);

  return timeLeft;
}

function TimeBlock({ value, label }) {
  return (
    <div className="flex flex-col items-center">
      <span
        className="text-4xl md:text-5xl font-bold text-[var(--color-gold)] tabular-nums"
        style={{ fontFamily: "var(--font-display)" }}
      >
        {String(value).padStart(2, "0")}
      </span>
      <span className="text-xs tracking-widest text-[var(--color-slate)] mt-1">{label}</span>
    </div>
  );
}

export default function LiveScoreboard() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showGoal, setShowGoal] = useState(false);
  const [showWinner, setShowWinner] = useState(false);
  const [winner, setWinner] = useState("");
  const prevScoreRef = useRef(null);
  const prevStatusRef = useRef(null);
  const prevTeamsRef = useRef(null);

  useEffect(() => {
    const fetchStatus = () => {
      api
        .get("/live-status")
        .then((res) => {
          const data = res.data;

          // Goal animation: total score increased while match is live
          if (prevScoreRef.current && data.mode === "live") {
            const prevTotal = prevScoreRef.current.home + prevScoreRef.current.away;
            const newTotal = (data.home_score || 0) + (data.away_score || 0);
            if (newTotal > prevTotal) setShowGoal(true);
          }
          if (data.mode === "live") {
            prevScoreRef.current = {
              home: data.home_score || 0,
              away: data.away_score || 0,
            };
            prevTeamsRef.current = {
              home: data.home_team,
              away: data.away_team,
            };
          }

          // Winner animation: match just finished
          if (prevStatusRef.current === "live" && data.mode === "countdown") {
            if (prevScoreRef.current && prevTeamsRef.current) {
              const h = prevScoreRef.current.home;
              const a = prevScoreRef.current.away;
              if (h > a) {
                setWinner(prevTeamsRef.current.home);
                setShowWinner(true);
              } else if (a > h) {
                setWinner(prevTeamsRef.current.away);
                setShowWinner(true);
              }
            }
          }

          prevStatusRef.current = data.mode;
          setStatus(data);
        })
        .catch((err) => console.error("Failed to fetch live status:", err))
        .finally(() => setLoading(false));
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const countdown = useCountdown(
    status?.mode === "countdown" ? status.kickoff_utc : null
  );

  if (loading) {
    return (
      <div className="stadium-glow relative overflow-hidden">
        <div className="pitch-stripes" />
        <div className="relative max-w-3xl mx-auto px-4 py-14 text-center text-[var(--color-slate)]">
          Loading match status...
        </div>
      </div>
    );
  }

  if (!status || status.mode === "none") {
    return (
      <div className="stadium-glow relative overflow-hidden">
        <div className="pitch-stripes" />
        <div className="relative max-w-3xl mx-auto px-4 py-14 text-center">
          <p className="text-[var(--color-slate)]" style={{ fontFamily: "var(--font-mono)" }}>
            No upcoming fixtures in the next window.
          </p>
        </div>
      </div>
    );
  }

  if (status.mode === "live") {
    return (
      <div className="stadium-glow relative overflow-hidden">
        <div className="pitch-stripes" />
        <div className="relative max-w-3xl mx-auto px-4 py-12 text-center">
          <div className="inline-flex items-center gap-2 mb-6 px-3 py-1 rounded-full bg-[var(--color-live-green)]/15 border border-[var(--color-live-green)]/40">
            <span className="w-2 h-2 rounded-full bg-[var(--color-live-green)] animate-pulse" />
            <span
              className="text-xs tracking-widest text-[var(--color-live-green)] font-bold"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              {status.status_label?.toUpperCase()}
              {status.minute != null && ` \u2022 ${status.minute}'`}
            </span>
          </div>

          <div className="flex items-center justify-center gap-8 md:gap-16">
            <p
              className="text-lg md:text-2xl font-semibold text-white text-right w-32 md:w-48 truncate"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {status.home_team}
            </p>
            <p
              className="text-5xl md:text-6xl font-bold text-[var(--color-gold)] tabular-nums"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {status.home_score}{" "}
              <span className="text-white/30 mx-1">-</span>{" "}
              {status.away_score}
            </p>
            <p
              className="text-lg md:text-2xl font-semibold text-white text-left w-32 md:w-48 truncate"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {status.away_team}
            </p>
          </div>
        </div>

        <GoalAnimation show={showGoal} onDone={() => setShowGoal(false)} />
        <WinnerAnimation
          show={showWinner}
          winner={winner}
          onDone={() => setShowWinner(false)}
        />
      </div>
    );
  }

  // Countdown mode
  return (
    <div className="stadium-glow relative overflow-hidden">
      <div className="pitch-stripes" />
      <div className="relative max-w-3xl mx-auto px-4 py-12 text-center">
        <p
          className="text-xs tracking-[0.3em] text-[var(--color-slate)] mb-3"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          NEXT KICKOFF
        </p>
        <p
          className="text-xl md:text-2xl font-semibold text-white mb-8"
          style={{ fontFamily: "var(--font-display)" }}
        >
          {status.home_team}{" "}
          <span className="text-[var(--color-gold)]">vs</span>{" "}
          {status.away_team}
        </p>

        {countdown && (
          <div className="flex items-center justify-center gap-6 md:gap-10">
            <TimeBlock value={countdown.days} label="DAYS" />
            <span className="text-2xl text-[var(--color-gold-dim)] -mt-4">:</span>
            <TimeBlock value={countdown.hours} label="HRS" />
            <span className="text-2xl text-[var(--color-gold-dim)] -mt-4">:</span>
            <TimeBlock value={countdown.minutes} label="MIN" />
            <span className="text-2xl text-[var(--color-gold-dim)] -mt-4">:</span>
            <TimeBlock value={countdown.seconds} label="SEC" />
          </div>
        )}
      </div>
       

      <GoalAnimation show={showGoal} onDone={() => setShowGoal(false)} />
      <WinnerAnimation
        show={showWinner}
        winner={winner}
        onDone={() => setShowWinner(false)}
      />
    </div>
  );
}