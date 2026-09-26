"use client";

import { useEffect, useRef, useState } from "react";
import CloudSky from "@/components/CloudSky";
import type { Room } from "@/lib/api";

const TILE_W = 204;
const TILE_H = 112;
const COL_GAP = 60;
const ROW_GAP = 32;
const BAND_GAP = 64; // vertical space between wrapped rows of the map
const PAD = 32;
const JOG = 16;      // how far corridors step out of a tile before turning

const LABEL: Record<Room["status"], string> = { locked: "sealed", open: "open", cleared: "cleared", respawned: "risen!" };

export function masteryColor(m: number) {
  return m < 0.5 ? "var(--peach-2)" : m < 0.75 ? "var(--peach)" : "var(--ink)";
}

/** A room has a mastery worth showing only once you've answered something there. */
export const explored = (r: Room) => r.attempts > 0;

/**
 * Lays rooms out by prerequisite depth, left to right, and wraps the depth columns
 * into rows that fit the window, like lines of text, so the whole dungeon is visible.
 */
function layout(rooms: Room[], available: number) {
  const cols = Math.max(1, Math.floor((available - 2 * PAD + COL_GAP) / (TILE_W + COL_GAP)));
  const lanesAt = new Map<number, number>();
  rooms.forEach((r) => lanesAt.set(r.depth, Math.max(lanesAt.get(r.depth) ?? 0, r.lane + 1)));
  const maxDepth = Math.max(0, ...rooms.map((r) => r.depth));
  const bands = Math.floor(maxDepth / cols) + 1;

  const bandLanes = Array.from({ length: bands }, (_, b) =>
    Math.max(1, ...Array.from({ length: cols }, (_, c) => lanesAt.get(b * cols + c) ?? 0)));
  const bandTop: number[] = [];
  let y = PAD;
  bandLanes.forEach((lanes) => { bandTop.push(y); y += lanes * TILE_H + (lanes - 1) * ROW_GAP + BAND_GAP; });
  const height = y - BAND_GAP + PAD;
  const width = PAD * 2 + Math.min(cols, maxDepth + 1) * (TILE_W + COL_GAP) - COL_GAP;

  const pos = new Map<number, { x: number; y: number; band: number }>();
  rooms.forEach((r) => {
    const band = Math.floor(r.depth / cols);
    const lanes = lanesAt.get(r.depth) ?? 1;
    const offset = ((bandLanes[band] - lanes) * (TILE_H + ROW_GAP)) / 2;
    pos.set(r.id, {
      x: PAD + (r.depth % cols) * (TILE_W + COL_GAP),
      y: bandTop[band] + offset + r.lane * (TILE_H + ROW_GAP),
      band,
    });
  });
  return { pos, bandTop, width, height };
}

export default function DungeonMap({ rooms, selected, recommended, onSelect }: {
  rooms: Room[];
  selected: number | null;
  recommended: number | null;
  onSelect: (id: number) => void;
}) {
  const box = useRef<HTMLDivElement>(null);
  const [available, setAvailable] = useState(900);
  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setAvailable(el.clientWidth));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const { pos, bandTop, width, height } = layout(rooms, available);

  function corridor(a: { x: number; y: number; band: number }, b: { x: number; y: number; band: number }, i: number) {
    const ay = a.y + TILE_H / 2, by = b.y + TILE_H / 2;
    if (a.band === b.band) {
      const mid = Math.round((a.x + TILE_W + b.x) / 2);
      return `M${a.x + TILE_W},${ay} H${mid} V${by} H${b.x}`;
    }
    if (a.x === b.x) return `M${a.x + TILE_W / 2},${a.y + TILE_H} V${b.y}`; // straight down a single column
    // wrap to a later row: out the right side, down the gap between rows, in from the left
    const gapY = bandTop[b.band] - BAND_GAP / 2 + ((i % 3) - 1) * 6;
    return `M${a.x + TILE_W},${ay} H${a.x + TILE_W + JOG} V${gapY} H${b.x - JOG} V${by} H${b.x}`;
  }

  return (
    <div className="map-scroll" ref={box}>
      <div className="map-sky" style={{ height }}>
        <CloudSky variant="soft" seed={11} />
        <div className="map" style={{ width, height }}>
          <svg className="map-edges" width={width} height={height} aria-hidden>
            {rooms.flatMap((r, i) =>
              r.prereqs.map((p) => (
                <path key={`${p}-${r.id}`} d={corridor(pos.get(p)!, pos.get(r.id)!, i)}
                  className={r.status === "locked" ? "edge locked" : "edge"} />
              )),
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
                  {r.status === "locked" ? (
                    <span className="tile-foot">locked</span>
                  ) : explored(r) ? (
                    <span className="tile-foot">
                      <span className="meter" title={`Mastery ${Math.round(r.mastery * 100)}%`}>
                        <span style={{ width: `${r.mastery * 100}%`, background: masteryColor(r.mastery) }} />
                      </span>
                      <span>{Math.round(r.mastery * 100)}%</span>
                    </span>
                  ) : (
                    <span className="tile-foot">unexplored</span>
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
