// 19 · Parallax Layers (2.5D) — procedural landscape layers (dunes, canal, field rows) moving at depth-dependent speeds.
import React, { useMemo } from "react";
import { random } from "remotion";
import { EASE, mix } from "../../lib/motion";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type ParallaxLayersProps = MotionStyleBaseProps & {
  title?: string;
  subtitle?: string;
  camera?: "pan" | "push";
  depth?: number; // parallax strength multiplier (default 1)
};

const ridge = (seed: string, base: number, amp: number, width = 2600) => {
  const n = 40;
  let d = `M -300 1080 L -300 ${base}`;
  for (let i = 0; i <= n; i++) {
    const x = -300 + (i / n) * width;
    const y = base - amp * (0.5 * Math.sin(i * 0.45 + random(`${seed}a`) * 6) + 0.3 * Math.sin(i * 1.1 + random(`${seed}b`) * 6) + 0.2 * Math.sin(i * 2.3));
    d += ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
  }
  return `${d} L ${width - 300} 1080 Z`;
};

export const ParallaxLayers: React.FC<ParallaxLayersProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, frame, total, intensity, seed, scale, rtl } = ctx;
  const depth = (props.depth ?? 1) * (0.5 + intensity);
  const t = frame / total;
  const dir = rtl ? 1 : -1; // camera moves toward the reading direction
  const push = props.camera === "push";
  const layer = (z: number) => (push ? `translate(960 700) scale(${1 + t * 0.12 * z * depth}) translate(-960 -700)` : `translate(${dir * t * 260 * z * depth} 0)`);
  const far = useMemo(() => ridge(`${seed}-far`, 640, 70), [seed]);
  const mid = useMemo(() => ridge(`${seed}-mid`, 720, 60), [seed]);
  const rise = (k: number) => EASE.out(phase(0.02 + k * 0.06, 0.25 + k * 0.06));
  const titleIn = phase(0.3, 0.45);
  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        <g transform={layer(0.15)} opacity={rise(0)}>
          <circle cx={rtl ? 300 : 1620} cy={210} r={80} fill={c.accent} opacity={0.85} />
        </g>
        <g transform={layer(0.35)} opacity={rise(1)}>
          <path d={far} fill={c.primary} opacity={0.35} transform={`translate(0 ${(1 - rise(1)) * 80})`} />
        </g>
        <g transform={layer(0.6)} opacity={rise(2)}>
          <path d={mid} fill={c.primary} opacity={0.6} transform={`translate(0 ${(1 - rise(2)) * 80})`} />
        </g>
        <g transform={layer(0.85)} opacity={rise(3)}>
          {/* canal band with shimmer */}
          <path d="M -300 860 C 400 820, 1200 900, 2300 840 L 2300 900 C 1200 960, 400 880, -300 920 Z" fill={c.primary} />
          {Array.from({ length: 14 }).map((_, i) => (
            <line key={i} x1={-200 + i * 170 + ((frame * 2) % 170)} y1={880} x2={-140 + i * 170 + ((frame * 2) % 170)} y2={878} stroke={c.text} strokeOpacity={0.5} strokeWidth={2} />
          ))}
        </g>
        <g transform={layer(1.3)} opacity={rise(4)}>
          <rect x={-400} y={930} width={2800} height={150} fill={c.primary} opacity={0.85} />
          {Array.from({ length: 22 }).map((_, i) => <line key={i} x1={-400 + i * 130} y1={1080} x2={mix(-400 + i * 130, 960, 0.35)} y2={935} stroke={c.accent} strokeOpacity={0.45} strokeWidth={2} />)}
        </g>
        {props.title && <text x={960} y={300} textAnchor="middle" direction={ctx.dir} fill={c.text} fontFamily={font.display} fontWeight={ctx.weight} fontSize={84 * scale} opacity={titleIn} transform={`translate(0 ${(1 - titleIn) * 20})`}>{props.title}</text>}
        {props.subtitle && <text x={960} y={370} textAnchor="middle" direction={ctx.dir} fill={c.muted} fontFamily={font.body} fontSize={36 * scale} opacity={titleIn}>{props.subtitle}</text>}
      </svg>
    </Stage>
  );
};
