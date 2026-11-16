// FX 7 · Standalone particle layer (transparent) — place under titles in Premiere or inside templates.
import React from "react";
import { useVideoConfig } from "remotion";
import type { Fx } from "../config/fx";
import { Particles } from "./Particles";
import { useFx } from "./useFx";

export type ParticlesLayerProps = { durationInSeconds: number; count?: number; colors?: string[]; seed?: string; fx?: Partial<Fx> };

export const ParticlesLayer: React.FC<ParticlesLayerProps> = ({ durationInSeconds, count, colors, seed, fx: fxProp }) => {
  const fx = useFx(fxProp);
  const { fps } = useVideoConfig();
  return <Particles frame={fx.frame} durationInFrames={durationInSeconds * fps * fx.speed} count={count} colors={colors} seed={seed} intensity={fx.intensity} speed={1} />;
};
