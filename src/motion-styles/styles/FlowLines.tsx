// 8 · Flow Lines — pipe/canal network that draws on, then carries animated flow pulses with live flow-rate labels.
import React from "react";
import { formatNumber } from "../../lib/numbers";
import { EASE } from "../../lib/motion";
import { Stage } from "../core/Stage";
import { drawOn } from "../core/svg";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type FlowGauge = { label: string; value: number; unit: string };

export type FlowLinesProps = MotionStyleBaseProps & {
  title?: string;
  gauges?: [FlowGauge, FlowGauge, FlowGauge]; // source, junction, outlet
  flowSpeed?: number; // pulse speed multiplier (default 1)
};

// Physical layout (LTR). Mirrored for RTL so water flows in the reading direction.
const PATHS = [
  "M 180 520 C 420 520 520 380 760 380 L 1180 380",
  "M 760 380 C 900 380 960 640 1180 640 L 1740 640",
  "M 1180 380 C 1380 380 1440 300 1740 300",
  "M 1180 380 L 1180 640",
];
const NODES: [number, number][] = [[180, 520], [760, 380], [1180, 380], [1180, 640], [1740, 300], [1740, 640]];

export const FlowLines: React.FC<FlowLinesProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, frame, intensity, rtl, scale } = ctx;
  const speed = (props.flowSpeed ?? 1) * (0.6 + intensity);
  const flowOn = phase(0.3, 0.42);
  const g = props.gauges;
  const mirror = rtl ? "translate(1920 0) scale(-1 1)" : undefined;
  const mx = (x: number) => (rtl ? 1920 - x : x);
  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        <g transform={mirror} fill="none" strokeLinecap="round">
          {PATHS.map((d, i) => (
            <g key={i}>
              <path d={d} stroke={c.primary} strokeOpacity={0.25} strokeWidth={34} pathLength={1} style={drawOn(phase(0.05 + i * 0.05, 0.3 + i * 0.05, EASE.inOut))} />
              <path d={d} stroke={c.primary} strokeWidth={4} pathLength={1} style={drawOn(phase(0.05 + i * 0.05, 0.3 + i * 0.05, EASE.inOut))} />
              {/* flow pulses: dashes travelling along the pipe */}
              <path d={d} stroke={c.accent} strokeWidth={10} pathLength={1000} strokeDasharray="26 54" strokeDashoffset={-frame * 6 * speed} opacity={flowOn * (0.55 + 0.45 * intensity)} />
            </g>
          ))}
          {NODES.map(([x, y], i) => {
            const t = phase(0.12 + i * 0.03, 0.22 + i * 0.03);
            return <circle key={i} cx={x} cy={y} r={18 * t} fill={c.background === "transparent" ? c.primary : c.primary} stroke={c.text} strokeWidth={3} opacity={t} />;
          })}
        </g>
        {g && [[0, 180, 520], [2, 1180, 380], [4, 1740, 640]].map(([gi, x, y], k) => {
          const t = phase(0.42 + k * 0.05, 0.55 + k * 0.05);
          const gauge = g[k];
          const v = gauge.value * phase(0.45 + k * 0.05, 0.85, EASE.count);
          return (
            <g key={gi} opacity={t} transform={`translate(${mx(x)} ${y - 80})`}>
              <text textAnchor="middle" y={-46} fill={c.muted} fontFamily={font.body} fontSize={26 * scale} direction={ctx.dir}>{gauge.label}</text>
              <text textAnchor="middle" y={0} fill={c.text} fontFamily={font.display} fontWeight={700} fontSize={44 * scale} style={{ unicodeBidi: "isolate" }}>
                {formatNumber(v, { digits: "latin" })} <tspan fill={c.accent} fontSize={26 * scale}>{gauge.unit}</tspan>
              </text>
            </g>
          );
        })}
        {props.title && (
          <text x={rtl ? 1840 : 80} y={130} textAnchor="start" direction={ctx.dir} fill={c.text} fontFamily={font.display} fontWeight={ctx.weight} fontSize={58 * scale} opacity={phase(0, 0.12)}>{props.title}</text>
        )}
      </svg>
    </Stage>
  );
};
