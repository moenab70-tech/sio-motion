// Local Arabic TTS (Piper voice via sherpa-onnx 1.13.8 CLI — fully offline, nothing uploaded).
// Usage: node src/audio/tools/tts-piper.mjs <lines.json> <outDir>
//   lines.json = [{ "id": "vo-01", "text": "…" }, …]   → <outDir>/<id>.wav + <outDir>/manifest.json (durations)
// Tools live outside the project:  $SIO_AUDIO_TOOLS (default ~/Library/Application Support/sio-audio)
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { wavInfo } from "./wav.mjs";

const [linesFile, outDir] = process.argv.slice(2);
if (!linesFile || !outDir) { console.error("Usage: node src/audio/tools/tts-piper.mjs <lines.json> <outDir>"); process.exit(1); }
const TOOLS = process.env.SIO_AUDIO_TOOLS ?? join(homedir(), "Library/Application Support/sio-audio");
const BIN = join(TOOLS, "sherpa-onnx-v1.13.8-osx-arm64-shared/bin/sherpa-onnx-offline-tts");
const VOICE = process.env.SIO_TTS_VOICE ?? "vits-piper-ar_JO-kareem-medium";
const V = join(TOOLS, "voices", VOICE);
if (!existsSync(BIN) || !existsSync(V)) { console.error(`TTS tools not found in ${TOOLS}`); process.exit(1); }
const model = join(V, `${VOICE.replace("vits-piper-", "")}.onnx`);
const lengthScale = process.env.SIO_TTS_LENGTH ?? "1.08"; // >1 = slower, calmer institutional delivery

mkdirSync(outDir, { recursive: true });
const lines = JSON.parse(readFileSync(linesFile, "utf8"));
const manifest = { engine: "sherpa-onnx 1.13.8 (Apache-2.0)", voice: VOICE, lengthScale: Number(lengthScale), generatedAt: new Date().toISOString(), clips: [] };
for (const l of lines) {
  const file = join(outDir, `${l.id}.wav`);
  const r = spawnSync(BIN, [`--vits-model=${model}`, `--vits-tokens=${join(V, "tokens.txt")}`, `--vits-data-dir=${join(V, "espeak-ng-data")}`, `--vits-length-scale=${lengthScale}`, "--num-threads=4", `--output-filename=${file}`, l.text], { encoding: "utf8" });
  if (r.status !== 0 || !existsSync(file)) { console.error(`✗ ${l.id}\n${r.stderr.split("\n").slice(-5).join("\n")}`); process.exit(1); }
  const info = wavInfo(file);
  manifest.clips.push({ id: l.id, text: l.text, file, durationInSeconds: Number(info.duration.toFixed(3)), sampleRate: info.sampleRate });
  console.log(`✓ ${l.id}  ${info.duration.toFixed(2)} s`);
}
writeFileSync(join(outDir, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
