// Single source for all hand-drawn line work (Grease Pencil in Blender + timing in Remotion).
// Coordinates are PIXELS of the target image; frames are shot-local (1-based like Blender).
export type Line = { pts: number[][]; from: number; to: number; color?: number[]; alpha?: number; px?: number; jitter?: number; overshoot?: number; fade?: number[][] };
export type LineSet = { w: number; h: number; frames: number; lines: Line[] };

const GRAPHITE = [0.17, 0.15, 0.13];
const LIGHT = { color: [0.3, 0.28, 0.26], alpha: 0.35, px: 1.6, jitter: 0.8 };
const INK = { color: GRAPHITE, alpha: 0.92, px: 3.4, jitter: 1.0, overshoot: 6 };
const GOLD = { color: [0.86, 0.68, 0.36], alpha: 1, px: 4.2, jitter: 0.6 };

// ── 1B: the idea, drawn on the paper plate (paper ≈ x 470–1450, y 330–940) ──
const scaleSet = (lines: Line[], k: number, cx: number, cy: number): Line[] => lines.map((l) => ({ ...l, pts: l.pts.map(([x, y]) => [cx + (x - cx) * k, cy + (y - cy) * k]) }));

const LW_1B_RAW: LineSet = {
  w: 1920, h: 1088, frames: 96,
  lines: [
    { ...LIGHT, pts: [[540, 560], [1380, 560]], from: 4, to: 12 },
    { ...LIGHT, pts: [[960, 470], [960, 860]], from: 11, to: 16 },
    { ...INK, pts: [[560, 600], [720, 600]], from: 16, to: 22 },
    { ...INK, pts: [[720, 600], [810, 740], [1110, 740], [1200, 600]], from: 22, to: 40 },
    { ...INK, pts: [[1200, 600], [1360, 600]], from: 40, to: 45 },
    // 45–58: pause — the pencil lifts while he studies the section
    { ...INK, alpha: 0.8, px: 2.6, pts: [[772, 680], [1148, 680]], from: 58, to: 66 },
    { ...INK, alpha: 0.6, px: 2, overshoot: 0, pts: [[860, 700], [905, 700]], from: 66, to: 68 },
    { ...INK, alpha: 0.6, px: 2, overshoot: 0, pts: [[1000, 712], [1052, 712]], from: 68, to: 70 },
    { ...INK, px: 2.4, pts: [[810, 800], [1110, 800]], from: 70, to: 77 },
    { ...INK, px: 2.4, overshoot: 0, pts: [[810, 788], [810, 812]], from: 77, to: 78 },
    { ...INK, px: 2.4, overshoot: 0, pts: [[1110, 788], [1110, 812]], from: 78, to: 79 },
    { ...INK, pts: [[930, 520], [930, 740]], from: 80, to: 84 },
    { ...INK, pts: [[990, 520], [990, 740]], from: 84, to: 88 },
    { ...INK, pts: [[918, 520], [1002, 520]], from: 88, to: 90 },
  ],
};

export const LW_1B: LineSet = { ...LW_1B_RAW, lines: scaleSet(LW_1B_RAW.lines, 1.3, 960, 660) };

