// ─────────────────────────────────────────────────────────────
// Brand configuration — edit once, every template follows.
// Each template can also override any of these per-use via props.
// ─────────────────────────────────────────────────────────────

export const VIDEO = { width: 1920, height: 1080, fps: 30 } as const;

export type Palette = {
  text: string; // primary text
  textMuted: string; // secondary text
  accent: string; // brand highlight (lines, rings, bars)
  secondary: string; // second brand colour
  panel: string; // card / panel fill (keep some transparency for overlays)
  panelBorder: string; // hairline borders
  track: string; // empty part of progress bars / rings
  shadow: string; // text & card shadow colour
};

export const defaultPalette: Palette = {
  text: "#FFFFFF",
  textMuted: "rgba(255,255,255,0.70)",
  accent: "#C8A45D", // refined gold
  secondary: "#3B82C4", // institutional blue
  panel: "rgba(9,18,33,0.80)",
  panelBorder: "rgba(255,255,255,0.12)",
  track: "rgba(255,255,255,0.14)",
  shadow: "rgba(0,0,0,0.45)",
};

export type FontName = "NotoKufiArabic" | "IBMPlexSansArabic" | "Tajawal" | "Cairo";

export type Fonts = {
  display: FontName; // titles, numbers
  body: FontName; // labels, descriptions
};

export const defaultFonts: Fonts = {
  display: "NotoKufiArabic",
  body: "IBMPlexSansArabic",
};

export type Digits = "arabic" | "latin"; // ٠١٢٣ or 0123

export const defaultDigits: Digits = "latin"; // all numbers in English digits

/**
 * Dedicated font for numbers. It applies automatically to every digit in every template
 * (counters, dates, labels) via CSS unicode-range; Arabic letters keep the display/body fonts.
 * Set to null to use the display/body fonts for numbers too.
 */
export const numberFont: { file: string; family: string; unicodeRange: string } | null = {
  file: "brand/fonts/Watad-Regular.otf", // Watad Regular — single weight, used as-is (no faux bold)
  family: "Brand Numbers",
  unicodeRange: "U+0030-0039, U+0025, U+002B, U+002C, U+002D, U+002E", // 0-9 % + , - .
};

// Shared animation timing (seconds)
export type Timing = {
  enter: number; // length of each element's entrance
  exit: number; // length of the closing animation
  stagger: number; // delay between consecutive elements
};

export const defaultTiming: Timing = { enter: 0.9, exit: 0.6, stagger: 0.12 };
