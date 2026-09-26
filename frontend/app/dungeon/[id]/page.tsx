"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import BossSprite from "@/components/BossSprite";
import DMPanel from "@/components/DMPanel";
import DungeonMap, { masteryColor } from "@/components/DungeonMap";
import RetroWindow from "@/components/RetroWindow";
import { api, level, xpForLevel, type DungeonSnapshot } from "@/lib/api";

const STATUS_TEXT = {
  locked: "Sealed. Clear the rooms before it first.",
  open: "The door stands open.",
  cleared: "Conquered. For now.",
  respawned: "The boss has risen again: your memory of this topic is fading.",
};

export default function DungeonPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [snap, setSnap] = useState<DungeonSnapshot | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [entering, setEntering] = useState(false);

  useEffect(() => {
    api.dungeon(id).then((s) => {
      setSnap(s);
      const first = s.dm?.recommended_room ?? s.rooms.find((r) => r.status === "respawned" || r.status === "open")?.id;
      setSelected(first ?? s.rooms[0]?.id ?? null);
    }).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <main className="page"><p className="notice">{error}</p><Link className="btn" href="/">← Back</Link></main>;
  if (!snap) return <main className="page"><div className="loader" aria-label="Loading" /></main>;

  const room = snap.rooms.find((r) => r.id === selected) ?? null;
  const lvl = level(snap.dungeon.xp);
  const progress = (snap.dungeon.xp - xpForLevel(lvl)) / (xpForLevel(lvl + 1) - xpForLevel(lvl));
  const cleared = snap.rooms.filter((r) => r.status === "cleared").length;
  const index = room ? snap.rooms.indexOf(room) + 1 : 0;

  async function enter() {
    if (!room) return;
    setEntering(true);
    try {
      const fight = await api.startFight(room.id);
      router.push(`/fight/${fight.id}`);
    } catch (e) {
      setError((e as Error).message);
      setEntering(false);
    }
  }

  return (
    <main className="page dungeon-page">
      <header className="menubar">
        <Link href="/" className="menu-exit pixel">← Exit</Link>
        <h1 className="pixel">{snap.dungeon.title}</h1>
        <div className="player">
          <span className="pixel">Lv {lvl}</span>
          <span className="xpbar" title={`${snap.dungeon.xp} XP`}><span style={{ width: `${progress * 100}%` }} /></span>
          <span className="player-meta">{snap.dungeon.xp} XP · {cleared}/{snap.rooms.length} cleared</span>
        </div>
      </header>

      <div className="dungeon-layout">
        <RetroWindow title="map.exe" className="map-win" bodyClassName="flush">
          <DungeonMap rooms={snap.rooms} selected={selected} recommended={snap.dm?.recommended_room ?? null} onSelect={setSelected} />
        </RetroWindow>

        <aside className="side">
          <DMPanel dm={snap.dm} rooms={snap.rooms} />
          {room && (
            <RetroWindow title={`room_${String(index).padStart(2, "0")}.dat`} className={`room-card ${room.status}`}>
              <div className="room-card-head">
                <div className="room-sprite"><BossSprite name={room.boss_name} size={72} /></div>
                <div>
                  <h2>{room.title}</h2>
                  <p className="boss-name pixel">{room.boss_name}</p>
                </div>
              </div>
              <p>{room.summary}</p>
              <p className="status-line">{STATUS_TEXT[room.status]}</p>
              {room.status !== "locked" && (
                <div className="mastery-row">
                  <span>Mastery</span>
                  <span className="meter big">
                    <span style={{ width: `${room.mastery * 100}%`, background: masteryColor(room.mastery) }} />
                  </span>
                  <b>{Math.round(room.mastery * 100)}%</b>
                </div>
              )}
              {room.status === "locked" ? (
                <p className="hint">
                  Requires: {room.prereqs.map((p) => snap.rooms.find((r) => r.id === p)?.title).join(", ")}
                </p>
              ) : (
                <button className="btn primary wide" onClick={enter} disabled={entering}>
                  {entering ? "Summoning the boss…" : room.status === "cleared" ? "Fight again" : "Enter the room"}
                </button>
              )}
            </RetroWindow>
          )}
        </aside>
      </div>
    </main>
  );
}
