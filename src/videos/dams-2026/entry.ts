// Isolated entry for the dams rainfall videos (does not touch src/Root.tsx).
// Studio:  npx remotion studio src/videos/dams-2026/entry.ts --port 3003
// Preview: PREVIEW=1 npx remotion render src/videos/dams-2026/entry.ts Dam-Harimla out/dams-2026/Harimla_preview.mp4
// Final:   PREVIEW=1 npx remotion render src/videos/dams-2026/entry.ts Dam-Harimla exports/dams-2026/Harimla_Dam_Final.mp4 --crf=16 --jpeg-quality=95
import { registerRoot } from "remotion";
import { DamsRoot } from "./Root";

registerRoot(DamsRoot);
