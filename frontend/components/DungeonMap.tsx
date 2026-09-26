"use client";

import CloudSky from "@/components/CloudSky";
import type { Room } from "@/lib/api";

const TILE_W = 204;
const TILE_H = 112;
const COL_GAP = 76;
const ROW_GAP = 40;
const PAD = 32;

const LABEL: Record<Room["status"], string> = { locked: "sealed", open: "open", cleared: "cleared", respawned: "risen!" };

export function masteryColor(m: number) {
  return m < 0.5 ? "var(--peach-2)" : m < 0.75 ? "var(--peach)" : "var(--ink)";
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
      <div className="map-sky" style={{ width, height }}>
      <CloudSky variant="soft" seed={11} />
      <div className="map" style={{ width, height }}>
        <svg className="map-edges" width={width} height={height} aria-hidden>
          {rooms.flatMap((r) =>
            r.prereqs.map((p) => {
              const a = pos.get(p)!;
              const b = pos.get(r.id)!;
              const x1 = a.x + TILE_W, y1 = a.y + TILE_H / 2, x2 = b.x, y2 = b.y + TILE_H / 2;
              const mid = Math.round((x1 + x2) / 2);
              // right-angled corridors read as more "dungeon" than curves
              return (
                <path
                  key={`${p}-${r.id}`}
                  d={`M${x1},${y1} H${mid} V${y2} H${x2}`}
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
              <span className="tile-bar">
                <span className="win-box" aria-hidden />
                <span className="tile-status">{LABEL[r.status]}</span>
                {r.clears > 0 && <span className="tile-clears">×{r.clears}</span>}
              </span>
              <span className="tile-body">
                <span className="tile-title">{r.title}</span>
                {r.status !== "locked" ? (
                  <span className="tile-foot">
                    <span className="meter" title={`Mastery ${Math.round(r.mastery * 100)}%`}>
                      <span style={{ width: `${r.mastery * 100}%`, background: masteryColor(r.mastery) }} />
                    </span>
                    <span>{Math.round(r.mastery * 100)}%</span>
                  </span>
                ) : (
                  <span className="tile-foot">locked</span>
                )}
              </span>
              {recommended === r.id && <span className="rec-badge pixel">Go!</span>}
            </button>
          );
        })}
      </div>
      </div>
    </div>
  );
}
