import React from "react";
import { AbsoluteFill, Img, interpolate, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Logo } from "../../lib/Logo";
import { PartnerLogo } from "../dams-2026/PartnerLogo";
import { DAM_LAYOUT as L } from "../dams-2026/config";
import type { SceneMedia } from "./data";

// Shared pieces for the Riyadh dams report. Same look as the approved DamRainfallReport
// (logos = equal circles, no plate; SIO left, MEWA right) — imported, not modified.

export type SceneProps = {
  durationInSeconds: number;
  /** true = no footage / shade → text & graphics only, for ProRes 4444 alpha export */
  transparent?: boolean;
  /** hide the logo row (e.g. when the master video draws it once on top) */
  showLogos?: boolean;
};

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const HeaderLogos: React.FC<{ opacity?: number }> = ({ opacity = 1 }) => (
  <div
    style={{
      position: "absolute",
      top: L.safeTop,
      left: L.safeSide,
      right: L.safeSide,
      display: "flex",
      flexDirection: "row-reverse",
      justifyContent: "space-between",
      alignItems: "center",
      direction: "ltr",
      opacity,
    }}
  >
    <PartnerLogo id="mewa" part="emblem" height={L.logoCircle} />
    <Logo form="emblem" variant="color" background="light" height={L.logoCircle} />
  </div>
);

/** Real footage or a still photo, reframed to 9:16 with a slow push-in (photos: pan & zoom).
 *  Optional darkening/blur for graphic scenes. */
export const Footage: React.FC<{ media: SceneMedia; frames: number; dim?: number; blur?: number }> = ({ media, frames, dim = 0, blur = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = interpolate(frame, [0, frames], [0, 1], clamp);
  const isImage = media.kind === "image";
  const [z0, z1] = media.zoom ?? (isImage ? [1.04, 1.14] : [1, 1.06]);
  const fx = interpolate(t, [0, 1], [media.focusX ?? 0.5, media.panToX ?? media.focusX ?? 0.5]);
  const fy = interpolate(t, [0, 1], [media.focusY ?? 0.5, media.panToY ?? media.focusY ?? 0.5]);
  const style: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    objectPosition: `${fx * 100}% ${fy * 100}%`,
    transform: `scale(${interpolate(t, [0, 1], [z0, z1]) + blur * 0.01})`,
    transformOrigin: `${fx * 100}% ${fy * 100}%`,
    filter: blur ? `blur(${blur}px)` : undefined,
  };
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      {isImage ? (
        <Img src={staticFile(media.src)} style={style} />
      ) : (
        <OffthreadVideo src={staticFile(media.src)} trimBefore={Math.round((media.from ?? 0) * fps)} volume={media.volume ?? 0} style={style} />
      )}
      {dim ? <AbsoluteFill style={{ backgroundColor: `rgba(2,22,44,${dim})` }} /> : null}
    </AbsoluteFill>
  );
};

/** Number + unit in RTL order (number first = right), digits isolated LTR. */
export const Quantity: React.FC<{ text: string; unit: string; unitScale?: number }> = ({ text, unit, unitScale = 0.5 }) => (
  <span style={{ unicodeBidi: "isolate", whiteSpace: "nowrap" }}>
    <bdi dir="ltr">{text}</bdi>
    <span style={{ fontSize: `${unitScale}em`, marginInlineStart: "0.3em" }}>{unit}</span>
  </span>
);
