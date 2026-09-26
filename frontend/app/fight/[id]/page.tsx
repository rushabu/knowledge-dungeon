"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import BossSprite from "@/components/BossSprite";
import { api, type DMTurn, type Fight } from "@/lib/api";

export default function FightPage() {
  const { id } = useParams<{ id: string }>();
  const [fight, setFight] = useState<Fight | null>(null);
  // `result` holds the answered state; `fight.question` is only swapped in on "Next"
  const [result, setResult] = useState<Fight | null>(null);
  const [picked, setPicked] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hitKey, setHitKey] = useState(0);
  const [dm, setDm] = useState<DMTurn | null>(null);

  useEffect(() => {
    api.fight(id).then(setFight).catch((e) => setError(e.message));
  }, [id]);

  const choose = useCallback(async (choice: number) => {
    if (!fight?.question || picked !== null) return;
    setPicked(choice);
    try {
      const next = await api.answer(fight.id, fight.question.id, choice);
      setResult(next);
      setHitKey((k) => k + 1);
    } catch (e) {
      setError((e as Error).message);
      setPicked(null);
    }
  }, [fight, picked]);

  const advance = useCallback(() => {
    if (!result) return;
    setFight(result);
    setResult(null);
    setPicked(null);
  }, [result]);

  // once the fight ends, the Dungeon Master takes its turn (slow: an LLM agent loop)
  const fightOver = (result ?? fight)?.status !== undefined && (result ?? fight)?.status !== "active";
  const fightId = fight?.id;
  useEffect(() => {
    if (!fightOver || fightId === undefined) return;
    let cancelled = false;
    api.dmTurn(fightId).then((t) => { if (!cancelled) setDm(t); }).catch(() => {});
    return () => { cancelled = true; };
  }, [fightOver, fightId]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (result && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); advance(); }
      else if (!result && ["1", "2", "3", "4"].includes(e.key)) choose(Number(e.key) - 1);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [result, advance, choose]);

  if (error) return <main className="page"><p className="error">{error}</p><Link href="/">← Back</Link></main>;
  if (!fight) return <main className="page"><div className="torch" aria-hidden /></main>;

  const view = result ?? fight;          // HP bars update the moment you answer
  const question = fight.question;        // question stays on screen until "Next"
  const outcome = result?.outcome;
  const over = view.status !== "active";

  return (
    <main className={`page fight-page${outcome && !outcome.correct ? " shake" : ""}`} key={outcome && !outcome.correct ? hitKey : undefined}>
      <header className="topbar">
        <Link href={`/dungeon/${fight.room.dungeon_id}`} className="pixel small back">← Flee</Link>
        <h1 className="pixel small">{fight.room.title}</h1>
        <span className={`diff ${fight.difficulty}`}>{fight.difficulty}</span>
      </header>

      <section className="arena">
        <div className="combatant boss">
          <div className="sprite-wrap" key={outcome?.correct ? hitKey : "idle"}>
            <BossSprite name={view.boss.name} size={180} hurt={!!outcome?.correct} defeated={view.status === "won"} />
            {outcome?.correct && <span className="damage pixel">-1</span>}
          </div>
          <div className="nameplate">
            <b>{view.boss.name}</b>
            <span className="hpbar boss"><span style={{ width: `${(view.boss.hp / view.boss.max_hp) * 100}%` }} /></span>
            <span className="muted">{view.boss.flavor}</span>
          </div>
        </div>
        <div className="combatant player">
          <span className="hearts" aria-label={`${view.player_hp} of ${view.max_player_hp} hearts`}>
            {Array.from({ length: view.max_player_hp }, (_, i) => (
              <span key={i} className={i < view.player_hp ? "heart" : "heart lost"}>♥</span>
            ))}
          </span>
          {outcome && (
            <span className="tracer">
              Mastery: <b>{Math.round((view.mastery ?? outcome.mastery) * 100)}%</b> → <b>{Math.round(outcome.mastery * 100)}%</b>
            </span>
          )}
        </div>
      </section>

      {!over || result ? (
        question && (
          <section className="panel question">
            <p className="prompt">{question.prompt}</p>
            <div className="options">
              {question.options.map((opt, i) => {
                const state = outcome
                  ? i === outcome.answer ? "right" : i === picked ? "wrong" : "dim"
                  : picked === i ? "pending" : "";
                return (
                  <button key={i} className={`option ${state}`} onClick={() => choose(i)} disabled={picked !== null}>
                    <span className="key pixel">{i + 1}</span>{opt}
                  </button>
                );
              })}
            </div>
            {outcome && (
              <div className={`feedback ${outcome.correct ? "good" : "bad"}`}>
                <b>{outcome.correct ? "Direct hit!" : "The boss strikes back."}</b> {outcome.explanation}
                <button className="btn primary" onClick={advance} autoFocus>
                  {over ? "See result" : "Next"} <span className="muted">⏎</span>
                </button>
              </div>
            )}
          </section>
        )
      ) : (
        <section className={`panel verdict ${view.status}`}>
          <h2 className="pixel">{view.status === "won" ? "VICTORY" : "DEFEATED"}</h2>
          {view.status === "won" ? (
            <p>
              {view.boss.name} falls. <b>+{fight.outcome?.xp_gained ?? 0} XP</b>
              {fight.outcome?.unlocked?.length ? ` · ${fight.outcome.unlocked.length} new room(s) unsealed` : ""}
            </p>
          ) : (
            <p>You retreat to lick your wounds. The boss is still there, and now you know its tricks.</p>
          )}
          <blockquote className="dm-quote">
            <span className="pixel small">Dungeon Master</span>
            {dm ? dm.message : <span className="deliberating">is surveying your map…</span>}
          </blockquote>
          <Link className="btn primary" href={`/dungeon/${fight.room.dungeon_id}`}>Back to the map</Link>
        </section>
      )}
    </main>
  );
}
