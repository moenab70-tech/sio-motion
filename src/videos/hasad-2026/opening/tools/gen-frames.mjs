// Batch image generation with local FLUX.1-schnell (mflux). Reusable for any SIO illustration job.
// Usage: node src/videos/hasad-2026/opening/tools/gen-frames.mjs <prompts.json> <outDir> [id …]
// prompts.json: { style, characters: {key: description}, frames: [{ id, w, h, seed, prompt with {key} }] }
// Skips frames that already exist (delete a file to regenerate it). Writes <outDir>/log.json (time per frame).
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const [file, outDir, ...only] = process.argv.slice(2);
const cfg = JSON.parse(readFileSync(file, "utf8"));
const MODEL = process.env.SIO_FLUX_MODEL ?? join(homedir(), ".cache/sio-models/flux1-schnell-mflux-4bit");
const BIN = join(homedir(), ".local/bin/mflux-generate");
mkdirSync(outDir, { recursive: true });
const logPath = join(outDir, "log.json");
const log = existsSync(logPath) ? JSON.parse(readFileSync(logPath, "utf8")) : {};

for (const f of cfg.frames) {
  if (only.length && !only.includes(f.id)) continue;
  const out = join(outDir, `${f.id}.png`);
  if (existsSync(out)) { console.log(`= ${f.id} (exists)`); continue; }
  const body = f.prompt.replace(/\{(\w+)\}/g, (_, k) => cfg.characters[k] ?? k);
  const prompt = `${cfg.style}. ${body}`;
  const t0 = Date.now();
  const args = ["--model", MODEL, "--base-model", "schnell", "--steps", String(f.steps ?? 4), "--seed", String(f.seed ?? 42), "--width", String(f.w), "--height", String(f.h), "--output", out, "--prompt", prompt];
  // img2img refine: { init: "path.png", strength: 0.7 } — higher strength = closer to the init image
  if (f.init) args.push("--image-path", f.init, "--image-strength", String(f.strength ?? 0.7));
  const r = spawnSync(BIN, args, { encoding: "utf8" });
  if (r.status !== 0 || !existsSync(out)) { console.error(`✗ ${f.id}\n${r.stderr.split("\n").slice(-6).join("\n")}`); continue; }
  log[f.id] = { seconds: Math.round((Date.now() - t0) / 1000), seed: f.seed, w: f.w, h: f.h, prompt, model: "FLUX.1-schnell 4-bit (Apache-2.0) via mflux", at: new Date().toISOString() };
  writeFileSync(logPath, JSON.stringify(log, null, 2) + "\n");
  console.log(`✓ ${f.id}  ${log[f.id].seconds}s`);
}
