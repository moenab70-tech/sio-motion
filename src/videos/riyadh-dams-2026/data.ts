// ─────────────────────────────────────────────────────────────
// SIO | تقرير سدود منطقة الرياض خلال الحالة المطرية — 10–11 نوفمبر 2026م
// ALL report data lives here (texts, numbers, dams, media). Design files read from this file only.
// Source: presentation «تقرير السدود التي بلغت سعتها التخزينية بمنطقة الرياض خلال الحالة المطرية».
// ─────────────────────────────────────────────────────────────

export const REPORT = {
  title: "سدود منطقة الرياض تستقبل مياه السيول خلال الحالة المطرية",
  subtitle: "خلال الفترة من 10 إلى 11 نوفمبر 2026م",
  chartTitle: "أعلى السدود من حيث السعة التخزينية", // drawn as 2 lines: «أعلى السدود» / «من حيث السعة التخزينية»
  outroText: "المؤسسة العامة للري",
};

/** Media for a scene: a real clip (path inside /public) + reframe. */
export type SceneMedia = {
  src: string;
  /** "image" = still photo (gets a slow pan & zoom); default "video" */
  kind?: "video" | "image";
  from?: number; // start inside the source clip (s)
  weight?: number; // relative length inside a dam scene (default 1)
  focusX?: number; // reframe: 0 = left, 1 = right
  focusY?: number; // 0 = top, 1 = bottom
  panToX?: number;
  panToY?: number;
  zoom?: [number, number]; // start → end scale
  volume?: number; // original sound (0 = muted)
};

const H = "media/video/dams/harimla/"; // drone footage (Drive)
const SB = "media/video/dams/sulbukh/"; // drone footage (Drive)
const P = "media/riyadh-dams-2026/original/"; // original media taken from the presentation (one file per dam)

export const SCENE_MEDIA = {
  intro: { src: `${P}05_fuhaihil.mp4`, from: 2, focusX: 0.5 } as SceneMedia, // strongest real flow: water over the Al-Fuhaihil spillway (4K source)
  stats: { src: `${H}harimla_3.mov`, from: 9, focusX: 0.45 } as SceneMedia, // wide reservoir
  chart: { src: `${SB}sulbukh_3.mov`, from: 3, focusX: 0.55 } as SceneMedia, // wide reservoir
  outro: { src: `${H}harimla_2.mov`, from: 19, focusX: 0.62 } as SceneMedia, // wide water, sun glint
  endCard: { src: `${H}harimla_2.mov`, from: 23, focusX: 0.6 } as SceneMedia, // same lake, continues the outro
};

export type Stat = { value: number; unit: string; label: string };

/** Numbers used exactly as in the presentation. */
export const STATS: Stat[] = [
  { value: 13, unit: "سدًا", label: "السدود التي بلغت سعتها التخزينية" },
  { value: 10_260_384, unit: "م³", label: "إجمالي الكميات الواردة للسدود المشمولة بالتقرير" },
  { value: 3_500_000, unit: "م³", label: "أعلى كمية واردة – سد حريملاء" },
];

export type Dam = {
  rank: number;
  name: string; // without the word «سد»
  governorate: string; // without the word «محافظة»
  storageCapacity: number; // m³
  incomingWater: number; // m³
  /** real media of THIS dam only — never another dam's footage */
  media: SceneMedia[];
  /** scene length (s) */
  seconds: number;
};

