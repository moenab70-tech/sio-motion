// 7 · Split-Flap — mechanical flipping board. Arabic flips whole WORDS (keeps letters joined);
// English flips characters; numbers flip digit-by-digit (counter mode).
import React from "react";
import { random } from "remotion";
import { formatNumber } from "../../lib/numbers";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle, type MotionCtx } from "../core/useMotionStyle";

export type SplitFlapProps = MotionStyleBaseProps & {
  rows: string[]; // text rows
  counter?: { from: number; to: number; suffix?: string; label?: string };
  pool?: string[]; // filler words for Arabic flips
  fontSize?: number;
  flips?: number; // flips per cell before landing (default by intensity)
};

const LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const DIGITS = "0123456789";

type CellPlan = { states: string[]; start: number; flipLen: number; widthEm: number };

const Half: React.FC<{ text: string; part: "top" | "bottom"; style?: React.CSSProperties; ctx: MotionCtx; size: number }> = ({ text, part, style, ctx, size }) => (
  <div style={{ position: "absolute", left: 0, right: 0, height: "50%", top: part === "top" ? 0 : "50%", overflow: "hidden", background: ctx.mode === "experimental" ? "#140b2a" : "#0E1A2C", backfaceVisibility: "hidden", ...style }}>
    <div style={{ position: "absolute", left: 0, right: 0, height: size * 1.5, top: part === "top" ? 0 : -size * 0.75, display: "flex", alignItems: "center", justifyContent: "center", color: ctx.palette.text, fontFamily: ctx.font.display, fontWeight: ctx.weight, fontSize: size, lineHeight: 1, whiteSpace: "nowrap" }}>
      {text}
    </div>
  </div>
);

const Cell: React.FC<{ plan: CellPlan; ctx: MotionCtx; size: number }> = ({ plan, ctx, size }) => {
  const { frame } = ctx;
  const n = plan.states.length - 1;
  const raw = (frame - plan.start) / plan.flipLen;
  const idx = Math.max(0, Math.min(n, Math.floor(raw)));
  const f = raw >= n ? 1 : raw < 0 ? 0 : raw - idx;
  const prev = plan.states[idx];
  const next = plan.states[Math.min(n, idx + 1)];
  const flipping = raw >= 0 && raw < n;
  const H = size * 1.5;
  const line = <div style={{ position: "absolute", left: 0, right: 0, top: "50%", height: 2, background: "rgba(0,0,0,0.55)", zIndex: 5 }} />;
  return (
    <div style={{ position: "relative", width: `${plan.widthEm}em`, height: H, fontSize: size, perspective: H * 4, borderRadius: 6, overflow: "hidden", boxShadow: `0 0 0 1px ${ctx.palette.primary}55` }}>
      {flipping ? (
        <>
          <Half text={next} part="top" ctx={ctx} size={size} />
          <Half text={prev} part="bottom" ctx={ctx} size={size} />
          {f < 0.5 ? (
            <Half text={prev} part="top" ctx={ctx} size={size} style={{ transformOrigin: "bottom", transform: `rotateX(${-f * 180}deg)`, filter: `brightness(${1 - f})` }} />
          ) : (
            <Half text={next} part="bottom" ctx={ctx} size={size} style={{ transformOrigin: "top", transform: `rotateX(${(1 - f) * 180}deg)`, filter: `brightness(${0.5 + f / 2})` }} />
          )}
        </>
      ) : (
        <>
          <Half text={raw < 0 ? plan.states[0] : plan.states[n]} part="top" ctx={ctx} size={size} />
          <Half text={raw < 0 ? plan.states[0] : plan.states[n]} part="bottom" ctx={ctx} size={size} />
        </>
      )}
      {line}
    </div>
  );
};

export const SplitFlap: React.FC<SplitFlapProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { total, seed, intensity, palette: c, scale } = ctx;
  const size = (props.fontSize ?? 72) * scale;
  const flips = props.flips ?? Math.round(3 + intensity * 6);
  const flipLen = Math.max(2, ctx.sec(0.085));
  const pool = props.pool ?? ["مياه", "ري", "قناة", "سد", "طاقة", "رقمي", "نمو", "شبكة"];
  const landBy = total * 0.55;

  const plans: CellPlan[][] = props.rows.map((row, r) => {
    const cells = ctx.lang === "ar" ? row.split(/\s+/).filter(Boolean) : [...row.toUpperCase()];
    return cells.map((target, i) => {
      const states: string[] = [" "];
      for (let k = 0; k < flips; k++) {
        const rnd = random(`${seed}-${r}-${i}-${k}`);
        states.push(ctx.lang === "ar" ? pool[Math.floor(rnd * pool.length)] : target === " " ? " " : /[0-9]/.test(target) ? DIGITS[Math.floor(rnd * 10)] : LATIN[Math.floor(rnd * 26)]);
      }
      states.push(target);
      const start = Math.min(landBy - states.length * flipLen, ctx.sec(0.2) + (r * cells.length * 0.3 + i) * ctx.sec(0.05));
      const longest = Math.max(...states.map((s) => s.length));
      return { states, start, flipLen, widthEm: ctx.lang === "ar" ? Math.max(1.6, longest * 0.62 + 0.6) : 0.9 };
    });
  });

  let counterPlans: CellPlan[] = [];
  if (props.counter) {
    const to = formatNumber(props.counter.to, { digits: "latin" });
    const from = formatNumber(props.counter.from, { digits: "latin" }).padStart(to.length, " ");
    counterPlans = [...to].map((d, i) => {
      const s = from[i] === "," || d === "," ? [d] : (() => {
        const a = from[i] === " " ? 0 : Number(from[i]);
        const b = Number(d);
        const seq: string[] = [];
        for (let v = a; v !== (b + 1) % 10; v = (v + 1) % 10) { seq.push(String(v)); if (seq.length > 10) break; }
        return seq.length ? seq : [d];
      })();
      return { states: s, start: ctx.sec(0.4) + (to.length - i) * ctx.sec(0.1), flipLen: flipLen * 1.4, widthEm: d === "," ? 0.45 : 0.85 };
    });
  }

  return (
    <Stage ctx={ctx}>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: size * 0.4 }}>
        {plans.map((cells, r) => (
          <div key={r} style={{ display: "flex", gap: size * 0.12, direction: ctx.dir }}>
            {cells.map((p, i) => <Cell key={i} plan={p} ctx={ctx} size={size} />)}
          </div>
        ))}
        {props.counter && (
          <div style={{ display: "flex", alignItems: "center", gap: size * 0.3, marginTop: size * 0.3, direction: ctx.dir }}>
            {props.counter.label && <div style={{ fontFamily: ctx.font.body, fontSize: size * 0.5, color: c.muted }}>{props.counter.label}</div>}
            <div style={{ display: "flex", gap: size * 0.08, direction: "ltr" }}>
              {counterPlans.map((p, i) => <Cell key={i} plan={p} ctx={ctx} size={size * 1.2} />)}
            </div>
            {props.counter.suffix && <div style={{ fontFamily: ctx.font.display, fontSize: size * 0.7, color: c.accent, fontWeight: 700 }}>{props.counter.suffix}</div>}
          </div>
        )}
      </div>
    </Stage>
  );
};

