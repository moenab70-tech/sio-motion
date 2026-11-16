// Generates the in-house SFX library + a placeholder ambient music bed, procedurally.
// No samples, no downloads → owned outright by SIO, no licence risk. Deterministic (seeded).
// Usage: node src/audio/tools/gen-sfx.mjs
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { biquad, buf, finish, pan, reverb, rng, SR, writeWav } from "./wav.mjs";

const SFX = "public/audio/sfx/generated", MUS = "public/audio/music/generated";
mkdirSync(SFX, { recursive: true }); mkdirSync(MUS, { recursive: true });
const env = (t, a, d) => (t < a ? t / a : Math.exp(-(t - a) / d)); // attack + exp decay
const noise = (sec, seed) => { const r = rng(seed), x = buf(sec); for (let i = 0; i < x.length; i++) x[i] = r() * 2 - 1; return x; };
const out = [];
const save = (dir, name, chs, desc, category, dbfs = -3) => {
  const path = `${dir}/${name}.wav`; writeWav(path, finish(chs, dbfs));
  out.push({ path, desc, category });
};

// 1 · Whoosh — band-passed noise sweep with RTL pan (right → left), soft tail.
{
  const d = 1.1, x = noise(d, 11);
  const f = biquad(x, "bp", (t) => 300 + 2400 * Math.sin(Math.PI * Math.min(1, t / 0.8)) ** 2, 0.9);
  for (let i = 0; i < f.length; i++) { const t = i / SR; f[i] *= Math.sin(Math.PI * Math.min(1, t / 0.85)) ** 2; }
  const [L, R] = pan(f, (t) => 0.8 - 1.6 * Math.min(1, t / 0.85));
  const wetL = reverb(L, { mix: 0.18 })[0], wetR = reverb(R, { mix: 0.18 })[1];
  save(SFX, "whoosh-soft", [wetL, wetR], "Whoosh: soft air sweep, right→left (RTL)", "Whoosh");
}
// 2 · Soft impact — low sine with pitch drop + muffled thump, roomy.
{
  const d = 1.8, x = buf(d), r = rng(22); let ph = 0;
  for (let i = 0; i < x.length; i++) { const t = i / SR, f = 48 + 34 * Math.exp(-t / 0.09); ph += (2 * Math.PI * f) / SR; x[i] = Math.sin(ph) * env(t, 0.004, 0.42) + (r() * 2 - 1) * env(t, 0.001, 0.025) * 0.35; }
  const y = biquad(x, "lp", 900);
  save(SFX, "impact-soft", reverb(y, { size: 1.2, mix: 0.22 }), "Soft Impact: warm low hit, no distortion", "Soft Impact");
}
// 3 · UI click — two tiny sine ticks.
{
  const x = buf(0.14);
  for (let i = 0; i < x.length; i++) { const t = i / SR; x[i] = Math.sin(2 * Math.PI * 2300 * t) * env(t, 0.0005, 0.008) + 0.6 * Math.sin(2 * Math.PI * 1500 * (t - 0.045)) * (t > 0.045 ? env(t - 0.045, 0.0005, 0.01) : 0); }
  save(SFX, "ui-click", [x, x.slice()], "UI Click: clean double tick", "UI Click", -6);
}
// 4 · Digital transition — stepped blips + falling filtered noise.
{
  const d = 0.9, x = buf(d), n = noise(d, 44), hp = biquad(n, "bp", (t) => 6000 - 5000 * Math.min(1, t / 0.7), 1.2);
  [880, 1320, 1760].forEach((f, k) => { const s = 0.06 * k; for (let i = 0; i < x.length; i++) { const t = i / SR - s; if (t > 0) x[i] += 0.5 * Math.sin(2 * Math.PI * f * t) * env(t, 0.002, 0.05); } });
  for (let i = 0; i < x.length; i++) x[i] += hp[i] * 0.35 * env(i / SR, 0.02, 0.25);
  save(SFX, "digital-transition", reverb(x, { size: 0.7, mix: 0.2 }), "Digital Transition: stepped blips + data sweep", "Digital Transition", -4);
}
// 5 · Ambient atmosphere — 12 s brown-ish noise bed, slow filter LFO, stereo.
{
  const d = 12, chs = [0, 1].map((c) => { const n = noise(d, 55 + c); let b = 0; const br = n.map((v) => (b = (b + v * 0.02) * 0.998)); return biquad(br, "lp", (t) => 380 + 200 * Math.sin(2 * Math.PI * 0.07 * t + c), 0.7); });
  for (const c of chs) for (let i = 0; i < c.length; i++) { const t = i / SR; c[i] *= Math.min(1, t / 2, (d - t) / 2); }
  save(SFX, "ambient-atmosphere", chs, "Ambient Atmosphere: calm low room tone (12 s)", "Ambient Atmosphere", -12);
}
// 6 · Cinematic rise — noise + sine glissando crescendo, short release (lands on a cut).
{
  const d = 2.6, x = buf(d), n = noise(d, 66), bp = biquad(n, "bp", (t) => 200 * Math.pow(20, t / 2.4), 1.4); let ph = 0;
  for (let i = 0; i < x.length; i++) { const t = i / SR, f = 110 * Math.pow(4, Math.min(1, t / 2.4)); ph += (2 * Math.PI * f) / SR; const a = Math.pow(Math.min(1, t / 2.4), 2.2) * (t > 2.45 ? Math.max(0, 1 - (t - 2.45) / 0.12) : 1); x[i] = a * (0.5 * Math.sin(ph) + 0.2 * Math.sin(2 * ph) + 0.6 * bp[i]); }
  save(SFX, "cinematic-rise", reverb(x, { size: 1.1, mix: 0.25 }), "Cinematic Rise: 2.5 s crescendo into a cut", "Cinematic Rise", -4);
}
// 7 · Subtle mechanical — soft precise ticks + faint hum (engineering feel).
{
  const d = 3, x = buf(d), r = rng(77);
  for (let k = 0; k < d * 6; k++) { const s = k / 6 + (r() - 0.5) * 0.004; for (let i = Math.round(s * SR); i < Math.min(x.length, Math.round((s + 0.03) * SR)); i++) { const t = i / SR - s; x[i] += Math.sin(2 * Math.PI * 3100 * t) * env(t, 0.0003, 0.004) * (k % 4 === 0 ? 1 : 0.55); } }
  for (let i = 0; i < x.length; i++) x[i] += 0.04 * Math.sin(2 * Math.PI * 100 * (i / SR)) * Math.min(1, i / SR / 0.3, (d - i / SR) / 0.3);
  save(SFX, "mechanical-subtle", reverb(biquad(x, "lp", 7000), { size: 0.5, mix: 0.15 }), "Subtle Mechanical: precise ticks + faint hum", "Subtle Mechanical", -8);
}

