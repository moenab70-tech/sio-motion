// 2b ─ Lower third (name / role / organisation)
import React from "react";
import { AbsoluteFill } from "remotion";
import { useTemplate, type CommonProps, type LogoSlot } from "../lib/brand";
import { Logo } from "../lib/Logo";
import { EASE, ramp } from "../lib/motion";

export type LowerThirdProps = CommonProps & {
  name: string;
  role: string;
  organization?: string;
  variant: "panel" | "minimal";
  side: "start" | "end"; // start = right side in RTL
  marginX?: number;
  marginBottom?: number;
  logo?: LogoSlot; // placed before the accent bar (fade only)
};

export const LowerThird: React.FC<LowerThirdProps> = (props) => {
  const t = useTemplate(props);
  const { palette: c, font, frame, s, out } = t;
  const panel = props.variant === "panel";
  const bar = ramp(frame, 0, s(0.55), EASE.out);
  const reveal = ramp(frame, s(0.2), s(0.9), EASE.out);
  const nameIn = t.enter(0, 0.4);
  const roleIn = t.enter(1, 0.5);
  const orgIn = t.enter(2, 0.5);
  // clip from the start edge (right in RTL) towards the end edge; exit reverses
  const hide = (1 - reveal) * 100 + (1 - out) * 100;
  const clip = t.rtl ? `inset(0 0 0 ${Math.min(100, hide)}%)` : `inset(0 ${Math.min(100, hide)}% 0 0)`;
  const shift = (v: number) => (1 - v) * (t.rtl ? 30 : -30);

  return (
    <AbsoluteFill
      style={{
        direction: t.dir,
        justifyContent: "flex-end",
        alignItems: props.side === "end" ? "flex-end" : "flex-start",
        padding: `0 ${props.marginX ?? 140}px ${props.marginBottom ?? 120}px`,
      }}
    >
      <div style={{ display: "flex", alignItems: "stretch" }}>
        {props.logo && (
          <div style={{ display: "flex", alignItems: "center", marginInlineEnd: 28 }}>
            <Logo {...props.logo} height={props.logo.height ?? 130} opacity={reveal * out} />
          </div>
        )}
        <div style={{ width: 6, background: c.accent, borderRadius: 3, transform: `scaleY(${bar * out})`, transformOrigin: "bottom", marginInlineEnd: panel ? 0 : 26 }} />
        <div
          style={{
            clipPath: clip,
            background: panel ? c.panel : undefined,
            borderTop: panel ? `1px solid ${c.panelBorder}` : undefined,
            padding: panel ? "24px 40px 26px" : "4px 0",
          }}
        >
          <div style={{ fontFamily: font.display, fontWeight: 700, fontSize: 54, lineHeight: 1.5, color: c.text, opacity: nameIn, transform: `translateX(${shift(nameIn)}px)`, textShadow: panel ? undefined : `0 4px 22px ${c.shadow}` }}>
            {props.name}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 16, fontFamily: font.body, fontSize: 32, lineHeight: 1.5, opacity: roleIn, transform: `translateX(${shift(roleIn)}px)` }}>
            <span style={{ color: c.accent, fontWeight: 500 }}>{props.role}</span>
            {props.organization && (
              <>
                <span style={{ width: 6, height: 6, borderRadius: 3, background: c.textMuted, opacity: orgIn }} />
                <span style={{ color: c.textMuted, opacity: orgIn }}>{props.organization}</span>
              </>
            )}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
