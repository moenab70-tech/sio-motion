// Writes Grease Pencil specs from linework.ts and renders them in Blender (transparent PNG sequences).
// Usage: node src/videos/hasad-2026/opening/tools/render-linework.mts [1B 2B 3B]
import { spawnSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
// dynamic import: Node strips the types itself; keeps tsc (which checks src/) happy
type LineSet = { w: number; h: number; frames: number; lines: unknown[] };
const { LW_1B, LW_2B, LW_3B } = (await import(new URL("../linework.ts", import.meta.url).href)) as { LW_1B: LineSet; LW_2B: LineSet[]; LW_3B: LineSet };

const ROOT = resolve(import.meta.dirname, "../../../../..");
const OUT = `${ROOT}/public/media/opening/lines`;
const SPEC = `${ROOT}/src/videos/hasad-2026/opening/blender/lines`;
const BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender";
mkdirSync(SPEC, { recursive: true });
const jobs: [string, LineSet][] = [["1B", LW_1B], ...LW_2B.map((s, i) => [`2B-sheet${i}`, s] as [string, LineSet]), ["3B", LW_3B]];
const only = process.argv.slice(2);
for (const [id, set] of jobs) {
  if (only.length && !only.some((o) => id.startsWith(o))) continue;
  const spec = { ...set, out: `${OUT}/${id}/` };
  const file = `${SPEC}/${id}.json`;
  writeFileSync(file, JSON.stringify(spec));
  const r = spawnSync(BLENDER, ["-b", "--factory-startup", "-P", `${ROOT}/src/videos/hasad-2026/opening/blender/gp_lines.py`, "--", file], { encoding: "utf8" });
  const ok = /GP_LINES_OK/.test(r.stdout);
  console.log(`${ok ? "✓" : "✗"} ${id}${ok ? "" : "\n" + (r.stdout + r.stderr).split("\n").filter((l) => /Error|rror:|Traceback/.test(l)).slice(-6).join("\n")}`);
}
