// Scene 01 — The Spark (5 s). Shot A: wide, dusk office, employee drawing (push-in + parallax).
// Shot B: top-down close-up — pencil really draws an irrigation-channel section; pause to examine; resumes.
import React from "react";
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame } from "remotion";
import { getLength, getPointAtLength } from "@remotion/paths";
import { Defs, P, SeatedFigure, WritingHand } from "./art";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.45, 0, 0.25, 1);
const CUT = 66; // shot A → B (6-frame dissolve)

// ── Shot A ─────────────────────────────────────────────────
const Palm: React.FC<{ x: number; y: number; s: number }> = ({ x, y, s }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} fill="#0D1A2C">
    <path d="M -3 0 C -2 -40, 2 -80, 6 -118 L 10 -118 C 7 -80, 4 -40, 4 0 Z" />
    {[-150, -120, -90, -60, -30, 0, 25].map((a, i) => (
      <path key={i} transform={`translate(8 -118) rotate(${a})`} d="M 0 0 C 18 -10, 42 -10, 62 4 C 42 0, 20 2, 0 6 Z" />
    ))}
  </g>
);

const ShotA: React.FC<{ f: number }> = ({ f }) => {
  const t = f / 30;
  const push = interpolate(f, [0, CUT + 6], [1, 1.14], { ...clamp, easing: ease });
  const wrist = { x: 1236 + 10 * Math.sin(t * 2 * Math.PI * 1.5) + f * 0.25, y: 700 + 3 * Math.sin(t * 2 * Math.PI * 3.1) };
  const headTilt = -1.2 + 1.4 * Math.sin(t * 1.3);
  const breath = Math.sin(t * 2 * Math.PI * 0.28);
  return (
    <AbsoluteFill>
      <svg viewBox="0 0 1920 1080" width={1920} height={1080}>
        <defs>
          <linearGradient id="a-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={P.night2} /><stop offset="1" stopColor={P.night0} /></linearGradient>
          <linearGradient id="a-sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={P.skyTop} /><stop offset="0.55" stopColor={P.skyMid} /><stop offset="0.86" stopColor={P.horizon} /><stop offset="1" stopColor="#7A5232" />
          </linearGradient>
          <radialGradient id="a-sun" cx="0.32" cy="0.9" r="0.5"><stop offset="0" stopColor={P.sun} stopOpacity="0.9" /><stop offset="1" stopColor={P.sun} stopOpacity="0" /></radialGradient>
          <radialGradient id="a-lamp" cx="1330" cy="722" r="420" gradientUnits="userSpaceOnUse"><stop offset="0" stopColor={P.warm} stopOpacity="0.55" /><stop offset="1" stopColor={P.warm} stopOpacity="0" /></radialGradient>
          <linearGradient id="a-cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={P.warm} stopOpacity="0.35" /><stop offset="1" stopColor={P.warm} stopOpacity="0.04" /></linearGradient>
          <linearGradient id="a-beam" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor={P.horizon} stopOpacity="0.16" /><stop offset="1" stopColor={P.horizon} stopOpacity="0" /></linearGradient>
          <clipPath id="a-win"><rect x="260" y="150" width="600" height="500" /></clipPath>
          <filter id="a-fg"><feGaussianBlur stdDeviation="9" /></filter>
          <radialGradient id="a-vig" cx="0.55" cy="0.55" r="0.75"><stop offset="0.55" stopColor="#000" stopOpacity="0" /><stop offset="1" stopColor="#000" stopOpacity="0.75" /></radialGradient>
        </defs>
        <g transform={`translate(960 560) scale(${push}) translate(-1060 -560)`}>
          <rect width="1920" height="1080" fill="url(#a-wall)" />
          {/* window — the outside drifts slower than the room (parallax) */}
          <g clipPath="url(#a-win)">
            <g transform={`translate(${(push - 1) * 260} ${(push - 1) * 60})`}>
              <rect x="200" y="120" width="740" height="560" fill="url(#a-sky)" />
              <rect x="200" y="120" width="740" height="560" fill="url(#a-sun)" />
              <path d="M 200 600 L 300 590 L 330 570 L 380 572 L 400 560 L 470 562 L 520 585 L 640 588 L 700 575 L 760 578 L 820 592 L 940 596 L 940 680 L 200 680 Z" fill="#132238" />
              <Palm x={340} y={600} s={1} /><Palm x={420} y={606} s={0.8} /><Palm x={700} y={600} s={1.15} /><Palm x={790} y={606} s={0.75} />
              <rect x="200" y="628" width="740" height="10" fill={P.horizon} opacity="0.35" />
            </g>
          </g>
          <path d="M 260 150 H 860 V 650 H 260 Z M 556 150 V 650 M 260 400 H 860" fill="none" stroke="#050A13" strokeWidth="14" />
          <path d="M 860 650 L 1180 1080 L 700 1080 L 260 650 Z" fill="url(#a-beam)" />
          {/* lamp light on the desk */}
          <rect width="1920" height="1080" fill="url(#a-lamp)" />
          <path d="M 1452 520 L 1500 512 L 1530 718 L 1270 718 Z" fill="url(#a-cone)" />
          {/* figure */}
          <SeatedFigure wrist={wrist} headTilt={headTilt} breath={breath} id="a" />
          {/* desk */}
          <path d="M 970 716 L 1780 716 L 1820 760 L 930 760 Z" fill="#2A1E14" />
          <path d="M 970 716 L 1780 716 L 1782 720 L 968 720 Z" fill={P.warm} opacity="0.35" />
          <rect x="930" y="760" width="890" height="320" fill="#0A0F18" />
          <path d="M 1200 712 L 1420 712 L 1446 726 L 1180 726 Z" fill={P.paper} />
          <path d="M 1230 716 L 1290 715 M 1300 717 L 1380 716 M 1240 721 L 1330 720" stroke={P.graphite} strokeWidth="1.4" opacity="0.6" />
          {/* lamp */}
          <ellipse cx="1600" cy="716" rx="46" ry="8" fill="#0B0F16" />
          <path d="M 1600 712 L 1640 560 L 1490 506" fill="none" stroke="#0B0F16" strokeWidth="8" strokeLinecap="round" />
          <path d="M 1440 492 L 1520 470 L 1540 520 L 1450 535 Z" fill="#101622" />
          <ellipse cx="1494" cy="526" rx="40" ry="8" fill={P.warm} opacity="0.9" />
          {/* mug + steam */}
          <path d="M 1680 668 L 1720 668 L 1716 714 L 1684 714 Z" fill="#131B28" />
          {[0, 1].map((k) => (
            <path key={k} d={`M ${1694 + k * 12} 664 C ${1686 + k * 12 + 8 * Math.sin(t * 2 + k)} 640, ${1704 + k * 12 - 8 * Math.sin(t * 2.4 + k)} 620, ${1696 + k * 12} 596`} fill="none" stroke={P.warm} strokeWidth="2" opacity={0.18 + 0.08 * Math.sin(t * 3 + k)} strokeLinecap="round" />
          ))}
          {/* dust in the lamp cone */}
          {Array.from({ length: 26 }).map((_, i) => {
            const x = 1290 + random(`dx${i}`) * 230, y = ((random(`dy${i}`) * 200 - t * 10 * (0.4 + random(`ds${i}`))) % 200 + 200) % 200 + 515;
            return <circle key={i} cx={x + Math.sin(t + i) * 6} cy={y} r={0.8 + random(`dr${i}`) * 1.6} fill={P.warm} opacity={0.25 + 0.35 * random(`do${i}`)} />;
          })}
        </g>
        {/* blurred foreground (rolled drawings) — moves faster: depth */}
        <g transform={`translate(${-(push - 1) * 900} ${(push - 1) * 120})`} filter="url(#a-fg)">
          <path d="M 1500 1080 L 1620 930 L 1940 930 L 1940 1080 Z" fill="#06090F" />
          <rect x="1560" y="900" width="420" height="40" rx="20" fill="#1A2436" transform="rotate(-8 1700 920)" />
          <rect x="1600" y="950" width="380" height="38" rx="19" fill="#22304A" transform="rotate(-4 1700 960)" />
        </g>
        <rect width="1920" height="1080" fill="url(#a-vig)" />
      </svg>
    </AbsoluteFill>
  );
};

