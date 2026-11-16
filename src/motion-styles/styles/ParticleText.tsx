// 5 · Particles — deterministic particles that gather into (shaped) text, hold, then disperse along a path.
// Text is rasterised once with the real font (Arabic shaping preserved), then sampled into points.
import React, { useEffect, useMemo, useState } from "react";
import { cancelRender, continueRender, delayRender, random } from "remotion";
import { EASE, mix, ramp } from "../../lib/motion";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type ParticleTextProps = MotionStyleBaseProps & {
  text: string;
  fontSize?: number;
  maxParticles?: number; // performance cap (default 2200)
  density?: number; // sampling step in px (default 5; higher = fewer particles)
  path?: "swirl" | "rise" | "explode";
  particleSize?: number;
};

const W = 1920, H = 1080;

const useTextPoints = (text: string, font: string, weight: number, size: number, rtl: boolean, step: number, max: number, seed: string) => {
  const [pts, setPts] = useState<[number, number][] | null>(null);
  const [handle] = useState(() => delayRender(`Sampling particle text "${text}"`));
  useEffect(() => {
    let cancelled = false;
    const css = `${weight} ${size}px ${font}`;
    document.fonts
      .load(css, text)
      .then(() => document.fonts.ready)
      .then(() => {
        if (cancelled) return;
        const cv = document.createElement("canvas");
        cv.width = W;
        cv.height = H;
        const g = cv.getContext("2d", { willReadFrequently: true })!;
        g.font = css;
        g.direction = rtl ? "rtl" : "ltr";
        g.textAlign = "center";
        g.textBaseline = "middle";
        g.fillStyle = "#fff";
        g.fillText(text, W / 2, H / 2);
        const data = g.getImageData(0, 0, W, H).data;
        const found: [number, number][] = [];
        for (let y = 0; y < H; y += step) for (let x = 0; x < W; x += step) if (data[(y * W + x) * 4 + 3] > 128) found.push([x, y]);
        // deterministic subsample
        const chosen = found.length <= max ? found : found.map((p, i) => ({ p, k: random(`${seed}-pick-${i}`) })).sort((a, b) => a.k - b.k).slice(0, max).map((o) => o.p);
        setPts(chosen);
        continueRender(handle);
      })
      .catch((e) => cancelRender(e));
    return () => {
      cancelled = true;
    };
  }, [text, font, weight, size, rtl, step, max, seed, handle]);
  return pts;
};

export const ParticleText: React.FC<ParticleTextProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { frame, total, palette: c, intensity, seed } = ctx;
  const size = (props.fontSize ?? 190) * ctx.scale;
  const pts = useTextPoints(props.text, ctx.font.display, ctx.weight, size, ctx.rtl, props.density ?? 5, props.maxParticles ?? 2200, seed);
  const path = props.path ?? "swirl";

  const particles = useMemo(
    () =>
      (pts ?? []).map(([tx, ty], i) => ({
        tx, ty,
        sx: random(`${seed}-sx-${i}`) * W,
        sy: random(`${seed}-sy-${i}`) * H,
        delay: random(`${seed}-d-${i}`) * 0.18,
        r: (props.particleSize ?? 2.6) * (0.6 + random(`${seed}-r-${i}`) * 0.8),
        accent: random(`${seed}-a-${i}`) < 0.18,
        swirl: (random(`${seed}-w-${i}`) - 0.5) * 2,
      })),
    [pts, seed, props.particleSize],
  );

  if (!pts) return null;
  const t = frame / total;
  return (
    <Stage ctx={ctx} fade={false}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        {particles.map((p, i) => {
          const gather = EASE.inOut(Math.max(0, Math.min(1, (t - 0.04 - p.delay) / 0.38)));
          const leave = EASE.in(Math.max(0, Math.min(1, (t - 0.7 - p.delay * 0.6) / 0.26)));
          const curve = Math.sin(gather * Math.PI) * 160 * intensity * p.swirl;
          let x = mix(p.sx, p.tx, gather) + curve;
          let y = mix(p.sy, p.ty, gather) - curve * 0.5;
          // gentle deterministic shimmer while holding
          x += Math.sin(frame / 9 + i) * 0.6 * intensity;
          y += Math.cos(frame / 11 + i) * 0.6 * intensity;
          if (leave > 0) {
            if (path === "rise") { y -= leave * (300 + 500 * p.swirl * p.swirl); x += Math.sin(leave * 4 + i) * 40 * leave; }
            else if (path === "explode") { const a = Math.atan2(p.ty - H / 2, p.tx - W / 2); x += Math.cos(a) * leave * 900; y += Math.sin(a) * leave * 900; }
            else { const a = leave * 3 * p.swirl; const dx = x - W / 2, dy = y - H / 2; x = W / 2 + dx * Math.cos(a) * (1 + leave) - dy * Math.sin(a); y = H / 2 + dx * Math.sin(a) + dy * Math.cos(a) * (1 + leave); }
          }
          const op = Math.min(1, 0.25 + gather) * (1 - leave) * ramp(frame, 0, ctx.sec(0.4));
          return <circle key={i} cx={x.toFixed(1)} cy={y.toFixed(1)} r={p.r} fill={p.accent ? c.accent : c.text} opacity={op.toFixed(3)} />;
        })}
      </svg>
    </Stage>
  );
};
