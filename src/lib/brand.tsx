import type React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { defaultDigits, defaultFonts, defaultPalette, defaultTiming, type Digits, type Fonts, type Palette, type Timing } from "../config/brand";
import { FONT_FAMILIES } from "./fonts";
import type { LogoProps } from "./Logo";
import { EASE, ramp } from "./motion";

/** Props every template accepts. Everything is optional except duration. */
/** Optional official logo inside a template (see src/lib/Logo.tsx). Omit = no logo. */
export type LogoSlot = Pick<LogoProps, "form" | "variant" | "background" | "height">;

export type CommonProps = {
  durationInSeconds: number;
  rtl?: boolean;
  digits?: Digits;
  colors?: Partial<Palette>;
  fonts?: Partial<Fonts>;
  timing?: Partial<Timing>;
};

/** Merges brand defaults with per-template overrides and exposes the shared timeline helpers. */
export const useTemplate = (p: CommonProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = { ...defaultPalette, ...p.colors };
  const fontNames = { ...defaultFonts, ...p.fonts };
  const timing = { ...defaultTiming, ...p.timing };
  const total = Math.round(p.durationInSeconds * fps); // from props, so it also works inside a preview Sequence
  const s = (sec: number) => Math.round(sec * fps);

  const exitStart = total - s(timing.exit);
  /** 1 → 0 during the closing animation. */
  const out = 1 - ramp(frame, exitStart, s(timing.exit), EASE.in);
  /** 0 → 1 entrance of element number `index`, after an optional delay (sec). */
  const enter = (index = 0, delaySec = 0, durSec = timing.enter) =>
    ramp(frame, s(delaySec + index * timing.stagger), s(durSec), EASE.out);

  return {
    frame, fps, total, s, out, enter, timing, palette,
    rtl: p.rtl ?? true,
    dir: (p.rtl ?? true) ? ("rtl" as const) : ("ltr" as const),
    digits: p.digits ?? defaultDigits,
    font: { display: FONT_FAMILIES[fontNames.display], body: FONT_FAMILIES[fontNames.body] },
  };
};

/** Standard “rise + unblur” entrance style shared across templates. */
export const riseStyle = (t: number, out = 1, distance = 28): React.CSSProperties => ({
  opacity: t * out,
  transform: `translateY(${(1 - t) * distance - (1 - out) * 14}px)`,
  filter: t < 1 || out < 1 ? `blur(${(1 - t) * 10 + (1 - out) * 6}px)` : undefined,
});
