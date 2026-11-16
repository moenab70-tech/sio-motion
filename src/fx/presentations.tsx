// FX 5 · Scene transitions for @remotion/transitions, designed for TRANSPARENT scenes:
// the exiting scene is masked out complementarily, so two overlays never show on top of each other.
import React from "react";
import { AbsoluteFill } from "remotion";
import type { TransitionPresentation, TransitionPresentationComponentProps } from "@remotion/transitions";
import { defaultPalette } from "../config/brand";

type BrandWipeProps = { rtl: boolean; feather: number; lineColor: string; intensity: number };

const BrandWipeComponent: React.FC<TransitionPresentationComponentProps<BrandWipeProps>> = ({ children, presentationProgress: p, presentationDirection, passedProps }) => {
  const { rtl, feather, lineColor, intensity } = passedProps;
  const edge = p * (100 + feather) - feather; // % from the start side
  const side = rtl ? "to left" : "to right";
  const entering = presentationDirection === "entering";
  const mask = entering
    ? `linear-gradient(${side}, black ${edge}%, transparent ${edge + feather}%)`
    : `linear-gradient(${side}, transparent ${edge}%, black ${edge + feather}%)`;
  const lineX = edge + feather / 2;
  const lineOpacity = Math.sin(Math.PI * p) * (0.4 + 0.6 * intensity);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ maskImage: mask, WebkitMaskImage: mask }}>{children}</AbsoluteFill>
      {entering && (
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            [rtl ? "right" : "left"]: `${lineX}%`,
            width: 3,
            background: lineColor,
            boxShadow: `0 0 ${20 + 30 * intensity}px ${lineColor}`,
            opacity: lineOpacity,
          }}
        />
      )}
    </AbsoluteFill>
  );
};

/** Soft feathered wipe with a thin accent light line, moving from the reading start side. */
export const brandWipe = (props: Partial<BrandWipeProps> = {}): TransitionPresentation<BrandWipeProps> => ({
  component: BrandWipeComponent,
  props: { rtl: true, feather: 18, lineColor: defaultPalette.accent, intensity: 0.5, ...props },
});

type BlurDissolveProps = { intensity: number };

const BlurDissolveComponent: React.FC<TransitionPresentationComponentProps<BlurDissolveProps>> = ({ children, presentationProgress: p, presentationDirection, passedProps }) => {
  const k = presentationDirection === "entering" ? 1 - p : p; // 0 = fully visible
  const blur = k * (6 + 14 * passedProps.intensity);
  const scale = presentationDirection === "entering" ? 1 + k * 0.03 : 1 - k * 0.02;
  return <AbsoluteFill style={{ opacity: 1 - k, filter: blur > 0.05 ? `blur(${blur}px)` : undefined, transform: `scale(${scale})` }}>{children}</AbsoluteFill>;
};

/** Defocus out → focus in (depth-of-field style dissolve). */
export const blurDissolve = (props: Partial<BlurDissolveProps> = {}): TransitionPresentation<BlurDissolveProps> => ({
  component: BlurDissolveComponent,
  props: { intensity: 0.5, ...props },
});
