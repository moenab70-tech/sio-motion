// Shot lengths (frames @30fps) incl. transition overlaps. Σ len − Σ out = 600 frames = 20 s.
// `out` = length of the transition INTO the next shot (0 = hard cut). v2: no 4B — 4A dissolves into the film's backdrop.
export type ShotId = "1A" | "1B" | "2A" | "2B" | "3A" | "3B" | "4A";

export const SHOTS: Record<ShotId, { len: number; out: number }> = {
  "1A": { len: 90, out: 0 }, // cut to the paper
  "1B": { len: 96, out: 15 }, // lamp light → night
  "2A": { len: 66, out: 0 }, // cut to top-down
  "2B": { len: 102, out: 18 }, // dawn flare
  "3A": { len: 84, out: 15 }, // into the drawing
  "3B": { len: 90, out: 0 }, // reverse angle
  "4A": { len: 120, out: 0 }, // ends on the film's backdrop
};

export const SHOT_ORDER: ShotId[] = ["1A", "1B", "2A", "2B", "3A", "3B", "4A"];
export const OPENING_FRAMES = SHOT_ORDER.reduce((a, id) => a + SHOTS[id].len - SHOTS[id].out, 0);

/** Absolute start frame of each shot on the opening timeline (for audio cues). */
export const shotStart = (() => {
  const out: Partial<Record<ShotId, number>> = {};
  let t = 0;
  for (const id of SHOT_ORDER) { out[id] = t; t += SHOTS[id].len - SHOTS[id].out; }
  return out as Record<ShotId, number>;
})();
