// One line per file: codec/profile/pix_fmt/fps + share of transparent/opaque/semi pixels in one frame.
// Usage: npm run check:alpha -- out/A.mov out/B.mov [--at=3]
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join } from "node:path";
import { inflateSync } from "node:zlib";

const args = process.argv.slice(2);
const at = args.find((a) => a.startsWith("--at="))?.slice(5) ?? "3";
const files = args.filter((a) => !a.startsWith("--"));
const tmp = mkdtempSync(join(tmpdir(), "sio-alpha-"));

const decodeAlpha = (buf) => {
  let p = 8, w, h, ct, idat = [];
  while (p < buf.length) { const len = buf.readUInt32BE(p), t = buf.toString("ascii", p + 4, p + 8), d = buf.subarray(p + 8, p + 8 + len); if (t === "IHDR") { w = d.readUInt32BE(0); h = d.readUInt32BE(4); ct = d[9]; } if (t === "IDAT") idat.push(d); p += 12 + len; }
  if (ct !== 6) return "no alpha channel";
  const raw = inflateSync(Buffer.concat(idat)), st = w * 4, o = Buffer.alloc(st * h);
  for (let y = 0; y < h; y++) { const f = raw[y * (st + 1)]; for (let x = 0; x < st; x++) { const a = x >= 4 ? o[y * st + x - 4] : 0, b = y ? o[(y - 1) * st + x] : 0, c = x >= 4 && y ? o[(y - 1) * st + x - 4] : 0; let v = raw[y * (st + 1) + 1 + x]; if (f === 1) v += a; else if (f === 2) v += b; else if (f === 3) v += (a + b) >> 1; else if (f === 4) { const pp = a + b - c, pa = Math.abs(pp - a), pb = Math.abs(pp - b), pc = Math.abs(pp - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c; } o[y * st + x] = v & 255; } }
  let clear = 0, solid = 0, semi = 0; for (let i = 3; i < o.length; i += 4) o[i] === 0 ? clear++ : o[i] === 255 ? solid++ : semi++;
  const n = w * h, pc = (x) => `${((100 * x) / n).toFixed(1)}%`;
  return `transparent ${pc(clear)} · opaque ${pc(solid)} · semi ${pc(semi)}`;
};

try {
  for (const f of files) {
    const probe = spawnSync("npx", ["remotion", "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name,profile,pix_fmt,r_frame_rate", "-of", "csv=p=0", f], { encoding: "utf8" }).stdout.trim();
    const png = join(tmp, "f.png");
    const r = spawnSync("npx", ["remotion", "ffmpeg", "-v", "error", "-y", "-ss", at, "-i", f, "-frames:v", "1", "-pix_fmt", "rgba", "-vf", "scale=iw/2:ih/2", png], { encoding: "utf8" });
    console.log(`${basename(f)} | ${probe} | ${r.status === 0 ? decodeAlpha(readFileSync(png)) : "frame extract failed"}`);
  }
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
