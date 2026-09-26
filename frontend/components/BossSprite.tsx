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

/** A mirrored pixel monster generated from the boss's name. */
export default function BossSprite({ name, size = 192, hurt = false, defeated = false }:
  { name: string; size?: number; hurt?: boolean; defeated?: boolean }) {
  const { cells, body, dark, eye } = useMemo(() => {
    const rand = rng(hash(name));
    const hue = Math.floor(rand() * 360);
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
    // eyes
    const ey = 3 + Math.floor(rand() * 3);
    const ex = 2 + Math.floor(rand() * 2);
    grid[ey][ex] = 3;
    grid[ey][W - 1 - ex] = 3;
    const cells: { x: number; y: number; v: number }[] = [];
    grid.forEach((row, y) => row.forEach((v, x) => v && cells.push({ x, y, v })));
    return {
      cells,
      body: `hsl(${hue} 65% 55%)`,
      dark: `hsl(${hue} 60% 32%)`,
      eye: `hsl(${(hue + 180) % 360} 100% 70%)`,
    };
  }, [name]);

  return (
    <svg
      viewBox={`-1 -1 ${W + 2} ${H + 2}`}
      width={size}
      height={size}
      className={`boss-sprite${hurt ? " hurt" : ""}${defeated ? " defeated" : ""}`}
      shapeRendering="crispEdges"
      role="img"
      aria-label={name}
    >
      {cells.map(({ x, y, v }) => (
        <rect key={`${x}-${y}`} x={x} y={y} width={1} height={1} fill={v === 3 ? eye : v === 2 ? dark : body} />
      ))}
    </svg>
  );
}
