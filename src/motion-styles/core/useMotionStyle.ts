import { useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILIES } from "../../lib/fonts"; // reuses brand font loading incl. Watad digits
import { EASE, ramp } from "../../lib/motion"; // reuses project easing
import { defaultFontsFor, paletteFor } from "./tokens";
import type { MotionStyleBaseProps } from "./types";

/** Resolves the shared API into concrete values + frame/fps-aware timing helpers. */
export const useMotionStyle = (p: MotionStyleBaseProps) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames: compDuration } = useVideoConfig();
  const mode = p.mode ?? "institutional";
  const lang = p.lang ?? "ar";
  const dir = p.direction && p.direction !== "auto" ? p.direction : lang === "ar" ? "rtl" : "ltr";
  const total = Math.max(1, Math.round(p.durationInFrames ?? compDuration));
  const intensity = Math.max(0, Math.min(1, p.intensity ?? 0.6));
  const palette = paletteFor(mode, p.colors);
  const fontNames = { ...defaultFontsFor(mode), ...p.typography };
  const scale = p.typography?.scale ?? 1;

  /** Progress 0→1 between two fractions of the total duration (durations stay configurable). */
  const phase = (from: number, to: number, easing = EASE.out) => ramp(frame, from * total, Math.max(1, (to - from) * total), easing);
  /** Seconds → frames at the composition fps. */
  const sec = (s: number) => Math.round(s * fps);
  /** Global fade in/out envelope (first/last 8% of the duration, max 0.6 s). */
  const edge = Math.min(sec(0.6), total * 0.08);
  const envelope = Math.min(ramp(frame, 0, edge), 1 - ramp(frame, total - edge, edge, EASE.in));

  return {
    frame, fps, width, height, total, mode, lang, dir: dir as "rtl" | "ltr", rtl: dir === "rtl",
    intensity, palette, scale, envelope, phase, sec,
    weight: p.typography?.weight ?? 700,
    font: { display: FONT_FAMILIES[fontNames.display!], body: FONT_FAMILIES[fontNames.body!] },
    transparent: p.transparent ?? true,
    seed: p.seed ?? "sio",
  };
};

export type MotionCtx = ReturnType<typeof useMotionStyle>;
