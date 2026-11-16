// 17 · Radar Scan — rotating sweep with a fading trail, blips revealed as the beam passes, alert ring, status list.
import React from "react";
import { EASE } from "../../lib/motion";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type RadarBlip = { angle: number; dist: number; label?: string; alert?: boolean }; // angle° clockwise from north, dist 0–1
export type RadarStatus = { label: string; value: string; alert?: boolean };
export type RadarScanProps = MotionStyleBaseProps & {
  title?: string;
  blips?: RadarBlip[];
  status?: RadarStatus[];
  rpm?: number; // sweeps per 10 s (default 2.5)
};

export const DEFAULT_BLIPS: RadarBlip[] = [
  { angle: 35, dist: 0.55, label: "محطة 12" }, { angle: 110, dist: 0.8 }, { angle: 160, dist: 0.35, label: "محطة 07" },
  { angle: 215, dist: 0.7, label: "تسرب محتمل", alert: true }, { angle: 290, dist: 0.5 }, { angle: 320, dist: 0.85, label: "محطة 21" },
];

export const RadarScan: React.FC<RadarScanProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, frame, fps, intensity, scale } = ctx;
  const R = 380, cx = ctx.rtl ? 1260 : 660, cy = 560;
  const open = phase(0.02, 0.15, EASE.out);
  const live = phase(0.12, 0.2);
  const degPerFrame = (360 * (props.rpm ?? 2.5)) / (10 * fps);
  const sweep = (frame * degPerFrame) % 360;
  const blips = props.blips ?? DEFAULT_BLIPS;
  const pt = (a: number, d: number) => [cx + Math.sin((a * Math.PI) / 180) * R * d, cy - Math.cos((a * Math.PI) / 180) * R * d] as const;
  const wedges = Math.round(10 + 20 * intensity);
  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        <g opacity={open} transform={`translate(${cx} ${cy}) scale(${0.85 + 0.15 * open}) translate(${-cx} ${-cy})`}>
          {[0.25, 0.5, 0.75, 1].map((k) => <circle key={k} cx={cx} cy={cy} r={R * k} fill="none" stroke={c.primary} strokeOpacity={k === 1 ? 0.8 : 0.3} strokeWidth={k === 1 ? 3 : 1.2} />)}
          {[0, 45, 90, 135].map((a) => { const [x1, y1] = pt(a, 1), [x2, y2] = pt(a + 180, 1); return <line key={a} x1={x1} y1={y1} x2={x2} y2={y2} stroke={c.primary} strokeOpacity={0.2} />; })}
          {Array.from({ length: wedges }).map((_, k) => {
            const a1 = sweep - k * 2.2, a2 = a1 - 2.4;
            const [x1, y1] = pt(a1, 1), [x2, y2] = pt(a2, 1);
            return <path key={k} d={`M ${cx} ${cy} L ${x1} ${y1} A ${R} ${R} 0 0 0 ${x2} ${y2} Z`} fill={c.primary} opacity={live * (1 - k / wedges) * (0.18 + 0.25 * intensity)} />;
          })}
          {(() => { const [x, y] = pt(sweep, 1); return <line x1={cx} y1={cy} x2={x} y2={y} stroke={c.primary} strokeWidth={3} opacity={live} />; })()}
          {blips.map((b, i) => {
            const since = ((sweep - b.angle + 360) % 360) / 360; // 0 just hit … 1 about to hit again
            const firstPass = frame * degPerFrame >= b.angle;
            const glow = firstPass ? Math.max(b.alert ? 0.55 : 0.25, 1 - since * 1.4) : 0;
            const [x, y] = pt(b.angle, b.dist);
            const ring = b.alert ? (frame % 40) / 40 : 0;
            return (
              <g key={i} opacity={live * glow}>
                {b.alert && <circle cx={x} cy={y} r={14 + ring * 50} fill="none" stroke={c.accent} strokeWidth={2.5} opacity={1 - ring} />}
                <circle cx={x} cy={y} r={b.alert ? 12 : 8} fill={b.alert ? c.accent : c.text} />
                {b.label && <text x={x + (ctx.rtl ? -20 : 20)} y={y + 8} textAnchor="start" direction={ctx.dir} fill={b.alert ? c.accent : c.text} fontFamily={font.body} fontWeight={600} fontSize={26 * scale}>{b.label}</text>}
              </g>
            );
          })}
          <circle cx={cx} cy={cy} r={8} fill={c.accent} />
        </g>
      </svg>
      {/* panel sits on the side opposite the radar (physical positioning) */}
      <div style={{ position: "absolute", top: 220, left: ctx.rtl ? 160 : 1160, width: 600, fontFamily: font.body, color: c.text, direction: ctx.dir }}>
        {props.title && <div style={{ fontFamily: font.display, fontWeight: ctx.weight, fontSize: 52 * scale, marginBottom: 40, opacity: phase(0, 0.12) }}>{props.title}</div>}
        {(props.status ?? []).map((s, i) => {
          const t = phase(0.2 + i * 0.06, 0.3 + i * 0.06);
          return (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "18px 0", borderBottom: `1px solid ${c.primary}55`, opacity: t, transform: `translateY(${(1 - t) * 14}px)` }}>
              <span style={{ fontSize: 30 * scale, color: c.muted }}>{s.label}</span>
              <span style={{ fontSize: 34 * scale, fontWeight: 700, fontFamily: font.display, color: s.alert ? c.accent : c.text, direction: "ltr", unicodeBidi: "isolate" }}>{s.value}</span>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};
