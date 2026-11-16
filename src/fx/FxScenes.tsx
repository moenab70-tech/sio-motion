// FX 5 · Multi-scene sequence with cinematic transitions between existing templates.
import React from "react";
import { useVideoConfig } from "remotion";
import { TransitionSeries, linearTiming, type TransitionPresentation } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import type { Fx } from "../config/fx";
import { EASE } from "../lib/motion";
import { blurDissolve, brandWipe } from "./presentations";
import { renderScene, type Scene } from "./registry";
import { defaultFx } from "../config/fx";

export type FxTransitionName = "brandWipe" | "blurDissolve" | "slide" | "fade";

export type FxScenesProps = {
  scenes: Scene[];
  transition: FxTransitionName | FxTransitionName[]; // one for all, or one per gap
  transitionSeconds?: number;
  rtl?: boolean;
  fx?: Partial<Fx>;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const presentationFor = (name: FxTransitionName, rtl: boolean, intensity: number): TransitionPresentation<any> => {
  switch (name) {
    case "brandWipe":
      return brandWipe({ rtl, intensity });
    case "blurDissolve":
      return blurDissolve({ intensity });
    case "slide":
      return slide({ direction: rtl ? "from-left" : "from-right" });
    default:
      return fade();
  }
};

/** Total length = sum of scenes − overlaps. Used by calculateMetadata. */
export const fxScenesDuration = (p: FxScenesProps, fps: number) => {
  const tr = Math.round((p.transitionSeconds ?? 1) * fps / (p.fx?.speed ?? defaultFx.speed));
  return p.scenes.reduce((a, sc) => a + Math.round(sc.props.durationInSeconds * fps), 0) - tr * Math.max(0, p.scenes.length - 1);
};

export const FxScenes: React.FC<FxScenesProps> = ({ scenes, transition, transitionSeconds = 1, rtl = true, fx }) => {
  const { fps } = useVideoConfig();
  const intensity = fx?.intensity ?? defaultFx.intensity;
  const trFrames = Math.round((transitionSeconds * fps) / (fx?.speed ?? defaultFx.speed));
  return (
    <TransitionSeries>
      {scenes.map((sc, i) => {
        const name = Array.isArray(transition) ? transition[(i - 1) % transition.length] : transition;
        return (
          <React.Fragment key={i}>
            {i > 0 && <TransitionSeries.Transition presentation={presentationFor(name, rtl, intensity)} timing={linearTiming({ durationInFrames: trFrames, easing: EASE.inOut })} />}
            <TransitionSeries.Sequence durationInFrames={Math.round(sc.props.durationInSeconds * fps)}>{renderScene(sc)}</TransitionSeries.Sequence>
          </React.Fragment>
        );
      })}
    </TransitionSeries>
  );
};
