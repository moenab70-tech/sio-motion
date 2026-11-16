// "After" version of any existing template: the template is rendered UNCHANGED,
// with optional depth layers behind it (3D rings, particles). Effects never cover the content.
import React from "react";
import { AbsoluteFill, useVideoConfig } from "remotion";
import type { Fx } from "../config/fx";
import { Depth3D } from "./Depth3D";
import { Particles } from "./Particles";
import { renderScene, type Scene } from "./registry";
import { useFx } from "./useFx";

export type FxEnhancedProps = {
  scene: Scene;
  layers: { depth3D?: boolean; particles?: boolean };
  fx?: Partial<Fx>;
};

export const FxEnhanced: React.FC<FxEnhancedProps> = ({ scene, layers, fx: fxProp }) => {
  const fx = useFx(fxProp);
  const { fps } = useVideoConfig();
  const total = scene.props.durationInSeconds * fps;
  return (
    <AbsoluteFill>
      {layers.depth3D && <Depth3D durationInSeconds={scene.props.durationInSeconds} fx={{ ...fxProp, intensity: fx.intensity * 0.7 }} />}
      {layers.particles && <Particles frame={fx.frame} durationInFrames={total * fx.speed} intensity={fx.intensity * 0.8} speed={fx.speed} />}
      {renderScene(scene)}
    </AbsoluteFill>
  );
};
