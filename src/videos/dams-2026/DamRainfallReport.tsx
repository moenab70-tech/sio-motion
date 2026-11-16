import React from "react";
import { AbsoluteFill, Audio, interpolate, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Logo } from "../../lib/Logo";
import { FONT_FAMILIES } from "../../lib/fonts";
import { formatNumber } from "../../lib/numbers";
import { EASE, ramp } from "../../lib/motion";
import { PartnerLogo } from "./PartnerLogo";
import { DAM_LAYOUT as L, DAM_STYLE as S } from "./config";

// ─────────────────────────────────────────────────────────────
// DamRainfallReport — one vertical (1080×1920) video per dam.
// Change the props (data + clips) to make a new dam video; the design stays the same.
// ─────────────────────────────────────────────────────────────

export type DamClip = {
  /** path inside /public, e.g. "media/video/dams/harimla/harimla_2.mp4" */
  src: string;
  /** where to start inside the source clip (seconds) */
  from?: number;
  /** relative length weight (default 1); all clips are scaled to fill `duration` */
  weight?: number;
  /** smart reframe: which part of a landscape frame stays visible (0 = left/top, 1 = right/bottom) */
  focusX?: number;
  focusY?: number;
  /** optional slow pan across the frame: focusX moves to panToX over the clip */
  panToX?: number;
  /** gentle push-in: start → end scale (default 1 → 1.06) */
  zoom?: [number, number];
  /** natural sound volume for this clip (0 = muted) */
  volume?: number;
  /** playback speed (e.g. 0.8 for calmer drone moves) */
  playbackRate?: number;
};

export type DamRainfallReportProps = {
  damName: string;
  governorate: string;
  storageCapacity: number; // m³
  incomingWater: number; // m³
  videoSources: DamClip[];
  duration: number; // seconds
  /** optional licensed background music (path inside /public) */
  music?: { src: string; volume: number } | null;
  /** optional looping ambience under the music (e.g. water flow), path inside /public */
  ambience?: { src: string; volume: number } | null;
  /** "lockup" = full logos, "emblem" = circles only. Both drawn with equal circle size, no backing plate. */
  logoMode?: "lockup" | "emblem";
};

const TRANSITION = 18; // frames of crossfade between shots

