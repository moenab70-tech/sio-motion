import type { DamRainfallReportProps } from "./DamRainfallReport";

// ─────────────────────────────────────────────────────────────
// Dams 2026 — vertical 9:16 reports. Edit the dam data / clips below;
// the layout and style are shared by every dam.
// ─────────────────────────────────────────────────────────────

export const DAM_VIDEO = { width: 1080, height: 1920, fps: 30 } as const;

/** Safe areas keep logos & text clear of Reels / TikTok / Shorts / Snapchat interface. */
export const DAM_LAYOUT = {
  safeTop: 80,
  safeBottom: 280,
  safeSide: 64,
  logoCircle: 150, // diameter of BOTH logo circles (px)
  infoStart: 18, // frames before the info boxes start
  stagger: 7,
  nameSize: 76,
  govSize: 44,
  rowSize: 40,
  nameBoxWidth: 640,
  rowWidth: 760,
};

/** Official SIO blue = the blue mono logo colour (#0071B8, public/brand/logos/README.md). */
export const DAM_STYLE = {
  blue: "rgba(0,113,184,0.94)",
  navy: "rgba(3,32,64,0.78)",
  padX: 30,
};

const H = "media/video/dams/harimla/";
const SB = "media/video/dams/sulbukh/";

export const harimla: DamRainfallReportProps = {
  damName: "سد حريملاء",
  governorate: "محافظة حريملاء",
  storageCapacity: 3_500_000,
  incomingWater: 3_500_000,
  duration: 20,
  music: { src: "audio/music/generated/placeholder-ambient-corporate.wav", volume: 1 }, // in-house, cleared (LICENSES.json)
  ambience: { src: "audio/sfx/generated/water-flow.wav", volume: 0.3 }, // in-house water flow, loops
  logoMode: "emblem",
  videoSources: [
    // harimla_5/6/7 are identical files; only _5 is used.
    { src: `${H}harimla_8.mov`, from: 1, focusX: 0.5, panToX: 0.6 }, // crest + full reservoir (opening)
    { src: `${H}harimla_2.mov`, from: 20, focusX: 0.68 }, // sun glint on the lake
    { src: `${H}harimla_5.mov`, from: 40, focusX: 0.72, panToX: 0.6 }, // dam wall / spillway side
    { src: `${H}harimla_3.mov`, from: 9, focusX: 0.45 }, // wide reservoir
    { src: `${H}harimla_8.mov`, from: 12, focusX: 0.42 }, // crest close (closing)
  ],
};

export const sulbukh: DamRainfallReportProps = {
  damName: "سد صلبوخ",
  governorate: "محافظة حريملاء",
  storageCapacity: 931_000,
  incomingWater: 931_000,
  duration: 18,
  music: { src: "audio/music/generated/placeholder-ambient-corporate.wav", volume: 1 }, // in-house, cleared (LICENSES.json)
  ambience: { src: "audio/sfx/generated/water-flow.wav", volume: 0.3 }, // in-house water flow, loops
  logoMode: "emblem",
  videoSources: [
    { src: `${SB}sulbukh_2.mov`, from: 19, focusX: 0.36 }, // dam & spillway over the water (opening)
    { src: `${SB}sulbukh_2.mov`, from: 46, focusX: 0.5, panToX: 0.42 }, // valley bend + dam
    { src: `${SB}sulbukh_3.mov`, from: 3, focusX: 0.55 }, // wide reservoir
    { src: `${SB}sulbukh_4.mov`, from: 28, focusX: 0.4, panToX: 0.55 }, // reservoir between the hills
    { src: `${SB}sulbukh_1.mov`, from: 11, focusX: 0.45 }, // on the crest, water behind (closing)
  ],
};
