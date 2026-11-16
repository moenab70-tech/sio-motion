// Final audio for «بصمة إنجاز & نمو»: music + sound effects only (no voice-over — user decision 2026-11-15).
// The sound-effect times are computed from the scene list in config.ts, so they stay in sync when a scene is added or reordered.
import type { AudioMixConfig, SfxCue } from "../../audio/AudioMix";
import { hasadConfig, sceneStarts, transitionFrames, type HasadConfig } from "./config";

const WHOOSH = "audio/sfx/generated/whoosh-soft.wav";

export const finalAudioFor = (c: HasadConfig): AudioMixConfig => {
  const starts = sceneStarts(c);
  const tf = transitionFrames(c);
  const sfx: SfxCue[] = [{ src: WHOOSH, atSeconds: 0.2, gainDb: -2, label: "title reveal" }];
  c.scenes.forEach((s, i) => {
    if (i === 0) return;
    // a cue at each scene change (middle of the transition); softer on blur transitions
    const at = (starts[i] + tf / 2) / c.fps;
    if (s.kind === "outro") {
      sfx.push({ src: "audio/sfx/generated/cinematic-rise.wav", atSeconds: Math.max(0, at - 2.6), gainDb: -3, label: "build into closing" });
      sfx.push({ src: "audio/sfx/generated/impact-soft.wav", atSeconds: at, label: "closing title" });
      if (s.brandOutro) {
        const outroAt = (starts[i] + Math.round(tf * 0.6) + Math.round(s.seconds * c.fps)) / c.fps;
        sfx.push({ src: "audio/sfx/generated/gold-shimmer.wav", atSeconds: outroAt, gainDb: -4, label: "official outro" });
      }
      return;
    }
    sfx.push({ src: WHOOSH, atSeconds: at, gainDb: s.transition === "wipe" ? 0 : -4, label: `→ ${s.id}` });
    if (s.kind === "section") sfx.push({ src: "audio/sfx/generated/gold-shimmer.wav", atSeconds: at + 0.5, gainDb: -8, label: `${s.id} title` });
  });
  return {
    enabled: { vo: false, music: true, sfx: true },
    preset: "institutional-documentary",
    vo: [],
    // In-house bed (owned by SIO), 87 s — longer than the film.
    music: { src: "audio/music/generated/placeholder-ambient-corporate-long.wav", startSeconds: 0 },
    sfx,
  };
};

export const finalAudio = finalAudioFor(hasadConfig);
