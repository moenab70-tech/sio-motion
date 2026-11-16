import React from "react";
import { AbsoluteFill } from "remotion";
import type { MotionCtx } from "./useMotionStyle";

/** Root wrapper: optional opaque background, direction, envelope. */
export const Stage: React.FC<{ ctx: MotionCtx; children: React.ReactNode; fade?: boolean }> = ({ ctx, children, fade = true }) => (
  <AbsoluteFill style={{ direction: ctx.dir, background: ctx.transparent ? undefined : ctx.palette.background, overflow: "hidden" }}>
    <AbsoluteFill style={{ opacity: fade ? ctx.envelope : 1 }}>{children}</AbsoluteFill>
  </AbsoluteFill>
);
