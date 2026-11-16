// Renders every shot of a production to exports/<production>/<preset>/.
// Usage:
//   npm run production:render -- <production>                       (ProRes 4444 + alpha)
//   npm run production:render -- <production> --preset=preview-h264  (review MP4s)
//   npm run production:render -- <production> --only=01-title,03-stats
import { execFileSync, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const args = process.argv.slice(2);
const name = args.find((a) => !a.startsWith("--"));
const opt = (k) => args.find((a) => a.startsWith(`--${k}=`))?.split("=")[1];
if (!name) {
  console.error("Usage: npm run production:render -- <production> [--preset=<id>] [--only=<shot,shot>]");
  process.exit(1);
}

const file = join("productions", name, "production.json");
if (!existsSync(file)) throw new Error(`Not found: ${file}`);
const production = JSON.parse(readFileSync(file, "utf8"));
const presets = JSON.parse(readFileSync("export-presets.json", "utf8"));
const presetId = opt("preset") ?? presets.default;
const preset = presets.presets[presetId];
if (!preset) throw new Error(`Unknown preset "${presetId}". Available: ${Object.keys(presets.presets).join(", ")}`);

const only = opt("only")?.split(",");
const shots = production.shots.filter((s) => !only || only.includes(s.id));
const ids = new Set();
for (const s of production.shots) {
  if (!s.id || !s.template) throw new Error(`Each shot needs "id" and "template": ${JSON.stringify(s)}`);
  if (ids.has(s.id)) throw new Error(`Duplicate shot id "${s.id}"`);
  ids.add(s.id);
}

const work = mkdtempSync(join(tmpdir(), "sio-production-"));
const env = { ...process.env, ...preset.env };
const run = (a) => execFileSync("npx", ["remotion", ...a], { env, stdio: "inherit" });
const outDir = join("exports", name, preset.folder);
mkdirSync(outDir, { recursive: true });

try {
  console.log(`\n▶ ${production.title ?? name} — ${shots.length} shot(s) — preset ${presetId}`);
  run(["bundle", "--out-dir", join(work, "bundle"), "--log=error"]);
  // `remotion compositions --quiet` prints the id list on its last output line (stdout or stderr depending on version)
  const listing = spawnSync("npx", ["remotion", "compositions", join(work, "bundle"), "--quiet"], { env, encoding: "utf8" });
  const lastLine = `${listing.stdout}\n${listing.stderr}`.trim().split("\n").filter(Boolean).pop() ?? "";
  const available = new Set(lastLine.trim().split(/\s+/));
  const missing = shots.filter((s) => !available.has(s.template));
  if (missing.length) throw new Error(`Unknown template(s): ${missing.map((s) => `${s.id} → ${s.template}`).join(", ")}\nAvailable: ${[...available].join(", ")}`);

  const results = [];
  for (const s of shots) {
    const propsFile = join(work, `${s.id}.json`);
    writeFileSync(propsFile, JSON.stringify(s.props ?? {}));
    const output = join(outDir, `${s.id}.${preset.extension}`);
    console.log(`\n● ${s.id}  (${s.template})`);
    run(["render", join(work, "bundle"), s.template, output, `--props=${propsFile}`, "--log=error", ...preset.flags]);
    results.push({ id: s.id, template: s.template, file: output, megabytes: +(statSync(output).size / 1e6).toFixed(1) });
  }

  const reportFile = join("exports", name, "render-report.json");
  const report = existsSync(reportFile) ? JSON.parse(readFileSync(reportFile, "utf8")) : {};
  report[presetId] = { renderedAt: new Date().toISOString(), preset: preset.description, shots: results };
  writeFileSync(reportFile, JSON.stringify(report, null, 2));
  console.log(`\n✓ ${results.length} file(s) → ${outDir}`);
} finally {
  rmSync(work, { recursive: true, force: true });
}
