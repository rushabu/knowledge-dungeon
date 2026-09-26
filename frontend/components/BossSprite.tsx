"use client";

import { useMemo } from "react";

// Deterministic 32-bit hash so every boss name always draws the same monster.
function hash(str: string) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function rng(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const W = 12;
const H = 12;
const TRAIL = 9; // extra columns for the scanline variant's trailing lines

/**
 * A mirrored pixel monster generated from the boss's name, inked in the site palette.
 * "scan" draws it in horizontal scanlines with a few glitching rows, like a CRT ghost.
 */
export default function BossSprite({ name, size = 192, hurt = false, defeated = false, variant = "solid" }:
  { name: string; size?: number; hurt?: boolean; defeated?: boolean; variant?: "solid" | "scan" }) {
  const { cells, trails, glitchRows } = useMemo(() => {
    const rand = rng(hash(name));
    const half = Math.ceil(W / 2);
    const grid: number[][] = [];
    for (let y = 0; y < H; y++) {
      const row: number[] = [];
      for (let x = 0; x < half; x++) {
        // denser toward the middle so it reads as a creature, not noise
        const centre = 1 - Math.abs(y - H / 2) / (H / 2);
        const inner = x / half;
        const p = 0.25 + 0.45 * centre + 0.3 * inner;
        row.push(rand() < p ? (rand() < 0.2 ? 2 : 1) : 0);
      }
      grid.push([...row, ...row.slice(0, W - half).reverse()]);
    }
    const ey = 3 + Math.floor(rand() * 3);
    const ex = 2 + Math.floor(rand() * 2);
    grid[ey][ex] = 3;
    grid[ey][W - 1 - ex] = 3;
    const cells: { x: number; y: number; v: number }[] = [];
    grid.forEach((row, y) => row.forEach((v, x) => v && cells.push({ x, y, v })));
    const trails = Array.from({ length: H }, (_, y) => (rand() < 0.35 ? { y, len: 2 + rand() * (TRAIL - 2), dy: rand() < 0.5 ? 0.1 : 0.6 } : null))
      .filter(Boolean) as { y: number; len: number; dy: number }[];
    const glitchRows = new Set([Math.floor(rand() * H), Math.floor(rand() * H)]);
    return { cells, trails, glitchRows };
  }, [name]);

  const cls = `boss-sprite ${variant}${hurt ? " hurt" : ""}${defeated ? " defeated" : ""}`;

  if (variant === "scan") {
    const lines = (filter: (y: number) => boolean) =>
      cells.filter((c) => filter(c.y)).map(({ x, y, v }) =>
        v === 3 ? (
          <g key={`${x}-${y}`}>
            <rect x={x - 0.15} y={y - 0.1} width={1.3} height={1.2} fill="var(--ink)" />
            <rect x={x + 0.55} y={y + 0.1} width={0.3} height={0.3} fill="var(--white)" />
          </g>
        ) : (
          <g key={`${x}-${y}`} fill={v === 2 ? "var(--peach-2)" : "var(--ink)"}>
            <rect x={x} y={y + 0.08} width={1.02} height={0.3} />
            <rect x={x} y={y + 0.58} width={1.02} height={0.3} />
          </g>
        ));
    return (
      <svg viewBox={`-1 -1 ${W + 2 + TRAIL} ${H + 2}`} width={size * (W + 2 + TRAIL) / (W + 2)} height={size}
        className={cls} shapeRendering="crispEdges" role="img" aria-label={name}>
        {trails.map((t) => <rect key={t.y} x={W + 0.4} y={t.y + t.dy} width={t.len} height={0.22} fill="var(--ink)" opacity={0.85} />)}
        <g>{lines((y) => !glitchRows.has(y))}</g>
        <g className="glitch">{lines((y) => glitchRows.has(y))}</g>
      </svg>
    );
  }

  return (
    <svg viewBox={`-1 -1 ${W + 2} ${H + 2}`} width={size} height={size} className={cls}
      shapeRendering="crispEdges" role="img" aria-label={name}>
      {cells.map(({ x, y, v }) => (
        <rect key={`${x}-${y}`} x={x} y={y} width={1.02} height={1.02}
          fill={v === 3 ? "var(--white)" : v === 2 ? "var(--peach-2)" : "var(--ink)"} />
      ))}
    </svg>
  );
}
