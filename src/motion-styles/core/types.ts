import type { FontName } from "../../config/brand";

export type StyleMode = "institutional" | "experimental";
export type Lang = "ar" | "en";

/** Colour roles every style understands. */
export type StylePalette = {
  primary: string; // main shapes / lines
  secondary: string; // supporting shapes
  accent: string; // highlights
  text: string;
  muted: string;
  background: string; // used only when transparent = false
};

export type Typography = {
  display?: FontName; // titles (default from brand in institutional mode)
  body?: FontName; // labels
  weight?: number; // display weight
  scale?: number; // multiplies every font size (1 = default)
};

/** Shared API — every Motion Style accepts these props. All optional; safe defaults apply. */
export type MotionStyleBaseProps = {
  mode?: StyleMode; // default "institutional"
  lang?: Lang; // default "ar"
  direction?: "rtl" | "ltr" | "auto"; // default "auto" (ar → rtl, en → ltr)
  colors?: Partial<StylePalette>; // overrides on top of the mode palette
  durationInFrames?: number; // default: composition length
  intensity?: number; // 0–1, default 0.6
  transparent?: boolean; // default true (alpha); false draws palette.background
  typography?: Typography;
  seed?: string; // deterministic variation
};
