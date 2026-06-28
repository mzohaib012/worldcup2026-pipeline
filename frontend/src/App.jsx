import LiveTicker from "./components/LiveTicker";
import Standings from "./components/Standings";

function App() {
  return (
    <div className="min-h-screen">
      <LiveTicker />
      <main className="max-w-5xl mx-auto px-4 py-10">
        <h1
          className="text-4xl font-bold text-[var(--color-gold)]"
          style={{ fontFamily: "var(--font-display)" }}
        >
          World Cup 2026 Dashboard
        </h1>
        <Standings />
      </main>
    </div>
  );
}

export default App;