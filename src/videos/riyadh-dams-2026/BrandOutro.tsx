import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { BRAND_OUTRO } from "./data";

/** The institution's official outro (16:9 animation) centred on black in the 9:16 frame — used as supplied, only scaled. */
export const BrandOutro: React.FC<{ durationInSeconds: number }> = () => {
  const w = 1080 * BRAND_OUTRO.scale;
  const h = (w * 9) / 16;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <OffthreadVideo
        src={staticFile(BRAND_OUTRO.src)}
        muted
        style={{ position: "absolute", width: w, height: h, left: (1080 - w) / 2, top: (1920 - h) / 2, maxWidth: "none" }}
      />
    </AbsoluteFill>
  );
};
