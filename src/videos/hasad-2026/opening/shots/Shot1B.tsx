// 1B v2 — The idea takes shape. Grease Pencil line work (Blender) draws itself on the paper; the engineer's hand is
// never cut out — only its soft shadow crosses the paper, following the pencil tip, and lifts during the pause.
// Plate and lines are shown 1:1 (no zoom) for full sharpness.
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { LW_1B, tipAt } from "../linework";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const Plate: React.FC<{ src: string; style?: React.CSSProperties }> = ({ src, style }) => (
  // 1920×1088 source shown pixel-for-pixel (4 px trimmed top & bottom)
  <Img src={staticFile(src)} style={{ position: "absolute", left: 0, top: -4, width: 1920, height: 1088, ...style }} />
);
export const LineSeq: React.FC<{ id: string; frames: number; style?: React.CSSProperties }> = ({ id, frames, style }) => {
  const f = useCurrentFrame();
  return <Plate src={`media/opening/lines/${id}/f_${String(Math.min(frames, f + 1)).padStart(4, "0")}.png`} style={style} />;
};

const HAND = { src: "media/opening/layers/hand-fg.png", w: 1080, h: 768, tipX: 1002, tipY: 273, s: 1.05 };

export const Shot1B: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  // shadow follows a slightly smoothed tip (a real hand lags the pencil a little)
  const t0 = tipAt(LW_1B, f + 1), t1 = tipAt(LW_1B, Math.max(1, f - 2));
  const tip = { x: (t0.x * 2 + t1.x) / 3, y: (t0.y * 2 + t1.y) / 3 - 4 };
  const lift = interpolate(f, [44, 49, 54, 58], [0, 1, 1, 0], clamp); // the pause: hand rises, shadow softens and drifts
  const ox = -14 - 46 * lift, oy = 18 + 60 * lift;
  const flicker = 1 + 0.02 * Math.sin(f / 3.1) + 0.012 * Math.sin(f / 1.7);
  const dim = interpolate(f, [len - 16, len], [0, 0.6], clamp);
  return (
    <AbsoluteFill style={{ background: "#0A0705", overflow: "hidden" }}>
      <Plate src="media/opening/assets/P-1B-paper.png" style={{ filter: `brightness(${flicker})` }} />
      <LineSeq id="1B" frames={LW_1B.frames} style={{ mixBlendMode: "multiply" }} />
      {/* the hand's shadow only — soft, lamp from the upper right */}
      <Img src={staticFile(HAND.src)} style={{
        position: "absolute", width: HAND.w * HAND.s, height: HAND.h * HAND.s,
        left: tip.x + ox - HAND.tipX * HAND.s, top: tip.y + oy - HAND.tipY * HAND.s,
        filter: `brightness(0) blur(${16 + 14 * lift}px)`, opacity: 0.34 - 0.1 * lift, mixBlendMode: "multiply",
        transformOrigin: `${HAND.tipX * HAND.s}px ${HAND.tipY * HAND.s}px`, transform: `rotate(${-14 + 4 * lift}deg)`,
      }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 62% 58% at 52% 60%, rgba(255,214,150,0.06), rgba(0,0,0,0.38))" }} />
      <AbsoluteFill style={{ background: `rgba(6,12,26,${dim})` }} />
    </AbsoluteFill>
  );
};
