// 12 · Charts — 2D animated line / area / bars / donut with axes, grid, labels and counting values.
import React from "react";
import { formatNumber } from "../../lib/numbers";
import { EASE, mix } from "../../lib/motion";
import { Stage } from "../core/Stage";
import { drawOn } from "../core/svg";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type ChartsProps = MotionStyleBaseProps & {
  chart: "line" | "area" | "bars" | "donut";
  title?: string;
  labels: string[];
  values: number[];
  unit?: string;
  mirrorX?: boolean; // reverse category order for RTL (default false: time axis stays left→right)
};

export const Charts: React.FC<ChartsProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, scale, intensity } = ctx;
  const vals = props.values;
  const n = vals.length;
  const max = Math.max(...vals) * 1.15 || 1;
  const L = 240, R = 1700, T = 260, B = 860;
  const order = (i: number) => (props.mirrorX ? n - 1 - i : i);
  const xAt = (i: number) => mix(L + 60, R - 60, n === 1 ? 0.5 : order(i) / (n - 1));
  const yAt = (v: number) => mix(B, T, v / max);
  const grow = phase(0.2, 0.7, EASE.count);
  const fmt = (v: number) => formatNumber(v, { digits: "latin" });
  const title = props.title && (
    <text x={ctx.rtl ? 1700 : 240} y={170} textAnchor="start" direction={ctx.dir} fill={c.text} fontFamily={font.display} fontWeight={ctx.weight} fontSize={54 * scale} opacity={phase(0, 0.12)}>{props.title}</text>
  );

  if (props.chart === "donut") {
    const sum = vals.reduce((a, b) => a + b, 0) || 1;
    let acc = 0;
    const colors = [c.accent, c.primary, c.secondary, c.muted];
    return (
      <Stage ctx={ctx}>
        <svg width={1920} height={1080} viewBox="0 0 1920 1080">
          {title}
          {vals.map((v, i) => {
            const start = acc / sum; acc += v;
            const len = (v / sum) * grow;
            return <circle key={i} cx={760} cy={580} r={250} fill="none" stroke={colors[i % colors.length]} strokeWidth={90 + 20 * intensity} pathLength={1} strokeDasharray={`${Math.max(0, len - 0.004)} 1`} strokeDashoffset={-start * grow} transform="rotate(-90 760 580)" />;
          })}
          <text x={760} y={600} textAnchor="middle" fill={c.text} fontFamily={font.display} fontWeight={700} fontSize={84 * scale}>{fmt(Math.round(sum * grow))}</text>
          {props.labels.map((l, i) => (
            <g key={i} opacity={phase(0.4 + i * 0.06, 0.55 + i * 0.06)} transform={`translate(1150 ${420 + i * 90})`}>
              <rect width={34} height={34} rx={6} fill={colors[i % colors.length]} />
              <text x={56} y={28} fill={c.text} fontFamily={font.body} fontSize={32 * scale}>{l} — {fmt(vals[i])}{props.unit ? ` ${props.unit}` : ""}</text>
            </g>
          ))}
        </svg>
      </Stage>
    );
  }

  const pts = vals.map((v, i) => [xAt(i), yAt(v * (props.chart === "bars" ? 1 : 1))] as const);
  const line = [...pts].sort((a, b) => a[0] - b[0]).map((p, i) => `${i ? "L" : "M"} ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
  const sorted = [...pts].sort((a, b) => a[0] - b[0]);
  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        {title}
        {[0, 0.25, 0.5, 0.75, 1].map((k, i) => (
          <g key={i} opacity={phase(0.05, 0.2)}>
            <line x1={L} x2={R} y1={mix(B, T, k)} y2={mix(B, T, k)} stroke={c.muted} strokeOpacity={k === 0 ? 0.6 : 0.18} />
            <text x={L - 20} y={mix(B, T, k) + 8} textAnchor="end" fill={c.muted} fontFamily={font.body} fontSize={22}>{fmt(Math.round(max * k))}</text>
          </g>
        ))}
        {props.labels.map((l, i) => <text key={i} x={xAt(i)} y={B + 50} textAnchor="middle" fill={c.muted} fontFamily={font.body} fontSize={26 * scale} opacity={phase(0.1, 0.25)}>{l}</text>)}
        {props.chart === "bars"
          ? vals.map((v, i) => {
              const g = phase(0.2 + i * 0.05, 0.55 + i * 0.05, EASE.count);
              const h = (B - yAt(v)) * g;
              return (
                <g key={i}>
                  <rect x={xAt(i) - 50} y={B - h} width={100} height={h} rx={8} fill={i === n - 1 ? c.accent : c.primary} />
                  <text x={xAt(i)} y={B - h - 20} textAnchor="middle" fill={c.text} fontFamily={font.display} fontWeight={700} fontSize={36 * scale} opacity={g}>{fmt(Math.round(v * g))}</text>
                </g>
              );
            })
          : (
            <>
              {props.chart === "area" && <path d={`${line} L ${sorted[n - 1][0]} ${B} L ${sorted[0][0]} ${B} Z`} fill={c.primary} opacity={0.25 * grow} />}
              <path d={line} fill="none" stroke={c.primary} strokeWidth={6} strokeLinejoin="round" pathLength={1} style={drawOn(grow)} />
              {pts.map(([x, y], i) => {
                const t = phase(0.25 + (order(i) / n) * 0.45, 0.35 + (order(i) / n) * 0.45);
                return (
                  <g key={i} opacity={t}>
                    <circle cx={x} cy={y} r={11} fill={i === n - 1 ? c.accent : c.text} />
                    <text x={x} y={y - 26} textAnchor="middle" fill={c.text} fontFamily={font.display} fontWeight={700} fontSize={30 * scale}>{fmt(vals[i])}</text>
                  </g>
                );
              })}
            </>
          )}
        {props.unit && <text x={L} y={T - 30} textAnchor="start" fill={c.accent} fontFamily={font.body} fontSize={26 * scale} direction={ctx.dir}>{props.unit}</text>}
      </svg>
    </Stage>
  );
};