// ── Shot B ─────────────────────────────────────────────────
// Paper coordinates (0..1300 × 0..900). Earlier work is already on the sheet; new strokes are drawn live.
const EARLIER = [
  "M 60 60 H 1240 V 840 H 60 Z", "M 900 720 H 1240 M 900 720 V 840 M 900 770 H 1240", "M 930 745 H 1060 M 930 800 H 1180 M 930 820 H 1100",
  "M 120 160 H 420 M 120 190 H 360", "M 1000 180 C 1060 150, 1120 150, 1180 180 M 1000 220 H 1180",
];
const STROKES = [
  { d: "M 230 520 L 380 520 L 470 640 L 730 640 L 820 520 L 970 520", from: 8, to: 44 }, // channel section
  { d: "M 425 580 L 775 580", from: 48, to: 60 }, // design water level
  { d: "M 470 690 L 730 690 M 470 676 L 470 704 M 730 676 L 730 704", from: 72, to: 88 }, // dimension (after the pause)
];
const lens = STROKES.map((s) => getLength(s.d));
const pointAt = (d: string, l: number) => { const p = getPointAtLength(d, l); return { x: p?.x ?? 0, y: p?.y ?? 0 }; };

const tipAt = (lf: number) => {
  // pencil position on the paper + lift (0 down, 1 raised)
  const i = STROKES.findIndex((s) => lf < s.to);
  const k = i === -1 ? STROKES.length - 1 : i;
  const s = STROKES[k];
  if (lf >= s.from) { const p = interpolate(lf, [s.from, s.to], [0, 1], clamp); const pt = pointAt(s.d, lens[k] * p); return { ...pt, lift: 0, k }; }
  const prev = k > 0 ? STROKES[k - 1] : null;
  const a = prev ? pointAt(prev.d, lens[k - 1]) : { x: 260, y: 470 };
  const b = pointAt(s.d, 0);
  const start = prev ? prev.to : 0;
  const p = interpolate(lf, [start, s.from], [0, 1], { ...clamp, easing: ease });
  // the pause before stroke 3 = the employee lifts the pencil and studies the drawing
  const study = k === 2 ? Math.sin(Math.PI * p) : 0;
  return { x: a.x + (b.x - a.x) * p + study * 60, y: a.y + (b.y - a.y) * p - study * 40, lift: Math.min(1, Math.sin(Math.PI * p) * (k === 2 ? 1.6 : 1)), k };
};

