// SIO audio-aware export: Final MP4 · Clean video (no audio) · Audio stems (WAV) · optional transparent ProRes.
// Uses only Remotion + the ffmpeg bundled with Remotion. Loudness: measured with loudnorm (EBU R128), then ONE
// linear gain is applied to the mix and to every stem (no limiter/compressor → no distortion; stems still sum to the mix).
//
// Usage:
//   node src/audio/tools/export.mjs --entry=src/videos/hasad-2026/entry.ts --id=Hasad-Audio-Trial-15s \
//        --name=hasad-2026-audio-trial [--lufs=-16] [--tp=-1] [--only=final,clean,stems] [--stems=vo,music,sfx] [--alpha]
// Output: exports/<name>/  (+ report.json with loudness of every file)
import { spawnSync } from "node:child_process";
import { mkdirSync, rmSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const arg = (k, d) => { const a = process.argv.find((x) => x.startsWith(`--${k}=`)); return a ? a.split("=").slice(1).join("=") : d; };
const flag = (k) => process.argv.includes(`--${k}`);
const entry = arg("entry"), id = arg("id"), name = arg("name", id);
const LUFS = Number(arg("lufs", "-16")), TP = Number(arg("tp", "-1"));
const only = new Set(arg("only", "final,clean,stems").split(","));
if (!entry || !id) { console.error("Usage: --entry=<entry.ts> --id=<CompositionId> [--name=] [--lufs=-16] [--tp=-1] [--only=final,clean,stems] [--alpha]"); process.exit(1); }

const OUT = join("exports", name), TMP = join(OUT, ".tmp");
mkdirSync(TMP, { recursive: true });
const run = (cmd, args, label) => {
  const r = spawnSync(cmd, args, { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  if (r.status !== 0) { console.error(`✗ ${label}\n${`${r.stdout}\n${r.stderr}`.trim().split("\n").slice(-12).join("\n")}`); process.exit(1); }
  return `${r.stdout}\n${r.stderr}`;
};
const render = (out, extra, label) => { run("npx", ["remotion", "render", entry, id, out, "--log=error", "--config=src/audio/tools/remotion.export.config.ts", ...extra], label); console.log(`✓ ${label}`); };
const ffmpeg = (args, label) => run("npx", ["remotion", "ffmpeg", "-hide_banner", "-nostats", "-y", ...args], label);
const measure = (file) => {
  const o = ffmpeg(["-i", file, "-vn", "-af", "loudnorm=print_format=json", "-f", "null", "-"], `measure ${file}`);
  const j = JSON.parse(o.match(/\{[\s\S]*?\}/g).pop());
  return { lufs: Number(j.input_i), truePeak: Number(j.input_tp), lra: Number(j.input_lra) };
};
const props = (solo) => `--props=${JSON.stringify({ audioSolo: solo })}`;
const report = { composition: id, entry, target: { lufs: LUFS, truePeak: TP }, files: {} };

// 1 · Mix (audio only) → measure → one linear gain
let gainDb = 0;
if (only.has("final") || only.has("stems")) {
  const rawMix = join(TMP, "mix.wav");
  render(rawMix, ["--codec=wav", props("all")], "mix (audio only)");
  const m = measure(rawMix);
  gainDb = LUFS - m.lufs;
  if (m.truePeak + gainDb > TP) gainDb = TP - m.truePeak - 0.1; // peak-safe: never push into clipping
  report.mixBeforeGain = m; report.appliedGainDb = Number(gainDb.toFixed(2));
  ffmpeg(["-i", rawMix, "-af", `volume=${gainDb.toFixed(2)}dB`, "-c:a", "pcm_s24le", "-ar", "48000", join(OUT, `${name}_Mix_48k24.wav`)], "master mix");
  report.files.mix = measure(join(OUT, `${name}_Mix_48k24.wav`));
}

// 2 · Stems (same gain as the mix)
if (only.has("stems")) for (const s of arg("stems", "vo,music,sfx").split(",")) {
  const raw = join(TMP, `${s}.wav`), out = join(OUT, `${name}_Stem_${s.toUpperCase()}_48k24.wav`);
  render(raw, ["--codec=wav", props(s)], `stem ${s}`);
  ffmpeg(["-i", raw, "-af", `volume=${gainDb.toFixed(2)}dB`, "-c:a", "pcm_s24le", "-ar", "48000", out], `stem ${s} gain`);
  report.files[`stem_${s}`] = measure(out);
}

// 3 · Clean video (no audio track) — ProRes 422 HQ for Premiere
if (only.has("clean")) {
  const out = join(OUT, `${name}_Clean_ProRes422HQ.mov`);
  render(out, ["--muted", "--codec=prores", "--prores-profile=hq", "--image-format=png", "--pixel-format=yuv422p10le"], "clean video (ProRes 422 HQ, no audio)");
  report.files.clean = { file: out, audio: "none" };
}

// 4 · Final MP4 = H.264 picture + mastered mix (AAC 320k)
if (only.has("final")) {
  const pic = join(TMP, "picture.mp4"), out = join(OUT, `${name}_Final.mp4`);
  render(pic, ["--muted", "--codec=h264", "--crf=16", "--image-format=jpeg", "--pixel-format=yuv420p"], "final picture (H.264)");
  ffmpeg(["-i", pic, "-i", join(OUT, `${name}_Mix_48k24.wav`), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out], "mux final");
  report.files.final = measure(out);
}

// 5 · Optional transparent motion (ProRes 4444 + alpha, no audio) — the existing overlay workflow, unchanged
if (flag("alpha")) {
  const out = join(OUT, `${name}_Alpha_ProRes4444.mov`);
  render(out, ["--muted", "--codec=prores", "--prores-profile=4444", "--image-format=png", "--pixel-format=yuva444p10le"], "alpha (ProRes 4444)");
  report.files.alpha = { file: out };
}

rmSync(TMP, { recursive: true, force: true });
writeFileSync(join(OUT, "report.json"), JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify(report, null, 2));
if (!existsSync(OUT)) process.exit(1);
