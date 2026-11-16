// 4B — Recognition symbol. The sun glint from 4A travels to the centre, becomes a golden drop, gold petals unfold
// around it (inspired by the Harvest of Excellence mark), then everything dissolves into the main film's own
// navy backdrop — the last frames equal the film's first frame, so the cut is invisible. No title here.
import React from "react";
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame } from "remotion";
import { Backdrop } from "../../parts";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.22, 1, 0.36, 1);
const SUN = { x: 1530, y: 372 }; // sun position in 4A
const C = { x: 960, y: 520 };
const DROP = "M 0 -118 C 34 -66, 78 -18, 78 34 A 78 78 0 0 1 -78 34 C -78 -18, -34 -66, 0 -118 Z";
const LEAF = "M 0 0 C 20 -26, 22 -70, 0 -104 C -22 -70, -20 -26, 0 0 Z";

export const Shot4B: React.FC<{ len: number }> = () => {
  const f = useCurrentFrame();
  const travel = interpolate(f, [0, 30], [0, 1], { ...clamp, easing: ease });
  const px = SUN.x + (C.x - SUN.x) * travel, py = SUN.y + (C.y - SUN.y) * travel;
  const drop = interpolate(f, [18, 44], [0, 1], { ...clamp, easing: ease });
  const shimmer = interpolate(f, [54, 72], [-1, 1.4], clamp);
  const out = interpolate(f, [68, 88], [1, 0], { ...clamp, easing: Easing.in(Easing.quad) });
  return (
    <AbsoluteFill>
      <Backdrop frame={0} total={1} particles={0} />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <radialGradient id="pt"><stop offset="0" stopColor="#FFF4D6" /><stop offset="0.35" stopColor="#F2CF85" stopOpacity="0.9" /><stop offset="1" stopColor="#C8A45D" stopOpacity="0" /></radialGradient>
          <linearGradient id="gd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#F6DFA4" /><stop offset="0.5" stopColor="#D2AE62" /><stop offset="1" stopColor="#9C7A3A" /></linearGradient>
          <linearGradient id="gl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#EBCB84" /><stop offset="1" stopColor="#A9883F" /></linearGradient>
          <linearGradient id="go" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#9E9663" /><stop offset="1" stopColor="#6E6A43" /></linearGradient>
          <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stopColor="#fff" stopOpacity="0" /><stop offset="0.5" stopColor="#fff" stopOpacity="0.65" /><stop offset="1" stopColor="#fff" stopOpacity="0" /></linearGradient>
          <filter id="bloom" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
          <clipPath id="dc"><path d={DROP} /></clipPath>
        </defs>
        <g opacity={out}>
          {/* converging gold particles */}
          {Array.from({ length: 70 }).map((_, i) => {
            const a = random(`a${i}`) * Math.PI * 2, r0 = 380 + random(`r${i}`) * 520;
            const p = interpolate(f, [4 + random(`d${i}`) * 14, 46 + random(`e${i}`) * 10], [0, 1], { ...clamp, easing: ease });
            const r = r0 * (1 - p) + 150 * p;
            return <circle key={i} cx={C.x + Math.cos(a + p * 0.8) * r} cy={C.y + Math.sin(a + p * 0.8) * r} r={1 + random(`s${i}`) * 2.4} fill="#F2CF85" opacity={(0.25 + 0.6 * random(`o${i}`)) * Math.sin(Math.PI * Math.min(1, p * 1.1))} />;
          })}
          {/* travelling glint (continues the 4A sun) */}
          <circle cx={px} cy={py} r={18 + 50 * travel * (1 - drop)} fill="url(#pt)" opacity={1 - drop * 0.9} filter="url(#bloom)" />
          <g transform={`translate(${C.x} ${C.y + 10}) scale(${0.2 + 0.8 * drop})`} opacity={drop}>
            {/* petals unfold around the drop: gold + olive, like the event mark */}
            {Array.from({ length: 10 }).map((_, i) => {
              const p = interpolate(f, [26 + i * 1.6, 46 + i * 1.6], [0, 1], { ...clamp, easing: ease });
              const ang = i * 36;
              // petals sit close around the drop (like the event mark) and are larger
              return <path key={i} d={LEAF} transform={`rotate(${ang + (1 - p) * 40}) translate(0 ${-112 - (1 - p) * 30}) scale(${1.3 * p})`} fill={i % 2 ? "url(#go)" : "url(#gl)"} opacity={p} />;
            })}
            <g filter="url(#bloom)"><path d={DROP} fill="url(#gd)" /></g>
            <path d="M -30 -40 C -48 -6, -44 20, -30 40" stroke="#FFF6DD" strokeWidth="6" fill="none" strokeLinecap="round" opacity="0.55" />
            <g clipPath="url(#dc)"><rect x={-90 + shimmer * 120} y="-130" width="60" height="260" fill="url(#sh)" transform="rotate(20)" /></g>
          </g>
        </g>
      </svg>
    </AbsoluteFill>
  );
};
