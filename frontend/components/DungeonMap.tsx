"use client";

import type { Room } from "@/lib/api";

const TILE_W = 200;
const TILE_H = 104;
const COL_GAP = 84;
const ROW_GAP = 40;
const PAD = 24;

const ICON: Record<Room["status"], string> = { locked: "🔒", open: "🚪", cleared: "🏆", respawned: "👻" };

export function masteryColor(m: number) {
  return m < 0.5 ? "var(--danger)" : m < 0.75 ? "var(--warn)" : "var(--good)";
}

export default function DungeonMap({ rooms, selected, recommended, onSelect }: {
  rooms: Room[];
  selected: number | null;
  recommended: number | null;
  onSelect: (id: number) => void;
}) {
  const lanesPerDepth = new Map<number, number>();
  rooms.forEach((r) => lanesPerDepth.set(r.depth, Math.max(lanesPerDepth.get(r.depth) ?? 0, r.lane + 1)));
  const maxLanes = Math.max(1, ...lanesPerDepth.values());
  const maxDepth = Math.max(0, ...rooms.map((r) => r.depth));

  const pos = new Map<number, { x: number; y: number }>();
  rooms.forEach((r) => {
    const offset = ((maxLanes - (lanesPerDepth.get(r.depth) ?? 1)) * (TILE_H + ROW_GAP)) / 2;
    pos.set(r.id, { x: PAD + r.depth * (TILE_W + COL_GAP), y: PAD + offset + r.lane * (TILE_H + ROW_GAP) });
  });
  const width = PAD * 2 + (maxDepth + 1) * TILE_W + maxDepth * COL_GAP;
  const height = PAD * 2 + maxLanes * TILE_H + (maxLanes - 1) * ROW_GAP;

  return (
    <div className="map-scroll">
      <div className="map" style={{ width, height }}>
        <svg className="map-edges" width={width} height={height} aria-hidden>
          {rooms.flatMap((r) =>
            r.prereqs.map((p) => {
              const a = pos.get(p)!;
              const b = pos.get(r.id)!;
              const x1 = a.x + TILE_W, y1 = a.y + TILE_H / 2, x2 = b.x, y2 = b.y + TILE_H / 2;
              const mid = (x1 + x2) / 2;
              return (
                <path
                  key={`${p}-${r.id}`}
                  d={`M${x1},${y1} C${mid},${y1} ${mid},${y2} ${x2},${y2}`}
                  className={r.status === "locked" ? "edge locked" : "edge"}
                />
              );
            }),
          )}
        </svg>
        {rooms.map((r) => {
          const { x, y } = pos.get(r.id)!;
          return (
            <button
              key={r.id}
              className={`tile ${r.status}${selected === r.id ? " selected" : ""}${recommended === r.id ? " recommended" : ""}`}
              style={{ left: x, top: y, width: TILE_W, height: TILE_H }}
              onClick={() => onSelect(r.id)}
            >
              <span className="tile-head">
                <span aria-hidden>{ICON[r.status]}</span>
                <span className="tile-title">{r.title}</span>
              </span>
              {r.status !== "locked" && (
                <span className="meter" title={`Mastery ${Math.round(r.mastery * 100)}%`}>
                  <span style={{ width: `${r.mastery * 100}%`, background: masteryColor(r.mastery) }} />
                </span>
              )}
              <span className="tile-foot">
                {r.status === "locked" ? "Sealed" : `${Math.round(r.mastery * 100)}% mastery`}
                {r.clears > 0 && ` · ×${r.clears}`}
              </span>
              {recommended === r.id && <span className="rec-badge pixel">GO</span>}
            </button>
          );
        })}
      </div>
    </div>
  );
}
