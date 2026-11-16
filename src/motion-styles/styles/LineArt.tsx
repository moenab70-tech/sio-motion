// 14 · Line Art — icons and a connecting line drawn stroke-by-stroke, then labelled. Reuses the project icon set.
import React from "react";
import { Icon, type IconName } from "../../lib/icons";
import { EASE } from "../../lib/motion";
import { Stage } from "../core/Stage";
import { drawOn } from "../core/svg";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type LineArtItem = { icon: IconName; label: string };
export type LineArtProps = MotionStyleBaseProps & {
  title?: string;
  items: LineArtItem[]; // 3–6
  strokeWidth?: number; // icon stroke (default 1.4)
  iconSize?: number;
};

export const LineArt: React.FC<LineArtProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, scale } = ctx;
  const items = props.items.slice(0, 6);
  const n = items.length;
  const size = props.iconSize ?? 150;
  const cls = `la-${ctx.seed.replace(/[^a-z0-9]/gi, "")}`;
  // Icon paths are ≤ ~100 units long in their 24-unit viewBox → dash 100 draws them on.
  const css = items.map((_, i) => `.${cls}-${i} svg * { stroke-dasharray: 100; stroke-dashoffset: ${(100 * (1 - phase(0.12 + i * 0.09, 0.4 + i * 0.09, EASE.inOut))).toFixed(2)}; }`).join("\n");
  const wave = "M 120 760 C 360 700, 520 820, 760 760 S 1160 700, 1400 760 S 1700 820, 1800 760";
  return (
    <Stage ctx={ctx}>
      <style>{css}</style>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <path d={wave} fill="none" stroke={c.primary} strokeWidth={3} strokeLinecap="round" pathLength={1} style={drawOn(phase(0.05, 0.5, EASE.inOut))} transform={ctx.rtl ? "translate(1920 0) scale(-1 1)" : undefined} />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: font.body, color: c.text }}>
        {props.title && <div style={{ fontFamily: font.display, fontWeight: ctx.weight, fontSize: 56 * scale, marginBottom: 80, opacity: phase(0, 0.12) }}>{props.title}</div>}
        <div style={{ display: "flex", gap: n > 4 ? 60 : 110, direction: ctx.dir }}>
          {items.map((it, i) => (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 26 }}>
              <div className={`${cls}-${i}`} style={{ width: size, height: size, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon name={it.icon} size={size} color={i % 2 ? c.accent : c.text} strokeWidth={props.strokeWidth ?? 1.4} />
              </div>
              <div style={{ fontSize: 30 * scale, fontWeight: 600, opacity: phase(0.35 + i * 0.09, 0.5 + i * 0.09), lineHeight: 1.4 }}>{it.label}</div>
            </div>
          ))}
        </div>
      </div>
    </Stage>
  );
};
