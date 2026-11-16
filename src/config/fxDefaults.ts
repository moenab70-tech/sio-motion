// Default content for FX compositions (FX folder in Studio). Same editing rules as defaults.ts.
import * as D from "./defaults";
import type { FxTitleProps } from "../fx/FxTitle";
import type { Bars3DProps } from "../fx/Bars3D";
import type { FxEnhancedProps } from "../fx/FxEnhanced";
import type { FxScenesProps } from "../fx/FxScenes";
import type { Depth3DProps } from "../fx/Depth3D";
import type { LightLeakLayerProps } from "../fx/LightLeak";
import type { ParticlesLayerProps } from "../fx/ParticlesLayer";

const titleText = { eyebrow: D.cinematicTitle.eyebrow, title: D.cinematicTitle.title, subtitle: D.cinematicTitle.subtitle };

export const fxTitleRise: FxTitleProps = { durationInSeconds: 6, style: "rise", align: "center", ...titleText };
export const fxTitleFocus: FxTitleProps = { durationInSeconds: 6, style: "focus", align: "center", ...titleText, titleSize: 108, logo: { background: "dark", height: 230 }, fx: { particles: true } };
export const fxTitleSweep: FxTitleProps = { durationInSeconds: 6, style: "sweep", align: "start", ...titleText };

export const fxBars3D: Bars3DProps = {
  durationInSeconds: 8,
  camera: "push",
  heading: "نمو المؤشر خلال خمس سنوات",
  items: [
    { label: "2022", value: 41 },
    { label: "2023", value: 55 },
    { label: "2024", value: 63 },
    { label: "2025", value: 74 },
    { label: "2026", value: 88, suffix: "%" },
  ],
  fx: { particles: true, intensity: 0.4 },
};

export const fxDepth3D: Depth3DProps = { durationInSeconds: 8, fx: { intensity: 0.5 } };
export const fxParticles: ParticlesLayerProps = { durationInSeconds: 8, count: 60, fx: { intensity: 0.5 } };
export const fxLightLeak: LightLeakLayerProps = { durationInSeconds: 4, hueShift: 0, fx: { intensity: 0.45 } };

export const fxStatRow: FxEnhancedProps = { scene: { template: "StatCounter", props: { ...D.statRow } }, layers: { depth3D: true, particles: true }, fx: { intensity: 0.45 } };
export const fxInfographic: FxEnhancedProps = { scene: { template: "InfographicCards", props: { ...D.infographic } }, layers: { particles: true }, fx: { intensity: 0.45 } };

export const fxScenes: FxScenesProps = {
  transition: ["brandWipe", "blurDissolve", "brandWipe"],
  transitionSeconds: 1.1,
  fx: { intensity: 0.5 },
  scenes: [
    { template: "FxTitle", props: { ...fxTitleRise } },
    { template: "StatCounter", props: { ...D.statRow } },
    { template: "Bars3D", props: { ...fxBars3D, fx: { intensity: 0.4 } } },
    { template: "ProjectCard", props: { ...D.projectWithLogo } },
  ],
};
