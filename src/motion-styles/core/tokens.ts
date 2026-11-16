// Brand isolation. Institutional mode READS the approved tokens (never writes them).
// Experimental palettes live only here and are never applied to production templates.
import { defaultFonts, defaultPalette, type FontName } from "../../config/brand";
import type { StyleMode, StylePalette } from "./types";

/** Institutional palette derived read-only from src/config/brand.ts (itself provisional until the brand guide). */
export const institutionalPalette: StylePalette = {
  primary: defaultPalette.secondary,
  secondary: defaultPalette.textMuted,
  accent: defaultPalette.accent,
  text: defaultPalette.text,
  muted: defaultPalette.textMuted,
  background: "#0B1626", // existing project navy (SectionTransition default layer)
};

/** NOT institutionally approved — for exploration only. */
export const experimentalPalette: StylePalette = {
  primary: "#22D3EE",
  secondary: "#A78BFA",
  accent: "#F472B6",
  text: "#F8FAFC",
  muted: "rgba(248,250,252,0.62)",
  background: "#05010F",
};

export const paletteFor = (mode: StyleMode, overrides?: Partial<StylePalette>): StylePalette => ({
  ...(mode === "experimental" ? experimentalPalette : institutionalPalette),
  ...overrides,
});

export const defaultFontsFor = (mode: StyleMode): { display: FontName; body: FontName } =>
  mode === "experimental" ? { display: "Cairo", body: "Tajawal" } : { display: defaultFonts.display, body: defaultFonts.body };