// ── 2B: four sheets (local 620×440), timeline = the shot (102 frames) ──
const SEC = [[60, 230], [170, 230], [240, 330], [380, 330], [450, 230], [560, 230]];
const FURN = (t: number): Line[] => [
  { ...LIGHT, alpha: 0.45, pts: [[18, 18], [602, 18], [602, 422], [18, 422], [18, 18]], from: t, to: t + 1, overshoot: 0 },
  { ...LIGHT, alpha: 0.45, pts: [[420, 360], [602, 360]], from: t, to: t + 1 },
  { ...LIGHT, alpha: 0.45, pts: [[420, 360], [420, 422]], from: t, to: t + 1 },
  { ...LIGHT, alpha: 0.4, pts: [[40, 48], [220, 48]], from: t, to: t + 1 },
  { ...LIGHT, alpha: 0.4, pts: [[40, 68], [170, 68]], from: t, to: t + 1 },
];
export const SHEET_LAND = [4, 24, 46, 66]; // frame each sheet lands
export const LW_2B: LineSet[] = [
  { w: 620, h: 440, frames: 102, lines: [...FURN(1), { ...INK, pts: SEC, from: 8, to: 20 },
    { ...INK, color: [0.42, 0.18, 0.15], px: 4, pts: [[130, 120], [500, 380]], from: 21, to: 24 }, { ...INK, color: [0.42, 0.18, 0.15], px: 4, pts: [[500, 120], [130, 380]], from: 24, to: 27 }] },
  { w: 620, h: 440, frames: 102, lines: [...FURN(1),
    { ...INK, pts: [[60, 230], [190, 230], [250, 330], [370, 330], [430, 230], [560, 230]], from: 28, to: 40, fade: [[48, 1], [58, 0.22]] },
    { ...INK, alpha: 0.8, px: 2.6, pts: [[215, 290], [405, 290]], from: 40, to: 44, fade: [[48, 1], [58, 0.22]] }] },
  { w: 620, h: 440, frames: 102, lines: [...FURN(1), { ...INK, pts: SEC, from: 50, to: 60 },
    { ...INK, alpha: 0.8, px: 2.6, pts: [[210, 290], [410, 290]], from: 60, to: 63 }, { ...INK, pts: [[300, 150], [300, 330]], from: 63, to: 65 }] },
  { w: 620, h: 440, frames: 102, lines: [...FURN(1), { ...INK, pts: SEC, from: 70, to: 78 },
    { ...INK, alpha: 0.8, px: 2.6, pts: [[210, 290], [410, 290]], from: 78, to: 80 },
    { ...INK, px: 2.4, pts: [[240, 372], [380, 372]], from: 80, to: 82 },
    { ...INK, pts: [[300, 150], [300, 330]], from: 82, to: 83 }, { ...INK, pts: [[320, 150], [320, 330]], from: 83, to: 84 },
    { ...GOLD, pts: SEC, from: 86, to: 98 }, { ...GOLD, px: 3.4, pts: [[210, 290], [410, 290]], from: 94, to: 99 }] },
];

// ── 3B: engineering lines in the canal's own perspective (plate 1920×1088) ──
const CANAL = [
  [[0, 300], [1920, 300]],
  [[930, 360], [700, 650]], [[1070, 360], [1290, 650]],
  [[820, 650], [1170, 650], [1170, 740], [820, 740], [820, 650]],
  [[830, 740], [540, 1088]], [[1170, 740], [1520, 1088]],
  [[700, 650], [300, 700], [0, 760]], [[1290, 650], [1660, 700], [1920, 760]],
];
export const LW_3B: LineSet = {
  w: 1920, h: 1088, frames: 90,
  lines: [
    { ...LIGHT, alpha: 0.4, pts: [[1000, 330], [300, 1088]], from: 1, to: 8, fade: [[30, 1], [44, 0]] },
    { ...LIGHT, alpha: 0.4, pts: [[1000, 330], [1700, 1088]], from: 2, to: 9, fade: [[30, 1], [44, 0]] },
    ...CANAL.map((pts, i) => ({ ...INK, px: 4, pts, from: 3 + i * 2, to: 11 + i * 2, fade: [[30, 1], [46, 0]] })),
    ...CANAL.map((pts, i) => ({ ...GOLD, pts, from: 22 + i, to: 32 + i, fade: [[44, 1], [62, 0]] })),
  ],
};

/** Pencil-tip position at a shot frame (for the hand shadow); null while lifted between strokes. */
export const tipAt = (set: LineSet, f: number): { x: number; y: number; drawing: boolean } => {
  const ink = set.lines.filter((l) => (l.px ?? 3) >= 2);
  const cur = ink.find((l) => f >= l.from && f < l.to);
  const along = (pts: number[][], t: number) => {
    const seg = pts.slice(1).map((p, i) => Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]));
    let d = t * seg.reduce((a, b) => a + b, 0);
    for (let i = 0; i < seg.length; i++) { if (d <= seg[i]) { const k = seg[i] ? d / seg[i] : 0; return { x: pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, y: pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k }; } d -= seg[i]; }
    const e = pts[pts.length - 1]; return { x: e[0], y: e[1] };
  };
  if (cur) return { ...along(cur.pts, (f - cur.from) / (cur.to - cur.from)), drawing: true };
  const prev = [...ink].reverse().find((l) => l.to <= f), next = ink.find((l) => l.from > f);
  const a = prev ? along(prev.pts, 1) : next ? along(next.pts, 0) : { x: 960, y: 540 };
  const b = next ? along(next.pts, 0) : a;
  const t = prev && next ? (f - prev.to) / Math.max(1, next.from - prev.to) : 0;
  return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t, drawing: false };
};
