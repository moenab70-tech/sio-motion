// 2 · Blueprint — animated grid, schematic draw-on, dimension lines, callouts, title block.
import React from "react";
import { EASE } from "../../lib/motion";
import { Stage } from "../core/Stage";
import { drawOn } from "../core/svg";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type BlueprintProps = MotionStyleBaseProps & {
  title: string;
  drawingNo?: string;
  callouts: [string, string, string]; // canal, pump station, water level
  dimensions: [string, string]; // width, depth
  gridOpacity?: number;
};

const W = 1920, H = 1080;

export const Blueprint: React.FC<BlueprintProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, intensity, rtl, scale } = ctx;
  const g = phase(0, 0.25, EASE.inOut);
  const minor = 40, major = 200;
  const gridAlpha = (props.gridOpacity ?? 0.18) * (0.6 + 0.4 * intensity);
  const stroke = c.primary;
  const p = (a: number, b: number) => drawOn(phase(a, b, EASE.inOut));
  const show = (a: number, b: number) => phase(a, b);
  // schematic geometry (canal cross-section + pipe + pump house)
  const cx = 860, base = 760;
  const canal = `M ${cx - 420} ${base - 260} L ${cx - 260} ${base} L ${cx + 260} ${base} L ${cx + 420} ${base - 260}`;
  const water = `M ${cx - 360} ${base - 170} L ${cx + 360} ${base - 170}`;
  const pipe = `M ${cx + 420} ${base - 120} L ${cx + 700} ${base - 120} L ${cx + 700} ${base - 330}`;
  // edge = which side of the text sits at x. SVG flips start/end for RTL text, so map physically.
  const anchorFor = (edge: "left" | "center" | "right") => (edge === "center" ? "middle" : (edge === "right") === rtl ? "start" : "end");
  const label = (x: number, y: number, s: string, t: number, edge: "left" | "center" | "right" = "center", size = 30) => (
    <text x={x} y={y} fill={c.text} fontFamily={font.body} fontSize={size * scale} fontWeight={500} textAnchor={anchorFor(edge)} direction={ctx.dir} opacity={t}>{s}</text>
  );
  return (
    <Stage ctx={ctx}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <defs>
          <marker id="bp-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={c.accent} />
          </marker>
        </defs>
        {/* grid grows from the reading-start side */}
        <g opacity={gridAlpha}>
          {Array.from({ length: Math.ceil(W / minor) + 1 }).map((_, i) => {
            const x = rtl ? W - i * minor : i * minor;
            const vis = Math.max(0, Math.min(1, g * 1.4 - (i * minor) / W * 0.4));
            return <line key={`v${i}`} x1={x} y1={0} x2={x} y2={H * vis} stroke={stroke} strokeWidth={(i * minor) % major === 0 ? 1.6 : 0.6} />;
          })}
          {Array.from({ length: Math.ceil(H / minor) + 1 }).map((_, i) => {
            const vis = Math.max(0, Math.min(1, g * 1.4 - (i * minor) / H * 0.4));
            return <line key={`h${i}`} x1={rtl ? W : 0} y1={i * minor} x2={rtl ? W - W * vis : W * vis} y2={i * minor} stroke={stroke} strokeWidth={(i * minor) % major === 0 ? 1.6 : 0.6} />;
          })}
        </g>
        {/* schematic */}
        <g fill="none" stroke={stroke} strokeWidth={4} strokeLinejoin="round" strokeLinecap="round">
          <path d={canal} pathLength={1} style={p(0.15, 0.4)} />
          <path d={water} pathLength={1} style={p(0.3, 0.45)} stroke={c.accent} strokeDasharray="1" />
          <path d={pipe} pathLength={1} style={p(0.35, 0.55)} strokeWidth={10} />
          <rect x={cx + 620} y={base - 470} width={160} height={140} pathLength={1} style={p(0.45, 0.6)} />
          <circle cx={cx + 700} cy={base - 400} r={36} pathLength={1} style={p(0.5, 0.62)} />
        </g>
        {/* water fill */}
        <path d={`M ${cx - 360} ${base - 170} L ${cx - 260} ${base} L ${cx + 260} ${base} L ${cx + 360} ${base - 170} Z`} fill={c.primary} opacity={0.18 * show(0.42, 0.6)} />
        {/* dimension lines */}
        <g stroke={c.accent} strokeWidth={2} opacity={show(0.5, 0.65)}>
          <line x1={cx - 260} y1={base + 60} x2={cx + 260} y2={base + 60} markerStart="url(#bp-arrow)" markerEnd="url(#bp-arrow)" />
          <line x1={cx - 520} y1={base - 170} x2={cx - 520} y2={base} markerStart="url(#bp-arrow)" markerEnd="url(#bp-arrow)" />
          <line x1={cx - 260} y1={base + 20} x2={cx - 260} y2={base + 80} />
          <line x1={cx + 260} y1={base + 20} x2={cx + 260} y2={base + 80} />
        </g>
        {label(cx, base + 110, props.dimensions[0], show(0.55, 0.7), "center", 32)}
        {label(cx - 560, base - 75, props.dimensions[1], show(0.55, 0.7), "right", 32)}
        {/* callouts */}
        <g stroke={c.muted} strokeWidth={1.5} fill="none">
          <path d={`M ${cx - 330} ${base - 220} L ${cx - 420} ${base - 360} L ${cx - 560} ${base - 360}`} pathLength={1} style={p(0.6, 0.7)} />
          <path d={`M ${cx + 700} ${base - 470} L ${cx + 700} ${base - 560} L ${cx + 560} ${base - 560}`} pathLength={1} style={p(0.62, 0.72)} />
          <path d={`M ${cx + 120} ${base - 170} L ${cx + 200} ${base - 300} L ${cx + 340} ${base - 300}`} pathLength={1} style={p(0.64, 0.74)} />
        </g>
        {label(cx - 570, base - 372, props.callouts[0], show(0.68, 0.78), "right")}
        {label(cx + 550, base - 572, props.callouts[1], show(0.7, 0.8), "right")}
        {label(cx + 350, base - 312, props.callouts[2], show(0.72, 0.82), "left")}
        {/* title block */}
        <g opacity={show(0.75, 0.9)}>
          <rect x={rtl ? 1340 : 80} y={900} width={500} height={120} fill="none" stroke={stroke} strokeWidth={2} />
          <line x1={rtl ? 1340 : 80} y1={960} x2={rtl ? 1840 : 580} y2={960} stroke={stroke} strokeWidth={1} />
          {label(rtl ? 1820 : 100, 944, props.title, 1, rtl ? "right" : "left", 34)}
          {label(rtl ? 1820 : 100, 1000, props.drawingNo ?? "DWG-001", 1, rtl ? "right" : "left", 22)}
        </g>
      </svg>
    </Stage>
  );
};
