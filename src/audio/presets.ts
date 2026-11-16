// Reusable audio presets per video type. Levels in dB (≤ 0 → never amplifies, never clips in the mix).
// Loudness targets are applied at export by src/audio/tools/export.mjs (linear gain, no limiter → no distortion).

export type AudioPreset = {
  label: string;
  voDb: number; // voice-over level
  musicDb: number; // music level when nobody speaks
  duckDb: number; // extra music reduction while the voice-over plays (ducking)
  duckAttack: number; // s — music dips this long BEFORE the voice starts
  duckRelease: number; // s — music recovers over this long AFTER the voice ends
  sfxDb: number; // sound-effects level
  maxSfxPer10s: number; // guard against over-use: extra cues are dropped (and warned)
  fadeIn: number; // s — music fade-in
  fadeOut: number; // s — music + sfx fade-out at the end
  lufs: number; // integrated loudness target of the final mix
  truePeak: number; // dBTP ceiling
};

export const AUDIO_PRESETS = {
  "institutional-documentary": { label: "Institutional Documentary", voDb: 0, musicDb: -10, duckDb: -12, duckAttack: 0.35, duckRelease: 0.9, sfxDb: -16, maxSfxPer10s: 4, fadeIn: 1.5, fadeOut: 2.5, lufs: -16, truePeak: -1 },
  "corporate-presentation": { label: "Corporate Presentation", voDb: 0, musicDb: -9, duckDb: -11, duckAttack: 0.3, duckRelease: 0.7, sfxDb: -14, maxSfxPer10s: 4, fadeIn: 1, fadeOut: 2, lufs: -16, truePeak: -1 },
  "technical-explainer": { label: "Technical Explainer", voDb: 0, musicDb: -12, duckDb: -14, duckAttack: 0.3, duckRelease: 0.8, sfxDb: -14, maxSfxPer10s: 5, fadeIn: 1, fadeOut: 2, lufs: -16, truePeak: -1 },
  "cinematic-showcase": { label: "Cinematic Project Showcase", voDb: 0, musicDb: -7, duckDb: -10, duckAttack: 0.45, duckRelease: 1.2, sfxDb: -11, maxSfxPer10s: 4, fadeIn: 2.5, fadeOut: 3.5, lufs: -14, truePeak: -1 },
  "social-short": { label: "Social Media Short", voDb: 0, musicDb: -8, duckDb: -10, duckAttack: 0.2, duckRelease: 0.5, sfxDb: -12, maxSfxPer10s: 5, fadeIn: 0.4, fadeOut: 1, lufs: -14, truePeak: -1 },
} satisfies Record<string, AudioPreset>;

export type AudioPresetId = keyof typeof AUDIO_PRESETS;
