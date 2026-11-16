import type React from "react";
import type { MotionStyleBaseProps } from "../core/types";

/** A registered Motion Style. Add new styles by creating a file in styles/ and calling registerStyle() in registry/index.ts. */
export type MotionStyleDef<P extends MotionStyleBaseProps = MotionStyleBaseProps> = {
  id: string; // PascalCase, used in composition ids (MS-<id>-…)
  name: { ar: string; en: string };
  description: string;
  component: React.FC<P>;
  durationInFrames: number; // default at 30 fps
  supportsTransparency: boolean;
  presets: { institutional: P; experimental: P; english: P };
  notes?: string; // limitations
};
