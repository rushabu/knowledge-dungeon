"use client";

import PixelArt, { BOSS_ROSTER, type Palette, type SpriteKey } from "@/components/PixelArt";

// A boss called "The Data Golem" should look like a golem: match the monster in its name first.
const KINDS: [RegExp, SpriteKey][] = [
  [/lich|necromancer|wizard|sorcer|\bmage\b|warlock|witch|reaper|\bsage\b|alchemist|enchant|conjur|conjug|oracle/, "lich"],
  [/ghost|phantom|spect|wraith|spirit|poltergeist|\bshade\b|banshee|haunt/, "ghost"],
  [/golem|titan|colossus|giant|troll|ogre|behemoth|brute/, "golem"],
  [/mimic|tome|book|grimoire|scroll|librar|codex|lexicon/, "mimic"],
  [/slime|ooze|blob|\bgoo\b|jelly/, "slime"],
  [/skull|skelet|bone|undead|zombie|revenant/, "skull"],
  [/\bbat\b|vampire|\bimp\b|raptor|harpy|gargoyle|wyvern/, "bat"],
  [/\beye\b|beholder|watcher|\bseer\b|gazer|kraken|leviathan|hydra|naga|serpent|octo/, "eye"],
  [/knight|guardian|sentinel|warden|paladin|\bking\b|\blord\b|\bsir\b|master|keeper/, "knight"],
  [/shroom|mushroom|fung|spore/, "shroom"],
  [/\bcat\b|sphinx|\blion\b|panther|feline|jester|trickster/, "cat"],
  [/robot|\bbot\b|automaton|machine|droid|cyborg|\bmech\b|construct|prime\b|builder/, "robot"],
];

// Deterministic 32-bit hash so every boss name always gets the same monster.
function hash(str: string) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

// colour schemes, so two bosses sharing a sprite still look different
const SCHEMES: (Palette | undefined)[] = [
  undefined,
  { p: "var(--peach-2)", o: "var(--peach)", c: "var(--peach)" },
  { w: "var(--peach)", p: "var(--white)", c: "var(--white)", o: "var(--peach-2)" },
];

/** A hand-drawn monster chosen from the boss's name. */
export default function BossSprite({ name, size = 192, hurt = false, defeated = false, variant = "solid" }:
  { name: string; size?: number; hurt?: boolean; defeated?: boolean; variant?: "solid" | "scan" }) {
  const h = hash(name);
  const lower = name.toLowerCase();
  const sprite = KINDS.find(([re]) => re.test(lower))?.[1] ?? BOSS_ROSTER[h % BOSS_ROSTER.length];
  const scheme = SCHEMES[(h >>> 8) % SCHEMES.length];
  return (
    <PixelArt sprite={sprite} size={size} variant={variant} palette={scheme} label={name}
      className={`boss-sprite ${variant}${hurt ? " hurt" : ""}${defeated ? " defeated" : ""}`} />
  );
}