/** Order = presentation order (highest → lowest storage capacity). */
export const DAMS: Dam[] = [
  { rank: 1, name: "حريملاء", governorate: "حريملاء", storageCapacity: 3_500_000, incomingWater: 3_500_000 , seconds: 7, media: [{ src: `${P}01_harimla.mp4`, from: 1.5, weight: 1.1 }, { src: `${H}harimla_8.mov`, from: 1, focusX: 0.5, panToX: 0.6 }, { src: `${H}harimla_2.mov`, from: 20, focusX: 0.68 }] },
  { rank: 2, name: "الغاط", governorate: "الغاط", storageCapacity: 1_000_000, incomingWater: 1_000_000 , seconds: 4, media: [{ src: `${P}02_ghat.mp4`, from: 6 }] },
  { rank: 3, name: "البرة", governorate: "حريملاء", storageCapacity: 1_000_000, incomingWater: 1_000_000 , seconds: 4.5, media: [{ src: `${P}03_bara.mp4`, from: 9.5 }, { src: `${P}03_bara.mp4`, from: 17 }] },
  { rank: 4, name: "صلبوخ", governorate: "حريملاء", storageCapacity: 931_000, incomingWater: 931_000 , seconds: 6, media: [{ src: `${P}04_sulbukh.mp4`, from: 0.3 }, { src: `${SB}sulbukh_2.mov`, from: 19, focusX: 0.36 }, { src: `${SB}sulbukh_3.mov`, from: 3, focusX: 0.55 }] },
  { rank: 5, name: "الفحيحيل", governorate: "المجمعة", storageCapacity: 801_985, incomingWater: 801_985 , seconds: 4.5, media: [{ src: `${P}05_fuhaihil.mp4`, from: 13 }] },
  { rank: 6, name: "خنقة عروة", governorate: "القويعية", storageCapacity: 680_143, incomingWater: 680_143 , seconds: 4, media: [{ src: `${P}06_khanqat-urwa.mp4`, from: 4 }] },
  { rank: 7, name: "الكلبي", governorate: "المجمعة", storageCapacity: 595_591, incomingWater: 595_591 , seconds: 4, media: [{ src: `${P}07_kalbi.mp4`, from: 2 }] },
  { rank: 8, name: "الحريق بالوشم", governorate: "شقراء", storageCapacity: 500_000, incomingWater: 500_000 , seconds: 4.5, media: [{ src: `${P}08_hariq-alwashm.mp4`, from: 1 }, { src: `${P}08_hariq-alwashm.mp4`, from: 13 }] },
  { rank: 9, name: "رغبة", governorate: "ثادق", storageCapacity: 474_153, incomingWater: 474_153 , seconds: 4, media: [{ src: `${P}09_rughba.mp4`, from: 3.5 }] },
  { rank: 10, name: "اثيثية", governorate: "مرات", storageCapacity: 250_000, incomingWater: 250_000 , seconds: 4, media: [{ src: `${P}10_uthaythiyah.jpg`, kind: "image", focusY: 0.55, zoom: [1.04, 1.14] }] },
  { rank: 11, name: "التمريه", governorate: "المجمعة", storageCapacity: 241_922, incomingWater: 241_922 , seconds: 4, media: [{ src: `${P}11_tamriyah.jpg`, kind: "image", focusX: 0.45, focusY: 0, zoom: [1.42, 1.5] }] /* top of photo only: hides the CamStamp box at the bottom */ },
  { rank: 12, name: "الخروعية", governorate: "القويعية", storageCapacity: 169_590, incomingWater: 169_590 , seconds: 4, media: [{ src: `${P}12_kharuiyah.mp4`, from: 3 }] },
  { rank: 13, name: "الداهنة", governorate: "شقراء", storageCapacity: 116_000, incomingWater: 116_000 , seconds: 4, media: [{ src: `${P}13_dahinah.mp4`, from: 0.5, focusX: 0.44, panToX: 0.3 } /* landscape clip: keep the dam gate, drop the burnt-in stamp (top-right) */] },
];

/** Chart = top 5 by storage capacity (kept in presentation order for ties). */
export const CHART_DAMS = DAMS.slice(0, 5);

/** Sanity checks so a data edit can't silently break the report. */
export const checkData = () => {
  const total = DAMS.reduce((a, d) => a + d.incomingWater, 0);
  if (total !== STATS[1].value) throw new Error(`Total incoming ${total} ≠ stat ${STATS[1].value}`);
  if (DAMS.length !== STATS[0].value) throw new Error(`Dam count ${DAMS.length} ≠ stat ${STATS[0].value}`);
};

/** Scene lengths (s) and the master sound. All audio is in-house and cleared for commercial use (public/audio/LICENSES.json). */
export const TIMING = { intro: 6, stats: 8, chart: 8, outro: 4, brandOutro: 5, endCard: 5, sectionFade: 15, damFade: 12 }; // fades in frames

/** Official SIO social-media outro (white logo animation on black), supplied by the user.
 *  Source: «التواصل الاجتماعي اوترو.mov» (QuickTime Animation 4096×2304) → converted losslessly in look to ProRes 4444 1920×1080, file untouched. */
/** SIO contact line (same as the official social outro). */
export const SOCIAL = { handle: "@siogov", website: "www.sio.gov.sa" };

export const BRAND_OUTRO = { src: "media/riyadh-dams-2026/outro/sio-social-outro-4444.mov", scale: 2.5 };

export const AUDIO = {
  music: { src: "audio/music/generated/placeholder-ambient-corporate-long.wav", start: 0.6, peak: 1 }, // calm start → gentle rise
  ambience: { src: "audio/sfx/generated/water-flow.wav", volume: 0.3 },
  transition: { src: "audio/sfx/generated/whoosh-soft.wav", volume: 0.25 }, // between sections only
};
