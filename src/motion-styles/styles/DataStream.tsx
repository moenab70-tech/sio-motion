// 18 · Data Stream — restrained columns of streaming digits that dim and resolve into KPI counters.
import React, { useMemo } from "react";
import { random } from "remotion";
import { formatNumber } from "../../lib/numbers";
import { EASE } from "../../lib/motion";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type StreamKpi = { label: string; value: number; suffix?: string; decimals?: number };
export type DataStreamProps = MotionStyleBaseProps & {
  title?: string;
  kpis: StreamKpi[]; // 2–4
  columns?: number; // stream density (default 42)
  glyphs?: string; // characters used in the stream (default digits)
};

const ROWS = 22;

export const DataStream: React.FC<DataStreamProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, frame, intensity, seed, scale } = ctx;
  const cols = props.columns ?? 42;
  const glyphs = props.glyphs ?? "0123456789";
  const colW = 1920 / cols, rowH = 1080 / ROWS;
  const meta = useMemo(() => Array.from({ length: cols }, (_, i) => ({ speed: 0.25 + random(`${seed}-s${i}`) * 0.6, off: random(`${seed}-o${i}`) * ROWS, len: 6 + Math.floor(random(`${seed}-l${i}`) * 10) })), [cols, seed]);
  const resolve = phase(0.42, 0.62, EASE.inOut); // stream dims as KPIs arrive
  const streamOpacity = (0.25 + 0.55 * intensity) * (1 - 0.8 * resolve) * phase(0, 0.08);
  const kpis = props.kpis.slice(0, 4);
  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        <g fontFamily={font.display} fontSize={rowH * 0.62} textAnchor="middle" opacity={streamOpacity}>
          {meta.map((m, i) => {
            const head = (frame * m.speed * 0.5 + m.off) % (ROWS + m.len);
            return Array.from({ length: m.len }).map((_, k) => {
              const row = Math.floor(head) - k;
              if (row < 0 || row >= ROWS) return null;
              const g = glyphs[Math.floor(random(`${seed}-${i}-${row}-${Math.floor(frame / 4)}`) * glyphs.length)];
              return <text key={`${i}-${k}`} x={(i + 0.5) * colW} y={(row + 0.8) * rowH} fill={k === 0 ? c.accent : c.primary} opacity={k === 0 ? 1 : 1 - k / m.len}>{g}</text>;
            });
          })}
        </g>
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: font.body, color: c.text }}>
        {props.title && <div style={{ fontFamily: font.display, fontWeight: ctx.weight, fontSize: 54 * scale, marginBottom: 60, opacity: resolve }}>{props.title}</div>}
        <div style={{ display: "flex", gap: 100, direction: ctx.dir }}>
          {kpis.map((k, i) => {
            const t = phase(0.5 + i * 0.06, 0.62 + i * 0.06);
            const v = k.value * phase(0.52 + i * 0.06, 0.85, EASE.count);
            return (
              <div key={i} style={{ textAlign: "center", opacity: t, transform: `scale(${0.9 + 0.1 * t})` }}>
                <div style={{ fontFamily: font.display, fontWeight: 800, fontSize: 110 * scale, lineHeight: 1.15, unicodeBidi: "isolate" }}>
                  {formatNumber(v, { digits: "latin", decimals: k.decimals ?? 0 })}{k.suffix && <span style={{ fontSize: "0.4em", color: c.accent, marginInlineStart: 8 }}>{k.suffix}</span>}
                </div>
                <div style={{ fontSize: 30 * scale, color: c.muted, marginTop: 6 }}>{k.label}</div>
              </div>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};
