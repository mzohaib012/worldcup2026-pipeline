import { useEffect, useRef } from "react";
import confetti from "canvas-confetti";

export function GoalAnimation({ show, onDone }) {
  useEffect(() => {
    if (!show) return;

    // Burst from both sides like a stadium celebration
    const left = confetti.create(null, { resize: true, useWorker: true });
    const right = confetti.create(null, { resize: true, useWorker: true });

    left({
      particleCount: 80,
      angle: 60,
      spread: 55,
      origin: { x: 0, y: 0.65 },
      colors: ["#ffd700", "#ffffff", "#00c853"],
    });
    right({
      particleCount: 80,
      angle: 120,
      spread: 55,
      origin: { x: 1, y: 0.65 },
      colors: ["#ffd700", "#ffffff", "#00c853"],
    });

    const timer = setTimeout(onDone, 3000);
    return () => clearTimeout(timer);
  }, [show, onDone]);

  if (!show) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
      <div
        className="text-center animate-bounce"
        style={{
          animation: "goalPop 0.4s ease-out forwards",
        }}
      >
        <p
          className="text-6xl md:text-8xl font-bold text-[var(--color-gold)]"
          style={{
            fontFamily: "var(--font-display)",
            textShadow: "0 0 40px rgba(255,215,0,0.8), 0 0 80px rgba(255,215,0,0.4)",
          }}
        >
          GOAL!
        </p>
        <p className="text-white text-lg mt-2" style={{ fontFamily: "var(--font-mono)" }}>
          ⚽
        </p>
      </div>
    </div>
  );
}

export function WinnerAnimation({ show, winner, onDone }) {
  useEffect(() => {
    if (!show) return;

    // Sustained celebration for match winner
    const duration = 4000;
    const end = Date.now() + duration;

    const frame = () => {
      confetti({
        particleCount: 6,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ["#ffd700", "#ffffff", "#0b1929"],
      });
      confetti({
        particleCount: 6,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ["#ffd700", "#ffffff", "#0b1929"],
      });
      if (Date.now() < end) requestAnimationFrame(frame);
    };
    frame();

    const timer = setTimeout(onDone, duration + 500);
    return () => clearTimeout(timer);
  }, [show, onDone]);

  if (!show) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: "rgba(3, 7, 18, 0.85)", backdropFilter: "blur(4px)" }}
      onClick={onDone}
    >
      <div className="text-center px-6">
        <p
          className="text-xs tracking-[0.4em] text-[var(--color-gold)] mb-4"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          FULL TIME
        </p>
        <p
          className="text-4xl md:text-6xl font-bold text-white mb-2"
          style={{
            fontFamily: "var(--font-display)",
            textShadow: "0 0 30px rgba(255,215,0,0.6)",
          }}
        >
          {winner}
        </p>
        <p
          className="text-[var(--color-gold)] text-xl font-bold"
          style={{ fontFamily: "var(--font-display)" }}
        >
          WINS! 🏆
        </p>
        <p className="text-[var(--color-slate)] text-xs mt-6" style={{ fontFamily: "var(--font-mono)" }}>
          tap to dismiss
        </p>
      </div>
    </div>
  );
}