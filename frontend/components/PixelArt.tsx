"use client";

/** Hand-drawn pixel sprites. # ink, o deep peach, p peach, w white, . transparent. */
export const SPRITES = {
  ghost: {
    name: "Forgetful Ghost",
    rows: [
      ".....######.....",
      "...##wwwwww##...",
      "..#wwwwwwwwww#..",
      ".#wwwwwwwwwwww#.",
      ".#ww##wwww##ww#.",
      "#www##wwww##www#",
      "#www##wwww##www#",
      "#wwwwwwwwwwwwww#",
      "#wppwww##wwwppw#",
      "#wwwwwwwwwwwwww#",
      "#wwwwwwwwwwwwww#",
      "#wwwwwwwwwwwwww#",
      "#pwwwwwwwwwwwwp#",
      "#ppp##pppp##ppp#",
      "#pp#..#pp#..#pp#",
      ".##....##....##.",
    ],
  },
  mimic: {
    name: "Tome Mimic",
    rows: [
      "...##########...",
      "..#oooooooooo#..",
      ".#oppppppppppo#.",
      ".#pp##pppp##pp#.",
      ".#pp#wpppp#wpp#.",
      ".#pppppppppppp#.",
      "#o############o#",
      "#ow#w#w##w#w#wo#",
      "#oooooooooooooo#",
      "#oooopppppppooo#",
      "#ow#w#pppp#w#wo#",
      "#o############o#",
      ".#wwwwwwwwwwww#.",
      ".#w##########w#.",
      ".#wwwwwwwwwwww#.",
      "..############..",
    ],
  },
  slime: {
    name: "Syntax Slime",
    rows: [
      "................",
      "................",
      "......####......",
      "....##wwpp##....",
      "...#wwpppppp#...",
      "..#wppppppppp#..",
      "..#ppw#pp#wpp#..",
      ".#ppp##pp##ppp#.",
      ".#ppp##pp##ppp#.",
      ".#pppppppppppp#.",
      "#ppoopppppppoop#",
      "#pppppp####pppo#",
      "#oppppppppppooo#",
      "#ooooooooooooo##",
      ".##############.",
      "................",
    ],
  },
  skull: {
    name: "Null Pointer Skull",
    rows: [
      "....########....",
      "..##wwwwwwww##..",
      ".#wwwwwwwwwwww#.",
      "#wwwwwwwwwwwwww#",
      "#wwwwwwwwwwwwww#",
      "#ww####ww####ww#",
      "#ww###wwww###ww#",
      "#www##wwww##www#",
      "#wwwwww##wwwwww#",
      ".#wwwww##wwwww#.",
      "..##wwwwwwww##..",
      "...#w#w#w#w#w#..",
      "...#wwwwwwwww#..",
      "...#w#w#w#w#w#..",
      "....#########...",
      "................",
    ],
  },
  logo: {
    name: "Knowledge Dungeon",
    rows: [
      "....####....",
      "..##wwww##..",
      ".#wwwwwwww#.",
      ".#w##ww##w#.",
      "#ww##ww##ww#",
      "#wwwwwwwwww#",
      "#wpwwwwwwpw#",
      "#wwwwwwwwww#",
      "#wwwwwwwwww#",
      "#ww#wwww#ww#",
      "#w#.#ww#.#w#",
      ".#...##...#.",
    ],
  },
} as const;

export type SpriteKey = keyof typeof SPRITES;

const FILL: Record<string, string> = { "#": "var(--ink)", o: "var(--peach-2)", p: "var(--peach)", w: "var(--white)" };
const TRAILS = [{ y: 1, len: 7, dy: 0.1 }, { y: 4, len: 5, dy: 0.55 }, { y: 7, len: 8, dy: 0.1 }, { y: 8, len: 6, dy: 0.55 }, { y: 12, len: 4, dy: 0.1 }];

/**
 * Renders a hand-drawn sprite. "scan" draws every pixel row as two thin scanlines,
 * with a few glitching rows and trailing lines, like a sprite on an old CRT.
 */
export default function PixelArt({ sprite, size = 64, variant = "solid", className = "" }:
  { sprite: SpriteKey; size?: number; variant?: "solid" | "scan"; className?: string }) {
  const { rows, name } = SPRITES[sprite];
  const w = rows[0].length, h = rows.length;
  const cells: { x: number; y: number; c: string }[] = [];
  rows.forEach((row, y) => [...row].forEach((c, x) => c !== "." && cells.push({ x, y, c })));

  if (variant === "solid") {
    return (
      <svg viewBox={`0 0 ${w} ${h}`} width={size * w / h} height={size} shapeRendering="crispEdges"
        className={`pixel-art ${className}`} role="img" aria-label={name}>
        {cells.map(({ x, y, c }) => <rect key={`${x}-${y}`} x={x} y={y} width={1.02} height={1.02} fill={FILL[c]} />)}
      </svg>
    );
  }

  const trail = 9;
  const glitch = new Set([3, 10]);
  const lines = (keep: (y: number) => boolean) => cells.filter((c) => keep(c.y)).map(({ x, y, c }) => (
    <g key={`${x}-${y}`} fill={FILL[c]}>
      <rect x={x} y={y + 0.04} width={1.02} height={0.4} />
      <rect x={x} y={y + 0.54} width={1.02} height={0.4} />
    </g>
  ));
  return (
    <svg viewBox={`-0.5 -0.5 ${w + trail + 1} ${h + 1}`} width={size * (w + trail + 1) / (h + 1)} height={size}
      shapeRendering="crispEdges" className={`pixel-art scan ${className}`} role="img" aria-label={name}>
      {TRAILS.map((t) => <rect key={t.y} x={w + 1} y={t.y + t.dy} width={t.len} height={0.3} fill="var(--ink)" />)}
      <g>{lines((y) => !glitch.has(y))}</g>
      <g className="glitch">{lines((y) => glitch.has(y))}</g>
    </svg>
  );
}
