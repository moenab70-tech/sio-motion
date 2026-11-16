import { Easing, interpolate } from "remotion";

// One easing family for the whole library = consistent feel.
export const EASE = {
  out: Easing.bezier(0.22, 1, 0.36, 1), // entrances (soft, cinematic settle)
  in: Easing.bezier(0.64, 0, 0.78, 0), // exits
  inOut: Easing.bezier(0.65, 0, 0.35, 1), // transitions, sweeps
  count: Easing.bezier(0.16, 1, 0.3, 1), // number counters
};

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** 0 → 1 between `start` and `start + duration` (frames). */
export const ramp = (frame: number, start: number, duration: number, easing = EASE.out) =>
  interpolate(frame, [start, start + Math.max(1, duration)], [0, 1], { ...clamp, easing });

export const mix = (a: number, b: number, t: number) => a + (b - a) * t;
