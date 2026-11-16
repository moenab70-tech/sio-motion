// 1 · Kinetic Typography — staggered word reveals, masking, directional movement, line-to-line transitions.
import React from "react";
import { AbsoluteFill } from "remotion";
import { EASE, mix, ramp } from "../../lib/motion";
import { Stage } from "../core/Stage";
import { segment } from "../core/text";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type KineticTypeProps = MotionStyleBaseProps & {
  lines: string[]; // shown one after another
  variant?: "rise" | "slide" | "mask" | "scale";
  unit?: "word" | "char"; // "char" applies to English only — Arabic always animates whole words
  fontSize?: number;
  align?: "center" | "start";
  accentLine?: boolean;
};

export const KineticType: React.FC<KineticTypeProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { frame, total, palette: c, font, intensity, rtl, scale } = ctx;
  const lines = props.lines.length ? props.lines : [" "];
  const per = total / lines.length;
  const idx = Math.min(lines.length - 1, Math.floor(frame / per));
  const local = frame - idx * per;
  // words always stay unbroken; English "char" mode animates graphemes inside each word
  const words = segment(lines[idx], ctx.lang, "word");
  const charMode = ctx.lang === "en" && props.unit === "char";
  const groups = words.map((w) => (charMode ? segment(w, "en", "char") : [w]));
  const units = groups.flat();
  const variant = props.variant ?? "rise";
  const size = (props.fontSize ?? 120) * scale;
  const dir = rtl ? -1 : 1;
  const enterSpan = per * 0.4;
  const stagger = Math.min(ctx.sec(0.12), (enterSpan * 0.6) / Math.max(1, units.length));
  const exitStart = per * 0.82;
  const isLast = idx === lines.length - 1;
  const travel = 40 + 120 * intensity;

  return (
    <Stage ctx={ctx} fade={false}>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: props.align === "start" ? "flex-start" : "center", padding: props.align === "start" ? "0 160px" : 0 }}>
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: props.align === "start" ? "flex-start" : "center", columnGap: "0.3em", maxWidth: 1600, fontFamily: font.display, fontWeight: ctx.weight, fontSize: size, lineHeight: 1.45, color: c.text }}>
          {(() => { let n = 0; return groups.map((g, gi) => (
            <span key={`${idx}-w${gi}`} style={{ display: "inline-block", whiteSpace: "nowrap" }}>
            {g.map((u) => { const i = n++;
            const pIn = ramp(local, i * stagger, enterSpan * 0.6, EASE.out);
            const pOut = ramp(local, exitStart + i * stagger * 0.5, per - exitStart - stagger, EASE.in);
            const out = isLast ? ramp(frame, total - ctx.sec(0.5), ctx.sec(0.5), EASE.in) : pOut;
            const k = 1 - pIn; // 1 = hidden before entering
            let transform = "";
            let clip: string | undefined;
            if (variant === "rise") transform = `translateY(${k * size * 0.9 - out * size * 0.5}px)`;
            if (variant === "slide") transform = `translateX(${(-k * travel + out * travel) * dir}px)`;
            if (variant === "scale") transform = `scale(${mix(1.4, 1, pIn) * mix(1, 0.85, out)})`;
            if (variant === "mask") clip = rtl ? `inset(0 0 0 ${k * 100 + 0}% )` : `inset(0 ${k * 100}% 0 0)`;
            return (
              <span key={`${idx}-${i}`} style={{ display: "inline-block", clipPath: variant === "rise" ? "inset(-25% -10% -5% -10%)" : undefined, whiteSpace: "pre" }}>
                <span style={{ display: "inline-block", transform, clipPath: clip, opacity: (variant === "mask" ? 1 : Math.min(1, pIn * 1.5)) * (1 - out), filter: variant === "scale" && k > 0.01 ? `blur(${k * 10 * intensity}px)` : undefined }}>{u}</span>
              </span>
            );
            })}
            </span>
          )); })()}
        </div>
        {props.accentLine !== false && (
          <div style={{ height: 4, marginTop: 26, width: 380 * ramp(local, enterSpan * 0.5, enterSpan, EASE.inOut) * (1 - (isLast ? ramp(frame, total - ctx.sec(0.5), ctx.sec(0.5)) : ramp(local, exitStart, per - exitStart))), background: c.accent, borderRadius: 2, alignSelf: props.align === "start" ? (rtl ? "flex-end" : "flex-start") : "center" }} />
        )}
      </AbsoluteFill>
    </Stage>
  );
};
