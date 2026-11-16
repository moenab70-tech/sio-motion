// Floating depth particles (bokeh). Deterministic (seeded), transparent background.
import React from "react";
import { AbsoluteFill, interpolate, random, useVideoConfig } from "remotion";
import { defaultPalette } from "../config/brand";

export type ParticlesProps = {
  count?: number; // 10–120
  intensity?: number; // 0–1 opacity scale
  speed?: number; // drift speed multiplier
  colors?: string[];
  seed?: string;
  frame: number; // pass the (speed-scaled) frame from useFx
  durationInFrames: number;
};

export const Particles: React.FC<ParticlesProps> = ({ count = 50, intensity = 0.5, speed = 1, colors = ["#FFFFFF", defaultPalette.accent], seed = "sio", frame, durationInFrames }) => {
  const { width, height } = useVideoConfig();
  const fade = interpolate(frame, [0, 20, durationInFrames - 20, durationInFrames], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ overflow: "hidden", pointerEvents: "none" }}>
      {Array.from({ length: Math.round(count) }).map((_, i) => {
        const z = random(`${seed}-z-${i}`); // 0 far … 1 near
        const size = 3 + z * 9;
        const travel = (0.15 + z * 0.6) * speed * frame * 1.4;
        const y = (((random(`${seed}-y-${i}`) * (height + 100) - travel) % (height + 100)) + height + 100) % (height + 100) - 50;
        const x = random(`${seed}-x-${i}`) * width + Math.sin(frame / 40 + i) * 12 * z;
        const color = colors[i % colors.length];
        const opacity = (0.12 + z * 0.45) * intensity * fade;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              background: `radial-gradient(circle, ${color} 0%, ${color} 35%, transparent 70%)`,
              opacity,
              filter: `blur(${(1 - z) * 2.5}px)`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
