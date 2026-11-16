// «من فكرة إلى إنجاز» — Blender v6 opening (engineer only, 3D office + canal). New, independent compositions:
// the approved opening (OpeningFilm) and the approved film are imported read-only and are NOT modified.
// Same 600-frame timing, transitions, film look, audio mix and final dissolve into the film's navy backdrop.
import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { AudioMix, type AudioSolo } from "../../../audio/AudioMix";
import { Backdrop } from "../parts";
import { hasadConfig as hasadBase, totalFrames } from "../config";
import { finalAudioFor } from "../audio.final";
// The openings run at 30 fps → embed the film re-timed at 30 fps (everything in config is in seconds).
const hasadConfig = { ...hasadBase, fps: 30 };
import { HasadVideo } from "../HasadVideo";
import { openingAudio } from "./audio";
import { SHOTS, shotStart, OPENING_FRAMES, type ShotId } from "./timing";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** One Blender v6 shot: 1920×1080 PNG sequence in public/media/opening/blender_v6/<id>/f_####.png (1-based). */
export const V6Shot: React.FC<{ id: ShotId; dir?: string; children?: React.ReactNode }> = ({ id, dir = "blender_v6", children }) => {
  const f = useCurrentFrame();
  const len = SHOTS[id].len;
  return (
    <AbsoluteFill style={{ background: "#060D18" }}>
      <Img src={staticFile(`media/opening/${dir}/${id}/f_${String(Math.min(len, Math.max(1, f + 1))).padStart(4, "0")}.png`)} style={{ width: 1920, height: 1080 }} />
      {children}
    </AbsoluteFill>
  );
};

/** 4A: last second dissolves into the approved film's own backdrop (seamless hand-off). */
const ToFilm: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [len - 34, len - 4], [0, 1], { ...clamp, easing: Easing.inOut(Easing.quad) });
  return <AbsoluteFill style={{ opacity: out }}><Backdrop frame={0} total={1} particles={0} /></AbsoluteFill>;
};

