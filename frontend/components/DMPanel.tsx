import type { DMTurn, Room } from "@/lib/api";

function describe(a: DMTurn["actions"][number], rooms: Room[]) {
  const room = rooms.find((r) => r.id === Number(a.args?.room_id));
  const why = typeof a.args?.reason === "string" && a.args.reason ? `: ${a.args.reason}` : "";
  switch (a.tool) {
    case "get_map": return "🔎 Surveyed the map";
    case "respawn_room": return `👻 Respawned ${room?.title ?? "a room"}${why}`;
    case "recommend_room": return `🧭 Pointed you to ${room?.title ?? "a room"}${why}`;
    case "finish": return null;
    default: return `⚙️ ${a.tool}`;
  }
}

export default function DMPanel({ dm, rooms }: { dm: DMTurn | null; rooms: Room[] }) {
  const steps = (dm?.actions ?? []).filter((a) => a.ok !== false).map((a) => describe(a, rooms)).filter(Boolean);
  return (
    <section className="panel dm">
      <h2 className="pixel small">Dungeon Master</h2>
      <p className="dm-message">
        {dm?.message ??
          "Welcome, adventurer. Each door holds a topic, each topic a guardian. Clear what you can. I'll be watching what you forget."}
      </p>
      {steps.length > 0 && (
        <ul className="dm-steps">
          {steps.map((s, i) => <li key={i}>{s}</li>)}
        </ul>
      )}
      {dm?.mode === "rules" && <p className="hint">Running on house rules (no LLM connected).</p>}
    </section>
  );
}
