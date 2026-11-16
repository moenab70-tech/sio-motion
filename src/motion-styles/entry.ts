// Isolated entry point for the Motion Styles library.
// Studio:  npx remotion studio src/motion-styles/entry.ts
// Render:  npx remotion render src/motion-styles/entry.ts <CompositionId> out/motion-styles/<file>.mov
import { registerRoot } from "remotion";
import { MotionStylesRoot } from "./gallery/Root";

registerRoot(MotionStylesRoot);
