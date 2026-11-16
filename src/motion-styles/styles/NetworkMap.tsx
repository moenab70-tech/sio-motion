// 9 · Network Map — stations (nodes) connected by links; nodes pop in, links draw, data pulses travel.
import React from "react";
import { EASE, mix } from "../../lib/motion";
import { Stage } from "../core/Stage";
import { drawOn } from "../core/svg";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type NetNode = { x: number; y: number; label?: string; hub?: boolean }; // x,y in 0–1 of the frame
export type NetworkMapProps = MotionStyleBaseProps & {
  title?: string;
  nodes?: NetNode[];
  links?: [number, number][];
  pulses?: number; // pulses per link (default by intensity)
};

export const DEFAULT_NODES: NetNode[] = [
  { x: 0.5, y: 0.52, label: "مركز التحكم", hub: true },
  { x: 0.25, y: 0.3, label: "محطة الشمال" }, { x: 0.22, y: 0.72, label: "محطة الغرب" },
  { x: 0.75, y: 0.28, label: "محطة الشرق" }, { x: 0.8, y: 0.7, label: "محطة الجنوب" },
  { x: 0.38, y: 0.18 }, { x: 0.62, y: 0.82 }, { x: 0.1, y: 0.5 }, { x: 0.9, y: 0.48 },
];
export const DEFAULT_LINKS: [number, number][] = [[0, 1], [0, 2], [0, 3], [0, 4], [1, 5], [3, 5], [2, 7], [4, 6], [2, 6], [3, 8], [4, 8], [1, 7]];

export const NetworkMap: React.FC<NetworkMapProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, frame, total, intensity, rtl, scale } = ctx;
  const nodes = props.nodes ?? DEFAULT_NODES;
  const links = props.links ?? DEFAULT_LINKS;
  // positions are geographic: never mirrored by reading direction
  const P = (n: NetNode) => [n.x * 1920, 100 + n.y * 900] as const;
  const pulses = props.pulses ?? Math.round(1 + intensity * 2);
  const live = phase(0.4, 0.5);
  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        {links.map(([a, b], i) => {
          const [x1, y1] = P(nodes[a]), [x2, y2] = P(nodes[b]);
          const t = phase(0.15 + i * 0.015, 0.35 + i * 0.015, EASE.inOut);
          return (
            <g key={i}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={c.primary} strokeWidth={3} strokeOpacity={0.7} pathLength={1} style={drawOn(t)} />
              {Array.from({ length: pulses }).map((_, k) => {
                const u = ((frame / total) * 3 + k / pulses + i * 0.17) % 1;
                return <circle key={k} cx={mix(x1, x2, u)} cy={mix(y1, y2, u)} r={6} fill={c.accent} opacity={live * Math.sin(u * Math.PI)} />;
              })}
            </g>
          );
        })}
        {nodes.map((n, i) => {
          const [x, y] = P(n);
          const t = phase(0.05 + i * 0.025, 0.18 + i * 0.025, EASE.out);
          const r = (n.hub ? 34 : n.label ? 20 : 11) * t;
          const ring = n.hub ? ((frame % 45) / 45) : 0;
          return (
            <g key={i} opacity={Math.min(1, t * 2)}>
              {n.hub && <circle cx={x} cy={y} r={34 + ring * 60} fill="none" stroke={c.accent} strokeWidth={2} opacity={(1 - ring) * live} />}
              <circle cx={x} cy={y} r={r} fill={n.hub ? c.accent : c.primary} stroke={c.text} strokeWidth={n.label ? 3 : 1.5} />
              {n.label && (
                <text x={x} y={y + r + 40} textAnchor="middle" direction={ctx.dir} fill={c.text} fontFamily={font.body} fontWeight={600} fontSize={(n.hub ? 32 : 26) * scale} opacity={phase(0.3 + i * 0.02, 0.4 + i * 0.02)}>{n.label}</text>
              )}
            </g>
          );
        })}
        {props.title && <text x={rtl ? 1840 : 80} y={100} textAnchor="start" direction={ctx.dir} fill={c.text} fontFamily={font.display} fontWeight={ctx.weight} fontSize={54 * scale} opacity={phase(0, 0.12)}>{props.title}</text>}
      </svg>
    </Stage>
  );
};
