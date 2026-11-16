// Half-size JPEG of one frame for quick visual review → .cache/stills/<Id>-<frame>.jpg
// Usage: npm run still -- <CompositionId> <frame> [--props=file.json]
import { spawnSync } from "node:child_process";
import { mkdirSync } from "node:fs";
const [id, frame = "60", ...rest] = process.argv.slice(2);
if (!id) { console.error("Usage: npm run still -- <CompositionId> <frame>"); process.exit(1); }
mkdirSync(".cache/stills", { recursive: true });
const out = `.cache/stills/${id}-${frame}.jpg`;
const r = spawnSync("npx", ["remotion", "still", id, out, `--frame=${frame}`, "--scale=0.5", "--image-format=jpeg", "--log=error", ...rest], { encoding: "utf8" });
if (r.status !== 0) { console.error(`${r.stdout}\n${r.stderr}`.trim().split("\n").slice(-15).join("\n")); process.exit(1); }
console.log(out);
