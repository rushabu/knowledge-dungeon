"use client";

import { useEffect, useRef } from "react";

/**
 * A drifting cumulus sky drawn at low resolution and ordered-dithered (Bayer 4x4)
 * into the site palette, then scaled up with crisp pixels.
 */

// darkest → lightest: ink, deep peach, peach, cream, white
const PALETTE = [[23, 20, 18], [236, 143, 108], [246, 180, 154], [244, 234, 213], [255, 253, 247]];
const PACKED = PALETTE.map(([r, g, b]) => (255 << 24) | (b << 16) | (g << 8) | r);
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map((v) => (v + 0.5) / 16);

type Variant = "hero" | "soft" | "arena";

const LOOK: Record<Variant, { skyTop: number; skyBottom: number; fade: number; cloudBase: number; cloudRange: number; count: number }> = {
  hero: { skyTop: 1.45, skyBottom: 2.35, fade: 1.9, cloudBase: 2.45, cloudRange: 1.6, count: 7 },
  soft: { skyTop: 3.05, skyBottom: 3.3, fade: 0.5, cloudBase: 3.2, cloudRange: 0.85, count: 6 },
  arena: { skyTop: 1.35, skyBottom: 2.4, fade: 0, cloudBase: 2.45, cloudRange: 1.6, count: 5 },
};

interface Puff { dx: number; dy: number; r: number }
interface Cloud { x: number; y: number; w: number; h: number; speed: number; puffs: Puff[] }

function rng(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeCloud(rand: () => number, x: number, y: number, w: number): Cloud {
  const puffs: Puff[] = [];
  const n = 5 + Math.floor(rand() * 4);
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1);
    const bulge = 1 - Math.abs(t - 0.5) * 1.3;
    const r = w * (0.1 + 0.12 * bulge + rand() * 0.05);
    puffs.push({ dx: (t - 0.5) * w * 0.8, dy: -r * 0.35, r });
    if (bulge > 0.45 && rand() < 0.8) {
      // a second, higher row of billows gives the cauliflower top
      const r2 = r * (0.65 + rand() * 0.3);
      puffs.push({ dx: (t - 0.5) * w * 0.7 + (rand() - 0.5) * r, dy: -r * 0.9 - r2 * 0.5, r: r2 });
    }
  }
  // higher puffs first, so lower billows overlap them and show their bright rims
  puffs.sort((a, b) => a.dy - b.dy);
  const top = Math.min(...puffs.map((p) => p.dy - p.r));
  return { x, y, w, h: -top, speed: 0, puffs };
}

function makeClouds(seed: number, W: number, H: number, variant: Variant): Cloud[] {
  const rand = rng(seed);
  const look = LOOK[variant];
  const clouds: Cloud[] = [];
  for (let i = 0; i < look.count; i++) {
    const w = Math.min(W, H * 2.2) * (0.35 + rand() * 0.4);
    // hero: keep the left third calmer so the headline reads
    const minX = variant === "hero" ? W * 0.3 : 0;
    const x = minX + rand() * (W - minX);
    const y = H * (0.3 + rand() * 0.8);
    const c = makeCloud(rand, x, y, w);
    c.speed = (0.6 + rand() * 1.2) * (i % 2 ? 1 : 0.7);
    clouds.push(c);
  }
  return clouds.sort((a, b) => a.y - b.y);
}

export default function CloudSky({ variant = "hero", pixel = 3, seed = 7, className = "" }:
  { variant?: Variant; pixel?: number; seed?: number; className?: string }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const look = LOOK[variant];
    const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let W = 0, H = 0, clouds: Cloud[] = [], img: ImageData | null = null, px: Uint32Array | null = null;
    let cover = new Uint8Array(0), light = new Float32Array(0), sky = new Float32Array(0);

    function resize() {
      const rect = canvas!.getBoundingClientRect();
      W = Math.max(40, Math.ceil(rect.width / pixel));
      H = Math.max(30, Math.ceil(rect.height / pixel));
      canvas!.width = W;
      canvas!.height = H;
      img = ctx!.createImageData(W, H);
      px = new Uint32Array(img.data.buffer);
      cover = new Uint8Array(W * H);
      light = new Float32Array(W * H);
      sky = new Float32Array(W * H);
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const fade = look.fade * Math.pow(Math.max(0, 1 - x / (W * 0.55)), 1.6);
          sky[y * W + x] = look.skyTop + (look.skyBottom - look.skyTop) * (y / H) + fade;
        }
      }
      clouds = makeClouds(seed, W, H, variant);
    }

    function draw(t: number) {
      cover.fill(0);
      for (const c of clouds) {
        const span = W + c.w * 1.4;
        const cx = ((c.x + (still ? 0 : t * c.speed)) % span + span) % span - c.w * 0.7;
        for (const p of c.puffs) {
          const px0 = cx + p.dx, py0 = c.y + p.dy;
          const x0 = Math.max(0, Math.floor(px0 - p.r)), x1 = Math.min(W - 1, Math.ceil(px0 + p.r));
          const y0 = Math.max(0, Math.floor(py0 - p.r)), y1 = Math.min(H - 1, Math.ceil(py0 + p.r));
          const r2 = p.r * p.r;
          for (let y = y0; y <= y1; y++) {
            const dy = y - py0;
            for (let x = x0; x <= x1; x++) {
              const dx = x - px0;
              if (dx * dx + dy * dy > r2) continue;
              const i = y * W + x;
              const rim = 0.5 - (dy + dx * 0.35) / (2 * p.r);           // lit from the upper left
              const body = 1 - Math.min(1, (y - (c.y - c.h)) / (c.h * 1.1)); // darker toward the base
              light[i] = Math.max(0, Math.min(1, 0.6 * rim + 0.5 * body));
              cover[i] = 1;
            }
          }
        }
      }
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const i = y * W + x;
          let L = cover[i] ? look.cloudBase + look.cloudRange * light[i] : sky[i];
          L = Math.max(0, Math.min(PALETTE.length - 1, L));
          const base = Math.floor(L);
          const level = L - base > BAYER[(y & 3) * 4 + (x & 3)] ? Math.min(base + 1, PALETTE.length - 1) : base;
          px![i] = PACKED[level];
        }
      }
      ctx!.putImageData(img!, 0, 0);
    }

    resize();
    let raf = 0, last = -1;
    const start = performance.now();
    const loop = (now: number) => {
      if (now - last > 90) { last = now; draw((now - start) / 1000); }
      raf = requestAnimationFrame(loop);
    };
    if (still) draw(0); else raf = requestAnimationFrame(loop);
    const ro = new ResizeObserver(() => { resize(); draw((performance.now() - start) / 1000); });
    ro.observe(canvas);
    return () => { cancelAnimationFrame(raf); ro.disconnect(); };
  }, [variant, pixel, seed]);

  return <canvas ref={ref} className={`cloud-sky ${className}`} aria-hidden />;
}
