// Motion Styles verification suite. Run: node src/motion-styles/tests/run.mjs
// Checks: typecheck, registry/compositions, every style renders (all variants), determinism,
// configurable duration + colour, transparent ProRes 4444 export, untouched production files.
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { inflateSync } from "node:zlib";

const ENTRY = "src/motion-styles/entry.ts";
const STYLES = ["KineticType", "Blueprint", "Isometric", "Holographic", "Particles", "LiquidMorph", "SplitFlap", "FlowLines", "NetworkMap", "Timeline", "ProcessFlow", "Charts", "SplitCompare", "LineArt", "GeometricPattern", "Topographic", "RadarScan", "DataStream", "ParallaxLayers", "SwissGrid"];
const ONLY = process.argv.slice(2); // optional: limit render checks to these styles
const tmp = mkdtempSync(join(tmpdir(), "ms-test-"));
const bundle = join(tmp, "b");
let failed = 0;
const ok = (m) => console.log(`✓ ${m}`);
const bad = (m) => { failed++; console.log(`✗ ${m}`); };
const sh = (cmd, args) => spawnSync(cmd, args, { encoding: "utf8", maxBuffer: 1 << 26 });
const remotion = (...a) => sh("npx", ["remotion", ...a]);
const sha = (f) => createHash("sha256").update(readFileSync(f)).digest("hex");

