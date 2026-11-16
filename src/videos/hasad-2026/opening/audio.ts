// Opening audio v2: in-house score (unchanged) + foley synced to the shots (seconds on the opening timeline).
// Shot starts: 1A 0 · 1B 3.0 · 2A 5.7 · 2B 7.9 · 3A 10.7 · 3B 13.0 · 4A 16.0 · end 20.0
import type { AudioMixConfig } from "../../../audio/AudioMix";

export const openingAudio: AudioMixConfig = {
  enabled: { vo: false, music: true, sfx: true },
  preset: "cinematic-showcase",
  overrides: { musicDb: -3, sfxDb: -4, maxSfxPer10s: 14, fadeIn: 0.3, fadeOut: 1.2 },
  vo: [],
  music: { src: "audio/music/generated/opening-cue-20s.wav", startSeconds: 0 },
  sfx: [
    { src: "audio/sfx/generated/ambient-atmosphere.wav", atSeconds: 0, gainDb: 2, label: "room tone" },
    { src: "audio/sfx/generated/pencil-scratch.wav", atSeconds: 0.6, gainDb: -8, label: "1A distant pencil" },
    { src: "audio/sfx/generated/pencil-scratch.wav", atSeconds: 3.5, gainDb: -2, label: "1B section stroke" },
    { src: "audio/sfx/generated/paper-rustle.wav", atSeconds: 4.47, gainDb: -6, label: "1B pencil lifts" },
    { src: "audio/sfx/generated/pencil-scratch.wav", atSeconds: 4.93, gainDb: -3, label: "1B water level + gate" },
    { src: "audio/sfx/generated/clock-accelerating.wav", atSeconds: 5.8, label: "2A time passes" },
    { src: "audio/sfx/generated/paper-rustle.wav", atSeconds: 7.9, gainDb: -3, label: "2B sheet 1" },
    { src: "audio/sfx/generated/pencil-scratch.wav", atSeconds: 8.13, gainDb: -10, label: "2B drawing 1" },
    { src: "audio/sfx/generated/paper-rustle.wav", atSeconds: 8.6, gainDb: -4, label: "2B sheet 2" },
    { src: "audio/sfx/generated/eraser-rub.wav", atSeconds: 9.5, gainDb: -2, label: "2B erasing" },
    { src: "audio/sfx/generated/paper-rustle.wav", atSeconds: 9.33, gainDb: -4, label: "2B sheet 3" },
    { src: "audio/sfx/generated/paper-rustle.wav", atSeconds: 10.0, gainDb: -3, label: "2B final sheet" },
    { src: "audio/sfx/generated/gold-shimmer.wav", atSeconds: 10.75, gainDb: -8, label: "2B gold trace" },
    { src: "audio/sfx/generated/paper-rustle.wav", atSeconds: 11.2, gainDb: -8, label: "3A drawing on the desk" },
    { src: "audio/sfx/generated/pencil-scratch.wav", atSeconds: 13.05, gainDb: -6, label: "3B lines drawn" },
    { src: "audio/sfx/generated/water-flow.wav", atSeconds: 13.4, gainDb: 4, label: "3B/4A canal water" },
    { src: "audio/sfx/generated/breeze.wav", atSeconds: 15.8, gainDb: -2, label: "4A breeze" },
  ],
};
