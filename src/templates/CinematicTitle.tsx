// 2a ─ Cinematic Arabic title (word-by-word reveal keeps Arabic letter joining intact)
import React from "react";
import { AbsoluteFill, interpolate } from "remotion";
import { useTemplate, riseStyle, type CommonProps, type LogoSlot } from "../lib/brand";
import { Logo } from "../lib/Logo";
import { EASE, ramp } from "../lib/motion";
import { localizeDigits } from "../lib/numbers";

export type CinematicTitleProps = CommonProps & {
  eyebrow?: string; // small kicker above the title
  title: string;
  subtitle?: string;
  align: "center" | "start";
  titleSize?: number;
  pushIn?: boolean; // slow cinematic scale-up during the hold
  logo?: LogoSlot; // shown above the title (fade only)
};

export const CinematicTitle: React.FC<CinematicTitleProps> = (props) => {
  const t = useTemplate(props);
  const { palette: c, font, frame, s, out, total } = t;
  const words = localizeDigits(props.title, t.digits).split(/\s+/).filter(Boolean);
  const center = props.align === "center";
  const size = props.titleSize ?? 124;

  const eyebrowIn = t.enter(0, 0);
  const wordsStart = 0.25;
  const lastWord = wordsStart + (words.length - 1) * t.timing.stagger * 1.4;
  const rule = ramp(frame, s(lastWord + 0.2), s(1.1), EASE.inOut);
  const subIn = t.enter(0, lastWord + 0.45);
  const push = props.pushIn === false ? 1 : interpolate(frame, [0, total], [1, 1.04]);

  return (
    <AbsoluteFill style={{ direction: t.dir, justifyContent: "center", alignItems: center ? "center" : "flex-start", padding: center ? 0 : "0 170px" }}>
      {props.logo && <Logo {...props.logo} height={props.logo.height ?? 150} opacity={t.enter(0, 0, 1.2) * out} style={{ marginBottom: 36 }} />}
      <div style={{ transform: `scale(${push})`, transformOrigin: center ? "center" : t.rtl ? "right center" : "left center", textAlign: center ? "center" : "start", maxWidth: 1580 }}>
        {props.eyebrow && (
          <div style={{ ...riseStyle(eyebrowIn, out, 14), fontFamily: font.body, fontSize: 32, fontWeight: 500, color: c.accent, marginBottom: 18, display: "flex", alignItems: "center", gap: 16, justifyContent: center ? "center" : "flex-start" }}>
            <span style={{ width: 44 * eyebrowIn, height: 2, background: c.accent }} />
            {localizeDigits(props.eyebrow, t.digits)}
          </div>
        )}
        <div style={{ fontFamily: font.display, fontWeight: 800, fontSize: size, lineHeight: 1.45, color: c.text, display: "flex", flexWrap: "wrap", justifyContent: center ? "center" : "flex-start", columnGap: "0.28em" }}>
          {words.map((w, i) => {
            const p = ramp(frame, s(wordsStart + i * t.timing.stagger * 1.4), s(t.timing.enter * 1.2), EASE.out);
            return (
              // overflow mask: each word rises from an invisible baseline
              <span key={i} style={{ display: "inline-block", clipPath: "inset(-20% -10% 0 -10%)" }}>
                <span style={{ display: "inline-block", transform: `translateY(${(1 - p) * 70}%)`, opacity: Math.min(1, p * 1.6) * out, filter: `blur(${(1 - p) * 6 + (1 - out) * 8}px)`, textShadow: `0 10px 50px ${c.shadow}` }}>
                  {w}
                </span>
              </span>
            );
          })}
        </div>
        <div style={{ height: 2.5, width: 560 * rule, background: `linear-gradient(${t.rtl ? 270 : 90}deg, ${c.accent}, transparent)`, margin: center ? "20px auto 26px" : "20px 0 26px", opacity: out }} />
        {props.subtitle && (
          <div style={{ ...riseStyle(subIn, out, 18), fontFamily: font.body, fontSize: 44, fontWeight: 400, color: c.textMuted, lineHeight: 1.6, textShadow: `0 4px 24px ${c.shadow}` }}>
            {localizeDigits(props.subtitle, t.digits)}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
