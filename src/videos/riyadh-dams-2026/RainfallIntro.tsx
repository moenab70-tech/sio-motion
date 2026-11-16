import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILIES } from "../../lib/fonts";
import { EASE, ramp } from "../../lib/motion";
import { DAM_LAYOUT as L, DAM_STYLE as S } from "../dams-2026/config";
import { REPORT, SCENE_MEDIA, type SceneMedia } from "./data";
import { Footage, HeaderLogos, type SceneProps } from "./shared";

export type RainfallIntroProps = SceneProps & { title?: string; subtitle?: string; media?: SceneMedia };

/** Scene 1 — strongest water shot + kinetic title (per-word rise, calm), subtitle in a blue bar. */
export const RainfallIntro: React.FC<RainfallIntroProps> = ({ title = REPORT.title, subtitle = REPORT.subtitle, media = SCENE_MEDIA.intro, transparent, showLogos = true }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const words = title.split(" ");
  const out = 1 - ramp(frame, durationInFrames - 14, 14, EASE.in);
  const subT = ramp(frame, 12 + words.length * 4 + 6, 22);
  const lineT = ramp(frame, 8, 30, EASE.inOut);

  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      {!transparent && <Footage media={media} frames={durationInFrames} />}
      {!transparent && (
        <AbsoluteFill style={{ background: "linear-gradient(to top, rgba(0,14,32,0.85) 0%, rgba(0,14,32,0.55) 38%, rgba(0,0,0,0) 62%)" }} />
      )}
      {showLogos && <HeaderLogos />}

      <div style={{ position: "absolute", right: L.safeSide, left: L.safeSide, bottom: L.safeBottom + 20, opacity: out }}>
        {/* accent line */}
        <div style={{ width: 120 * lineT, height: 8, backgroundColor: "#0071B8", marginBottom: 34, borderRadius: 4 }} />
        <div style={{ fontFamily: FONT_FAMILIES.NotoKufiArabic, fontWeight: 800, fontSize: 84, lineHeight: 1.45, color: "#fff", display: "flex", flexWrap: "wrap", columnGap: "0.28em" }}>
          {words.map((w, i) => {
            const t = ramp(frame, 12 + i * 4, 22, EASE.out);
            return (
              <span key={i} style={{ display: "inline-block", opacity: t, transform: `translateY(${(1 - t) * 34}px)`, filter: t < 1 ? `blur(${(1 - t) * 8}px)` : undefined }}>
                {w}
              </span>
            );
          })}
        </div>
        <div
          style={{
            display: "inline-block",
            marginTop: 30,
            padding: `10px ${S.padX}px`,
            background: `linear-gradient(to left, ${S.blue} 0%, ${S.blue} 60%, rgba(0,113,184,0) 100%)`,
            fontFamily: FONT_FAMILIES.IBMPlexSansArabic,
            fontWeight: 700,
            fontSize: 44,
            lineHeight: 1.4,
            color: "#fff",
            opacity: subT,
            clipPath: `inset(0 0 0 ${(1 - subT) * 100}%)`,
            transform: `translateX(${(1 - subT) * 50}px)`,
          }}
        >
          {subtitle}
        </div>
      </div>
    </AbsoluteFill>
  );
};
