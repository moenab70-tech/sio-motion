import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { FONT_FAMILIES } from "../../lib/fonts";
import { EASE, ramp } from "../../lib/motion";
import { formatNumber } from "../../lib/numbers";
import { DAM_LAYOUT as L, DAM_STYLE as S } from "../dams-2026/config";
import { DAMS, type Dam } from "./data";
import { Footage, HeaderLogos, type SceneProps } from "./shared";

// Scene 4 unit — one dam: its own real media + the approved info boxes
// (same look as DamRainfallReport: blue name bar, navy rows, bottom-right, gradient to transparent).

export type DamProfileProps = SceneProps & { dam: Dam };

const XFADE = 12; // frames between this dam's own shots

const framesFor = (weights: number[], total: number) => {
  const sum = total + (weights.length - 1) * XFADE;
  const w = weights.reduce((a, b) => a + b, 0);
  const f = weights.map((x) => Math.max(XFADE + 1, Math.floor((sum * x) / w)));
  f[f.length - 1] += sum - f.reduce((a, b) => a + b, 0);
  return f;
};

const InfoBox: React.FC<{ delay: number; color: string; padY: number; minWidth: number; out: number; children: React.ReactNode }> = ({ delay, color, padY, minWidth, out, children }) => {
  const frame = useCurrentFrame();
  const p = ramp(frame, delay, 22, EASE.out);
  return (
    <div
      style={{
        alignSelf: "flex-start", // RTL: start = right edge
        minWidth,
        padding: `${padY}px ${S.padX}px`,
        background: `linear-gradient(to left, ${color} 0%, ${color} 55%, ${color.replace(/[\d.]+\)$/, "0)")} 100%)`,
        opacity: p * out,
        transform: `translateX(${(1 - p) * 60}px)`,
        clipPath: `inset(0 0 0 ${(1 - p) * 100}%)`,
      }}
    >
      {children}
    </div>
  );
};

const Row: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div style={{ fontFamily: FONT_FAMILIES.IBMPlexSansArabic, fontSize: L.rowSize, lineHeight: 1.4, color: "#fff", display: "flex", gap: 14, alignItems: "baseline" }}>
    <span style={{ fontWeight: 600, opacity: 0.92 }}>{label}:</span>
    <span style={{ fontWeight: 700, unicodeBidi: "isolate" }}>
      <bdi dir="ltr">{formatNumber(value, { digits: "latin" })}</bdi> م³
    </span>
  </div>
);

export const DamProfile: React.FC<DamProfileProps> = ({ dam = DAMS[0], transparent, showLogos = true }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const frames = framesFor(dam.media.map((m) => m.weight ?? 1), durationInFrames);
  const out = 1 - ramp(frame, durationInFrames - 10, 10, EASE.in);
  const start = 8;
  const stagger = 5;

  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      {!transparent && (
        <TransitionSeries>
          {dam.media.map((m, i) => (
            <React.Fragment key={i}>
              {i > 0 && <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: XFADE })} />}
              <TransitionSeries.Sequence durationInFrames={frames[i]}>
                <Footage media={m} frames={frames[i]} />
              </TransitionSeries.Sequence>
            </React.Fragment>
          ))}
        </TransitionSeries>
      )}
      {!transparent && <AbsoluteFill style={{ background: "linear-gradient(to top, rgba(0,12,28,0.6) 0%, rgba(0,12,28,0.28) 28%, rgba(0,0,0,0) 45%)" }} />}
      {showLogos && <HeaderLogos />}

      <div style={{ position: "absolute", right: L.safeSide, left: L.safeSide, bottom: L.safeBottom, display: "flex", flexDirection: "column", gap: 10 }}>
        <InfoBox delay={start} color={S.blue} padY={14} minWidth={L.nameBoxWidth} out={out}>
          <div style={{ fontFamily: FONT_FAMILIES.NotoKufiArabic, fontWeight: 800, fontSize: L.nameSize, lineHeight: 1.35, color: "#fff" }}>سد {dam.name}</div>
        </InfoBox>
        <InfoBox delay={start + stagger} color={S.navy} padY={8} minWidth={L.rowWidth} out={out}>
          <div style={{ fontFamily: FONT_FAMILIES.IBMPlexSansArabic, fontWeight: 700, fontSize: L.govSize, lineHeight: 1.4, color: "#fff" }}>محافظة {dam.governorate}</div>
        </InfoBox>
        <InfoBox delay={start + stagger * 2} color={S.navy} padY={8} minWidth={L.rowWidth} out={out}>
          <Row label="السعة التخزينية" value={dam.storageCapacity} />
        </InfoBox>
        <InfoBox delay={start + stagger * 3} color={S.navy} padY={8} minWidth={L.rowWidth} out={out}>
          <Row label="الكمية الواردة" value={dam.incomingWater} />
        </InfoBox>
      </div>
    </AbsoluteFill>
  );
};
