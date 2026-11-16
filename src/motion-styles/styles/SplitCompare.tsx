// 13 · Split Compare — before/after (or two indicators) with a sweeping divider, counting values and a delta badge.
import React from "react";
import { formatNumber } from "../../lib/numbers";
import { EASE, mix } from "../../lib/motion";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type CompareSide = { label: string; value: number; unit?: string; caption?: string; decimals?: number };
export type SplitCompareProps = MotionStyleBaseProps & {
  title?: string;
  before: CompareSide; // shown on the reading-start side
  after: CompareSide;
  showDelta?: boolean; // % change badge (default true)
  lowerIsBetter?: boolean; // colour the delta accordingly (e.g. losses)
};

export const SplitCompare: React.FC<SplitCompareProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, scale, rtl } = ctx;
  const sweep = phase(0.05, 0.3, EASE.inOut); // divider travels from the start edge to centre
  const divX = rtl ? mix(1920, 960, sweep) : mix(0, 960, sweep);
  const count = (s: number) => phase(0.3 + s * 0.08, 0.7 + s * 0.08, EASE.count);
  const delta = ((props.after.value - props.before.value) / (props.before.value || 1)) * 100;
  const good = props.lowerIsBetter ? delta < 0 : delta > 0;
  const badge = phase(0.72, 0.82, EASE.out);
  const side = (s: CompareSide, k: 0 | 1) => {
    const t = phase(0.15 + k * 0.12, 0.35 + k * 0.12);
    const v = s.value * count(k);
    return (
      <div style={{ width: 760, textAlign: "center", opacity: t, transform: `translateY(${(1 - t) * 30}px)` }}>
        <div style={{ fontSize: 36 * scale, color: k ? c.accent : c.muted, fontWeight: 600, marginBottom: 10 }}>{s.label}</div>
        <div style={{ fontFamily: font.display, fontWeight: 800, fontSize: 150 * scale, lineHeight: 1.15, color: c.text, unicodeBidi: "isolate" }}>
          {formatNumber(v, { digits: "latin", decimals: s.decimals ?? 0 })}
          {s.unit && <span style={{ fontSize: "0.35em", color: c.accent, marginInlineStart: 12 }}>{s.unit}</span>}
        </div>
        {s.caption && <div style={{ fontSize: 28 * scale, color: c.muted, marginTop: 8, lineHeight: 1.5 }}>{s.caption}</div>}
      </div>
    );
  };
  return (
    <Stage ctx={ctx}>
      <div style={{ position: "absolute", inset: 0, fontFamily: font.body, color: c.text }}>
        {props.title && <div style={{ position: "absolute", top: 110, left: 0, right: 0, textAlign: "center", fontFamily: font.display, fontWeight: ctx.weight, fontSize: 56 * scale, opacity: phase(0, 0.12) }}>{props.title}</div>}
        <div style={{ position: "absolute", top: 260, bottom: 160, left: divX - 1.5, width: 3, background: `linear-gradient(180deg, transparent, ${c.accent}, transparent)` }} />
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "space-around", direction: ctx.dir, paddingTop: 60 }}>
          {side(props.before, 0)}
          {side(props.after, 1)}
        </div>
        {props.showDelta !== false && (
          <div style={{ position: "absolute", left: 960, top: 540, transform: `translate(-50%, -50%) scale(${0.6 + 0.4 * badge})`, opacity: badge, background: good ? c.accent : c.primary, color: ctx.mode === "experimental" ? "#05010F" : "#0B1626", fontFamily: font.display, fontWeight: 800, fontSize: 40 * scale, padding: "10px 28px", borderRadius: 999, direction: "ltr", unicodeBidi: "isolate", whiteSpace: "nowrap" }}>
            {delta > 0 ? "+" : ""}{formatNumber(delta, { digits: "latin", decimals: 0 })}%
          </div>
        )}
      </div>
    </Stage>
  );
};
