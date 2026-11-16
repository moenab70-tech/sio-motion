// Quiet health check: typecheck + bundle + composition list. Prints only a short summary or the errors.
import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const step = (label, cmd, args) => {
  const r = spawnSync(cmd, args, { encoding: "utf8" });
  if (r.status !== 0) {
    console.error(`✗ ${label}\n${`${r.stdout}\n${r.stderr}`.trim().split("\n").slice(-25).join("\n")}`);
    process.exit(1);
  }
  return `${r.stdout}\n${r.stderr}`;
};

step("typecheck", "npx", ["tsc", "--noEmit"]);
const dir = mkdtempSync(join(tmpdir(), "sio-verify-"));
try {
  step("bundle", "npx", ["remotion", "bundle", "--out-dir", join(dir, "b"), "--log=error"]);
  const ids = step("compositions", "npx", ["remotion", "compositions", join(dir, "b"), "--quiet"]).trim().split("\n").filter(Boolean).pop().trim().split(/\s+/);
  console.log(`✓ typecheck  ✓ bundle  ✓ ${ids.length} compositions`);
} finally {
  rmSync(dir, { recursive: true, force: true });
}
