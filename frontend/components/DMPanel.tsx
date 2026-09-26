"use client";

import { useEffect, useState } from "react";
import RetroWindow from "@/components/RetroWindow";
import type { DMTurn, Room } from "@/lib/api";

const WELCOME = "Welcome, adventurer. Each door holds a topic, each topic a guardian. Clear what you can. I'll be watching what you forget.";

function describe(a: DMTurn["actions"][number], rooms: Room[]) {
  const room = rooms.find((r) => r.id === Number(a.args?.room_id));
  const why = typeof a.args?.reason === "string" && a.args.reason ? `: ${a.args.reason}` : "";
  switch (a.tool) {
    case "get_map": return { tag: "scan", text: "Surveyed the map" };
    case "respawn_room": return { tag: "respawn", text: `${room?.title ?? "A room"}${why}` };
    case "recommend_room": return { tag: "next", text: `${room?.title ?? "A room"}${why}` };
    case "finish": return null;
    default: return { tag: "tool", text: a.tool };
  }
}

/** Types the message out like an old terminal. */
export function useTypewriter(text: string, speed = 18) {
  const [shown, setShown] = useState(0);
  useEffect(() => {
    setShown(0);
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { setShown(text.length); return; }
    const id = setInterval(() => setShown((n) => (n >= text.length ? (clearInterval(id), n) : n + 1)), speed);
    return () => clearInterval(id);
  }, [text, speed]);
  return text.slice(0, shown);
}

export default function DMPanel({ dm, rooms }: { dm: DMTurn | null; rooms: Room[] }) {
  const message = dm?.message ?? WELCOME;
  const typed = useTypewriter(message);
  const steps = (dm?.actions ?? []).filter((a) => a.ok !== false).map((a) => describe(a, rooms)).filter((s) => s !== null);
  return (
    <RetroWindow title="dungeon_master.txt" className="dm">
      <p className="dm-message" aria-label={message}>
        <span aria-hidden>{typed}</span>
        <span className="caret" aria-hidden />
      </p>
      {steps.length > 0 && (
        <ul className="dm-steps">
          {steps.map((s, i) => <li key={i}><span className={`tag ${s.tag}`}>{s.tag}</span>{s.text}</li>)}
        </ul>
      )}
      {dm?.mode === "rules" && <p className="hint">Running on house rules (no LLM connected).</p>}
    </RetroWindow>
  );
}
