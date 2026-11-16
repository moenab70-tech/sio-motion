// 10 · Timeline — axis draws from the reading-start side, milestones appear in order, a marker travels to "current".
import React from "react";
import { EASE, mix } from "../../lib/motion";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type Milestone = { year: string; label: string };
export type TimelineProps = MotionStyleBaseProps & {
  title?: string;
  items: Milestone[]; // 3–7
  currentIndex?: number; // highlighted milestone (default last)
};

export const Timeline: React.FC<TimelineProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, rtl, scale } = ctx;
  const items = props.items.slice(0, 7);
  const n = items.length;
  const cur = props.currentIndex ?? n - 1;
  const left = 180, right = 1740, y = 560;
  const xAt = (i: number) => { const t = n === 1 ? 0.5 : i / (n - 1); return rtl ? mix(right, left, t) : mix(left, right, t); };
  const axis = phase(0.05, 0.35, EASE.inOut);
  const marker = phase(0.55, 0.85, EASE.inOut) * cur;
  const mFloor = Math.floor(marker);
  const mX = mix(xAt(mFloor), xAt(Math.min(n - 1, mFloor + 1)), marker - mFloor);
  return (
    <Stage ctx={ctx}>
      <div style={{ position: "absolute", inset: 0, fontFamily: font.body, color: c.text }}>
        {props.title && <div style={{ position: "absolute", top: 120, insetInlineStart: 180, fontFamily: font.display, fontWeight: ctx.weight, fontSize: 56 * scale, opacity: phase(0, 0.12) }}>{props.title}</div>}
        {/* axis */}
        <div style={{ position: "absolute", top: y - 2, left, width: right - left, height: 4, background: `${c.primary}55` }} />
        <div style={{ position: "absolute", top: y - 2, left: rtl ? undefined : left, right: rtl ? 1920 - right : undefined, width: (right - left) * axis, height: 4, background: c.primary }} />
        {/* progress up to the marker */}
        <div style={{ position: "absolute", top: y - 3, left: rtl ? mX : left, width: rtl ? right - mX : mX - left, height: 6, background: c.accent, opacity: phase(0.55, 0.6) }} />
        {items.map((it, i) => {
          const t = phase(0.18 + i * 0.06, 0.3 + i * 0.06, EASE.out);
          const up = i % 2 === 0;
          const active = i <= marker + 0.01;
          return (
            <div key={i} style={{ position: "absolute", left: xAt(i), top: y, opacity: t }}>
              <div style={{ position: "absolute", left: -13, top: -13, width: 26, height: 26, borderRadius: 13, background: active ? c.accent : c.primary, border: `3px solid ${c.text}`, transform: `scale(${t})` }} />
              <div style={{ position: "absolute", left: -1, top: up ? -110 * t : 13, width: 2, height: 97 * t, background: `${c.text}66` }} />
              <div style={{ position: "absolute", width: 300, left: -150, top: up ? -230 : 120, textAlign: "center", transform: `translateY(${(1 - t) * (up ? 20 : -20)}px)` }}>
                <div style={{ fontFamily: font.display, fontWeight: 700, fontSize: 52 * scale, color: i === cur ? c.accent : c.text, lineHeight: 1.2 }}>{it.year}</div>
                <div style={{ fontSize: 26 * scale, color: c.muted, lineHeight: 1.5, direction: ctx.dir }}>{it.label}</div>
              </div>
            </div>
          );
        })}
        <div style={{ position: "absolute", left: mX - 22, top: y - 22, width: 44, height: 44, borderRadius: 22, border: `3px solid ${c.accent}`, opacity: phase(0.55, 0.6) }} />
      </div>
    </Stage>
  );
};
