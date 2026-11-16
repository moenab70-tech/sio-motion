// Audio settings for the 15-second audio trial of «حصاد التميز 2026» (one file: voice, music, sfx).
// Paths are relative to public/. Every file must have an entry in public/audio/LICENSES.json.
import type { AudioMixConfig } from "../../audio/AudioMix";

export const TRIAL_SECONDS = 15;

export const trialAudio: AudioMixConfig = {
  enabled: { vo: true, music: true, sfx: true },
  preset: "institutional-documentary",
  // Voice-over: local Piper voice (ar_JO-kareem) — SCRATCH quality for timing tests, not for the final film.
  // Durations are read from the files automatically (calculateMetadata).
  vo: [
    { src: "audio/vo/hasad-2026-trial/vo-01-intro.wav", startSeconds: 0.6, label: "حصاد التميز 2026 – المؤسسة العامة للري" },
    { src: "audio/vo/hasad-2026-trial/vo-02-goal-1.wav", startSeconds: 5.85, label: "تقدير جهود منسوبي المؤسسة وشركائها" },
    { src: "audio/vo/hasad-2026-trial/vo-03-goal-2.wav", startSeconds: 9.95, label: "ترسيخ ثقافة التميز" },
  ],
  // Placeholder bed generated in-house — replace with a licensed track (Pixabay / Mixkit …) and log it.
  music: { src: "audio/music/generated/placeholder-ambient-corporate.wav", startSeconds: 0 },
  // Linked to on-screen events of the Hasad edit (title, scene transition at 5.1 s, kicker, line 2).
  sfx: [
    { src: "audio/sfx/generated/whoosh-soft.wav", atSeconds: 0.2, label: "title reveal" },
    { src: "audio/sfx/generated/whoosh-soft.wav", atSeconds: 4.8, gainDb: -2, label: "transition 1→2" },
    { src: "audio/sfx/generated/ui-click.wav", atSeconds: 5.7, label: "kicker هدف المبادرة" },
    { src: "audio/sfx/generated/digital-transition.wav", atSeconds: 9.7, gainDb: -3, label: "goal line 2" },
  ],
};
