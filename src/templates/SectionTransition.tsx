// 5 ─ Section transitions. Fully covers the frame at the midpoint: place the cut there in Premiere.
import React from "react";
import { AbsoluteFill, interpolate } from "remotion";
import { useTemplate, type CommonProps } from "../lib/brand";
import { EASE, ramp } from "../lib/motion";
import { localizeDigits } from "../lib/numbers";

export type SectionTransitionProps = CommonProps & {
  variant: "panels" | "sweep" | "shutter";
  layers?: string[]; // colours, front-most last; defaults to brand colours
  panelCount?: number; // for "panels"
  holdSeconds?: number; // how long the frame stays fully covered (for a section label)
  label?: string; // optional section title shown while covered
  sublabel?: string;
};

export const SectionTransition: React.FC<SectionTransitionProps> = (props) => {
  const t = useTemplate({ ...props, timing: { exit: 0, ...props.timing } });
  const { palette: c, font, frame, total, s } = t;
  const hold = s(props.holdSeconds ?? 0);
  const half = Math.floor((total - hold) / 2);
  const layers = props.layers ?? [c.accent, c.secondary, "#0B1626"];
  const sign = t.rtl ? -1 : 1; // RTL sweeps right → left

  // Per-layer timing. In: back layers lead, front layer completes exactly at the midpoint.
  // Out: front layer leaves first, back layer finishes on the last frame.
  const lag = s(0.08);
  const n = layers.length;
  const phase = (li: number, extra = 0, maxExtra = 0) => {
    const inDur = half - (n - 1) * lag - maxExtra;
    const outDur = total - half - hold - (n - 1) * lag - maxExtra;
    const cover = ramp(frame, li * lag + extra, inDur, EASE.inOut);
    const uncover = ramp(frame, half + hold + (n - 1 - li) * lag + extra, outDur, EASE.inOut);
    return { cover, uncover };
  };
  const strips = props.panelCount ?? 6;
  const stripLag = s(0.035);

  const labelOpacity = hold > 0 ? interpolate(frame, [half - s(0.1), half + s(0.35), half + hold - s(0.3), half + hold], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;

  const renderLayers = () => {
    if (props.variant === "shutter") {
      return layers.map((col, li) => {
        const { cover, uncover } = phase(li);
        const h = 50 * (cover - uncover);
        return (
          <React.Fragment key={li}>
            <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: `${h + 0.2}%`, background: col }} />
            <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: `${h + 0.2}%`, background: col }} />
          </React.Fragment>
        );
      });
    }
    if (props.variant === "panels") {
      const lastColor = layers[layers.length - 1];
      return (
        <>
          {layers.slice(0, -1).map((col, li) => {
            const { cover, uncover } = phase(li);
            return <div key={li} style={{ position: "absolute", inset: 0, background: col, transform: `translateX(${sign * -100 * (1 - cover) + sign * 100 * uncover}%)` }} />;
          })}
          {Array.from({ length: strips }).map((_, k) => {
            const order = k;
            const { cover, uncover } = phase(n - 1, order * stripLag, (strips - 1) * stripLag);
            const w = 100 / strips;
            const pos = t.rtl ? 100 - (k + 1) * w : k * w;
            return (
              <div
                key={k}
                style={{
                  position: "absolute", top: 0, bottom: 0, left: `${pos - 0.05}%`, width: `${w + 0.1}%`, background: lastColor,
                  transform: `scaleX(${cover - uncover})`,
                  transformOrigin: (uncover > 0) === t.rtl ? "left" : "right",
                }}
              />
            );
          })}
        </>
      );
    }
    // sweep: skewed planes that pass across the frame
    return layers.map((col, li) => {
      const { cover, uncover } = phase(li);
      const x = sign * (-130 * (1 - cover) + 130 * uncover);
      return <div key={li} style={{ position: "absolute", top: 0, bottom: 0, left: "-15%", width: "130%", background: col, transform: `translateX(${x}%) skewX(${sign * -12}deg)` }} />;
    });
  };

  return (
    <AbsoluteFill style={{ direction: t.dir, overflow: "hidden" }}>
      {renderLayers()}
      {props.label && (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: labelOpacity }}>
          {props.sublabel && <div style={{ fontFamily: font.body, fontSize: 32, color: c.accent, marginBottom: 6, lineHeight: 1.5 }}>{localizeDigits(props.sublabel, t.digits)}</div>}
          <div style={{ fontFamily: font.display, fontWeight: 700, fontSize: 84, color: c.text, lineHeight: 1.5, transform: `translateY(${(1 - labelOpacity) * 16}px)` }}>{localizeDigits(props.label, t.digits)}</div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