const ShotB: React.FC<{ lf: number }> = ({ lf }) => {
  const tip = tipAt(lf);
  const push = interpolate(lf, [0, 90], [1.06, 1.16], { ...clamp, easing: ease });
  const cam = { x: (tip.x - 650) * 0.12, y: (tip.y - 520) * 0.12 };
  const grip = Math.sin(lf / 4) * 0.5;
  return (
    <AbsoluteFill>
      <svg viewBox="0 0 1920 1080" width={1920} height={1080}>
        <Defs />
        <defs>
          <radialGradient id="b-desk" cx="0.5" cy="0.45" r="0.7"><stop offset="0" stopColor="#4A3220" /><stop offset="1" stopColor="#140D08" /></radialGradient>
          <radialGradient id="b-lamp" cx="0.52" cy="0.5" r="0.6"><stop offset="0" stopColor={P.warm} stopOpacity="0.28" /><stop offset="1" stopColor="#000" stopOpacity="0.55" /></radialGradient>
          <pattern id="b-grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 H 0 V 40" fill="none" stroke="#6E8FB8" strokeWidth="0.8" opacity="0.22" /></pattern>
        </defs>
        <g transform={`translate(960 540) scale(${push}) translate(${-960 - cam.x} ${-540 - cam.y})`}>
          <rect x="-200" y="-200" width="2320" height="1480" fill="url(#b-desk)" />
          {Array.from({ length: 18 }).map((_, i) => <path key={i} d={`M -200 ${i * 80 + 20} C 600 ${i * 80 + 40 * Math.sin(i)}, 1300 ${i * 80 + 30}, 2120 ${i * 80 - 10}`} stroke="#000" strokeOpacity="0.12" strokeWidth="2" fill="none" />)}
          <g transform="translate(310 90) rotate(-4 650 450)">
            <rect x="12" y="16" width="1300" height="900" fill="#000" opacity="0.35" filter="url(#soft8)" />
            <rect width="1300" height="900" fill={P.paper} />
            <rect width="1300" height="900" fill="url(#b-grid)" />
            <g filter="url(#pencilTex)">
              {EARLIER.map((d, i) => <path key={i} d={d} fill="none" stroke="#5A544C" strokeWidth="2" opacity="0.55" />)}
              {STROKES.map((s, i) => {
                const p = interpolate(lf, [s.from, s.to], [0, 1], clamp);
                return <path key={i} d={s.d} fill="none" stroke={P.graphite} strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={lens[i]} strokeDashoffset={lens[i] * (1 - p)} />;
              })}
            </g>
            <g transform={`translate(${tip.x} ${tip.y})`}><WritingHand lift={tip.lift} grip={grip} /></g>
          </g>
        </g>
        <rect width="1920" height="1080" fill="url(#b-lamp)" />
      </svg>
    </AbsoluteFill>
  );
};

export const SPARK_FRAMES = 150;

export const SparkScene: React.FC = () => {
  const f = useCurrentFrame();
  const mix = interpolate(f, [CUT - 6, CUT], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ background: P.night0 }}>
      {mix < 1 && <AbsoluteFill style={{ opacity: 1 }}><ShotA f={f} /></AbsoluteFill>}
      {mix > 0 && <AbsoluteFill style={{ opacity: mix }}><ShotB lf={f - (CUT - 6)} /></AbsoluteFill>}
    </AbsoluteFill>
  );
};
