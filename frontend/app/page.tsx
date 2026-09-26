"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import BossSprite from "@/components/BossSprite";
import CloudSky from "@/components/CloudSky";
import PixelArt, { SPRITES, type SpriteKey } from "@/components/PixelArt";
import RetroWindow from "@/components/RetroWindow";
import { api, level } from "@/lib/api";

type DungeonRow = Awaited<ReturnType<typeof api.dungeons>>[number];
type Popup =
  | { kind: "upload" }
  | { kind: "busy"; label: string }
  | { kind: "done"; id: number; title: string; rooms: number; boss: string }
  | { kind: "error"; message: string };

const HERO_BOSSES: SpriteKey[] = ["ghost", "mimic", "slime", "skull"];

const EVAL = [
  { name: "Overall accuracy (baseline)", auc: 0.682 },
  { name: "Logistic regression", auc: 0.725 },
  { name: "Our topic-agnostic tracer", auc: 0.759, ours: true },
  { name: "DKT LSTM (fixed skills only)", auc: 0.819 },
];

export default function Home() {
  const router = useRouter();
  const input = useRef<HTMLInputElement>(null);
  const [dungeons, setDungeons] = useState<DungeonRow[]>([]);
  const [llm, setLlm] = useState<boolean | null>(null);
  const [offline, setOffline] = useState(false);
  const [popup, setPopup] = useState<Popup | null>(null);
  const [dragging, setDragging] = useState(false);
  const [boss, setBoss] = useState(0);

  useEffect(() => {
    api.health().then((h) => setLlm(h.llm)).catch(() => setOffline(true));
    api.dungeons().then(setDungeons).catch(() => {});
  }, []);

  useEffect(() => {
    if (!popup || popup.kind === "busy") return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setPopup(null);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [popup]);

  async function run(label: string, fn: () => Promise<{ id: number }>) {
    setPopup({ kind: "busy", label });
    try {
      const { id } = await fn();
      const snap = await api.dungeon(String(id));
      const first = snap.rooms.find((r) => r.status === "open") ?? snap.rooms[0];
      setPopup({ kind: "done", id, title: snap.dungeon.title, rooms: snap.rooms.length, boss: first?.boss_name ?? snap.dungeon.title });
    } catch (e) {
      setPopup({ kind: "error", message: (e as Error).message });
    }
  }

  function onFile(file?: File) {
    if (file) run("The Dungeon Master is reading your notes and carving rooms…", () => api.upload(file));
  }

  const demo = () => run("Unlocking the Kernel Catacombs…", api.createDemo);

  return (
    <main className="landing">
      <section className="hero">
        <CloudSky variant="hero" />
        <nav className="nav">
          <span className="logo">
            <PixelArt sprite="logo" size={28} />
            <span className="pixel">Knowledge Dungeon</span>
          </span>
          <span className="nav-links">
            <a href="#how">How it works</a>
            <a href="#model">The model</a>
            {dungeons.length > 0 && <a href="#saves">Saves</a>}
            <button onClick={demo}>Demo</button>
          </span>
        </nav>

        <div className="hero-grid">
          <div className="hero-copy">
            <h1 className="display">Knowledge<br />Dungeon</h1>
            <p className="lede">
              Turn your notes into a dungeon. Every chapter is a room, every room has a boss,
              and an AI Dungeon Master sends back the ones you&apos;re forgetting.
            </p>
            <div className="cta-row">
              <button className="btn primary" onClick={() => setPopup({ kind: "upload" })}>Upload notes</button>
              <button className="btn link" onClick={demo}>Try the demo <span aria-hidden>›</span></button>
            </div>
            {offline && <p className="notice">Can&apos;t reach the game server. Is the backend running on port 8000?</p>}
          </div>
          <button className="hero-boss" onClick={() => setBoss((b) => (b + 1) % HERO_BOSSES.length)} title="Summon another boss">
            <PixelArt sprite={HERO_BOSSES[boss]} size={340} variant="scan" key={boss} />
            <span className="caption pixel">A wild {SPRITES[HERO_BOSSES[boss]].name} appeared!</span>
          </button>
        </div>

        <div className="ticker" aria-hidden>
          <div>
            {Array.from({ length: 2 }, (_, k) => (
              <span key={k}>
                ✦ trained on 325k real student answers ✦ tracer AUC 0.759 on unseen topics ✦ bosses write questions from your own notes
                ✦ every question double-checked by a blind verifier ✦ forgotten bosses respawn ✦ spaced repetition 1 → 3 → 7 → 14 → 30 days&nbsp;
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className="section" id="how">
        <h2 className="section-title pixel">How it works</h2>
        <div className="how-grid">
          <RetroWindow title="01_map.exe">
            <svg viewBox="0 0 60 26" className="how-art" shapeRendering="crispEdges" aria-hidden>
              <path d="M14 13 H22 M36 7 H44 M36 19 H44 M30 10 V16" stroke="var(--ink)" strokeWidth="1.5" fill="none" strokeDasharray="2 1.5" />
              <rect x="2" y="8" width="12" height="10" fill="var(--ink)" />
              <rect x="22" y="8" width="14" height="10" fill="var(--peach)" stroke="var(--ink)" />
              <rect x="44" y="2" width="12" height="10" fill="var(--white)" stroke="var(--ink)" />
              <rect x="44" y="14" width="12" height="10" fill="var(--white)" stroke="var(--ink)" />
            </svg>
            <h3 className="pixel">Map</h3>
            <p>An LLM reads your notes, or a whole textbook&apos;s chapter list, and carves one room per topic, locked behind the topics it builds on.</p>
          </RetroWindow>
          <RetroWindow title="02_fight.exe">
            <div className="how-art"><PixelArt sprite="mimic" size={56} /></div>
            <h3 className="pixel">Fight</h3>
            <p>Bosses ask questions written from your notes. The weaker the topic, the tougher the boss and the longer the fight.</p>
          </RetroWindow>
          <RetroWindow title="03_remember.exe">
            <div className="how-art"><PixelArt sprite="ghost" size={56} variant="scan" /></div>
            <h3 className="pixel">Remember</h3>
            <p>A knowledge-tracing model predicts what you&apos;re forgetting. The Dungeon Master respawns those bosses and points you to the next room.</p>
          </RetroWindow>
        </div>
      </section>

      {dungeons.length > 0 && (
        <section className="section" id="saves">
          <h2 className="section-title pixel">Continue</h2>
          <RetroWindow title="saves.dat" bodyClassName="saves">
            <ul>
              {dungeons.map((d) => (
                <li key={d.id}>
                  <Link href={`/dungeon/${d.id}`} className="save-row">
                    <BossSprite name={d.title} size={34} />
                    <span className="save-title">{d.title}{d.is_demo ? <em> · demo</em> : null}</span>
                    <span className="save-meta">Lv {level(d.xp)} · {d.xp} XP</span>
                    <span className="pixel" aria-hidden>›</span>
                  </Link>
                </li>
              ))}
            </ul>
          </RetroWindow>
        </section>
      )}

      <section className="section" id="model">
        <h2 className="section-title pixel">The model</h2>
        <div className="model-grid">
          <div className="model-copy">
            <p>
              Classic knowledge tracing learns a fixed list of skills, so a model trained on maths can&apos;t
              judge your DBMS notes. Our tracer learns <b>how people learn</b> instead: attempts, streaks,
              recency and accuracy, signals that exist for any topic.
            </p>
            <p>
              It trades some accuracy for working on topics it has never seen, which is exactly what a game
              built from your own notes needs. Trained and tested on ASSISTments 2009 (325k answers).
            </p>
          </div>
          <RetroWindow title="tracer_eval.log" bodyClassName="eval">
            {EVAL.map((m) => (
              <div key={m.name} className={`eval-row${m.ours ? " ours" : ""}`}>
                <span>{m.name}</span>
                <span className="eval-bar"><span style={{ width: `${((m.auc - 0.5) / 0.35) * 100}%` }} /></span>
                <b>{m.auc.toFixed(3)}</b>
              </div>
            ))}
            <p className="eval-note">Test AUC, higher is better</p>
          </RetroWindow>
        </div>
      </section>

      <footer className="footer">
        <span className="pixel">Knowledge Dungeon</span>
        <span>ML Empowerment Build Challenge 3.0 · built on a laptop CPU</span>
      </footer>

      {popup && (
        <div className="backdrop" onClick={() => popup.kind !== "busy" && setPopup(null)}>
          <div onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
            {popup.kind === "upload" && (
              <RetroWindow title="new_dungeon.exe" onClose={() => setPopup(null)} className="popup">
                <div
                  className={`dropzone${dragging ? " dragging" : ""}${llm === false ? " disabled" : ""}`}
                  onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={(e) => { e.preventDefault(); setDragging(false); if (llm) onFile(e.dataTransfer.files[0]); }}
                  onClick={() => llm && input.current?.click()}
                  role="button"
                  tabIndex={0}
                >
                  <span className="drop-icon" aria-hidden>
                    <svg viewBox="0 0 10 12" width="40" height="48" shapeRendering="crispEdges">
                      <path d="M0 0H7L10 3V12H0Z" fill="var(--white)" stroke="var(--ink)" strokeWidth="1" />
                      <path d="M2 5H8M2 7H8M2 9H6" stroke="var(--peach-2)" strokeWidth="1" />
                    </svg>
                  </span>
                  <b>Drop your notes here</b>
                  <span>PDF, Markdown or text, up to a whole textbook</span>
                </div>
                {llm === false && <p className="notice">Building from your own notes needs an LLM key on the server. The demo works without one.</p>}
                <input ref={input} type="file" accept=".pdf,.md,.txt" hidden onChange={(e) => onFile(e.target.files?.[0])} />
                <div className="popup-actions">
                  <button className="btn" onClick={() => setPopup(null)}>Cancel</button>
                  <button className="btn primary" onClick={() => input.current?.click()} disabled={!llm} autoFocus>Choose file</button>
                </div>
              </RetroWindow>
            )}
            {popup.kind === "busy" && (
              <RetroWindow title="please_wait.exe" className="popup">
                <p className="popup-text">{popup.label}</p>
                <div className="blocks" aria-hidden>{Array.from({ length: 14 }, (_, i) => <span key={i} style={{ animationDelay: `${i * 0.12}s` }} />)}</div>
              </RetroWindow>
            )}
            {popup.kind === "done" && (
              <RetroWindow title="ダンジョンのメッセージ" onClose={() => setPopup(null)} className="popup">
                <p className="popup-text big">You have received a dungeon.</p>
                <p className="popup-sub">{popup.title} · {popup.rooms} rooms</p>
                <div className="popup-sprite"><BossSprite name={popup.boss} size={84} /></div>
                <div className="popup-actions center">
                  <button className="btn ok" onClick={() => router.push(`/dungeon/${popup.id}`)} autoFocus>Ok</button>
                </div>
              </RetroWindow>
            )}
            {popup.kind === "error" && (
              <RetroWindow title="error.exe" onClose={() => setPopup(null)} className="popup">
                <p className="popup-text">{popup.message}</p>
                <div className="popup-actions center">
                  <button className="btn ok" onClick={() => setPopup(null)} autoFocus>Ok</button>
                </div>
              </RetroWindow>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
