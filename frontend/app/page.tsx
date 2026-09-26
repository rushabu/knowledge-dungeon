"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import BossSprite from "@/components/BossSprite";
import { api, level } from "@/lib/api";

type DungeonRow = Awaited<ReturnType<typeof api.dungeons>>[number];

export default function Home() {
  const router = useRouter();
  const input = useRef<HTMLInputElement>(null);
  const [dungeons, setDungeons] = useState<DungeonRow[]>([]);
  const [llm, setLlm] = useState<boolean | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    api.health().then((h) => setLlm(h.llm)).catch(() => setError("Can't reach the game server. Is the backend running?"));
    api.dungeons().then(setDungeons).catch(() => {});
  }, []);

  async function run(label: string, fn: () => Promise<{ id: number }>) {
    setBusy(label);
    setError(null);
    try {
      const { id } = await fn();
      router.push(`/dungeon/${id}`);
    } catch (e) {
      setError((e as Error).message);
      setBusy(null);
    }
  }

  function onFile(file?: File) {
    if (file) run("The Dungeon Master is reading your notes and carving rooms…", () => api.upload(file));
  }

  return (
    <main className="home">
      <header className="hero">
        <div className="hero-sprites" aria-hidden>
          <BossSprite name="Paging Lich" size={72} />
          <BossSprite name="Mutex Golem" size={96} />
          <BossSprite name="Forkling Hydra" size={72} />
        </div>
        <h1 className="pixel">Knowledge<br />Dungeon</h1>
        <p className="tagline">
          Drop in your notes. Every topic becomes a room, every room has a boss.
          An AI Dungeon Master tracks what you&apos;re forgetting and sends the bosses back.
        </p>
      </header>

      {busy ? (
        <div className="panel loading">
          <div className="torch" aria-hidden />
          <p>{busy}</p>
        </div>
      ) : (
        <section className="start-grid">
          <div
            className={`panel dropzone${dragging ? " dragging" : ""}${llm === false ? " disabled" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => { e.preventDefault(); setDragging(false); if (llm) onFile(e.dataTransfer.files[0]); }}
            onClick={() => llm && input.current?.click()}
            role="button"
            tabIndex={0}
          >
            <span className="pixel small">Your notes</span>
            <p>Drop a PDF, Markdown or text file here, or click to choose.</p>
            {llm === false && <p className="hint">Needs an LLM key on the server (LLM_API_KEY). The demo works without one.</p>}
            <input ref={input} type="file" accept=".pdf,.md,.txt" hidden onChange={(e) => onFile(e.target.files?.[0])} />
          </div>
          <button className="panel demo-card" onClick={() => run("Opening the Kernel Catacombs…", api.createDemo)}>
            <span className="pixel small">Demo dungeon</span>
            <p>The Kernel Catacombs: 6 rooms of Operating Systems, from processes to page replacement.</p>
            <span className="cta">Enter →</span>
          </button>
        </section>
      )}

      {error && <p className="error">{error}</p>}

      {dungeons.length > 0 && !busy && (
        <section className="saves">
          <h2 className="pixel small">Continue</h2>
          <ul>
            {dungeons.map((d) => (
              <li key={d.id}>
                <Link href={`/dungeon/${d.id}`} className="save-row">
                  <span>{d.title}{d.is_demo ? <em> · demo</em> : null}</span>
                  <span className="muted">Lv {level(d.xp)} · {d.xp} XP</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <footer className="how">
        <div><b>1 · Map</b><span>An LLM finds the topics in your notes and how they depend on each other.</span></div>
        <div><b>2 · Fight</b><span>Bosses ask questions written from your notes. Weak topics mean longer fights.</span></div>
        <div><b>3 · Remember</b><span>A knowledge-tracing model predicts what you&apos;re forgetting. Those bosses respawn.</span></div>
      </footer>
    </main>
  );
}
