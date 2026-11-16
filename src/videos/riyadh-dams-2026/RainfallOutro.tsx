import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILIES } from "../../lib/fonts";
import { Logo } from "../../lib/Logo";
import { EASE, ramp } from "../../lib/motion";
import { PartnerLogo } from "../dams-2026/PartnerLogo";
import { REPORT, SCENE_MEDIA, type SceneMedia } from "./data";
import { Footage, type SceneProps } from "./shared";

export type RainfallOutroProps = SceneProps & { text?: string; media?: SceneMedia };

const BIG = 230; // outro logo circle diameter (both equal)

/** Scene 5 — wide water shot, «المؤسسة العامة للري», then both official logos (whole logo fades/rises — no part animation). */
export const RainfallOutro: React.FC<RainfallOutroProps> = ({ text = REPORT.outroText, media = SCENE_MEDIA.outro, transparent }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const dim = ramp(frame, 0, 30, EASE.inOut);
  const words = text.split(" ");
  const lineT = ramp(frame, 30, 26, EASE.inOut);
  const logoT = (i: number) => ramp(frame, 40 + i * 8, 26, EASE.out);
  const out = 1 - ramp(frame, durationInFrames - 12, 12, EASE.in);

  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      {!transparent && <Footage media={media} frames={durationInFrames} />}
      {!transparent && <AbsoluteFill style={{ backgroundColor: `rgba(2,22,44,${0.62 * dim})` }} />}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out }}>
        <div style={{ display: "flex", columnGap: "0.28em", fontFamily: FONT_FAMILIES.NotoKufiArabic, fontWeight: 800, fontSize: 88, color: "#fff", lineHeight: 1.4 }}>
          {words.map((w, i) => {
            const t = ramp(frame, 8 + i * 5, 22);
            return (
              <span key={i} style={{ display: "inline-block", opacity: t, transform: `translateY(${(1 - t) * 30}px)`, filter: t < 1 ? `blur(${(1 - t) * 8}px)` : undefined }}>
                {w}
              </span>
            );
          })}
        </div>
        <div style={{ width: 160 * lineT, height: 8, borderRadius: 4, backgroundColor: "#0071B8", margin: "44px 0 70px" }} />
        <div style={{ display: "flex", flexDirection: "row-reverse", direction: "ltr", gap: 120, alignItems: "center" }}>
          <div style={{ opacity: logoT(0), transform: `translateY(${(1 - logoT(0)) * 26}px)` }}>
            <PartnerLogo id="mewa" part="emblem" height={BIG} />
          </div>
          <div style={{ opacity: logoT(1), transform: `translateY(${(1 - logoT(1)) * 26}px)` }}>
            <Logo form="emblem" variant="color" background="light" height={BIG} />
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
