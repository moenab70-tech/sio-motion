// FX 1–3 · Cinematic Arabic typography with directional motion blur, soft glow and one light sweep.
// Words animate as whole words (keeps Arabic letter joining intact). The logo never receives effects.
import React from "react";
import { AbsoluteFill } from "remotion";
import type { Fx } from "../config/fx";
import { useTemplate, type CommonProps, type LogoSlot } from "../lib/brand";
import { Logo } from "../lib/Logo";
import { EASE, ramp } from "../lib/motion";
import { localizeDigits } from "../lib/numbers";
import { DirectionalBlur, velocityBlur } from "./DirectionalBlur";
import { Particles } from "./Particles";
import { useFx } from "./useFx";

export type FxTitleProps = CommonProps & {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  style: "rise" | "focus" | "sweep";
  align: "center" | "start";
  titleSize?: number;
  logo?: LogoSlot;
  fx?: Partial<Fx>;
};

export const FxTitle: React.FC<FxTitleProps> = (props) => {
  const t = useTemplate(props);
  const fx = useFx(props.fx);
  const { palette: c, font, s, total } = t;
  const f = fx.frame; // speed-scaled frame
  const outT = 1 - ramp(f, total * fx.speed - s(t.timing.exit), s(t.timing.exit), EASE.in);
  const words = localizeDigits(props.title, t.digits).split(/\s+/).filter(Boolean);
  const center = props.align === "center";
  const size = props.titleSize ?? 128;
  const stagger = t.timing.stagger * 1.5;
  const start = 0.35;
  const wordP = (i: number, frame: number) => ramp(frame, s(start + i * stagger), s(t.timing.enter * 1.25), EASE.out);
  const lastLand = start + (words.length - 1) * stagger + t.timing.enter * 1.25;

  const eyebrowIn = ramp(f, s(0.1), s(0.8));
  const ruleIn = ramp(f, s(lastLand - 0.4), s(1.0), EASE.inOut);
  const subIn = ramp(f, s(lastLand - 0.2), s(0.9));
  const logoIn = ramp(f, 0, s(1.2));
  const sweep = ramp(f, s(lastLand + 0.1), s(1.4), EASE.inOut); // single highlight pass
  const glow = fx.glow ? fx.intensity : 0;
  const dir = t.rtl ? -1 : 1;

  const wordStyle = (i: number): { transform: string; opacity: number; bx: number; by: number; extraBlur: number } => {
    const p = wordP(i, f);
    const prev = wordP(i, f - fx.speed);
    if (props.style === "focus") {
      const scale = 1.3 - 0.3 * p;
      return { transform: `scale(${scale})`, opacity: p, bx: 0, by: 0, extraBlur: (1 - p) * 16 };
    }
    if (props.style === "sweep") {
      const dx = (1 - p) * 140 * -dir;
      const dPrev = (1 - prev) * 140 * -dir;
      return { transform: `translateX(${dx}px)`, opacity: p, bx: velocityBlur(dx - dPrev, fx.intensity, fx.motionBlur), by: 0, extraBlur: 0 };
    }
    const dy = (1 - p) * size * 0.9;
    const dPrev = (1 - prev) * size * 0.9;
    return { transform: `translateY(${dy}px)`, opacity: Math.min(1, p * 1.5), bx: 0, by: velocityBlur(dy - dPrev, fx.intensity, fx.motionBlur), extraBlur: 0 };
  };

  const titleText = (layer: "base" | "sweep") => (
    <div style={{ fontFamily: font.display, fontWeight: 800, fontSize: size, lineHeight: 1.45, display: "flex", flexWrap: "wrap", justifyContent: center ? "center" : "flex-start", columnGap: "0.28em" }}>
      {words.map((w, i) => {
        const ws = wordStyle(i);
        const inner = (
          <span
            style={{
              display: "inline-block",
              transform: ws.transform,
              opacity: ws.opacity * outT,
              filter: ws.extraBlur > 0.05 || outT < 1 ? `blur(${ws.extraBlur + (1 - outT) * 8}px)` : undefined,
              color: layer === "base" ? c.text : "transparent",
              textShadow: layer === "base" && glow > 0 ? `0 0 ${18 + 40 * glow}px ${c.accent}${Math.round(glow * 0x55).toString(16).padStart(2, "0")}, 0 10px 50px ${c.shadow}` : layer === "base" ? `0 10px 50px ${c.shadow}` : undefined,
              backgroundImage: layer === "sweep" ? `linear-gradient(${t.rtl ? 250 : 110}deg, transparent 35%, ${c.accent} 50%, transparent 65%)` : undefined,
              backgroundSize: layer === "sweep" ? "300% 100%" : undefined,
              backgroundPosition: layer === "sweep" ? `${t.rtl ? sweep * 100 : 100 - sweep * 100}% 0` : undefined,
              WebkitBackgroundClip: layer === "sweep" ? "text" : undefined,
              backgroundClip: layer === "sweep" ? "text" : undefined,
            }}
          >
            {w}
          </span>
        );
        return (
          <span key={i} style={{ display: "inline-block", clipPath: props.style === "rise" ? "inset(-30% -10% 0 -10%)" : undefined }}>
            <DirectionalBlur x={ws.bx} y={ws.by} style={{ display: "inline-block" }}>
              {inner}
            </DirectionalBlur>
          </span>
        );
      })}
    </div>
  );

  const sweepVisible = fx.lightSweep && sweep > 0 && sweep < 1;

  return (
    <AbsoluteFill style={{ direction: t.dir }}>
      {fx.particles && <Particles frame={f} durationInFrames={total * fx.speed} intensity={fx.intensity} speed={1} />}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: center ? "center" : "flex-start", padding: center ? 0 : "0 170px" }}>
        {props.logo && <Logo {...props.logo} height={props.logo.height ?? 230} opacity={logoIn * outT} style={{ marginBottom: 30 }} />}
        <div style={{ textAlign: center ? "center" : "start", maxWidth: 1600 }}>
          {props.eyebrow && (
            <div style={{ fontFamily: font.body, fontSize: 32, fontWeight: 500, color: c.accent, marginBottom: 14, opacity: eyebrowIn * outT, display: "flex", gap: 16, alignItems: "center", justifyContent: center ? "center" : "flex-start" }}>
              <span style={{ width: 44 * eyebrowIn, height: 2, background: c.accent }} />
              {localizeDigits(props.eyebrow, t.digits)}
            </div>
          )}
          <div style={{ position: "relative" }}>
            {titleText("base")}
            {sweepVisible && (
              <div style={{ position: "absolute", inset: 0, opacity: 0.55 + 0.45 * fx.intensity }}>{titleText("sweep")}</div>
            )}
          </div>
          <div style={{ height: 2.5, width: 560 * ruleIn, background: `linear-gradient(${t.rtl ? 270 : 90}deg, ${c.accent}, transparent)`, margin: center ? "18px auto 24px" : "18px 0 24px", opacity: outT }} />
          {props.subtitle && (
            <div style={{ fontFamily: font.body, fontSize: 44, color: c.textMuted, lineHeight: 1.6, opacity: subIn * outT, transform: `translateY(${(1 - subIn) * 16}px)`, textShadow: `0 4px 24px ${c.shadow}` }}>
              {localizeDigits(props.subtitle, t.digits)}
            </div>
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

