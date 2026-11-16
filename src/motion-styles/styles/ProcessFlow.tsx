// 11 · Process Flow — steps with icons, connectors that draw, and an active highlight travelling step to step.
import React from "react";
import { Icon, type IconName } from "../../lib/icons"; // reuses the project icon set
import { EASE } from "../../lib/motion";
import { Stage } from "../core/Stage";
import type { MotionStyleBaseProps } from "../core/types";
import { useMotionStyle } from "../core/useMotionStyle";

export type ProcessStep = { icon: IconName; title: string; desc?: string };
export type ProcessFlowProps = MotionStyleBaseProps & {
  title?: string;
  steps: ProcessStep[]; // 3–5
};

export const ProcessFlow: React.FC<ProcessFlowProps> = (props) => {
  const ctx = useMotionStyle(props);
  const { palette: c, font, phase, scale } = ctx;
  const steps = props.steps.slice(0, 5);
  const n = steps.length;
  const active = phase(0.5, 0.92, EASE.inOut) * (n - 1);
  const W = 300;
  return (
    <Stage ctx={ctx}>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: font.body, color: c.text }}>
        {props.title && <div style={{ fontFamily: font.display, fontWeight: ctx.weight, fontSize: 54 * scale, marginBottom: 70, opacity: phase(0, 0.12) }}>{props.title}</div>}
        <div style={{ display: "flex", alignItems: "flex-start", direction: ctx.dir }}>
          {steps.map((s, i) => {
            const t = phase(0.08 + i * 0.08, 0.22 + i * 0.08, EASE.out);
            const on = Math.max(0, 1 - Math.abs(active - i));
            const conn = phase(0.15 + i * 0.08, 0.28 + i * 0.08, EASE.inOut);
            return (
              <React.Fragment key={i}>
                <div style={{ width: W, display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", opacity: t, transform: `translateY(${(1 - t) * 30}px)` }}>
                  <div style={{ width: 140, height: 140, borderRadius: 70, display: "flex", alignItems: "center", justifyContent: "center", background: `${c.primary}${on > 0.5 ? "55" : "22"}`, border: `3px solid ${on > 0.5 ? c.accent : c.primary}`, transform: `scale(${1 + 0.08 * on})` }}>
                    <Icon name={s.icon} size={64} color={on > 0.5 ? c.accent : c.text} />
                  </div>
                  <div style={{ fontFamily: font.display, fontWeight: 700, fontSize: 32 * scale, marginTop: 24, lineHeight: 1.4 }}>{s.title}</div>
                  {s.desc && <div style={{ fontSize: 22 * scale, color: c.muted, marginTop: 6, lineHeight: 1.5, maxWidth: 260 }}>{s.desc}</div>}
                  <div style={{ fontFamily: font.display, fontSize: 22, color: c.accent, marginTop: 10 }}>{String(i + 1).padStart(2, "0")}</div>
                </div>
                {i < n - 1 && (
                  <div style={{ width: 90, height: 140, display: "flex", alignItems: "center", position: "relative" }}>
                    <div style={{ height: 3, width: `${conn * 100}%`, background: active > i ? c.accent : c.primary }} />
                    <div style={{ position: "absolute", insetInlineEnd: -4, width: 0, height: 0, borderTop: "9px solid transparent", borderBottom: "9px solid transparent", [ctx.rtl ? "borderRight" : "borderLeft"]: `14px solid ${active > i ? c.accent : c.primary}`, opacity: conn >= 1 ? 1 : 0 }} />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};