const pngPixels = (file) => {
  const buf = readFileSync(file); let p = 8, w, h, ct, idat = [];
  while (p < buf.length) { const len = buf.readUInt32BE(p), t = buf.toString("ascii", p + 4, p + 8), d = buf.subarray(p + 8, p + 8 + len); if (t === "IHDR") { w = d.readUInt32BE(0); h = d.readUInt32BE(4); ct = d[9]; } if (t === "IDAT") idat.push(d); p += 12 + len; }
  const bpp = ct === 6 ? 4 : 3, raw = inflateSync(Buffer.concat(idat)), st = w * bpp, o = Buffer.alloc(st * h);
  for (let y = 0; y < h; y++) { const f = raw[y * (st + 1)]; for (let x = 0; x < st; x++) { const a = x >= bpp ? o[y * st + x - bpp] : 0, b = y ? o[(y - 1) * st + x] : 0, c = x >= bpp && y ? o[(y - 1) * st + x - bpp] : 0; let v = raw[y * (st + 1) + 1 + x]; if (f === 1) v += a; else if (f === 2) v += b; else if (f === 3) v += (a + b) >> 1; else if (f === 4) { const pp = a + b - c, pa = Math.abs(pp - a), pb = Math.abs(pp - b), pc = Math.abs(pp - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c; } o[y * st + x] = v & 255; } }
  return { w, h, bpp, o };
};

try {
  // 1 typecheck
  sh("npx", ["tsc", "--noEmit"]).status === 0 ? ok("typecheck") : bad("typecheck");

  // 2 bundle + compositions
  remotion("bundle", ENTRY, "--out-dir", bundle, "--log=error").status === 0 ? ok("bundle (isolated entry)") : bad("bundle");
  const list = remotion("compositions", bundle, "--quiet");
  const ids = `${list.stdout}\n${list.stderr}`.trim().split("\n").filter(Boolean).pop().trim().split(/\s+/);
  const expected = STYLES.length * 3 + STYLES.length + 1;
  ids.length === expected ? ok(`${ids.length} compositions registered`) : bad(`expected ${expected} compositions, got ${ids.length}`);

  // 3 every style × variant renders (mid frame)
  for (const s of STYLES.filter((x) => !ONLY.length || ONLY.includes(x))) for (const v of ["Institutional", "Experimental", "English"]) {
    const id = `MS-${s}-${v}`;
    const t0 = Date.now();
    const r = remotion("still", bundle, id, join(tmp, `${id}.png`), "--frame=120", "--scale=0.25", "--log=error");
    r.status === 0 ? ok(`${id} renders (${Date.now() - t0} ms)`) : bad(`${id}: ${r.stderr.slice(-300)}`);
  }

  // 4 determinism (particles + liquid): same frame twice → identical pixels
  for (const id of ["MS-Particles-Institutional", "MS-LiquidMorph-Experimental"]) {
    remotion("still", bundle, id, join(tmp, "d1.png"), "--frame=100", "--scale=0.5", "--log=error");
    remotion("still", bundle, id, join(tmp, "d2.png"), "--frame=100", "--scale=0.5", "--log=error");
    sha(join(tmp, "d1.png")) === sha(join(tmp, "d2.png")) ? ok(`${id} deterministic`) : bad(`${id} not deterministic`);
  }

  // 5 configurable duration
  writeFileSync(join(tmp, "dur.json"), JSON.stringify({ durationInFrames: 90 }));
  const meta = remotion("compositions", bundle, "--props", join(tmp, "dur.json"));
  /MS-KineticType-Institutional\s+30\s+1920x1080\s+90/.test(`${meta.stdout}${meta.stderr}`.replace(/\u001b\[[0-9;]*m/g, "")) ? ok("durationInFrames prop → 90-frame composition") : bad("duration override not applied");

  // 6 configurable colour: force text red, expect red pixels
  writeFileSync(join(tmp, "col.json"), JSON.stringify({ colors: { text: "#FF0000" }, transparent: false }));
  remotion("still", bundle, "MS-KineticType-Institutional", join(tmp, "col.png"), "--frame=60", "--scale=0.5", "--props", join(tmp, "col.json"), "--log=error");
  { const { o, bpp } = pngPixels(join(tmp, "col.png")); let red = 0; for (let i = 0; i < o.length; i += bpp) if (o[i] > 200 && o[i + 1] < 60 && o[i + 2] < 60) red++; red > 500 ? ok(`colour override (red text pixels: ${red})`) : bad("colour override not visible"); }

  // 7 transparent ProRes 4444 exports
  // exports go to the temp dir (deleted after the run) — avoids duplicate renders; deliverables live in outputs/
  const msOut = join(tmp, "exports");
  mkdirSync(msOut, { recursive: true });
  for (const id of ["MS-Holographic-Institutional", "MS-Particles-Institutional", "MS-FlowLines-Institutional", "MS-Charts-Institutional", "MS-GeometricPattern-Institutional", "MS-Topographic-Institutional", "MS-RadarScan-Institutional", "MS-SwissGrid-Institutional"]) {
    const t0 = Date.now();
    const r = remotion("render", bundle, id, join(msOut, `${id}.mov`), "--log=error");
    if (r.status !== 0) { bad(`${id} ProRes export failed`); continue; }
    const probe = remotion("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name,profile,pix_fmt", "-of", "csv=p=0", join(msOut, `${id}.mov`)).stdout.trim();
    remotion("ffmpeg", "-v", "error", "-y", "-ss", "4", "-i", join(msOut, `${id}.mov`), "-frames:v", "1", "-pix_fmt", "rgba", join(tmp, "a.png"));
    const { o } = pngPixels(join(tmp, "a.png")); let clear = 0; for (let i = 3; i < o.length; i += 4) if (o[i] === 0) clear++;
    const pct = ((100 * clear) / (o.length / 4)).toFixed(1);
    probe.includes("yuva444p") && clear > 0 ? ok(`${id} → ${probe}, ${pct}% transparent (${((Date.now() - t0) / 1000).toFixed(0)} s, ${(statSync(join(msOut, `${id}.mov`)).size / 1e6).toFixed(0)} MB)`) : bad(`${id} alpha check failed (${probe})`);
  }

  // 8 production files unchanged vs. baseline
  const base = ".cache/audit/baseline.sha256";
  if (existsSync(base)) {
    const changed = readFileSync(base, "utf8").trim().split("\n").map((l) => [l.slice(0, 64), l.slice(66)]).filter(([h, f]) => !existsSync(f) || sha(f) !== h).map(([, f]) => f);
    changed.length === 0 ? ok("all baseline files unchanged") : bad(`changed baseline files: ${changed.join(", ")}`);
  }
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
console.log(failed ? `\n${failed} check(s) failed` : "\nAll checks passed");
process.exit(failed ? 1 : 0);
