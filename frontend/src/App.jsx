import { useEffect, useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// Turns a country code like "BD" into its flag emoji.
const flag = (iso2) =>
  iso2 && /^[A-Z]{2}$/.test(iso2)
    ? String.fromCodePoint(...[...iso2].map((c) => 0x1f1e6 + c.charCodeAt(0) - 65))
    : "🌍";

const pct = (v) => `${Math.min(v, 100).toFixed(0)}%`;
const COMPARE = [
  ["Life expectancy", "life_expectancy", (v) => `${v.toFixed(0)} years`],
  ["Children who die before age 5", "under5_mortality", (v) => `${v.toFixed(0)} in 1,000`],
  ["Average income (price-adjusted)", "gdp_per_capita", (v) => `$${Math.round(v).toLocaleString()}`],
  ["Finish primary school", "primary_completion", pct],
  ["Finish secondary school", "secondary_completion", pct],
  ["Have electricity", "electricity", pct],
  ["Use the internet", "internet", pct],
  ["Live in extreme poverty", "extreme_poverty", pct],
];

export default function App() {
  const [stage, setStage] = useState("intro"); // intro -> rolling -> life
  const [life, setLife] = useState(null);
  const [shown, setShown] = useState(0);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/stats`).then((r) => r.json()).then(setStats).catch(() => {});
    const seed = new URLSearchParams(window.location.search).get("life");
    if (seed) load(`${API}/api/life/${encodeURIComponent(seed)}`);
  }, []);

  // Reveal the life one event at a time.
  useEffect(() => {
    if (stage !== "life" || !life || shown >= life.events.length) return;
    const t = setTimeout(() => setShown((s) => s + 1), 1100);
    return () => clearTimeout(t);
  }, [stage, life, shown]);

  async function load(url) {
    setError("");
    setStage("rolling");
    setShown(0);
    setCopied(false);
    try {
      const [res] = await Promise.all([fetch(url), new Promise((r) => setTimeout(r, 1800))]);
      if (!res.ok) throw new Error("bad response");
      const data = await res.json();
      setLife(data);
      window.history.replaceState(null, "", `?life=${data.seed}`);
      setStage("life");
    } catch {
      setError("Couldn't reach the server. Is the backend running?");
      setStage("intro");
    }
  }

  async function share() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
    } catch {
      setError("Couldn't copy. Copy the link from the address bar instead.");
    }
  }

  const bornAgain = () => load(`${API}/api/born`);
  const done = life && shown >= life.events.length;

  return (
    <main>
      {stage === "intro" && (
        <section className="intro">
          <h1>The Lottery of Birth</h1>
          <p>
            About {stats ? stats.births_per_year.toLocaleString() : "134 million"} babies are born every year.
            None of them choose where.
          </p>
          <p className="muted">Press the button. You'll be born somewhere on Earth, with the real odds of that place.</p>
          <button onClick={bornAgain}>Be born</button>
          {error && <p className="error">{error}</p>}
        </section>
      )}

      {stage === "rolling" && (
        <section className="rolling">
          <div className="globe">🌍</div>
          <p>Rolling the dice of birth…</p>
        </section>
      )}

      {stage === "life" && life && (
        <section>
          <header className="reveal">
            <div className="flag">{flag(life.country.iso2)}</div>
            <h2>You are born in {life.country.name}</h2>
            <p className="muted">
              A {life.sex} · {life.country.region} · {life.birth_chance_percent}% of the world's babies are born here
            </p>
          </header>

          <ol className="timeline">
            {life.events.slice(0, shown).map((e, i) => (
              <li key={i} className={e.good === true ? "good" : e.good === false ? "bad" : ""}>
                <span className="age">Age {e.age}</span>
                <span>{e.text}</span>
              </li>
            ))}
          </ol>

          {done && (
            <>
              {life.compare && (
                <table>
                  <thead>
                    <tr><th></th><th>{life.country.name}</th><th>{life.compare.name}</th></tr>
                  </thead>
                  <tbody>
                    {COMPARE.map(([label, key, f]) =>
                      life.stats[key] != null && life.compare.stats[key] != null ? (
                        <tr key={key}>
                          <td>{label}</td>
                          <td>{f(life.stats[key])}</td>
                          <td>{f(life.compare.stats[key])}</td>
                        </tr>
                      ) : null
                    )}
                  </tbody>
                </table>
              )}
              <div className="actions">
                <button onClick={bornAgain}>Be born again</button>
                <button className="secondary" onClick={share}>{copied ? "Link copied!" : "Share this life"}</button>
              </div>
              <p className="source">Data: World Bank. Each life is a simulation using the real odds of where you're born.</p>
            </>
          )}
          {error && <p className="error">{error}</p>}
        </section>
      )}
    </main>
  );
}
