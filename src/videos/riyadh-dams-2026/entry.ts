// Isolated entry — SIO | تقرير سدود منطقة الرياض خلال الحالة المطرية (Nov 2026). Does not touch src/Root.tsx.
// Studio:  npx remotion studio src/videos/riyadh-dams-2026/entry.ts --port 3004
// Still:   PREVIEW=1 npx remotion still src/videos/riyadh-dams-2026/entry.ts RD-Intro out/riyadh-dams/intro.png --frame=120
// Alpha:   npx remotion render src/videos/riyadh-dams-2026/entry.ts RD-Stats-Alpha exports/riyadh-dams-2026/alpha/Stats.mov
import { registerRoot } from "remotion";
import { RiyadhDamsRoot } from "./Root";

registerRoot(RiyadhDamsRoot);
