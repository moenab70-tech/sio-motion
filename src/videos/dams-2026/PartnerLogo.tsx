import React from "react";
import { Img, staticFile } from "remotion";

// Partner (non-SIO) official logos, used exactly as supplied — same guarantees as src/lib/Logo.tsx:
// aspect ratio locked, colours untouched, no filter / shadow / blend / per-part animation.
// Files live in public/brand/partners/ (read-only, hashes in its README.md).
export const PARTNER_LOGOS = {
  mewa: {
    file: "brand/partners/mewa-lockup-color.png",
    width: 1935,
    height: 626,
    content: { x: 130, y: 109, w: 1674, h: 407 }, // measured visible artwork (file not modified)
    emblem: { x: 1398, y: 110, w: 406, h: 405 }, // measured circle only (shown by masking, file not modified)
    label: "Ministry of Environment, Water & Agriculture logo",
  },
} as const;

export type PartnerLogoId = keyof typeof PARTNER_LOGOS;

/** `part`: "lockup" = full logo, "emblem" = the circle only. `height` = circle diameter in both cases
 *  (the circle fills the full artwork height), so logos sized by the same height have equal circles. */
export const PartnerLogo: React.FC<{ id: PartnerLogoId; height: number; part?: "lockup" | "emblem"; style?: React.CSSProperties }> = ({ id, height, part = "lockup", style }) => {
  const a = PARTNER_LOGOS[id];
  const box = part === "emblem" ? a.emblem : a.content;
  const scale = height / box.h; // uniform → never distorted
  return (
    <div
      aria-label={a.label}
      style={{ ...style, width: box.w * scale, height, overflow: "hidden", position: "relative", flexShrink: 0, filter: "none", mixBlendMode: "normal" }}
    >
      <Img
        src={staticFile(a.file)}
        style={{ position: "absolute", left: -box.x * scale, top: -box.y * scale, width: a.width * scale, height: a.height * scale, maxWidth: "none" }}
      />
    </div>
  );
};