/** 0→1 fade-in, hold, 1→0 fade-out (frames). */
const envelope = (f: number, total: number, fadeIn: number, fadeOut: number) =>
  interpolate(f, [0, fadeIn, total - fadeOut, total], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

/** Frames per clip so that the clips + crossfades fill exactly `totalFrames`. */
export const clipFrames = (clips: DamClip[], totalFrames: number) => {
  const n = clips.length;
  const sum = totalFrames + (n - 1) * TRANSITION;
  const weights = clips.map((c) => c.weight ?? 1);
  const wSum = weights.reduce((a, b) => a + b, 0);
  const frames = weights.map((w) => Math.max(TRANSITION + 1, Math.floor((sum * w) / wSum)));
  frames[n - 1] += sum - frames.reduce((a, b) => a + b, 0); // remainder to the last clip
  return frames;
};

const Shot: React.FC<{ clip: DamClip; frames: number }> = ({ clip, frames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = interpolate(frame, [0, frames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const [z0, z1] = clip.zoom ?? [1, 1.06];
  const fx = interpolate(t, [0, 1], [clip.focusX ?? 0.5, clip.panToX ?? clip.focusX ?? 0.5]);
  const fy = clip.focusY ?? 0.5;
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo
        src={staticFile(clip.src)}
        trimBefore={Math.round((clip.from ?? 0) * fps)}
        playbackRate={clip.playbackRate ?? 1}
        volume={clip.volume ?? 0}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover", // fills 9:16 without stretching
          objectPosition: `${fx * 100}% ${fy * 100}%`,
          transform: `scale(${interpolate(t, [0, 1], [z0, z1])})`,
          transformOrigin: `${fx * 100}% ${fy * 100}%`,
        }}
      />
    </AbsoluteFill>
  );
};

const m3 = (v: number) => `${formatNumber(v, { digits: "latin" })}`;

/** One info box: gradient from solid (right, RTL start) to transparent (left). */
const InfoBox: React.FC<{ delay: number; color: string; children: React.ReactNode; padY: number; minWidth: number }> = ({ delay, color, children, padY, minWidth }) => {
  const frame = useCurrentFrame();
  const p = ramp(frame, delay, 22, EASE.out);
  return (
    <div
      style={{
        alignSelf: "flex-start", // RTL: start = right edge
        minWidth,
        padding: `${padY}px ${S.padX}px`,
        background: `linear-gradient(to left, ${color} 0%, ${color} 55%, ${color.replace(/[\d.]+\)$/, "0)")} 100%)`,
        opacity: p,
        transform: `translateX(${(1 - p) * 60}px)`,
        clipPath: `inset(0 0 0 ${(1 - p) * 100}%)`,
      }}
    >
      {children}
    </div>
  );
};

export const DamRainfallReport: React.FC<DamRainfallReportProps> = (p) => {
  const { durationInFrames } = useVideoConfig();
  const frames = clipFrames(p.videoSources, durationInFrames);
  const logoMode = p.logoMode ?? "lockup";
  const display = FONT_FAMILIES.NotoKufiArabic;
  const body = FONT_FAMILIES.IBMPlexSansArabic;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", direction: "rtl" }}>
      {/* footage */}
      <TransitionSeries>
        {p.videoSources.map((clip, i) => (
          <React.Fragment key={i}>
            {i > 0 && <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />}
            <TransitionSeries.Sequence durationInFrames={frames[i]}>
              <Shot clip={clip} frames={frames[i]} />
            </TransitionSeries.Sequence>
          </React.Fragment>
        ))}
      </TransitionSeries>

      {p.music ? <Audio src={staticFile(p.music.src)} volume={(f) => p.music!.volume * envelope(f, durationInFrames, 12, 45)} /> : null}
      {p.ambience ? <Audio src={staticFile(p.ambience.src)} loop volume={(f) => p.ambience!.volume * envelope(f, durationInFrames, 20, 45)} /> : null}

      {/* soft bottom shade so the info boxes read on bright water/sky */}
      <AbsoluteFill style={{ background: "linear-gradient(to top, rgba(0,12,28,0.55) 0%, rgba(0,12,28,0.25) 28%, rgba(0,0,0,0) 45%)" }} />

      {/* logos — static, inside the top safe area. Ministry right, SIO left (as the reference). */}
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
        }}
      >
        {/* both circles share one diameter → neither logo looks bigger */}
        <PartnerLogo id="mewa" part={logoMode} height={L.logoCircle} />
        <Logo form={logoMode === "emblem" ? "emblem" : "lockup"} variant="color" background="light" height={L.logoCircle} />
      </div>

      {/* info boxes — bottom right, inside the safe area */}
      <div
        style={{
          position: "absolute",
          right: L.safeSide,
          left: L.safeSide,
          bottom: L.safeBottom,
          display: "flex",
          flexDirection: "column",
          gap: 10,
        }}
      >
        <InfoBox delay={L.infoStart} color={S.blue} padY={14} minWidth={L.nameBoxWidth}>
          <div style={{ fontFamily: display, fontWeight: 800, fontSize: L.nameSize, lineHeight: 1.35, color: "#fff" }}>{p.damName}</div>
        </InfoBox>
        <InfoBox delay={L.infoStart + L.stagger} color={S.navy} padY={8} minWidth={L.rowWidth}>
          <div style={{ fontFamily: body, fontWeight: 700, fontSize: L.govSize, lineHeight: 1.4, color: "#fff" }}>{p.governorate}</div>
        </InfoBox>
        <InfoBox delay={L.infoStart + L.stagger * 2} color={S.navy} padY={8} minWidth={L.rowWidth}>
          <Row label="السعة التخزينية" value={p.storageCapacity} body={body} />
        </InfoBox>
        <InfoBox delay={L.infoStart + L.stagger * 3} color={S.navy} padY={8} minWidth={L.rowWidth}>
          <Row label="الكمية الواردة" value={p.incomingWater} body={body} />
        </InfoBox>
      </div>
    </AbsoluteFill>
  );
};

const Row: React.FC<{ label: string; value: number; body: string }> = ({ label, value, body }) => (
  <div style={{ fontFamily: body, fontSize: L.rowSize, lineHeight: 1.4, color: "#fff", display: "flex", gap: 14, alignItems: "baseline" }}>
    <span style={{ fontWeight: 600, opacity: 0.92 }}>{label}:</span>
    <span style={{ fontWeight: 700, unicodeBidi: "isolate" }}>
      <bdi dir="ltr">{m3(value)}</bdi> م³
    </span>
  </div>
);