/** Warm late-afternoon flare carried over the 2B → 3A transition (the light that marks the breakthrough). */
const WarmFlare: React.FC = () => {
  const f = useCurrentFrame();
  const env = Math.sin(Math.PI * Math.min(1, f / 52));
  const x = 75 - 30 * (f / 52);
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.55 * env }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 55% 75% at ${x}% 40%, rgba(255,214,150,0.8), rgba(255,170,90,0.3) 40%, rgba(0,0,0,0) 75%)` }} />
    </AbsoluteFill>
  );
};

const FilmLook: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 75% 70% at 50% 48%, rgba(0,0,0,0) 55%, rgba(4,8,16,0.45) 100%)" }} />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: 0.05, mixBlendMode: "overlay" }}>
        <filter id="grainv6"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 24} /></filter>
        <rect width="1920" height="1080" filter="url(#grainv6)" />
      </svg>
    </AbsoluteFill>
  );
};

const FADE = (len: number) => <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: len, easing: Easing.bezier(0.45, 0, 0.25, 1) })} />;

/** Frame folder per shot: v6 = all from blender_v6; v6.2 = re-rendered shots from blender_v6_2, 3A reused from v6. */
type ShotDirs = Record<ShotId, string>;
const V6_DIRS: ShotDirs = { "1A": "blender_v6", "1B": "blender_v6", "2A": "blender_v6", "2B": "blender_v6", "3A": "blender_v6", "3B": "blender_v6", "4A": "blender_v6" };
export const V6_2_DIRS: ShotDirs = { "1A": "blender_v6_2", "1B": "blender_v6_2", "2A": "blender_v6_2", "2B": "blender_v6_2", "3A": "blender_v6", "3B": "blender_v6_2", "4A": "blender_v6_2" };

/** Picture only (used by the full composition and by the per-shot exports). */
export const OpeningBlenderV6Picture: React.FC<{ dirs?: ShotDirs }> = ({ dirs = V6_DIRS }) => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 12], [1, 0], clamp);
  const look = interpolate(frame, [560, 590], [1, 0], clamp); // last frame = the film's first frame
  const S = SHOTS;
  return (
    <AbsoluteFill style={{ background: "#060D18" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={S["1A"].len} name="1A · اليوم الأول — الفكرة"><V6Shot id="1A" dir={dirs["1A"]} /></TransitionSeries.Sequence>
        <TransitionSeries.Sequence durationInFrames={S["1B"].len} name="1B · القلم يرسم المقطع"><V6Shot id="1B" dir={dirs["1B"]} /></TransitionSeries.Sequence>
        {FADE(S["1B"].out)}
        <TransitionSeries.Sequence durationInFrames={S["2A"].len} name="2A · يوم جديد — محاولات"><V6Shot id="2A" dir={dirs["2A"]} /></TransitionSeries.Sequence>
        <TransitionSeries.Sequence durationInFrames={S["2B"].len} name="2B · اليوم الثالث — تحسين"><V6Shot id="2B" dir={dirs["2B"]} /></TransitionSeries.Sequence>
        {FADE(S["2B"].out)}
        <TransitionSeries.Sequence durationInFrames={S["3A"].len} name="3A · لحظة الحل"><V6Shot id="3A" dir={dirs["3A"]} /></TransitionSeries.Sequence>
        {FADE(S["3A"].out)}
        <TransitionSeries.Sequence durationInFrames={S["3B"].len} name="3B · المشروع منجز"><V6Shot id="3B" dir={dirs["3B"]} /></TransitionSeries.Sequence>
        <TransitionSeries.Sequence durationInFrames={S["4A"].len} name="4A · التقدير → الفيلم"><V6Shot id="4A" dir={dirs["4A"]}><ToFilm len={S["4A"].len} /></V6Shot></TransitionSeries.Sequence>
      </TransitionSeries>
      <Sequence from={shotStart["3A"] - 26} durationInFrames={52} name="warm flare"><WarmFlare /></Sequence>
      <AbsoluteFill style={{ opacity: look }}><FilmLook /></AbsoluteFill>
      <AbsoluteFill style={{ background: "#000", opacity: fadeIn }} />
    </AbsoluteFill>
  );
};

export const OpeningBlenderV6: React.FC<{ audioSolo: AudioSolo }> = ({ audioSolo }) => (
  <AbsoluteFill>
    <OpeningBlenderV6Picture />
    <AudioMix mix={openingAudio} durationInFrames={OPENING_FRAMES} solo={audioSolo} />
  </AbsoluteFill>
);

const OPENING_AUDIO_FRAMES = OPENING_FRAMES + 45;
export const OpeningBlenderV6PlusFilm: React.FC<{ audioSolo: AudioSolo }> = ({ audioSolo }) => (
  <AbsoluteFill>
    <Sequence durationInFrames={OPENING_FRAMES} name="Opening v6"><OpeningBlenderV6Picture /></Sequence>
    <Sequence from={OPENING_FRAMES} name="Film · بصمة إنجاز & نمو"><HasadVideo {...hasadConfig} /></Sequence>
    <Sequence durationInFrames={OPENING_AUDIO_FRAMES} name="Opening audio"><AudioMix mix={openingAudio} durationInFrames={OPENING_AUDIO_FRAMES} solo={audioSolo} /></Sequence>
    <Sequence from={OPENING_FRAMES} name="Film audio"><AudioMix mix={finalAudioFor(hasadConfig)} durationInFrames={totalFrames(hasadConfig)} solo={audioSolo} /></Sequence>
  </AbsoluteFill>
);
export const OPENING_V6_PLUS_FILM_FRAMES = OPENING_FRAMES + totalFrames(hasadConfig);

/** v6.2: cinematography + render-quality pass (new 2B profile, new 4A canal-axis shot, sharp 1B, clean shadows). */
export const OpeningBlenderV6_2: React.FC<{ audioSolo: AudioSolo }> = ({ audioSolo }) => (
  <AbsoluteFill>
    <OpeningBlenderV6Picture dirs={V6_2_DIRS} />
    <AudioMix mix={openingAudio} durationInFrames={OPENING_FRAMES} solo={audioSolo} />
  </AbsoluteFill>
);
