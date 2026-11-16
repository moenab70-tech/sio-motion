// 3B v2 — From drawing to project (locked camera, plate 1:1). Grease Pencil engineering lines are drawn in the
// canal's own perspective over a faint, tracing-paper version of the painting; the painting comes to life, the
// lines turn gold and dissolve. Water flows inside the canal, mist drifts, birds cross.
import React from "react";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame } from "remotion";
import { LW_3B } from "../linework";
import { LineSeq } from "./Shot1B";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.45, 0, 0.25, 1);
const PLATE = staticFile("media/opening/assets/M-03B-canal-reveal.png");
const WATER = ["930,360 1070,360 1290,650 700,650", "830,740 1170,740 1520,1088 540,1088"];

const Bird: React.FC<{ x: number; y: number; s: number; f: number; ph: number }> = ({ x, y, s, f, ph }) => {
  const w = Math.sin(f / 3 + ph) * 6;
  return <path d={`M ${x - 12 * s} ${y + w * s * 0.3} Q ${x - 5 * s} ${y - 6 * s + w * s * 0.4} ${x} ${y} Q ${x + 5 * s} ${y - 6 * s + w * s * 0.4} ${x + 12 * s} ${y + w * s * 0.3}`} fill="none" stroke="#2A2118" strokeWidth={2 * s} strokeLinecap="round" opacity="0.7" />;
};

export const Shot3B: React.FC<{ len: number }> = () => {
  const f = useCurrentFrame();
  const paint = interpolate(f, [0, 18, 48], [0.26, 0.3, 1], { ...clamp, easing: ease });
  return (
    <AbsoluteFill style={{ background: "#EFE6D2", overflow: "hidden" }}>
      <svg width={1920} height={1088} viewBox="0 0 1920 1088" style={{ position: "absolute", left: 0, top: -4 }}>
        <defs>
          <filter id="flow" x="0" y="0" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.012 0.05" numOctaves="2" seed="9" result="n" />
            <feOffset in="n" dy={(f * 4) % 400} result="m" />
            <feTile in="m" result="t" />
            <feDisplacementMap in="SourceGraphic" in2="t" scale="9" xChannelSelector="R" yChannelSelector="G" />
          </filter>
          <clipPath id="water">{WATER.map((p, i) => <polygon key={i} points={p} />)}</clipPath>
          <linearGradient id="mist" x1="0" x2="1"><stop offset="0" stopColor="#FFE7C0" stopOpacity="0" /><stop offset="0.5" stopColor="#FFE7C0" stopOpacity="0.35" /><stop offset="1" stopColor="#FFE7C0" stopOpacity="0" /></linearGradient>
          <filter id="soft"><feGaussianBlur stdDeviation="18" /></filter>
        </defs>
        <g opacity={paint} style={{ filter: `sepia(${(1 - paint) * 0.9}) contrast(${0.7 + 0.3 * paint})` }}>
          <image href={PLATE} width="1920" height="1088" />
          <g clipPath="url(#water)"><image href={PLATE} width="1920" height="1088" filter="url(#flow)" /></g>
          <rect x={-600 + f * 6} y="300" width="1400" height="110" fill="url(#mist)" filter="url(#soft)" />
          <rect x={900 - f * 4} y="360" width="1200" height="80" fill="url(#mist)" filter="url(#soft)" opacity="0.7" />
          <Bird x={400 + f * 5} y={150 - f * 0.4} s={1.1} f={f} ph={0} />
          <Bird x={450 + f * 5} y={175 - f * 0.4} s={0.9} f={f} ph={1.4} />
          <Bird x={360 + f * 5.3} y={190 - f * 0.3} s={0.8} f={f} ph={2.6} />
        </g>
      </svg>
      <LineSeq id="3B" frames={LW_3B.frames} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(255,200,120,0.10), rgba(0,0,0,0) 40%, rgba(0,0,0,0.22))" }} />
    </AbsoluteFill>
  );
};
