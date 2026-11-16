// FX 4 + 7 · Abstract 3D depth layer: thin brand rings and soft spheres drifting past a slow dolly camera.
// Transparent. Designed to sit BEHIND titles/cards at low intensity — never over information.
import React from "react";
import { AbsoluteFill, interpolate, random, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { defaultPalette } from "../config/brand";
import type { Fx } from "../config/fx";
import { useFx } from "./useFx";

export type Depth3DProps = {
  durationInSeconds: number;
  rings?: number;
  spheres?: number;
  colors?: string[];
  fx?: Partial<Fx>;
};

const Dolly: React.FC<{ z: number; x: number }> = ({ z, x }) => {
  const camera = useThree((st) => st.camera);
  camera.position.set(x, 0, z);
  camera.lookAt(0, 0, z - 10);
  camera.updateMatrixWorld();
  return null;
};

export const Depth3D: React.FC<Depth3DProps> = ({ durationInSeconds, rings = 7, spheres = 18, colors = [defaultPalette.accent, defaultPalette.secondary], fx: fxProp }) => {
  const fx = useFx(fxProp);
  const { width, height, fps } = useVideoConfig();
  const total = durationInSeconds * fps * fx.speed;
  const f = fx.frame;
  const fade = interpolate(f, [0, 25, total - 25, total], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const camZ = interpolate(f, [0, total], [12, 6]);

  return (
    <AbsoluteFill style={{ opacity: fade }}>
      <ThreeCanvas width={width} height={height} gl={{ alpha: true, antialias: true, premultipliedAlpha: false }} camera={{ fov: 40, near: 0.1, far: 60 }}>
        <Dolly z={camZ} x={Math.sin(f / 120) * 0.4} />
        <ambientLight intensity={0.7} />
        <pointLight position={[3, 3, 8]} intensity={40} />
        {Array.from({ length: rings }).map((_, i) => {
          // keep rings to the sides so they never cross the information area
          const x = (random(`rx${i}`) < 0.5 ? -1 : 1) * (3.2 + random(`rx${i}b`) * 3.5);
          const y = (random(`ry${i}`) - 0.5) * 5;
          const z = -2 - random(`rz${i}`) * 14;
          const r = 0.6 + random(`rr${i}`) * 1.6;
          return (
            <mesh key={`r${i}`} position={[x, y, z]} rotation={[0.5 + f * 0.004 * (i % 2 ? 1 : -1), f * 0.006 + i, 0]}>
              <torusGeometry args={[r, 0.018 + 0.02 * random(`rt${i}`), 16, 96]} />
              <meshStandardMaterial color={colors[i % colors.length]} emissive={colors[i % colors.length]} emissiveIntensity={0.55} metalness={0.05} roughness={0.5} transparent opacity={0.15 + 0.45 * fx.intensity} />
            </mesh>
          );
        })}
        {Array.from({ length: spheres }).map((_, i) => {
          const x = (random(`sx${i}`) - 0.5) * 12;
          const y = (random(`sy${i}`) - 0.5) * 7 + Math.sin(f / 60 + i) * 0.1;
          const z = -random(`sz${i}`) * 16;
          return (
            <mesh key={`s${i}`} position={[x, y, z]}>
              <sphereGeometry args={[0.04 + random(`ss${i}`) * 0.08, 16, 16]} />
              <meshStandardMaterial color="#FFFFFF" emissive={colors[i % colors.length]} emissiveIntensity={0.6} transparent opacity={0.2 + 0.5 * fx.intensity} />
            </mesh>
          );
        })}
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
