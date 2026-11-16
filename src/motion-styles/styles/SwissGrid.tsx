// 20 · Swiss Grid Typography — strict 12-column grid, giant number, ruled blocks, snappy stepped motion.
import React from "react";
import { Easing } from "remotion";
import { formatNumber } from "../../lib/numbers";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type SwissGridProps = MotionStyleBaseProps & {
  kicker?: string; // small label
  bigNumber: { value: number; suffix?: string; decimals?: number };
  title: string;
  body?: string;
  caption?: string;
  showGrid?: boolean; // visible column guides (default true)
};

const SNAP = Easing.bezier(0.85, 0, 0.15, 1); // decisive, Swiss-style motion

export const SwissGrid: React.FC<SwissGridProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, scale, intensity, rtl } = ctx;
  const M = 120, G = 24, colW = (1920 - 2 * M - 11 * G) / 12;
  const colX = (k: number) => (rtl ? 1920 - M - (k + 1) * colW - k * G : M + k * (colW + G));
  const span = (k: number, n: number) => ({ left: rtl ? colX(k + n - 1) : colX(k), width: n * colW + (n - 1) * G });
  const grid = phase(0, 0.15, SNAP);
  const block = phase(0.12, 0.3, SNAP);
  const num = phase(0.2, 0.55, SNAP);
  const val = props.bigNumber.value * phase(0.22, 0.6, Easing.out(Easing.cubic));
  const txt = (a: number) => phase(a, a + 0.12, SNAP);
  const slide = (p: number) => `translateX(${(1 - p) * (rtl ? 60 : -60)}px)`;
  return (
    <Stage ctx={ctx}>
      <div style={{ position: "absolute", inset: 0, fontFamily: font.body, color: c.text, direction: ctx.dir }}>
        {props.showGrid !== false && Array.from({ length: 12 }).map((_, k) => (
          <div key={k} style={{ position: "absolute", top: 0, left: colX(k), width: colW, height: 1080 * grid, background: `${c.primary}${Math.round((0.05 + 0.08 * intensity) * 255).toString(16).padStart(2, "0")}` }} />
        ))}
        <div style={{ position: "absolute", top: 120, height: 10, background: c.accent, ...span(0, 4), transform: `scaleX(${block})`, transformOrigin: rtl ? "right" : "left" }} />
        {props.kicker && <div style={{ position: "absolute", top: 160, ...span(0, 6), fontSize: 30 * scale, fontWeight: 600, color: c.accent, opacity: txt(0.18), transform: slide(txt(0.18)) }}>{props.kicker}</div>}
        <div style={{ position: "absolute", top: 210, ...span(0, 7), fontFamily: font.display, fontWeight: 800, fontSize: 380 * scale, lineHeight: 1, letterSpacing: "-0.02em", opacity: num, transform: slide(num), unicodeBidi: "isolate", textAlign: "start" }}>
          {formatNumber(val, { digits: "latin", decimals: props.bigNumber.decimals ?? 0 })}<span style={{ color: c.accent, fontSize: "0.45em" }}>{props.bigNumber.suffix}</span>
        </div>
        <div style={{ position: "absolute", top: 640, height: 3, background: c.text, ...span(0, 12), transform: `scaleX(${txt(0.35)})`, transformOrigin: rtl ? "right" : "left" }} />
        <div style={{ position: "absolute", top: 680, ...span(0, 6), fontFamily: font.display, fontWeight: ctx.weight, fontSize: 64 * scale, lineHeight: 1.35, opacity: txt(0.4), transform: slide(txt(0.4)) }}>{props.title}</div>
        {props.body && <div style={{ position: "absolute", top: 690, ...span(7, 5), fontSize: 30 * scale, lineHeight: 1.7, color: c.muted, opacity: txt(0.48), transform: slide(txt(0.48)) }}>{props.body}</div>}
        {props.caption && <div style={{ position: "absolute", top: 960, ...span(0, 4), fontSize: 22 * scale, color: c.muted, opacity: txt(0.55), letterSpacing: ctx.lang === "en" ? "0.12em" : 0, textTransform: ctx.lang === "en" ? "uppercase" : undefined }}>{props.caption}</div>}
      </div>
    </Stage>
  );
};
