// ─────────────────────────────────────────────────────────────
// Official logo registry (part of the central brand system).
// Files live in public/brand/logos and are used exactly as supplied.
// Only combinations that exist as official files are registered.
// ─────────────────────────────────────────────────────────────

export type LogoForm =
  | "emblem" // circular symbol only
  | "lockup" // horizontal: names on the left, symbol on the right
  | "lockupVertical"; // stacked: symbol above names

export type LogoVariant = "color" | "white" | "black" | "blue";

export type LogoAsset = {
  file: string; // path inside /public
  width: number; // intrinsic pixel size of the file
  height: number;
  /** Bounding box of the visible artwork inside the file (measured, not edited).
   *  Used only to align the logo without the file's built-in empty margin. */
  content: { x: number; y: number; w: number; h: number };
};

export const LOGOS: Record<LogoForm, Partial<Record<LogoVariant, LogoAsset>>> = {
  emblem: {
    color: { file: "brand/logos/sio-emblem-color.png", width: 1497, height: 1453, content: { x: 0, y: 0, w: 1497, h: 1453 } },
  },
  lockup: {
    color: { file: "brand/logos/sio-lockup-color.webp", width: 2000, height: 933, content: { x: 151, y: 147, w: 1794, h: 630 } },
    blue: { file: "brand/logos/sio-lockup-blue.webp", width: 2000, height: 933, content: { x: 142, y: 145, w: 1803, h: 641 } },
  },
  lockupVertical: {
    white: { file: "brand/logos/sio-lockup-vertical-white.png", width: 827, height: 827, content: { x: 131, y: 121, w: 571, h: 591 } },
    black: { file: "brand/logos/sio-lockup-vertical-black.png", width: 827, height: 827, content: { x: 131, y: 121, w: 571, h: 591 } },
  },
};

/** Order tried when variant is "auto", by background. */
export const AUTO_PREFERENCE: Record<"dark" | "light", LogoVariant[]> = {
  dark: ["white", "color"],
  light: ["color", "blue", "black"],
};

/** Default logo form per background (approved: vertical white on dark). */
export const DEFAULT_FORM: Record<"dark" | "light", LogoForm> = {
  dark: "lockupVertical", // → sio-lockup-vertical-white
  light: "lockup", // → sio-lockup-color
};

/** Brand-wide logo defaults; any template can override them. */
export const defaultLogo = {
  variant: "auto" as LogoVariant | "auto", // auto = pick by background
  background: "dark" as "dark" | "light", // what the logo will sit on in the final video
};
