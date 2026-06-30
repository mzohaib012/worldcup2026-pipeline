import { API_BASE_URL } from "../api/client";

export default function PlayerCardModal({ playerName, onClose }) {
  if (!playerName) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div className="relative max-w-sm w-full" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={onClose}
          className="absolute -top-3 -right-3 w-9 h-9 rounded-full bg-[var(--color-gold)] text-[var(--color-pitch-navy)] font-bold flex items-center justify-center hover:brightness-110 z-10"
          aria-label="Close"
        >
          ✕
        </button>
        <img
          src={`${API_BASE_URL}/player-card/${encodeURIComponent(playerName)}`}
          alt={playerName}
          className="w-full h-auto rounded-lg"
        />
      </div>
    </div>
  );
}