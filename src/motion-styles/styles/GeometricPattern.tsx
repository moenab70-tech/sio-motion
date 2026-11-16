// 15 · Geometric Patterns — Islamic-inspired 8-point star (khatam) lattice built outward from the centre, framing a title.
import React from "react";
import { EASE } from "../../lib/motion";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type GeometricPatternProps = MotionStyleBaseProps & {
  title?: string;
  subtitle?: string;
  cell?: number; // tile size in px (default 120)
  lineWidth?: number;
  clearCenter?: boolean; // keep a calm medallion behind the title (default true)
};

const star = (cx: number, cy: number, r: number) => {
  const pts: string[] = [];
  for (let k = 0; k < 16; k++) {
    const a = (Math.PI / 8) * k - Math.PI / 2;
    const rr = k % 2 === 0 ? r : r * 0.62;
    pts.push(`${(cx + Math.cos(a) * rr).toFixed(1)},${(cy + Math.sin(a) * rr).toFixed(1)}`);
  }
  return pts.join(" ");
};

export const GeometricPattern: React.FC<GeometricPatternProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, frame, total, intensity, scale } = ctx;
  const cell = props.cell ?? 120;
  const lw = props.lineWidth ?? 2;
  const cols = Math.ceil(1920 / cell) + 2, rows = Math.ceil(1080 / cell) + 2;
  const maxD = Math.hypot(960, 540);
  const build = phase(0.02, 0.6, EASE.inOut);
  const medR = 300;
  const titleIn = phase(0.4, 0.6);
  const spin = (frame / total) * 22.5 * intensity;
  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        {Array.from({ length: rows }).map((_, r) =>
          Array.from({ length: cols }).map((__, q) => {
            const cx = (q - 0.5) * cell + (1920 % cell) / 2, cy = (r - 0.5) * cell + (1080 % cell) / 2;
            const d = Math.hypot(cx - 960, cy - 540);
            if (props.clearCenter !== false && d < medR + cell * 0.2) return null;
            const t = Math.max(0, Math.min(1, build * 1.5 - (d / maxD) * 0.5) * 1);
            const e = EASE.out(Math.min(1, t * 1.6));
            if (e <= 0) return null;
            const accent = (q + r) % 4 === 0;
            return (
              <g key={`${r}-${q}`} opacity={e * (0.35 + 0.5 * intensity)} transform={`rotate(${(1 - e) * 45 + (accent ? spin : 0)} ${cx} ${cy})`}>
                <polygon points={star(cx, cy, (cell / 2) * 0.92 * e)} fill="none" stroke={accent ? c.accent : c.primary} strokeWidth={lw} />
                <rect x={cx - cell * 0.18} y={cy - cell * 0.18} width={cell * 0.36} height={cell * 0.36} fill="none" stroke={c.primary} strokeWidth={lw * 0.6} transform={`rotate(45 ${cx} ${cy})`} opacity={0.7} />
              </g>
            );
          }),
        )}
        {/* medallion */}
        <circle cx={960} cy={540} r={medR * phase(0.3, 0.5, EASE.out)} fill="none" stroke={c.accent} strokeWidth={3} />
        <circle cx={960} cy={540} r={(medR - 18) * phase(0.33, 0.53, EASE.out)} fill="none" stroke={c.accent} strokeWidth={1} opacity={0.6} />
        {props.title && <text x={960} y={props.subtitle ? 545 : 560} textAnchor="middle" direction={ctx.dir} fill={c.text} fontFamily={font.display} fontWeight={ctx.weight} fontSize={74 * scale} opacity={titleIn}>{props.title}</text>}
        {props.subtitle && <text x={960} y={615} textAnchor="middle" direction={ctx.dir} fill={c.muted} fontFamily={font.body} fontSize={32 * scale} opacity={titleIn}>{props.subtitle}</text>}
      </svg>
    </Stage>
  );
};
