// Gallery: four variants of one style side by side (default/institutional, English LTR, experimental, transparent).
import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { FONT_FAMILIES } from "../../lib/fonts";
import type { MotionStyleDef } from "../registry/types";
import type { MotionStyleBaseProps } from "../core/types";
import { getStyles } from "../registry";

const S = 0.42;
const PW = 1920 * S, PH = 1080 * S;

const checker = "repeating-conic-gradient(#3a3f47 0% 25%, #2a2e35 0% 50%) 50% / 28px 28px";

const Pane: React.FC<{ label: string; tag?: string; bg: string; children: React.ReactNode }> = ({ label, tag, bg, children }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
    <div style={{ display: "flex", gap: 12, alignItems: "center", fontFamily: FONT_FAMILIES.IBMPlexSansArabic, fontSize: 24, color: "#E2E8F0", direction: "rtl" }}>
      {label}
      {tag && <span style={{ fontSize: 16, padding: "2px 10px", borderRadius: 999, border: "1px solid #F472B6", color: "#F472B6" }}>{tag}</span>}
    </div>
    <div style={{ width: PW, height: PH, position: "relative", overflow: "hidden", borderRadius: 10, background: bg, border: "1px solid rgba(255,255,255,0.12)" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 1080, transform: `scale(${S})`, transformOrigin: "top left", direction: "ltr" }}>{children}</div>
    </div>
  </div>
);

export const StyleGallery: React.FC<{ styleId: string }> = ({ styleId }) => {
  const def = getStyles().find((d) => d.id === styleId) as MotionStyleDef<MotionStyleBaseProps>;
  const C = def.component;
  return (
    <AbsoluteFill style={{ background: "#0A0F17", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", top: 10, fontFamily: FONT_FAMILIES.NotoKufiArabic, fontSize: 34, color: "#fff" }}>
        {def.name.ar} · <span style={{ fontFamily: FONT_FAMILIES.IBMPlexSansArabic, fontSize: 26, color: "#94A3B8" }}>{def.name.en}</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: `${PW}px ${PW}px`, gap: "14px 40px", marginTop: 70, direction: "rtl" }}>
        <Pane label="مؤسسي · عربي (افتراضي)" bg="#0B1626"><C {...def.presets.institutional} transparent={false} /></Pane>
        <Pane label="English · LTR" bg="#0B1626"><C {...def.presets.english} transparent={false} /></Pane>
        <Pane label="تجريبي" tag="غير معتمد مؤسسياً" bg="#05010F"><C {...def.presets.experimental} transparent={false} /></Pane>
        <Pane label="شفاف (Alpha) فوق نقش اختبار" bg={checker}><C {...def.presets.institutional} transparent /></Pane>
      </div>
    </AbsoluteFill>
  );
};

/** All styles in sequence. */
export const AllStylesGallery: React.FC = () => {
  let at = 0;
  return (
    <AbsoluteFill>
      {getStyles().map((d) => {
        const from = at;
        at += d.durationInFrames;
        return (
          <Sequence key={d.id} from={from} durationInFrames={d.durationInFrames} name={d.name.en}>
            <StyleGallery styleId={d.id} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const allStylesDuration = () => getStyles().reduce((a, d) => a + d.durationInFrames, 0);
