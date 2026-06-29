import Header from "./components/Header";
import Hero from "./components/Hero";
import LiveTicker from "./components/LiveTicker";
import Standings from "./components/Standings";
import TopScorers from "./components/TopScorers";
import PredictionWidget from "./components/PredictionWidget";

function App() {
  return (
    <div className="min-h-screen">
      <Header />
      <LiveTicker />
      <Hero />
      <main className="max-w-6xl mx-auto px-4 py-10">
        <Standings />
        <TopScorers />
        <PredictionWidget />
      </main>
    </div>
  );
}

export default App;