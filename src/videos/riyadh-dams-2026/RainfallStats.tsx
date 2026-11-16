import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILIES } from "../../lib/fonts";
import { EASE, ramp } from "../../lib/motion";
import { formatNumber } from "../../lib/numbers";
import { DAM_LAYOUT as L, DAM_STYLE as S } from "../dams-2026/config";
import { SCENE_MEDIA, STATS, type SceneMedia, type Stat } from "./data";
import { Footage, HeaderLogos, Quantity, type SceneProps } from "./shared";

export type RainfallStatsProps = SceneProps & { stats?: Stat[]; media?: SceneMedia };

const CARD_GAP = 14; // frames between cards
const COUNT = 42; // frames of count-up

const StatCard: React.FC<{ stat: Stat; delay: number; out: number }> = ({ stat, delay, out }) => {
  const frame = useCurrentFrame();
  const t = ramp(frame, delay, 22, EASE.out);
  const c = ramp(frame, delay + 4, COUNT, EASE.count);
  const shown = c >= 1 ? stat.value : Math.round(stat.value * c);
  return (
    <div
      style={{
        position: "relative",
        padding: "34px 44px 34px 40px",
        background: `linear-gradient(to left, ${S.navy.replace(/[\d.]+\)$/, "0.86)")} 0%, ${S.navy.replace(/[\d.]+\)$/, "0.62)")} 100%)`,
        borderRight: `10px solid #0071B8`,
        opacity: t * out,
        transform: `translateX(${(1 - t) * 70}px)`,
        clipPath: `inset(0 0 0 ${(1 - t) * 100}%)`,
      }}
    >
      <div style={{ fontFamily: FONT_FAMILIES.NotoKufiArabic, fontWeight: 800, fontSize: 128, lineHeight: 1.15, color: "#fff" }}>
        <Quantity text={formatNumber(shown, { digits: "latin" })} unit={stat.unit} unitScale={stat.unit === "م³" ? 0.42 : 0.4} />
      </div>
      <div style={{ fontFamily: FONT_FAMILIES.IBMPlexSansArabic, fontWeight: 600, fontSize: 40, lineHeight: 1.45, color: "rgba(255,255,255,0.92)", marginTop: 6 }}>
        {stat.label}
      </div>
    </div>
  );
};

/** Scene 2 — three stat cards, count-up numbers (values exactly as the presentation). */
export const RainfallStats: React.FC<RainfallStatsProps> = ({ stats = STATS, media = SCENE_MEDIA.stats, transparent, showLogos = true }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const out = 1 - ramp(frame, durationInFrames - 14, 14, EASE.in);
  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      {!transparent && <Footage media={media} frames={durationInFrames} dim={0.55} blur={6} />}
      {showLogos && <HeaderLogos />}
      <div
        style={{
          position: "absolute",
          right: L.safeSide,
          left: L.safeSide,
          top: L.safeTop + L.logoCircle + 120,
          bottom: L.safeBottom - 40,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          gap: 34,
        }}
      >
        {stats.map((s, i) => (
          <StatCard key={i} stat={s} delay={10 + i * CARD_GAP} out={out} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
