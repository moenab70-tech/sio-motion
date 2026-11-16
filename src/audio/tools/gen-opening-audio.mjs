// «من فكرة إلى إنجاز» — in-house opening score (20 s) + scene foley. Procedural, owned by SIO, deterministic.
// Arc: 0–5 s soft piano + low pad (curiosity) · 5–10 s pulse + tension · 10–15 s warm strings open up ·
// 15–19 s swell and resolve on D minor (the key the main film's bed starts in) · 19–20 s tail.
// Usage: node src/audio/tools/gen-opening-audio.mjs
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { biquad, buf, finish, pan, reverb, rng, SR, writeWav } from "./wav.mjs";

const MUS = "public/audio/music/generated", SFX = "public/audio/sfx/generated";
mkdirSync(MUS, { recursive: true }); mkdirSync(SFX, { recursive: true });
const hz = (m) => 440 * Math.pow(2, (m - 69) / 12);
const env = (t, a, d) => (t < 0 ? 0 : t < a ? t / a : Math.exp(-(t - a) / d));
const noise = (sec, seed) => { const r = rng(seed), x = buf(sec); for (let i = 0; i < x.length; i++) x[i] = r() * 2 - 1; return x; };
const made = [];
const save = (dir, name, chs, desc, category, dbfs = -3) => { const p = `${dir}/${name}.wav`; writeWav(p, finish(chs, dbfs)); made.push({ p, desc, category }); };

// ── Score ───────────────────────────────────────────────
{
  const D = 21, L = buf(D), R = buf(D);
  const add = (t0, fn, len, p = 0) => { const s = Math.round(t0 * SR), n = Math.round(len * SR); for (let i = 0; i < n && s + i < L.length; i++) { const v = fn(i / SR); L[s + i] += v * (1 - p) * 0.9; R[s + i] += v * (1 + p) * 0.9; } };
  // felt-piano note: harmonics, fast attack, two-stage decay
  const piano = (m, vel) => (t) => { const f = hz(m); let v = 0; [1, 2, 3, 4.01].forEach((h, k) => { v += Math.sin(2 * Math.PI * f * h * t) * [1, 0.45, 0.18, 0.08][k] * Math.exp(-t * (0.9 + k * 0.9)); }); return v * vel * Math.min(1, t / 0.004); };
  // string pad voice: detuned additive saw, slow attack/release
  const strings = (m, len, vel, att = 1.2) => (t) => { let v = 0; for (const det of [-0.08, 0, 0.07]) { const f = hz(m) * Math.pow(2, det / 12); for (let h = 1; h <= 6; h++) v += Math.sin(2 * Math.PI * f * h * t + h) / h; } const a = Math.min(1, t / att) * Math.min(1, Math.max(0, (len - t) / 1.2)); return v * a * vel / 3; };
  // 0–5 s: motif D F A C (sparse) over a low D pad
  [[0.3, 62], [1.1, 65], [1.9, 69], [2.9, 72], [3.6, 69], [4.3, 65]].forEach(([t, m], i) => add(t, piano(m, 0.16), 3.2, i % 2 ? 0.25 : -0.25));
  add(0, strings(38, 10.5, 0.05, 2.5), 10.5); add(0, strings(50, 10.5, 0.035, 3), 10.5);
  // 5–10 s: low pulse on D (eighths at 90 bpm), tension pad Bb(add9)
  for (let k = 0; k < 15; k++) { const t0 = 5 + k / 3; add(t0, (t) => Math.sin(2 * Math.PI * hz(38) * t) * env(t, 0.006, 0.16) * (0.10 + 0.012 * k), 0.5); }
  [58, 62, 65, 72].forEach((m) => add(5.2, strings(m, 5.3, 0.028, 2.2), 5.3));
  [[5.6, 74], [6.9, 72], [8.2, 70], [9.2, 69]].forEach(([t, m]) => add(t, piano(m, 0.12), 2.5, 0.2));
  // 10–15 s: warm opening — F major → C/E → Dm → Bb, piano arpeggio brighter
  const prog = [[10, [53, 60, 65, 69]], [11.4, [52, 60, 64, 67]], [12.8, [50, 57, 62, 65]], [14.0, [46, 53, 58, 62]]];
  prog.forEach(([t, ch], i) => ch.forEach((m) => add(t, strings(m, (i < 3 ? 1.6 : 2.4) + 0.8, 0.045 + 0.006 * i, 0.5), 3.2)));
  [65, 69, 72, 77, 76, 72, 74, 77, 81, 77, 74, 70].forEach((m, k) => add(10.1 + k * 0.33, piano(m, 0.1), 2, k % 2 ? 0.3 : -0.3));
  // 15–19 s: swell C → resolve Dm (with F on top), soft high shimmer
  [48, 55, 60, 64, 67].forEach((m) => add(15.2, strings(m, 2.4, 0.055, 1.6), 2.4));
  [50, 57, 62, 65, 69, 74].forEach((m) => add(17.4, strings(m, 3.6, 0.06, 0.6), 3.6));
  [74, 77, 81, 86].forEach((m, k) => add(17.5 + k * 0.12, piano(m, 0.09), 3, 0.2 * (k - 1.5)));
  add(0, (t) => Math.sin(2 * Math.PI * hz(26) * t) * 0.06 * Math.min(1, t / 3) * Math.max(0, Math.min(1, (20.5 - t) / 2)), 21); // sub foundation
  const lp = [biquad(L, "lp", 6500), biquad(R, "lp", 6500)];
  const wet = [reverb(lp[0], { size: 1.5, mix: 0.32 })[0], reverb(lp[1], { size: 1.5, mix: 0.32 })[1]];
  for (const c of wet) for (let i = 0; i < c.length; i++) { const t = i / SR; c[i] *= Math.min(1, t / 0.4, Math.max(0, (D - t) / 1.6)); }
  save(MUS, "opening-cue-20s", wet, "Opening score «من فكرة إلى إنجاز»: piano + strings, D minor arc, resolves into the main bed", "Cinematic, Inspirational", -4);
}

