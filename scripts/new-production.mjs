// Creates productions/<name>/ from the template. Usage: npm run production:new -- <name>
import { cpSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const name = process.argv[2];
if (!name || !/^[a-z0-9][a-z0-9-]*$/.test(name)) {
  console.error("Usage: npm run production:new -- <name>   (lowercase letters, digits, dashes)");
  process.exit(1);
}
const dest = join("productions", name);
if (existsSync(dest)) throw new Error(`${dest} already exists — nothing was overwritten.`);
cpSync(join("productions", "_template"), dest, { recursive: true });
const f = join(dest, "production.json");
const p = JSON.parse(readFileSync(f, "utf8"));
p.title = name;
p.createdAt = new Date().toISOString().slice(0, 10);
writeFileSync(f, JSON.stringify(p, null, 2) + "\n");
console.log(`✓ Created ${dest}/production.json — edit the shots, then: npm run production:render -- ${name}`);
