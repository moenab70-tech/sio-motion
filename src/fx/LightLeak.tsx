// FX 3 · Light leak layer from @remotion/effects (WebGL). Opaque by nature:
// deliver as a separate layer and set its Blend Mode to "Screen" or "Add" in Premiere.
import React from "react";
import { AbsoluteFill, Solid, interpolate, useVideoConfig } from "remotion";
import { lightLeak } from "@remotion/effects";
import type { Fx } from "../config/fx";
import { useFx } from "./useFx";

export type LightLeakLayerProps = {
  durationInSeconds: number;
  hueShift?: number; // 0–360; 0 = warm gold/amber
  seed?: number;
  fx?: Partial<Fx>;
};

export const LightLeakLayer: React.FC<LightLeakLayerProps> = ({ durationInSeconds, hueShift = 0, seed = 3, fx: fxProp }) => {
  const fx = useFx(fxProp);
  const { width, height, fps } = useVideoConfig();
  const total = durationInSeconds * fps * fx.speed;
  const progress = interpolate(fx.frame, [0, total], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: fx.intensity }}>
      <Solid width={width} height={height} color="#000000" effects={[lightLeak({ progress, hueShift, seed })]} />
    </AbsoluteFill>
  );
};
