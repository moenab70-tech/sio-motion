// «من فكرة إلى إنجاز» v2 — 20 s animated opening (independent composition; the approved film is untouched).
// Quality rules (v2): every plate is shown 1:1 (no zoom, no overscan); motion comes from inside the picture —
// puppet-warped characters (Blender), Grease Pencil line work (Blender), light, water, mist, particles (Remotion).
import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, random, Sequence, staticFile, useCurrentFrame } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Backdrop } from "../parts";
import { SHOTS, shotStart, type ShotId } from "./timing";
import { Shot1B } from "./shots/Shot1B";
import { Shot2B } from "./shots/Shot2B";
import { Shot3B } from "./shots/Shot3B";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Blender PNG sequence of a shot (frames are 1-based on disk), rendered 1:1 at 1920×1080. */
export const RenderedShot: React.FC<{ id: ShotId; len: number; children?: React.ReactNode }> = ({ id, len, children }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#060D18" }}>
      <Img src={staticFile(`media/opening/render/${id}/f_${String(Math.min(len, Math.max(1, f + 1))).padStart(4, "0")}.png`)} style={{ width: 1920, height: 1080 }} />
      {children}
    </AbsoluteFill>
  );
};

/** Floating dust in a light beam (screen-space region). */
export const Dust: React.FC<{ x: number; y: number; w: number; h: number; n?: number; seed: string; opacity?: number }> = ({ x, y, w, h, n = 40, seed, opacity = 0.5 }) => {
  const f = useCurrentFrame();
  return (
    <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, mixBlendMode: "screen" }}>
      {Array.from({ length: n }).map((_, i) => {
        const px = x + random(`${seed}x${i}`) * w + Math.sin(f / 40 + i) * 8;
        const py = y + ((random(`${seed}y${i}`) * h - f * (0.15 + 0.35 * random(`${seed}s${i}`))) % h + h) % h;
        return <circle key={i} cx={px} cy={py} r={0.8 + random(`${seed}r${i}`) * 1.8} fill="#F5D9A0" opacity={opacity * (0.3 + 0.7 * random(`${seed}o${i}`))} />;
      })}
    </svg>
  );
};

