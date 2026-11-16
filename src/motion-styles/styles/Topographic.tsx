// 16 · Topographic — contour lines from a deterministic terrain (marching squares), drawn level by level,
// with a rising water level and elevation markers.
import React, { useMemo } from "react";
import { random } from "remotion";
import { formatNumber } from "../../lib/numbers";
import { EASE, mix } from "../../lib/motion";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type TopographicProps = MotionStyleBaseProps & {
  title?: string;
  levelLabel?: string; // e.g. "منسوب المياه"
  minElevation?: number; // metres for level 0 (default 280)
  maxElevation?: number; // metres for level 1 (default 420)
  waterTo?: number; // final water level 0–1 (default 0.38)
  levels?: number; // number of contour levels (default 14)
};

const GX = 96, GY = 54; // grid resolution (performance: ~5k cells)

const field = (seed: string) => {
  const hills = Array.from({ length: 6 }, (_, i) => ({ x: random(`${seed}-hx${i}`), y: random(`${seed}-hy${i}`), s: 0.12 + random(`${seed}-hs${i}`) * 0.2, a: 0.5 + random(`${seed}-ha${i}`) }));
  const h: number[][] = [];
  let lo = Infinity, hi = -Infinity;
  for (let j = 0; j <= GY; j++) {
    h.push([]);
    for (let i = 0; i <= GX; i++) {
      const x = i / GX, y = j / GY;
      let v = 0.08 * Math.sin(x * 9 + y * 4);
      for (const k of hills) v += k.a * Math.exp(-(((x - k.x) ** 2 + ((y - k.y) * 0.6) ** 2) / (k.s * k.s)));
      h[j].push(v); lo = Math.min(lo, v); hi = Math.max(hi, v);
    }
  }
  return h.map((row) => row.map((v) => (v - lo) / (hi - lo)));
};

// marching squares → one SVG path string per level
const contour = (h: number[][], level: number) => {
  const sx = 1920 / GX, sy = 1080 / GY;
  let d = "";
  const lerp = (a: number, b: number) => (level - a) / (b - a || 1e-6);
  for (let j = 0; j < GY; j++) for (let i = 0; i < GX; i++) {
    const a = h[j][i], b = h[j][i + 1], c = h[j + 1][i + 1], e = h[j + 1][i];
    const idx = (a > level ? 8 : 0) | (b > level ? 4 : 0) | (c > level ? 2 : 0) | (e > level ? 1 : 0);
    if (idx === 0 || idx === 15) continue;
    const T: [number, number] = [(i + lerp(a, b)) * sx, j * sy];
    const R: [number, number] = [(i + 1) * sx, (j + lerp(b, c)) * sy];
    const B: [number, number] = [(i + lerp(e, c)) * sx, (j + 1) * sy];
    const L: [number, number] = [i * sx, (j + lerp(a, e)) * sy];
    const seg = (p: [number, number], q: [number, number]) => { d += `M${p[0].toFixed(1)} ${p[1].toFixed(1)}L${q[0].toFixed(1)} ${q[1].toFixed(1)}`; };
    switch (idx) {
      case 1: case 14: seg(L, B); break;
      case 2: case 13: seg(B, R); break;
      case 3: case 12: seg(L, R); break;
      case 4: case 11: seg(T, R); break;
      case 6: case 9: seg(T, B); break;
      case 7: case 8: seg(L, T); break;
      case 5: seg(L, T); seg(B, R); break;
      case 10: seg(T, R); seg(L, B); break;
    }
  }
  return d;
};

export const Topographic: React.FC<TopographicProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, scale, intensity, seed } = ctx;
  const L = props.levels ?? 14;
  const lines = useMemo(() => { const h = field(seed); return Array.from({ length: L }, (_, k) => contour(h, (k + 1) / (L + 1))); }, [seed, L]);
  const water = phase(0.45, 0.85, EASE.inOut) * (props.waterTo ?? 0.38);
  const minE = props.minElevation ?? 280, maxE = props.maxElevation ?? 420;
  const elev = mix(minE, maxE, water);
  return (
    <Stage ctx={ctx}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        {lines.map((d, k) => {
          const lv = (k + 1) / (L + 1);
          const t = phase(0.03 + (k / L) * 0.35, 0.12 + (k / L) * 0.35);
          const under = lv <= water;
          return <path key={k} d={d} fill="none" stroke={under ? c.primary : k % 4 === 3 ? c.accent : c.muted} strokeWidth={under ? 3.2 : k % 4 === 3 ? 2 : 1.1} opacity={t * (under ? 0.95 : 0.35 + 0.35 * intensity)} />;
        })}
      </svg>
      <div style={{ position: "absolute", inset: 0, fontFamily: font.body, color: c.text }}>
        {props.title && <div style={{ position: "absolute", top: 90, insetInlineStart: 120, fontFamily: font.display, fontWeight: ctx.weight, fontSize: 56 * scale, opacity: phase(0, 0.12) }}>{props.title}</div>}
        <div style={{ position: "absolute", bottom: 110, insetInlineStart: 120, opacity: phase(0.45, 0.55), display: "flex", alignItems: "baseline", gap: 20 }}>
          <span style={{ fontSize: 32 * scale, color: c.muted }}>{props.levelLabel ?? "منسوب المياه"}</span>
          <span style={{ fontFamily: font.display, fontWeight: 800, fontSize: 84 * scale, color: c.text, unicodeBidi: "isolate" }}>{formatNumber(elev, { digits: "latin" })}<span style={{ fontSize: "0.4em", color: c.accent, marginInlineStart: 10 }}>{ctx.lang === "ar" ? "م" : "m"}</span></span>
        </div>
      </div>
    </Stage>
  );
};
