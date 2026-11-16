// Before / after gallery: original template (right, "قبل") vs FX version (left, "بعد"), same frame timing.
import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { VIDEO } from "../config/brand";
import * as D from "../config/defaults";
import * as FX from "../config/fxDefaults";
import { FONT_FAMILIES } from "../lib/fonts";
import { CinematicTitle } from "../templates/CinematicTitle";
import { StatCounter } from "../templates/StatCounter";
import { InfographicCards } from "../templates/InfographicCards";
import { FxTitle } from "../fx/FxTitle";
import { FxEnhanced } from "../fx/FxEnhanced";
import { FxScenes, fxScenesDuration } from "../fx/FxScenes";

const SCALE = 0.47;
const sec = (s: number) => Math.round(s * VIDEO.fps);

const Pane: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
    <div style={{ fontFamily: FONT_FAMILIES.IBMPlexSansArabic, fontSize: 34, fontWeight: 600, color: "#C8A45D" }}>{label}</div>
    <div style={{ width: VIDEO.width * SCALE, height: VIDEO.height * SCALE, borderRadius: 14, overflow: "hidden", position: "relative", border: "1px solid rgba(255,255,255,0.15)", background: "radial-gradient(circle at 40% 40%, #1d3354 0%, #0c1626 50%, #05090f 100%)" }}>
      <div style={{ width: VIDEO.width, height: VIDEO.height, transform: `scale(${SCALE})`, transformOrigin: "top left", position: "absolute", left: 0, top: 0, direction: "ltr" }}>{children}</div>
    </div>
  </div>
);

const twoScenes = { ...FX.fxScenes, scenes: FX.fxScenes.scenes.slice(0, 2), transition: "brandWipe" as const };
const cutScenes = { ...twoScenes, transitionSeconds: 1 / 30 };

const pairs: { title: string; seconds: number; before: React.ReactNode; after: React.ReactNode }[] = [
  { title: "العنوان السينمائي", seconds: 6, before: <CinematicTitle {...D.cinematicTitle} />, after: <FxTitle {...FX.fxTitleFocus} /> },
  { title: "الإحصائيات", seconds: 6, before: <StatCounter {...D.statRow} />, after: <FxEnhanced {...FX.fxStatRow} /> },
  { title: "الإنفوغرافيك", seconds: 7, before: <InfographicCards {...D.infographic} />, after: <FxEnhanced {...FX.fxInfographic} /> },
  { title: "الانتقال بين المشاهد", seconds: Math.round(fxScenesDuration(twoScenes, VIDEO.fps) / VIDEO.fps * 10) / 10, before: <FxScenes {...cutScenes} />, after: <FxScenes {...twoScenes} /> },
];

export const fxCompareDuration = pairs.reduce((a, p) => a + sec(p.seconds), 0);

export const FxCompare: React.FC = () => {
  let at = 0;
  return (
    <AbsoluteFill style={{ background: "#070C14", direction: "rtl" }}>
      {pairs.map((p, i) => {
        const from = at;
        at += sec(p.seconds);
        return (
          <Sequence key={i} from={from} durationInFrames={sec(p.seconds)} name={p.title}>
            <AbsoluteFill style={{ alignItems: "center", paddingTop: 70 }}>
              <div style={{ fontFamily: FONT_FAMILIES.NotoKufiArabic, fontSize: 52, fontWeight: 700, color: "#fff", marginBottom: 44 }}>{p.title}</div>
              <div style={{ display: "flex", gap: 40 }}>
                <Pane label="قبل">{p.before}</Pane>
                <Pane label="بعد">{p.after}</Pane>
              </div>
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