// ── Foley ───────────────────────────────────────────────
{ // pencil on paper: band-passed grainy noise, 1.4 s with natural pressure changes
  const d = 1.4, n = noise(d, 501), r = rng(502), x = biquad(biquad(n, "bp", 3200, 0.6), "hp", 1200);
  for (let i = 0; i < x.length; i++) { const t = i / SR; const press = 0.55 + 0.45 * Math.sin(2 * Math.PI * 5.3 * t) ** 2; x[i] *= press * (0.7 + 0.6 * r()) * Math.min(1, t / 0.03, (d - t) / 0.05); }
  save(SFX, "pencil-scratch", pan(x, () => 0.15), "Pencil on paper (1.4 s)", "Foley", -9);
}
{ // paper rustle: crinkle spikes in low-passed noise
  const d = 0.7, n = noise(d, 511), r = rng(512), x = biquad(n, "bp", 2200, 0.5);
  for (let i = 0; i < x.length; i++) { const t = i / SR; x[i] *= env(t, 0.05, 0.25) * (r() < 0.004 ? 3 : 0.6); }
  save(SFX, "paper-rustle", reverb(biquad(x, "lp", 7000), { size: 0.5, mix: 0.12 }), "Paper rustle (0.7 s)", "Foley", -8);
}
{ // clock ticking that accelerates (time passing), 3 s
  const d = 3.0, x = buf(d); let t0 = 0.05, gap = 0.5, k = 0;
  while (t0 < d - 0.05) { for (let i = Math.round(t0 * SR); i < Math.min(x.length, Math.round((t0 + 0.04) * SR)); i++) { const t = i / SR - t0; x[i] += Math.sin(2 * Math.PI * (k % 2 ? 2600 : 3100) * t) * env(t, 0.0004, 0.006) + 0.3 * Math.sin(2 * Math.PI * 900 * t) * env(t, 0.0005, 0.01); } t0 += gap; gap = Math.max(0.09, gap * 0.82); k++; }
  save(SFX, "clock-accelerating", reverb(x, { size: 0.6, mix: 0.18 }), "Clock ticks accelerating (3 s)", "Foley", -8);
}
{ // eraser rub: two low strokes
  const d = 0.8, n = noise(d, 521), x = biquad(n, "bp", 900, 0.8);
  for (let i = 0; i < x.length; i++) { const t = i / SR; x[i] *= Math.sin(Math.PI * Math.min(1, (t % 0.4) / 0.4)) ** 2; }
  save(SFX, "eraser-rub", pan(x, () => -0.1), "Eraser rubbing (0.8 s)", "Foley", -10);
}
{ // water flow: layered filtered noise with gentle movement, 6 s, stereo
  const d = 6, chs = [0, 1].map((c) => { const n = noise(d, 531 + c), lo = biquad(n, "lp", (t) => 700 + 250 * Math.sin(2 * Math.PI * 0.4 * t + c)), hi = biquad(noise(d, 541 + c), "bp", (t) => 2600 + 900 * Math.sin(2 * Math.PI * 1.7 * t + c * 2), 1.5); return lo.map((v, i) => (v * 0.8 + hi[i] * 0.25) * Math.min(1, i / SR / 1, (d - i / SR) / 1)); });
  save(SFX, "water-flow", chs, "Canal water flow (6 s)", "Ambient", -10);
}
{ // breeze: slow gusts
  const d = 5, chs = [0, 1].map((c) => { const n = noise(d, 551 + c); return biquad(n, "bp", (t) => 500 + 300 * Math.sin(2 * Math.PI * 0.25 * t + c), 0.7).map((v, i) => { const t = i / SR; return v * (0.4 + 0.6 * Math.sin(Math.PI * t / d) ** 2) * Math.min(1, t / 0.8, (d - t) / 0.8); }); });
  save(SFX, "breeze", chs, "Soft desert breeze (5 s)", "Ambient", -12);
}
{ // gold shimmer: rising cluster of soft bells (recognition)
  const d = 3, L = buf(d), R = buf(d);
  [86, 89, 93, 96, 98, 101, 105].forEach((m, k) => { const st = k * 0.16, p = (k % 2 ? 0.4 : -0.4); for (let i = Math.round(st * SR); i < L.length; i++) { const t = i / SR - st; const v = (Math.sin(2 * Math.PI * hz(m) * t) + 0.3 * Math.sin(2 * Math.PI * hz(m) * 2.76 * t)) * env(t, 0.003, 0.7) * 0.15; L[i] += v * (1 - p); R[i] += v * (1 + p); } });
  save(SFX, "gold-shimmer", [reverb(L, { size: 1.3, mix: 0.4 })[0], reverb(R, { size: 1.3, mix: 0.4 })[1]], "Golden shimmer (3 s)", "Cinematic", -8);
}

const LIC = "public/audio/LICENSES.json";
const log = existsSync(LIC) ? JSON.parse(readFileSync(LIC, "utf8")) : { files: [] };
for (const o of made) {
  log.files = log.files.filter((f) => f.path !== o.p);
  log.files.push({ path: o.p, type: o.p.includes("/music/") ? "music" : "sfx", category: o.category, description: o.desc, source: "Generated in-house by src/audio/tools/gen-opening-audio.mjs (procedural synthesis, no samples)", license: "Owned by SIO — no third-party rights", attribution: "none required", commercialUse: true, addedAt: new Date().toISOString().slice(0, 10), sha256: createHash("sha256").update(readFileSync(o.p)).digest("hex") });
}
writeFileSync(LIC, JSON.stringify(log, null, 2) + "\n");
console.log(made.map((o) => o.p).join("\n"));
