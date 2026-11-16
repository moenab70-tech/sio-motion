// Institutional + experimental (+ English) presets per style. Institutional = brand tokens, restrained intensity.
import type { KineticTypeProps } from "../styles/KineticType";
import type { BlueprintProps } from "../styles/Blueprint";
import type { IsometricProps } from "../styles/Isometric";
import type { HolographicProps } from "../styles/Holographic";
import type { ParticleTextProps } from "../styles/ParticleText";
import type { LiquidMorphProps } from "../styles/LiquidMorph";
import type { SplitFlapProps } from "../styles/SplitFlap";
import { AR, EN } from "./samples";

const inst = { mode: "institutional" as const, intensity: 0.45 };
const exp = { mode: "experimental" as const, intensity: 0.9 };
const en = { mode: "institutional" as const, lang: "en" as const, intensity: 0.45 };

export const kinetic = {
  institutional: { ...inst, lines: AR.lines, variant: "rise" } as KineticTypeProps,
  experimental: { ...exp, lines: AR.lines, variant: "scale", typography: { display: "Cairo", weight: 800 } } as KineticTypeProps,
  english: { ...en, lines: EN.lines, variant: "slide", unit: "char" } as KineticTypeProps,
};

export const blueprint = {
  institutional: { ...inst, title: AR.blueprintTitle, callouts: AR.callouts, dimensions: AR.dims, drawingNo: "SIO-DWG-014" } as BlueprintProps,
  experimental: { ...exp, title: AR.blueprintTitle, callouts: AR.callouts, dimensions: AR.dims, drawingNo: "EXP-01" } as BlueprintProps,
  english: { ...en, title: EN.blueprintTitle, callouts: EN.callouts, dimensions: EN.dims, drawingNo: "SIO-DWG-014" } as BlueprintProps,
};

export const isometric = {
  institutional: { ...inst, title: AR.isoTitle, camera: "push" } as IsometricProps,
  experimental: { ...exp, title: AR.isoTitle, camera: "pan" } as IsometricProps,
  english: {
    ...en, title: EN.isoTitle, camera: "push",
    blocks: [
      { x: 0, y: 0, w: 9, d: 2.2, h: 0.35, role: "water", label: "Main canal" },
      { x: 1, y: 3.4, w: 2.4, d: 2.4, h: 2.2, role: "primary", label: "Pump station" },
      { x: 4.2, y: 3.6, w: 1.8, d: 1.8, h: 3.4, role: "structure", label: "Tank" },
      { x: 6.6, y: 3.4, w: 2.2, d: 1.6, h: 1.4, role: "accent", label: "Control centre" },
    ],
  } as IsometricProps,
};

export const holographic = {
  institutional: { ...inst, title: AR.holoTitle, rows: AR.holoRows, gauge: AR.gauge } as HolographicProps,
  experimental: { ...exp, title: AR.holoTitle, rows: AR.holoRows, gauge: AR.gauge } as HolographicProps,
  english: { ...en, title: EN.holoTitle, rows: EN.holoRows, gauge: EN.gauge } as HolographicProps,
};

export const particles = {
  institutional: { ...inst, text: AR.particle, path: "rise" } as ParticleTextProps,
  experimental: { ...exp, text: AR.particle, path: "swirl", particleSize: 3.2 } as ParticleTextProps,
  english: { ...en, text: EN.particle, path: "explode", fontSize: 260 } as ParticleTextProps,
};

export const liquid = {
  institutional: { ...inst, title: AR.liquidTitle, subtitle: AR.liquidSub } as LiquidMorphProps,
  experimental: { ...exp, title: AR.liquidTitle, subtitle: AR.liquidSub, shapes: 6, blobScale: 1.2 } as LiquidMorphProps,
  english: { ...en, title: EN.liquidTitle, subtitle: EN.liquidSub } as LiquidMorphProps,
};

export const splitFlap = {
  institutional: { ...inst, rows: AR.flapRows, counter: AR.counter } as SplitFlapProps,
  experimental: { ...exp, rows: AR.flapRows, counter: AR.counter } as SplitFlapProps,
  english: { ...en, rows: EN.flapRows, counter: EN.counter } as SplitFlapProps,
};
