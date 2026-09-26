export type RoomStatus = "locked" | "open" | "cleared" | "respawned";

export interface Room {
  id: number;
  title: string;
  summary: string;
  keywords: string[];
  prereqs: number[];
  boss_name: string;
  boss_flavor: string;
  status: RoomStatus;
  clears: number;
  depth: number;
  lane: number;
  mastery: number;
  attempts: number;
  days_since_cleared: number | null;
}

export interface DMAction {
  tool: string;
  args?: Record<string, unknown>;
  ok?: boolean;
}

export interface DMTurn {
  message: string;
  actions: DMAction[];
  recommended_room: number | null;
  mode?: "agent" | "rules";
}

export interface DungeonSnapshot {
  dungeon: { id: number; title: string; xp: number; is_demo: number };
  rooms: Room[];
  dm: DMTurn | null;
  llm: boolean;
}

export interface Question {
  id: number;
  prompt: string;
  options: string[];
  difficulty: "easy" | "medium" | "hard";
}

export interface Fight {
  id: number;
  status: "active" | "won" | "lost";
  difficulty: "easy" | "medium" | "hard";
  boss: { name: string; flavor: string; hp: number; max_hp: number };
  player_hp: number;
  max_player_hp: number;
  room: { id: number; title: string; dungeon_id: number };
  question: Question | null;
  mastery?: number;
  outcome?: {
    correct: boolean;
    answer: number;
    explanation: string;
    mastery: number;
    xp_gained?: number;
    unlocked?: number[];
  };
  dm?: DMTurn;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, init);
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed (${res.status})`);
  }
  return res.json();
}

const post = <T,>(path: string, body?: unknown) =>
  request<T>(path, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });

export const api = {
  health: () => request<{ ok: boolean; llm: boolean; model: string }>("/health"),
  dungeons: () => request<{ id: number; title: string; xp: number; is_demo: number }[]>("/dungeons"),
  dungeon: (id: number | string) => request<DungeonSnapshot>(`/dungeons/${id}`),
  createDemo: () => post<{ id: number }>("/dungeons/demo"),
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<{ id: number }>("/dungeons", { method: "POST", body: form });
  },
  startFight: (roomId: number) => post<Fight>(`/rooms/${roomId}/fight`),
  fight: (id: number | string) => request<Fight>(`/fights/${id}`),
  answer: (fightId: number, questionId: number, choice: number) =>
    post<Fight>(`/fights/${fightId}/answer`, { question_id: questionId, choice }),
};

export const level = (xp: number) => Math.floor(Math.sqrt(xp / 40)) + 1;
export const xpForLevel = (lvl: number) => 40 * (lvl - 1) ** 2;