// Placeholder music bed — "Corporate Cinematic / Inspirational" pad, 90 BPM, D minor → Bb → F → C.
// Generated in-house: fully owned, but it is a functional placeholder, not a composed score.
// cycles = passes through the 4-chord loop; arp = which chord indices get the bell arpeggio (shapes the arc).
for (const [cycles, file, label, arp] of [
  [2, "placeholder-ambient-corporate", "~44 s", () => true],
  // ~87 s full-film bed: calm opening (1st pass) → motion during the awards → calm again for the logo outro (last pass)
  [4, "placeholder-ambient-corporate-long", "~87 s, calm intro / moving middle / calm ending", (k) => k >= 4 && k < 12],
]) {
  const bpm = 90, beat = 60 / bpm, bar = 4 * beat, chords = [[50, 57, 60, 64, 65], [46, 53, 57, 62, 65], [41, 53, 57, 60, 64], [48, 55, 60, 62, 67]];
  const bars = 2, d = chords.length * bars * bar * cycles + 2, L = buf(d), R = buf(d); const hz = (m) => 440 * Math.pow(2, (m - 69) / 12);
  const seq = Array.from({ length: cycles }, () => chords).flat();
  seq.forEach((ch, k) => {
    const s = k * bars * bar, e = s + bars * bar;
    ch.forEach((m, v) => [-0.06, 0, 0.06].forEach((det, j) => { // 3 detuned voices per note
      const f = hz(m) * Math.pow(2, det / 12), amp = (v === 0 ? 0.11 : 0.06) / 3, p = (j - 1) * 0.5;
      for (let i = Math.round(s * SR); i < Math.min(L.length, Math.round((e + 1.6) * SR)); i++) {
        const t = i / SR - s, a = Math.min(1, t / 1.4) * (i / SR > e ? Math.max(0, 1 - (i / SR - e) / 1.6) : 1);
        const w = Math.sin(2 * Math.PI * f * t) + 0.18 * Math.sin(4 * Math.PI * f * t); const val = w * a * amp;
        L[i] += val * (1 - p) * 0.8; R[i] += val * (1 + p) * 0.8;
      }
    }));
    // bass root
    for (let i = Math.round(s * SR); i < Math.min(L.length, Math.round((e + 0.8) * SR)); i++) { const t = i / SR - s, a = Math.min(1, t / 0.3) * (i / SR > e ? Math.max(0, 1 - (i / SR - e) / 0.8) : 1); const v = Math.sin(2 * Math.PI * hz(ch[0] - 12) * t) * 0.16 * a; L[i] += v; R[i] += v; }
    // soft bell arpeggio on eighths
    if (arp(k)) for (let b = 0; b < bars * 8; b++) { const m = ch[[1, 2, 3, 4, 3, 2, 4, 3][b % 8]] + 12, st = s + (b * beat) / 2, pn = b % 2 ? 0.3 : -0.3;
      for (let i = Math.round(st * SR); i < Math.min(L.length, Math.round((st + 1.2) * SR)); i++) { const t = i / SR - st, v = (Math.sin(2 * Math.PI * hz(m) * t) + 0.3 * Math.sin(2 * Math.PI * hz(m) * 2.01 * t)) * env(t, 0.004, 0.32) * 0.028; L[i] += v * (1 - pn); R[i] += v * (1 + pn); } }
  });
  const lp = [biquad(L, "lp", 5200), biquad(R, "lp", 5200)];
  const wet = [reverb(lp[0], { size: 1.4, mix: 0.3 })[0], reverb(lp[1], { size: 1.4, mix: 0.3 })[1]];
  for (const c of wet) for (let i = 0; i < c.length; i++) { const t = i / SR; c[i] *= Math.min(1, t / 1.5, (d - t) / 2.5); }
  save(MUS, file, wet, `In-house music bed: calm corporate/inspirational pad, 90 BPM, ${label}`, "Corporate Cinematic, Inspirational, Ambient", -6);
}

// Licence log — every generated file is recorded with its hash.
const LIC = "public/audio/LICENSES.json";
const log = existsSync(LIC) ? JSON.parse(readFileSync(LIC, "utf8")) : { notes: "Source & licence of every audio file used by SIO productions. Never add a file without an entry.", files: [] };
for (const o of out) {
  const sha256 = createHash("sha256").update(readFileSync(o.path)).digest("hex");
  log.files = log.files.filter((f) => f.path !== o.path);
  log.files.push({ path: o.path, type: o.path.includes("/music/") ? "music" : "sfx", category: o.category, description: o.desc, source: "Generated in-house by src/audio/tools/gen-sfx.mjs (procedural synthesis, no samples)", license: "Owned by SIO — no third-party rights", attribution: "none required", commercialUse: true, addedAt: new Date().toISOString().slice(0, 10), sha256 });
}
writeFileSync(LIC, JSON.stringify(log, null, 2) + "\n");
console.log(out.map((o) => o.path).join("\n"));
