// 6 · Liquid Morph — organic SVG blobs morphing between seeded shapes, used as fluid masks over text.
// Pure path geometry (no blur/goo filters), so it renders identically everywhere.
import React from "react";
import { random } from "remotion";
import { EASE, mix } from "../../lib/motion";
import { Stage } from "../core/Stage";
import { smoothClosedPath } from "../core/svg";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type LiquidMorphProps = MotionStyleBaseProps & {
  title: string;
  subtitle?: string;
  shapes?: number; // number of morph targets (2–6)
  blobScale?: number; // 1 = default size
  fontSize?: number;
};

const N = 48;
const radii = (seed: string, k: number) =>
  Array.from({ length: N }, (_, i) => {
    const th = (i / N) * Math.PI * 2;
    let r = 1;
    for (let h = 2; h <= 5; h++) r += (random(`${seed}-${k}-a${h}`) - 0.5) * (0.42 / h) * 2 * Math.sin(h * th + random(`${seed}-${k}-p${h}`) * Math.PI * 2);
    return r;
  });

export const LiquidMorph: React.FC<LiquidMorphProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { frame, total, palette: c, font, intensity, seed, scale } = ctx;
  const K = Math.max(2, Math.min(6, props.shapes ?? 4));
  const shapes = React.useMemo(() => Array.from({ length: K }, (_, k) => radii(seed, k)), [seed, K]);
  const pos = (frame / total) * (K - 1);
  const k = Math.min(K - 2, Math.floor(pos));
  const m = EASE.inOut(pos - k);
  const wobble = (i: number) => Math.sin(frame / 18 + i * 0.7) * 0.025 * intensity;
  const blob = (cx: number, cy: number, R: number, rot: number) =>
    smoothClosedPath(shapes[k].map((r0, i) => {
      const r = mix(r0, shapes[k + 1][i], m) + wobble(i);
      const th = (i / N) * Math.PI * 2 + rot;
      return [cx + Math.cos(th) * R * r, cy + Math.sin(th) * R * r] as [number, number];
    }));
  const grow = EASE.out(Math.min(1, frame / (total * 0.18)));
  const R = 330 * (props.blobScale ?? 1) * grow;
  const rot = frame / 260;
  const main = blob(960, 520, R, rot);
  const second = blob(960 + (ctx.rtl ? -260 : 260), 600, R * 0.55, -rot * 1.4);
  const size = (props.fontSize ?? 128) * scale;
  const id = `lm-${seed.replace(/[^a-z0-9]/gi, "")}`;
  const title = (fill: string) => (
    <text x={960} y={540} textAnchor="middle" dominantBaseline="middle" direction={ctx.dir} fontFamily={font.display} fontWeight={ctx.weight} fontSize={size} fill={fill}>{props.title}</text>
  );
  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        <defs>
          <clipPath id={`${id}-clip`}><path d={main} /></clipPath>
          <linearGradient id={`${id}-g`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor={c.primary} stopOpacity={0.95} />
            <stop offset="1" stopColor={c.primary} stopOpacity={0.55} />
          </linearGradient>
        </defs>
        <path d={second} fill={c.accent} opacity={0.35 + 0.35 * intensity} />
        <path d={main} fill={`url(#${id}-g)`} opacity={0.85} />
        {/* fluid mask: text outside blob = text colour, inside blob = accent */}
        {title(c.text)}
        <g clipPath={`url(#${id}-clip)`}>{title(c.accent === c.primary ? c.text : c.accent)}</g>
        {props.subtitle && (
          <text x={960} y={540 + size * 0.95} textAnchor="middle" direction={ctx.dir} fontFamily={font.body} fontSize={40 * scale} fill={c.muted} opacity={EASE.out(Math.min(1, Math.max(0, frame / total - 0.2) / 0.2))}>{props.subtitle}</text>
        )}
      </svg>
    </Stage>
  );
};
