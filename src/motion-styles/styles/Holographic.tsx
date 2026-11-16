// 4 · Holographic — translucent data panels, scan line, typed data rows, sparkline, gauge.
import React from "react";
import { AbsoluteFill, interpolate } from "remotion";
import { formatNumber } from "../../lib/numbers";
import { EASE } from "../../lib/motion";
import { Stage } from "../core/Stage";
import { drawOn } from "../core/svg";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type HoloRow = { label: string; value: number; suffix?: string; decimals?: number };

export type HolographicProps = MotionStyleBaseProps & {
  title: string;
  rows: HoloRow[]; // 3–5
  gauge: { label: string; value: number }; // 0–100
  series?: number[]; // sparkline values
};

const Corner: React.FC<{ color: string; pos: "tl" | "tr" | "bl" | "br" }> = ({ color, pos }) => {
  const s: React.CSSProperties = { position: "absolute", width: 26, height: 26, borderColor: color, borderStyle: "solid", borderWidth: 0 };
  if (pos[0] === "t") { s.top = -2; s.borderTopWidth = 3; } else { s.bottom = -2; s.borderBottomWidth = 3; }
  if (pos[1] === "l") { s.left = -2; s.borderLeftWidth = 3; } else { s.right = -2; s.borderRightWidth = 3; }
  return <div style={s} />;
};

export const Holographic: React.FC<HolographicProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, frame, total, intensity, scale } = ctx;
  const open = phase(0.02, 0.18, EASE.out);
  const scanY = interpolate(frame % Math.max(30, Math.round(total * 0.45)), [0, Math.max(30, Math.round(total * 0.45))], [-10, 110]);
  const series = props.series ?? [32, 41, 38, 52, 49, 63, 70, 68, 79, 86];
  const max = Math.max(...series), min = Math.min(...series);
  const pts = series.map((v, i) => [40 + (i / (series.length - 1)) * 640, 210 - ((v - min) / (max - min || 1)) * 170]);
  const line = pts.map((p, i) => `${i ? "L" : "M"} ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
  const g = phase(0.35, 0.75, EASE.count);
  const glow = `0 0 ${10 + 18 * intensity}px ${c.primary}`;
  const panel = (style: React.CSSProperties, children: React.ReactNode, delay: number) => {
    const t = phase(delay, delay + 0.15, EASE.out);
    return (
      <div style={{ position: "absolute", ...style, transform: `scaleY(${0.02 + 0.98 * t})`, opacity: Math.min(1, t * 2), background: `linear-gradient(180deg, ${c.primary}22, ${c.primary}0d)`, border: `1px solid ${c.primary}88`, boxShadow: `inset 0 0 40px ${c.primary}22`, padding: 30 }}>
        {/* scanlines + sweeping scan bar, confined to the panel (keeps alpha area and file size small) */}
        <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: `repeating-linear-gradient(0deg, ${c.primary}14 0px, ${c.primary}14 1px, transparent 1px, transparent 5px)`, opacity: 0.35 + 0.4 * intensity }} />
          <div style={{ position: "absolute", left: 0, right: 0, top: `${scanY}%`, height: 80, background: `linear-gradient(180deg, transparent, ${c.primary}30, transparent)`, opacity: 0.4 + 0.5 * intensity }} />
        </div>
        <Corner color={c.accent} pos="tl" /><Corner color={c.accent} pos="tr" /><Corner color={c.accent} pos="bl" /><Corner color={c.accent} pos="br" />
        {children}
      </div>
    );
  };
  return (
    <Stage ctx={ctx}>
      <AbsoluteFill style={{ fontFamily: font.body, color: c.text }}>
        <div style={{ position: "absolute", top: 90, insetInlineStart: 140, fontFamily: font.display, fontWeight: ctx.weight, fontSize: 58 * scale, opacity: open, textShadow: glow, letterSpacing: ctx.lang === "en" ? "0.04em" : 0 }}>{props.title}</div>
        <div style={{ position: "absolute", top: 180, insetInlineStart: 140, width: 300 * open, height: 3, background: c.accent }} />
        {panel({ top: 250, insetInlineStart: 140, width: 760, height: 520 }, (
          <div style={{ display: "flex", flexDirection: "column", gap: 26 }}>
            {props.rows.slice(0, 5).map((r, i) => {
              const t = phase(0.2 + i * 0.06, 0.32 + i * 0.06);
              const v = r.value * phase(0.25 + i * 0.06, 0.6 + i * 0.06, EASE.count);
              return (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", borderBottom: `1px solid ${c.primary}44`, paddingBottom: 14, opacity: t, transform: `translateX(${(1 - t) * 30 * (ctx.rtl ? 1 : -1)}px)` }}>
                  <span style={{ fontSize: 30 * scale, color: c.muted }}>{r.label}</span>
                  <span style={{ fontSize: 46 * scale, fontWeight: 700, fontFamily: font.display, textShadow: glow, unicodeBidi: "isolate" }}>
                    {formatNumber(v, { digits: "latin", decimals: r.decimals ?? 0 })}<span style={{ fontSize: "0.55em", color: c.accent, marginInlineStart: 6 }}>{r.suffix}</span>
                  </span>
                </div>
              );
            })}
          </div>
        ), 0.08)}
        {panel({ top: 250, insetInlineEnd: 140, width: 760, height: 250 }, (
          <svg width={700} height={220} style={{ overflow: "visible" }}>
            {[0, 1, 2, 3].map((i) => <line key={i} x1={40} x2={680} y1={40 + i * 57} y2={40 + i * 57} stroke={`${c.primary}33`} />)}
            <path d={`${line} L 680 220 L 40 220 Z`} fill={`${c.primary}26`} opacity={g} />
            <path d={line} pathLength={1} style={drawOn(g)} fill="none" stroke={c.primary} strokeWidth={4} />
            <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r={8} fill={c.accent} opacity={g >= 1 ? 1 : 0} />
          </svg>
        ), 0.14)}
        {panel({ top: 540, insetInlineEnd: 140, width: 760, height: 230 }, (
          <div style={{ display: "flex", alignItems: "center", gap: 40 }}>
            <svg width={170} height={170} viewBox="0 0 170 170">
              <circle cx={85} cy={85} r={70} stroke={`${c.primary}33`} strokeWidth={12} fill="none" />
              <circle cx={85} cy={85} r={70} stroke={c.accent} strokeWidth={12} fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - (props.gauge.value / 100) * phase(0.35, 0.7, EASE.count)} transform="rotate(-90 85 85)" strokeLinecap="round" />
              <text x={85} y={98} textAnchor="middle" fill={c.text} fontFamily={font.display} fontSize={40} fontWeight={700}>{Math.round(props.gauge.value * phase(0.35, 0.7, EASE.count))}%</text>
            </svg>
            <div style={{ fontSize: 34 * scale, fontWeight: 600 }}>{props.gauge.label}</div>
          </div>
        ), 0.2)}
      </AbsoluteFill>
    </Stage>
  );
};
