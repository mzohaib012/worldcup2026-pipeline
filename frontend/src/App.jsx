import Header from "./components/Header";
import Hero from "./components/Hero";
 import KnockoutBracket from "./components/KnockoutBracket";
import LiveTicker from "./components/LiveTicker";
import Standings from "./components/Standings";
import TopScorers from "./components/TopScorers";
import PredictionWidget from "./components/PredictionWidget";
import LiveScoreboard from "./components/LiveScoreboard";
import Schedule from "./components/Schedule";
import PlayerH2H from "./components/PlayerH2H";

function App() {
  return (
    <div className="min-h-screen">
      <Header />
      <Hero />
      <LiveScoreboard />
      <LiveTicker />
      <main className="max-w-6xl mx-auto px-4 py-10">
        <Standings />
        <Schedule />
        <PlayerH2H />
        <KnockoutBracket />
        <TopScorers />
        <PredictionWidget />
      </main>
    </div>
  );
}

export default App;