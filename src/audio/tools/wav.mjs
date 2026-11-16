// Minimal WAV + DSP helpers for the SIO audio tools (no dependencies).
import { readFileSync, writeFileSync } from "node:fs";

export const SR = 48000;

/** Writes stereo/mono float channels (−1…1) as 24-bit PCM WAV. */
export const writeWav = (path, channels, sr = SR) => {
  const n = channels[0].length, ch = channels.length, bps = 3;
  const buf = Buffer.alloc(44 + n * ch * bps);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * ch * bps, 4); buf.write("WAVE", 8);
  buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(ch, 22);
  buf.writeUInt32LE(sr, 24); buf.writeUInt32LE(sr * ch * bps, 28); buf.writeUInt16LE(ch * bps, 32); buf.writeUInt16LE(24, 34);
  buf.write("data", 36); buf.writeUInt32LE(n * ch * bps, 40);
  let o = 44;
  for (let i = 0; i < n; i++) for (let c = 0; c < ch; c++) {
    const v = Math.max(-1, Math.min(1, channels[c][i]));
    buf.writeIntLE(Math.round(v * 8388607), o, 3); o += 3;
  }
  writeFileSync(path, buf);
};

/** Reads duration (s), sample rate and channels from a PCM WAV header. */
export const wavInfo = (path) => {
  const b = readFileSync(path);
  let p = 12, sr = 0, ch = 0, bits = 0, dataLen = 0;
  while (p < b.length - 8) {
    const id = b.toString("ascii", p, p + 4), len = b.readUInt32LE(p + 4);
    if (id === "fmt ") { ch = b.readUInt16LE(p + 10); sr = b.readUInt32LE(p + 12); bits = b.readUInt16LE(p + 22); }
    if (id === "data") { dataLen = len; break; }
    p += 8 + len + (len % 2);
  }
  return { sampleRate: sr, channels: ch, bits, duration: dataLen / (sr * ch * (bits / 8)) };
};

/** Deterministic PRNG so every generated asset is reproducible. */
export const rng = (seed) => () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

export const buf = (sec) => new Float32Array(Math.round(sec * SR));

/** RBJ biquad (lowpass / highpass / bandpass) with per-sample cutoff function. */
export const biquad = (x, type, freqAt, q = 0.707) => {
  const y = new Float32Array(x.length); let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  for (let i = 0; i < x.length; i++) {
    const f = Math.min(SR * 0.45, Math.max(20, typeof freqAt === "function" ? freqAt(i / SR) : freqAt));
    const w = (2 * Math.PI * f) / SR, cs = Math.cos(w), al = Math.sin(w) / (2 * q);
    let b0, b1, b2; const a0 = 1 + al, a1 = -2 * cs, a2 = 1 - al;
    if (type === "lp") { b0 = (1 - cs) / 2; b1 = 1 - cs; b2 = (1 - cs) / 2; }
    else if (type === "hp") { b0 = (1 + cs) / 2; b1 = -(1 + cs); b2 = (1 + cs) / 2; }
    else { b0 = al; b1 = 0; b2 = -al; }
    const v = (b0 * x[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2) / a0;
    x2 = x1; x1 = x[i]; y2 = y1; y1 = v; y[i] = v;
  }
  return y;
};

/** Small Schroeder reverb → returns [L, R] wet signals (decorrelated). */
export const reverb = (x, { size = 1, damp = 0.4, mix = 0.25 } = {}) => {
  const combs = [1557, 1617, 1491, 1422, 1277, 1356, 1188, 1116].map((d) => Math.round(d * size * (SR / 44100)));
  const out = [new Float32Array(x.length), new Float32Array(x.length)];
  combs.forEach((d, k) => {
    const line = new Float32Array(d), side = out[k % 2]; let idx = 0, lp = 0;
    for (let i = 0; i < x.length; i++) { const o = line[idx]; lp = o * (1 - damp) + lp * damp; line[idx] = x[i] * 0.015 + lp * 0.84; idx = (idx + 1) % d; side[i] += o; }
  });
  for (const s of out) for (const a of [556, 441]) {
    const d = Math.round(a * size * (SR / 44100)), line = new Float32Array(d); let idx = 0;
    for (let i = 0; i < s.length; i++) { const b = line[idx], v = -s[i] + b; line[idx] = s[i] + b * 0.5; s[i] = v; idx = (idx + 1) % d; }
  }
  return out.map((s) => s.map((v, i) => x[i] * (1 - mix) + v * mix));
};

/** Scales so the highest peak is at `dbfs`, adds 5 ms edge fades (no clicks). */
export const finish = (chs, dbfs = -3) => {
  let peak = 0; for (const c of chs) for (const v of c) peak = Math.max(peak, Math.abs(v));
  const g = peak > 0 ? Math.pow(10, dbfs / 20) / peak : 1, e = Math.round(0.005 * SR);
  return chs.map((c) => c.map((v, i) => v * g * Math.min(1, i / e, (c.length - 1 - i) / e)));
};

export const pan = (x, posAt) => { // posAt(t): −1 = left … +1 = right (equal power)
  const L = new Float32Array(x.length), R = new Float32Array(x.length);
  for (let i = 0; i < x.length; i++) { const p = (posAt(i / SR) + 1) * Math.PI / 4; L[i] = x[i] * Math.cos(p); R[i] = x[i] * Math.sin(p); }
  return [L, R];
};
