"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import BossSprite from "@/components/BossSprite";
import CloudSky from "@/components/CloudSky";
import RetroWindow from "@/components/RetroWindow";
import { api, type DMTurn, type Fight } from "@/lib/api";

const HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"];

function PixelHeart({ full }: { full: boolean }) {
  return (
    <svg viewBox="-0.5 -0.5 8 7" width={34} height={30} shapeRendering="crispEdges" className={`heart${full ? "" : " lost"}`} aria-hidden>
      {HEART.flatMap((row, y) => [...row].map((c, x) => c === "1" && (
        <rect key={`${x}-${y}`} x={x} y={y} width={1.02} height={1.02}
          fill={full ? (x === 1 && y === 1 ? "var(--white)" : "var(--peach-2)") : "var(--cream-2)"} stroke="none" />
      )))}
    </svg>
  );
}

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

  if (error) return <main className="page"><p className="notice">{error}</p><Link className="btn" href="/">← Back</Link></main>;
  if (!fight) return <main className="page"><div className="loader" aria-label="Loading" /></main>;

  const view = result ?? fight;          // HP bars update the moment you answer
  const question = fight.question;        // question stays on screen until "Next"
  const outcome = result?.outcome;
  const over = view.status !== "active";
  const showVerdict = over && !result;

  return (
    <main className={`page fight-page${outcome && !outcome.correct ? " shake" : ""}`} key={outcome && !outcome.correct ? hitKey : undefined}>
      <header className="menubar">
        <Link href={`/dungeon/${fight.room.dungeon_id}`} className="menu-exit pixel">← Flee</Link>
        <h1 className="pixel">{fight.room.title}</h1>
        <span className={`diff ${fight.difficulty}`}>{fight.difficulty}</span>
      </header>

      <RetroWindow title="boss_fight.exe" bodyClassName="flush">
        <div className="arena">
          <CloudSky variant="arena" seed={fight.room.id} />
          <div className="nameplate">
            <b className="pixel">{view.boss.name}</b>
            <span className="hp-blocks" aria-label={`Boss HP ${view.boss.hp} of ${view.boss.max_hp}`}>
              {Array.from({ length: view.boss.max_hp }, (_, i) => <span key={i} className={i < view.boss.hp ? "on" : ""} />)}
            </span>
            <span className="flavor">{view.boss.flavor}</span>
          </div>
          <div className="sprite-wrap" key={outcome?.correct ? hitKey : "idle"}>
            <BossSprite name={view.boss.name} size={190} hurt={!!outcome?.correct} defeated={view.status === "won"} />
            {outcome?.correct && <span className="damage pixel">-1</span>}
          </div>
          <div className="player-plate">
            <span className="hearts" aria-label={`${view.player_hp} of ${view.max_player_hp} hearts`}>
              {Array.from({ length: view.max_player_hp }, (_, i) => <PixelHeart key={i} full={i < view.player_hp} />)}
            </span>
            {outcome && (
              <span className="tracer">
                Mastery <b>{Math.round((view.mastery ?? outcome.mastery) * 100)}%</b> → <b>{Math.round(outcome.mastery * 100)}%</b>
              </span>
            )}
          </div>
        </div>
      </RetroWindow>

      {!showVerdict && question && (
        <RetroWindow title="question.txt" className="question">
          <p className="prompt">{question.prompt}</p>
          <div className="options">
            {question.options.map((opt, i) => {
              const state = outcome
                ? i === outcome.answer ? "right" : i === picked ? "wrong" : "dim"
                : picked === i ? "pending" : "";
              return (
                <button key={i} className={`option ${state}`} onClick={() => choose(i)} disabled={picked !== null}>
                  <span className="key pixel">{i + 1}</span>
                  <span>{opt}</span>
                  {state === "right" && <span className="mark pixel">✓</span>}
                  {state === "wrong" && <span className="mark pixel">✗</span>}
                </button>
              );
            })}
          </div>
          {outcome && (
            <div className={`feedback ${outcome.correct ? "good" : "bad"}`}>
              <p><b className="pixel">{outcome.correct ? "Direct hit!" : "The boss strikes back."}</b> {outcome.explanation}</p>
              <button className="btn primary" onClick={advance} autoFocus>
                {over ? "See result" : "Next"} <span aria-hidden>⏎</span>
              </button>
            </div>
          )}
        </RetroWindow>
      )}

      {showVerdict && (
        <div className="backdrop">
          <div role="dialog" aria-modal="true">
            <RetroWindow title={view.status === "won" ? "victory.exe" : "defeat.exe"} className={`popup verdict ${view.status}`}>
              <h2 className="pixel">{view.status === "won" ? "Victory!" : "Defeated"}</h2>
              <p className="popup-text">
                {view.status === "won"
                  ? <>You have defeated {view.boss.name}. <b>+{fight.outcome?.xp_gained ?? 0} XP</b>
                    {fight.outcome?.unlocked?.length ? ` · ${fight.outcome.unlocked.length} new room(s) unsealed` : ""}</>
                  : <>You retreat to lick your wounds. {view.boss.name} is still there, and now you know its tricks.</>}
              </p>
              <div className="popup-sprite"><BossSprite name={view.boss.name} size={72} variant={view.status === "won" ? "scan" : "solid"} /></div>
              <blockquote className="dm-quote">
                <span className="pixel">Dungeon Master</span>
                {dm ? dm.message : <span className="deliberating">is surveying your map…</span>}
              </blockquote>
              <div className="popup-actions center">
                <Link className="btn ok" href={`/dungeon/${fight.room.dungeon_id}`} autoFocus>Ok</Link>
              </div>
            </RetroWindow>
          </div>
        </div>
      )}
    </main>
  );
}
