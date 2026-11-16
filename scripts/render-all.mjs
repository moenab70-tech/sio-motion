// Renders every template as ProRes 4444 + alpha into out/, bundling only once.
// Usage: npm run render:all            (all templates)
//        npm run render:all -- Stat-Row Title-Cinematic   (selected ones)
import { execFileSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const ALL = [
  "Stat-Single", "Stat-Row", "Title-Cinematic", "LowerThird-Panel", "LowerThird-Minimal",
  "Infographic-Rings", "Infographic-Bars", "Project-Card", "Project-Wide",
  "Transition-Panels", "Transition-Sweep", "Transition-Shutter",
  "Title-WithLogo", "LowerThird-WithLogo", "Project-WithLogo", "Project-Wide-WithLogo",
  "FX-Title-Rise", "FX-Title-Focus", "FX-Title-Sweep", "FX-Bars-3D", "FX-Stat-Row", "FX-Infographic",
  "FX-Scenes", "FX-Depth-3D", "FX-Particles", "FX-LightLeak",
];
const ids = process.argv.slice(2).length ? process.argv.slice(2) : ALL;
const bundleDir = mkdtempSync(join(tmpdir(), "remotion-bundle-"));
const run = (args) => execFileSync("npx", ["remotion", ...args], { stdio: "inherit" });

try {
  run(["bundle", "--out-dir", bundleDir, "--log=error"]);
  for (const id of ids) {
    run(["render", bundleDir, id, `out/${id}.mov`, "--log=error"]);
    console.log(`✓ ${id}`);
  }
  console.log(`\n✓ Rendered ${ids.length} file(s) to out/`);
} finally {
  rmSync(bundleDir, { recursive: true, force: true });
}
