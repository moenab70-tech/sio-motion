// 3 · Isometric — infrastructure blocks built in sequence, layered diagram, slow camera move, labels.
import React from "react";
import { EASE, mix } from "../../lib/motion";
import { Stage } from "../core/Stage";
import { iso } from "../core/svg";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type IsoBlock = { x: number; y: number; w: number; d: number; h: number; role: "primary" | "accent" | "structure" | "water"; label?: string };

export type IsometricProps = MotionStyleBaseProps & {
  title?: string;
  blocks?: IsoBlock[];
  camera?: "push" | "pan" | "static";
};

const hex = (c: string) => (/^#([0-9a-f]{6})$/i.test(c) ? c : null);
const shade = (c: string, k: number) => {
  const h = hex(c);
  if (!h) return c;
  const n = parseInt(h.slice(1), 16);
  const f = (v: number) => Math.round(Math.max(0, Math.min(255, v * k))).toString(16).padStart(2, "0");
  return `#${f(n >> 16)}${f((n >> 8) & 255)}${f(n & 255)}`;
};

export const DEFAULT_ISO_BLOCKS: IsoBlock[] = [
  { x: 0, y: 0, w: 9, d: 2.2, h: 0.35, role: "water", label: "قناة رئيسية" },
  { x: 1, y: 3.4, w: 2.4, d: 2.4, h: 2.2, role: "primary", label: "محطة ضخ" },
  { x: 4.2, y: 3.6, w: 1.8, d: 1.8, h: 3.4, role: "structure", label: "خزان" },
  { x: 6.6, y: 3.4, w: 2.2, d: 1.6, h: 1.4, role: "accent", label: "مركز التحكم" },
  { x: 3.4, y: 4.3, w: 0.8, d: 0.3, h: 0.3, role: "structure" },
  { x: 6.0, y: 4.3, w: 0.6, d: 0.3, h: 0.3, role: "structure" },
];

export const Isometric: React.FC<IsometricProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, frame, total, scale, intensity } = ctx;
  const blocks = props.blocks ?? DEFAULT_ISO_BLOCKS;
  const unit = 70;
  const roleColor = { primary: c.primary, accent: c.accent, structure: shade(hex(c.text) ? c.text : "#FFFFFF", 0.62), water: c.primary };
  const order = blocks.map((b, i) => ({ b, i })).sort((a, z) => a.b.x + a.b.y - (z.b.x + z.b.y));
  const cam = props.camera ?? "push";
  const camT = frame / total;
  const zoom = cam === "push" ? mix(0.92, 1.08, camT) : 1;
  const panX = cam === "pan" ? mix(-60, 60, camT) * (ctx.rtl ? -1 : 1) : 0;

  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="-960 -620 1920 1080">
        <g transform={`translate(${panX} -20) scale(${zoom}) translate(${-unit * 0.866 * 1.5} ${-unit * 3.6})`}>
          {/* ground grid */}
          <g opacity={0.25 * phase(0, 0.15)} stroke={c.muted} strokeWidth={1}>
            {Array.from({ length: 11 }).map((_, i) => {
              const a = iso(i - 1, -1, 0, unit), b = iso(i - 1, 7, 0, unit);
              const e = iso(-1, i - 1 - 2, 0, unit), f = iso(10, i - 1 - 2, 0, unit);
              return <g key={i}><line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} /><line x1={e[0]} y1={e[1]} x2={f[0]} y2={f[1]} /></g>;
            })}
          </g>
          {order.map(({ b, i }) => {
            const t = phase(0.1 + i * 0.07, 0.3 + i * 0.07, EASE.out);
            if (t <= 0) return null;
            const h = b.h * t;
            const col = roleColor[b.role];
            const P = (x: number, y: number, z: number) => iso(x, y, z, unit).map((v) => v.toFixed(1)).join(",");
            const top = [P(b.x, b.y, h), P(b.x + b.w, b.y, h), P(b.x + b.w, b.y + b.d, h), P(b.x, b.y + b.d, h)].join(" ");
            const left = [P(b.x, b.y + b.d, 0), P(b.x + b.w, b.y + b.d, 0), P(b.x + b.w, b.y + b.d, h), P(b.x, b.y + b.d, h)].join(" ");
            const right = [P(b.x + b.w, b.y, 0), P(b.x + b.w, b.y + b.d, 0), P(b.x + b.w, b.y + b.d, h), P(b.x + b.w, b.y, h)].join(" ");
            const alpha = b.role === "water" ? 0.55 + 0.25 * intensity : 1;
            return (
              <g key={i} opacity={Math.min(1, t * 2) * alpha}>
                <polygon points={left} fill={shade(col, 0.72)} />
                <polygon points={right} fill={shade(col, 0.52)} />
                <polygon points={top} fill={col} stroke={shade(col, 1.25)} strokeWidth={1} />
              </g>
            );
          })}
          {/* labels after construction */}
          {blocks.map((b, i) => {
            if (!b.label) return null;
            const t = phase(0.62 + i * 0.04, 0.75 + i * 0.04);
            const [x, y] = iso(b.x + b.w / 2, b.y + b.d / 2, b.h, unit);
            return (
              <g key={`l${i}`} opacity={t}>
                <line x1={x} y1={y} x2={x} y2={y - 70 * t} stroke={c.accent} strokeWidth={2} />
                <circle cx={x} cy={y} r={5} fill={c.accent} />
                <text x={x} y={y - 84} fill={c.text} fontFamily={font.body} fontSize={28 * scale} fontWeight={600} textAnchor="middle" direction={ctx.dir}>{b.label}</text>
              </g>
            );
          })}
        </g>
        {props.title && (
          <text x={ctx.rtl ? 860 : -860} y={-520} fill={c.text} fontFamily={font.display} fontSize={56 * scale} fontWeight={ctx.weight} textAnchor="start" direction={ctx.dir} opacity={phase(0, 0.15)}>{props.title}</text>
        )}
      </svg>
    </Stage>
  );
};
