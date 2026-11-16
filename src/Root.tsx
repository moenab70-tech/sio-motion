import React from "react";
import { Composition, Folder } from "remotion";
import { VIDEO } from "./config/brand";
import * as D from "./config/defaults";
import type { CommonProps } from "./lib/brand";
import { StatCounter } from "./templates/StatCounter";
import { CinematicTitle } from "./templates/CinematicTitle";
import { LowerThird } from "./templates/LowerThird";
import { InfographicCards } from "./templates/InfographicCards";
import { ProjectCard } from "./templates/ProjectCard";
import { SectionTransition } from "./templates/SectionTransition";
import { Showreel, showreelDuration } from "./preview/Showreel";
import { LogoBoard } from "./preview/LogoBoard";
import * as FX from "./config/fxDefaults";
import { FxTitle } from "./fx/FxTitle";
import { Bars3D } from "./fx/Bars3D";
import { Depth3D } from "./fx/Depth3D";
import { ParticlesLayer } from "./fx/ParticlesLayer";
import { LightLeakLayer } from "./fx/LightLeak";
import { FxEnhanced, type FxEnhancedProps } from "./fx/FxEnhanced";
import { FxScenes, fxScenesDuration, type FxScenesProps } from "./fx/FxScenes";
import { FxCompare, fxCompareDuration } from "./preview/FxCompare";

// Composition length follows the `durationInSeconds` prop.
const byDuration = ({ props }: { props: Pick<CommonProps, "durationInSeconds"> }) => ({
  durationInFrames: Math.max(1, Math.round(props.durationInSeconds * VIDEO.fps)),
});

const byScene = ({ props }: { props: FxEnhancedProps }) => ({ durationInFrames: Math.round(props.scene.props.durationInSeconds * VIDEO.fps) });
const byScenes = ({ props }: { props: FxScenesProps }) => ({ durationInFrames: fxScenesDuration(props, VIDEO.fps) });

// No backgrounds anywhere in the templates = transparent alpha in ProRes 4444.
const base = { ...VIDEO, durationInFrames: 1 } as const;

export const RemotionRoot: React.FC = () => (
  <>
    <Folder name="Statistics">
      <Composition id="Stat-Single" component={StatCounter} defaultProps={D.statSingle} calculateMetadata={byDuration} {...base} />
      <Composition id="Stat-Row" component={StatCounter} defaultProps={D.statRow} calculateMetadata={byDuration} {...base} />
    </Folder>
    <Folder name="Titles">
      <Composition id="Title-Cinematic" component={CinematicTitle} defaultProps={D.cinematicTitle} calculateMetadata={byDuration} {...base} />
      <Composition id="LowerThird-Panel" component={LowerThird} defaultProps={D.lowerThird} calculateMetadata={byDuration} {...base} />
      <Composition id="LowerThird-Minimal" component={LowerThird} defaultProps={{ ...D.lowerThird, variant: "minimal" }} calculateMetadata={byDuration} {...base} />
    </Folder>
    <Folder name="Infographics">
      <Composition id="Infographic-Rings" component={InfographicCards} defaultProps={D.infographic} calculateMetadata={byDuration} {...base} />
      <Composition id="Infographic-Bars" component={InfographicCards} defaultProps={{ ...D.infographic, indicator: "bar" }} calculateMetadata={byDuration} {...base} />
    </Folder>
    <Folder name="Projects">
      <Composition id="Project-Card" component={ProjectCard} defaultProps={D.projectCard} calculateMetadata={byDuration} {...base} />
      <Composition id="Project-Wide" component={ProjectCard} defaultProps={{ ...D.projectCard, layout: "wide" }} calculateMetadata={byDuration} {...base} />
    </Folder>
    <Folder name="Transitions">
      <Composition id="Transition-Panels" component={SectionTransition} defaultProps={D.transitionPanels} calculateMetadata={byDuration} {...base} />
      <Composition id="Transition-Sweep" component={SectionTransition} defaultProps={D.transitionSweep} calculateMetadata={byDuration} {...base} />
      <Composition id="Transition-Shutter" component={SectionTransition} defaultProps={D.transitionShutter} calculateMetadata={byDuration} {...base} />
    </Folder>
    <Folder name="Brand">
      <Composition id="Logo-Board" component={LogoBoard} {...VIDEO} durationInFrames={60} />
      <Composition id="Title-WithLogo" component={CinematicTitle} defaultProps={D.titleWithLogo} calculateMetadata={byDuration} {...base} />
      <Composition id="LowerThird-WithLogo" component={LowerThird} defaultProps={D.lowerThirdWithLogo} calculateMetadata={byDuration} {...base} />
      <Composition id="Project-WithLogo" component={ProjectCard} defaultProps={D.projectWithLogo} calculateMetadata={byDuration} {...base} />
      <Composition id="Project-Wide-WithLogo" component={ProjectCard} defaultProps={D.projectWideWithLogo} calculateMetadata={byDuration} {...base} />
    </Folder>
    <Folder name="FX">
      <Composition id="FX-Title-Rise" component={FxTitle} defaultProps={FX.fxTitleRise} calculateMetadata={byDuration} {...base} />
      <Composition id="FX-Title-Focus" component={FxTitle} defaultProps={FX.fxTitleFocus} calculateMetadata={byDuration} {...base} />
      <Composition id="FX-Title-Sweep" component={FxTitle} defaultProps={FX.fxTitleSweep} calculateMetadata={byDuration} {...base} />
      <Composition id="FX-Bars-3D" component={Bars3D} defaultProps={FX.fxBars3D} calculateMetadata={byDuration} {...base} />
      <Composition id="FX-Stat-Row" component={FxEnhanced} defaultProps={FX.fxStatRow} calculateMetadata={byScene} {...base} />
      <Composition id="FX-Infographic" component={FxEnhanced} defaultProps={FX.fxInfographic} calculateMetadata={byScene} {...base} />
      <Composition id="FX-Scenes" component={FxScenes} defaultProps={FX.fxScenes} calculateMetadata={byScenes} {...base} />
      <Composition id="FX-Depth-3D" component={Depth3D} defaultProps={FX.fxDepth3D} calculateMetadata={byDuration} {...base} />
      <Composition id="FX-Particles" component={ParticlesLayer} defaultProps={FX.fxParticles} calculateMetadata={byDuration} {...base} />
      <Composition id="FX-LightLeak" component={LightLeakLayer} defaultProps={FX.fxLightLeak} calculateMetadata={byDuration} {...base} />
      <Composition id="FX-Compare" component={FxCompare} {...VIDEO} durationInFrames={fxCompareDuration} />
    </Folder>
    <Folder name="Preview">
      <Composition id="Showreel" component={Showreel} defaultProps={{ showBackground: true }} {...VIDEO} durationInFrames={showreelDuration} />
    </Folder>
  </>
);