/** 1A: the dusk sky in the window slowly deepens + the lamp breathes. */
const Dusk: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const k = interpolate(f, [0, len], [0, 1], clamp);
  return (
    <>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 34% 30% at 34% 46%, rgba(255,205,130,0.16), rgba(0,0,0,0) 70%)", mixBlendMode: "screen", opacity: 0.8 + 0.2 * Math.sin(f / 6) }} />
      <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(10,22,50,${0.18 * k}), rgba(10,22,50,0) 55%)`, mixBlendMode: "multiply" }} />
    </>
  );
};

/** 4A: breathing sun bloom + glints on the water; the last second dissolves into the film's own backdrop. */
const SunsetToFilm: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [len - 34, len - 4], [0, 1], { ...clamp, easing: Easing.inOut(Easing.quad) });
  return (
    <>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, mixBlendMode: "screen" }}>
        <defs><radialGradient id="sun"><stop offset="0" stopColor="#FFF1CC" stopOpacity="0.9" /><stop offset="0.25" stopColor="#FFC977" stopOpacity="0.45" /><stop offset="1" stopColor="#FF9F3D" stopOpacity="0" /></radialGradient></defs>
        <circle cx={1530} cy={372} r={170 + 14 * Math.sin(f / 9)} fill="url(#sun)" opacity={0.75} />
        {Array.from({ length: 28 }).map((_, i) => {
          const x = 1380 + random(`gx${i}`) * 300 + (random(`gd${i}`) - 0.5) * 8 * Math.sin(f / 4 + i);
          const y = 420 + random(`gy${i}`) * 520;
          const tw = Math.max(0, Math.sin(f / (3 + random(`gt${i}`) * 4) + i));
          return <circle key={i} cx={x} cy={y} r={1.5 + random(`gr${i}`) * 2.5} fill="#FFF3D6" opacity={tw * 0.8} />;
        })}
      </svg>
      <AbsoluteFill style={{ opacity: out }}><Backdrop frame={0} total={1} particles={0} /></AbsoluteFill>
    </>
  );
};

const FilmLook: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 75% 70% at 50% 48%, rgba(0,0,0,0) 55%, rgba(4,8,16,0.5) 100%)" }} />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: 0.06, mixBlendMode: "overlay" }}>
        <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 24} /></filter>
        <rect width="1920" height="1080" filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};

const FADE = (len: number) => <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: len, easing: Easing.bezier(0.45, 0, 0.25, 1) })} />;

export const OpeningFilm: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 12], [1, 0], clamp);
  const look = interpolate(frame, [560, 590], [1, 0], clamp); // the last frame equals the film's first frame
  const S = SHOTS;
  const dawnAt = shotStart["3A"]; // centre of the 2B → 3A dawn flare
  return (
    <AbsoluteFill style={{ background: "#060D18", filter: look > 0 ? `contrast(${1 + 0.04 * look}) saturate(${1 - 0.04 * look})` : undefined }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={S["1A"].len} name="1A · المكتب عند الغروب">
          <RenderedShot id="1A" len={S["1A"].len}><Dusk len={S["1A"].len} /><Dust x={560} y={420} w={420} h={420} seed="1a" /></RenderedShot>
        </TransitionSeries.Sequence>
        <TransitionSeries.Sequence durationInFrames={S["1B"].len} name="1B · الفكرة ترتسم"><Shot1B len={S["1B"].len} /></TransitionSeries.Sequence>
        {FADE(S["1B"].out)}
        <TransitionSeries.Sequence durationInFrames={S["2A"].len} name="2A · منتصف الليل">
          <RenderedShot id="2A" len={S["2A"].len}><Dust x={180} y={260} w={420} h={520} n={26} seed="2a" opacity={0.35} /></RenderedShot>
        </TransitionSeries.Sequence>
        <TransitionSeries.Sequence durationInFrames={S["2B"].len} name="2B · محاولات تتراكم"><Shot2B len={S["2B"].len} /></TransitionSeries.Sequence>
        {FADE(S["2B"].out)}
        <TransitionSeries.Sequence durationInFrames={S["3A"].len} name="3A · الفريق عند الفجر"><RenderedShot id="3A" len={S["3A"].len} /></TransitionSeries.Sequence>
        {FADE(S["3A"].out)}
        <TransitionSeries.Sequence durationInFrames={S["3B"].len} name="3B · من الرسم إلى المشروع"><Shot3B len={S["3B"].len} /></TransitionSeries.Sequence>
        <TransitionSeries.Sequence durationInFrames={S["4A"].len} name="4A · لحظة الفخر → الفيلم">
          <RenderedShot id="4A" len={S["4A"].len}><SunsetToFilm len={S["4A"].len} /></RenderedShot>
        </TransitionSeries.Sequence>
      </TransitionSeries>
      {/* dawn light flare across the night → dawn transition (warm scene, Screen blend, behind no text) */}
      <Sequence from={dawnAt - 26} durationInFrames={52} name="dawn flare">
        <DawnFlare />
      </Sequence>
      <AbsoluteFill style={{ opacity: look }}><FilmLook /></AbsoluteFill>
      <AbsoluteFill style={{ background: "#000", opacity: fadeIn }} />
    </AbsoluteFill>
  );
};

const DawnFlare: React.FC = () => {
  const f = useCurrentFrame();
  // warm sunrise flare sweeping from the window side (the LightLeak effect tinted the scene olive — not used)
  const env = Math.sin(Math.PI * Math.min(1, f / 52));
  const x = 75 - 30 * (f / 52);
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.7 * env }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 55% 75% at ${x}% 40%, rgba(255,214,150,0.85), rgba(255,170,90,0.35) 40%, rgba(0,0,0,0) 75%)` }} />
      <AbsoluteFill style={{ background: `linear-gradient(105deg, rgba(0,0,0,0) ${x - 30}%, rgba(255,226,180,0.35) ${x - 8}%, rgba(0,0,0,0) ${x + 12}%)` }} />
    </AbsoluteFill>
  );
};
