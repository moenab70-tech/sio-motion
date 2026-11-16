// SIO audio mixer: three independent tracks (voice-over, music, sfx) with dB levels, ducking and fades.
// Drop <AudioMix> into any composition; every track is optional. Files come from public/ (staticFile paths).
// Volumes are computed per frame with plain maths (deterministic in Studio and in renders).
import React from "react";
import { Html5Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { getAudioDurationInSeconds } from "@remotion/media-utils";
import { AUDIO_PRESETS, type AudioPreset, type AudioPresetId } from "./presets";

export type VoClip = { src: string; startSeconds: number; durationInSeconds?: number; gainDb?: number; label?: string };
export type MusicTrack = { src: string; startSeconds?: number; trimBeforeSeconds?: number; gainDb?: number; loop?: boolean };
export type SfxCue = { src: string; atSeconds: number; gainDb?: number; label?: string };
export type AudioSolo = "all" | "vo" | "music" | "sfx";

export type AudioMixConfig = {
  enabled: { vo: boolean; music: boolean; sfx: boolean }; // each track is optional per project
  preset: AudioPresetId;
  overrides?: Partial<AudioPreset>;
  vo: VoClip[];
  music: MusicTrack | null;
  sfx: SfxCue[];
};

export const db = (d: number) => Math.pow(10, d / 20);
const smooth = (x: number) => { const t = Math.max(0, Math.min(1, x)); return t * t * (3 - 2 * t); };

export const resolvePreset = (mix: AudioMixConfig): AudioPreset => ({ ...AUDIO_PRESETS[mix.preset], ...mix.overrides });

/** 0 → 1 ducking amount at time t (s), from every voice-over window (attack before, release after). */
export const duckAmount = (t: number, vo: VoClip[], p: AudioPreset) =>
  vo.reduce((k, c) => {
    const s = c.startSeconds, e = s + (c.durationInSeconds ?? 0);
    const v = t < s ? smooth((t - (s - p.duckAttack)) / p.duckAttack) : t <= e ? 1 : 1 - smooth((t - e) / p.duckRelease);
    return Math.max(k, v);
  }, 0);

/** Keeps at most `max` cues in any 10-second window (prevents over-use). */
export const limitSfx = (cues: SfxCue[], max: number) => {
  const kept: SfxCue[] = [];
  for (const c of [...cues].sort((a, b) => a.atSeconds - b.atSeconds)) {
    if (kept.filter((k) => c.atSeconds - k.atSeconds < 10).length < max) kept.push(c);
    else console.warn(`[AudioMix] SFX dropped (more than ${max} per 10 s): ${c.label ?? c.src} @ ${c.atSeconds}s`);
  }
  return kept;
};

/** For calculateMetadata: reads real voice-over durations so ducking follows the actual files. */
export const withVoDurations = async (mix: AudioMixConfig): Promise<AudioMixConfig> => ({
  ...mix,
  vo: await Promise.all(mix.vo.map(async (c) => (c.durationInSeconds ? c : { ...c, durationInSeconds: await getAudioDurationInSeconds(staticFile(c.src)) }))),
});

const MusicLayer: React.FC<{ track: MusicTrack; vo: VoClip[]; p: AudioPreset; durationInFrames: number }> = ({ track, vo, p, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps, total = durationInFrames / fps, start = track.startSeconds ?? 0;
  const fade = Math.min(smooth((t - start) / Math.max(0.01, p.fadeIn)), smooth((total - t) / Math.max(0.01, p.fadeOut)));
  const duck = 1 - duckAmount(t, vo, p) * (1 - db(p.duckDb));
  const volume = db(p.musicDb + (track.gainDb ?? 0)) * duck * fade;
  return (
    <Sequence from={Math.round(start * fps)} name="music" layout="none">
      <Html5Audio src={staticFile(track.src)} volume={Math.max(0, volume)} loop={track.loop} trimBefore={Math.round((track.trimBeforeSeconds ?? 0) * fps)} />
    </Sequence>
  );
};

const SfxLayer: React.FC<{ cue: SfxCue; p: AudioPreset; durationInFrames: number }> = ({ cue, p, durationInFrames }) => {
  const frame = useCurrentFrame(); // local to the cue's Sequence
  const { fps } = useVideoConfig();
  const t = cue.atSeconds + frame / fps, total = durationInFrames / fps;
  const fade = smooth((total - t) / Math.max(0.01, p.fadeOut));
  return <Html5Audio src={staticFile(cue.src)} volume={db(p.sfxDb + (cue.gainDb ?? 0)) * fade} />;
};

export const AudioMix: React.FC<{ mix: AudioMixConfig; durationInFrames: number; solo?: AudioSolo }> = ({ mix, durationInFrames, solo = "all" }) => {
  const { fps } = useVideoConfig();
  const p = resolvePreset(mix);
  const on = (k: "vo" | "music" | "sfx") => mix.enabled[k] && (solo === "all" || solo === k);
  const vo = mix.enabled.vo ? mix.vo : []; // ducking follows the voice even in the music stem
  return (
    <>
      {on("music") && mix.music && <MusicLayer track={mix.music} vo={vo} p={p} durationInFrames={durationInFrames} />}
      {on("vo") && mix.vo.map((c, i) => (
        <Sequence key={`vo-${i}`} from={Math.round(c.startSeconds * fps)} name={`VO · ${c.label ?? c.src}`} layout="none">
          <Html5Audio src={staticFile(c.src)} volume={db(p.voDb + (c.gainDb ?? 0))} />
        </Sequence>
      ))}
      {on("sfx") && limitSfx(mix.sfx, p.maxSfxPer10s).map((c, i) => (
        <Sequence key={`sfx-${i}`} from={Math.round(c.atSeconds * fps)} name={`SFX · ${c.label ?? c.src}`} layout="none">
          <SfxLayer cue={c} p={p} durationInFrames={durationInFrames} />
        </Sequence>
      ))}
    </>
  );
};
