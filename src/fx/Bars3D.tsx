// FX 4 + 6 · 3D animated bar chart with a slow camera move. Transparent background.
// Values/labels are crisp HTML placed with the same camera maths, so numbers stay sharp and on-brand.
import React from "react";
import { AbsoluteFill, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { PerspectiveCamera, Vector3 } from "three";
import type { Fx } from "../config/fx";
import { useTemplate, type CommonProps } from "../lib/brand";
import { AnimatedNumber } from "../lib/AnimatedNumber";
import { EASE, mix, ramp } from "../lib/motion";
import { localizeDigits, percentSign } from "../lib/numbers";
import { Particles } from "./Particles";
import { useFx } from "./useFx";

export type Bars3DItem = { label: string; value: number; suffix?: string; decimals?: number; compact?: boolean };

export type Bars3DProps = CommonProps & {
  heading?: string;
  items: Bars3DItem[]; // 2–7 comparable values
  camera: "push" | "orbit" | "static";
  highlightIndex?: number; // bar drawn in accent colour (default: largest)
  fx?: Partial<Fx>;
};

const FOV = 32;
const TARGET = new Vector3(0, 2.1, 0);

const cameraAt = (p: number, mode: Bars3DProps["camera"], dir: number): [number, number, number] => {
  if (mode === "static") return [0, 3.2, 12.5];
  if (mode === "orbit") {
    const a = mix(0.55, 0.12, p) * dir;
    const r = mix(14, 12.5, p);
    return [Math.sin(a) * r, mix(5, 3.2, p), Math.cos(a) * r];
  }
  return [mix(1.2 * dir, 0, p), mix(5.5, 3.2, p), mix(17, 12.5, p)]; // push-in
};

const CameraRig: React.FC<{ pos: [number, number, number] }> = ({ pos }) => {
  const camera = useThree((st) => st.camera);
  camera.position.set(...pos);
  camera.lookAt(TARGET);
  camera.updateMatrixWorld();
  return null;
};

export const Bars3D: React.FC<Bars3DProps> = (props) => {
  const t = useTemplate(props);
  const fx = useFx(props.fx);
  const { width, height } = useVideoConfig();
  const { palette: c, font, digits, s, total } = t;
  const f = fx.frame;
  const out = 1 - ramp(f, total * fx.speed - s(t.timing.exit), s(t.timing.exit), EASE.in);
  const dir = t.rtl ? -1 : 1;

  const items = props.items.slice(0, 7);
  const max = Math.max(...items.map((i) => i.value), 1);
  const hi = props.highlightIndex ?? items.findIndex((i) => i.value === max);
  const gap = 1.65;
  // RTL: first item on the right
  const xOf = (i: number) => (i - (items.length - 1) / 2) * gap * -dir;
  const maxH = 3.1;

  const camP = ramp(f, 0, s(3.2), EASE.inOut);
  const pos = cameraAt(camP, props.camera, dir);
  const grow = (i: number) => ramp(f, s(0.5 + i * t.timing.stagger * 1.6), s(1.6), EASE.count);

  // same camera, used to place HTML labels exactly over the 3D bars
  const cam = new PerspectiveCamera(FOV, width / height, 0.1, 100);
  cam.position.set(...pos);
  cam.lookAt(TARGET);
  cam.updateMatrixWorld();
  const project = (v: Vector3) => {
    const p = v.clone().project(cam);
    return { x: ((p.x + 1) / 2) * width, y: ((1 - p.y) / 2) * height };
  };

  const headIn = ramp(f, 0, s(0.8));

  return (
    <AbsoluteFill style={{ direction: t.dir, fontFamily: font.body }}>
      {fx.particles && <Particles frame={f} durationInFrames={total * fx.speed} intensity={fx.intensity * 0.8} />}
      <AbsoluteFill style={{ opacity: out }}>
        <ThreeCanvas width={width} height={height} gl={{ alpha: true, antialias: true, premultipliedAlpha: false }} camera={{ fov: FOV, near: 0.1, far: 100 }}>
          <CameraRig pos={pos} />
          <ambientLight intensity={0.55} />
          <directionalLight position={[4 * dir, 8, 7]} intensity={1.5} />
          <directionalLight position={[-5 * dir, 3, -6]} intensity={0.35 + 0.5 * fx.intensity} color={c.accent} />
          {/* base plate */}
          <mesh position={[0, -0.06, 0]}>
            <boxGeometry args={[items.length * gap + 0.6, 0.06, 1.8]} />
            <meshStandardMaterial color="#050A12" transparent opacity={0.55} roughness={1} metalness={0} />
          </mesh>
          {items.map((it, i) => {
            const h = Math.max(0.02, (it.value / max) * maxH * grow(i));
            return (
              <mesh key={i} position={[xOf(i), h / 2, 0]}>
                <boxGeometry args={[1.05, h, 1.05]} />
                <meshStandardMaterial color={i === hi ? c.accent : c.secondary} emissive={i === hi ? c.accent : c.secondary} emissiveIntensity={0.18} roughness={0.45} metalness={0.05} />
              </mesh>
            );
          })}
        </ThreeCanvas>

        {/* crisp HTML labels following the 3D bars */}
        {items.map((it, i) => {
          const g = grow(i);
          const h = (it.value / max) * maxH * g;
          const top = project(new Vector3(xOf(i), h + 0.25, 0));
          const base = project(new Vector3(xOf(i), -0.2, 1.1));
          const suffix = it.suffix === "%" ? percentSign(digits) : it.suffix;
          return (
            <React.Fragment key={i}>
              <div style={{ position: "absolute", left: top.x, top: top.y, transform: "translate(-50%, -100%)", fontFamily: font.display, fontWeight: 700, fontSize: 46, color: c.text, opacity: Math.min(1, g * 3), textShadow: `0 4px 20px ${c.shadow}`, whiteSpace: "nowrap" }}>
                <AnimatedNumber value={it.value} progress={g} digits={digits} decimals={it.decimals} compact={it.compact} suffix={suffix} suffixColor={c.accent} />
              </div>
              <div style={{ position: "absolute", left: base.x, top: base.y, transform: "translate(-50%, 0)", fontSize: 28, fontWeight: 600, color: c.textMuted, opacity: Math.min(1, g * 2), whiteSpace: "nowrap", textShadow: `0 2px 12px ${c.shadow}` }}>
                {localizeDigits(it.label, digits)}
              </div>
            </React.Fragment>
          );
        })}

        {props.heading && (
          <div style={{ position: "absolute", top: 70, left: 0, right: 0, textAlign: "center", fontFamily: font.display, fontSize: 54, fontWeight: 700, color: c.text, opacity: headIn, transform: `translateY(${(1 - headIn) * 20}px)`, textShadow: `0 6px 30px ${c.shadow}` }}>
            {localizeDigits(props.heading, digits)}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
