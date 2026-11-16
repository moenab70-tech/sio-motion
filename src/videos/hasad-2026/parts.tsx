// Small building blocks for «بصمة إنجاز & نمو» (formerly «حصاد التميز 2026»). Reuses the project's easing, fonts, palette tokens,
// FX layers (Particles, LightLeak) and Arabic word segmentation — read-only imports, nothing shared is modified.
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { defaultPalette } from "../../config/brand";
import { FONT_FAMILIES } from "../../lib/fonts";
import { EASE, mix, ramp } from "../../lib/motion";
import { Particles } from "../../fx/Particles";
import { LightLeakLayer } from "../../fx/LightLeak";
import { segment } from "../../motion-styles/core/text";
import { institutionalPalette } from "../../motion-styles/core/tokens";
import type { PhotoGroup, PhotoSlot } from "./config";

export const C = { ...institutionalPalette, panel: defaultPalette.panel, border: defaultPalette.panelBorder };
export const FONT = { display: FONT_FAMILIES.NotoKufiArabic, body: FONT_FAMILIES.IBMPlexSansArabic };
/** Safe frame: everything stays inside these margins (px). */
export const SAFE = { x: 130, y: 90 };
/** Reserved top-right area for the institution logo — no text or photo ever enters it. */
export const LOGO_ZONE = { left: 1400, top: 0, right: 1920, bottom: 320 };

/** Calm navy backdrop + slow gold dust, continuous across the whole video (glues the scenes together). */
export const Backdrop: React.FC<{ frame: number; total: number; particles: number }> = ({ frame, total, particles }) => {
  const drift = Math.sin(frame / 140) * 40;
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 85% 75% at ${62 + drift / 40}% 35%, #142B4C 0%, ${C.background} 58%, #060D18 100%)` }}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        <circle cx={1560 + drift} cy={-180} r={620} fill="none" stroke={C.accent} strokeOpacity={0.09} strokeWidth={2} />
        <circle cx={1560 + drift} cy={-180} r={700} fill="none" stroke={C.accent} strokeOpacity={0.05} strokeWidth={1} />
        <circle cx={260 - drift} cy={1260} r={560} fill="none" stroke={C.primary} strokeOpacity={0.1} strokeWidth={2} />
      </svg>
      {particles > 0 && <Particles frame={frame * 0.6} durationInFrames={total * 0.6} count={30} intensity={particles} colors={[C.accent, "#FFFFFF"]} seed="hasad" />}
    </AbsoluteFill>
  );
};

/** Warm light leak (src/fx/LightLeak) blended with Screen behind the content, with a soft in/out envelope. */
export const Leak: React.FC<{ frame: number; dur: number; fps: number; strength: number; seed: number }> = ({ frame, dur, fps, strength, seed }) => {
  if (strength <= 0) return null;
  const env = Math.min(ramp(frame, 0, fps * 0.8, EASE.inOut), 1 - ramp(frame, dur - fps * 0.8, fps * 0.8, EASE.inOut));
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen", opacity: env }}>
      <LightLeakLayer durationInSeconds={dur / fps} seed={seed} fx={{ intensity: strength }} />
    </AbsoluteFill>
  );
};

/**
 * Arabic-safe staggered reveal: whole words only (never letters, no letter-spacing), rising out of a soft
 * focus blur. "\n" in the text forces a line break so names never get split or left alone on a line.
 */
export const WordReveal: React.FC<{
  text: string;
  frame: number;
  start: number; // frames
  stagger?: number;
  span?: number;
  align?: "start" | "center";
  style?: React.CSSProperties;
}> = ({ text, frame, start, stagger = 3, span = 24, align = "start", style }) => {
  const lines = text.split("\n").map((l) => segment(l, "ar", "word"));
  let n = 0;
  return (
    <div data-hasad-text={text} data-hasad-lines={lines.length} style={{ display: "flex", flexDirection: "column", alignItems: align === "center" ? "center" : "flex-start", ...style }}>
      {lines.map((words, li) => (
        <div key={li} data-hasad-line style={{ display: "flex", flexWrap: "wrap", columnGap: "0.28em", justifyContent: align === "center" ? "center" : "flex-start" }}>
          {words.map((w) => {
            const i = n++;
            const p = ramp(frame, start + i * stagger, span, EASE.out);
            const blur = (1 - p) * 8;
            return (
              <span key={i} style={{ display: "inline-block", clipPath: "inset(-30% -8% -12% -8%)", whiteSpace: "nowrap" }}>
                <span style={{ display: "inline-block", opacity: Math.min(1, p * 1.3), transform: `translateY(${(1 - p) * 0.6}em)`, filter: blur > 0.1 ? `blur(${blur}px)` : undefined }}>{w}</span>
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

/** Small gold heading above a scene; hidden when empty. */
export const Kicker: React.FC<{ text: string; frame: number; start?: number }> = ({ text, frame, start = 0 }) => {
  if (!text) return null;
  const p = ramp(frame, start, 22);
  return (
    <div data-hasad-text={text} style={{ display: "flex", alignItems: "center", gap: 18, opacity: p, color: C.accent, fontFamily: FONT.body, fontWeight: 600, fontSize: 34, lineHeight: 1.4, transform: `translateY(${(1 - p) * 14}px)` }}>
      <span style={{ display: "inline-block", width: 56 * p, height: 3, background: C.accent, borderRadius: 2 }} />
      <span>{text}</span>
    </div>
  );
};

/** Uniform photo frame: every frame in a group has the same size and inner margin. The photo is shown whole
 *  (contain, original ratio, never stretched or cropped) over a soft, darkened blur of itself that fills the rest.
 *  src = null → dedicated empty placeholder. */
export const FRAME_PAD = 18;
const Photo: React.FC<{ slot: PhotoSlot; w: number; h: number; captionH: number }> = ({ slot, w, h, captionH }) => {
  const frameStyle: React.CSSProperties = {
    width: w, height: h, borderRadius: 14, overflow: "hidden", flexShrink: 0, position: "relative",
    boxShadow: "0 30px 70px rgba(0,0,0,0.5)", border: `2px solid rgba(200,164,93,0.55)`,
  };
  const caption = captionH > 0 && (
    <div data-hasad-text={slot.caption ?? ""} style={{ height: captionH, width: w, display: "flex", alignItems: "flex-end", justifyContent: "center", fontFamily: FONT.body, fontWeight: 500, fontSize: 28, lineHeight: 1.3, color: C.muted, direction: "rtl", textAlign: "center" }}>
      {slot.caption ?? ""}
    </div>
  );
  if (!slot.src) {
    return (
      <div style={{ display: "flex", flexDirection: "column" }}>
        <div data-hasad-photo="placeholder" style={{ ...frameStyle, border: `3px dashed ${C.accent}`, background: "rgba(255,255,255,0.04)", boxShadow: "none", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 18, textAlign: "center", padding: 30 }}>
          <div style={{ fontFamily: FONT.body, fontSize: 30, color: C.text, lineHeight: 1.5 }}>{slot.label}</div>
        </div>
        {caption}
      </div>
    );
  }
  const src = staticFile(slot.src);
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <div data-hasad-photo={slot.src} style={{ ...frameStyle, background: "#08111F" }}>
        <Img src={src} aria-hidden style={{ position: "absolute", inset: -40, width: w + 80, height: h + 80, objectFit: "cover", filter: "blur(28px) brightness(0.45) saturate(0.8)" }} />
        <div style={{ position: "absolute", inset: FRAME_PAD, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Img src={src} style={{ maxWidth: "100%", maxHeight: "100%", width: "auto", height: "auto", objectFit: "contain", display: "block", borderRadius: 6, boxShadow: "0 10px 30px rgba(0,0,0,0.45)" }} />
        </div>
      </div>
      {caption}
    </div>
  );
};

/** Lays a group out on one row of equal, uniform frames that fill box W×H. */
const GroupRow: React.FC<{ group: PhotoGroup; W: number; H: number; gap: number; captionH: number }> = ({ group, W, H, gap, captionH }) => {
  const n = group.length;
  const w = (W - gap * (n - 1)) / n;
  return (
    <div style={{ display: "flex", gap, alignItems: "flex-start", justifyContent: "center", width: W, height: H }}>
      {group.map((s, i) => <Photo key={i} slot={s} w={w} h={H - captionH} captionH={captionH} />)}
    </div>
  );
};

/**
 * Groups follow one another with a long, eased depth dissolve (outgoing defocuses and recedes,
 * incoming comes into focus) while a single continuous push-in runs underneath — no resets, no crop.
 */
export const PhotoSequence: React.FC<{ groups: PhotoGroup[]; frame: number; start: number; end: number; W: number; H: number }> = ({ groups, frame, start, end, W, H }) => {
  const n = Math.max(1, groups.length);
  const per = (end - start) / n;
  const xf = 26; // cross-dissolve length (frames)
  // one caption row for the whole scene (if any photo has a caption) → every frame in the scene keeps the same size
  const captionH = groups.some((g) => g.some((sl) => sl.caption)) ? 56 : 0;
  return (
    <div style={{ position: "relative", width: W, height: H }}>
      {groups.map((g, i) => {
        const s = start + i * per;
        const pin = i === 0 ? ramp(frame, s, 30) : ramp(frame, s - xf / 2, xf, EASE.inOut);
        const pout = i === n - 1 ? 0 : ramp(frame, s + per - xf / 2, xf, EASE.inOut);
        const o = pin * (1 - pout);
        if (o <= 0.001) return null;
        // continuous slow push from this group's appearance to its disappearance (linear = no speed bumps)
        const life = Math.min(1, Math.max(0, (frame - (s - xf / 2)) / (per + xf)));
        const push = mix(1.0, 1.035, life);
        const settle = mix(1.04, 1, pin) * mix(1, 0.97, pout);
        const blur = (1 - pin) * 10 + pout * 8;
        const lift = i === 0 ? (1 - pin) * 50 : 0;
        return (
          <div key={i} style={{ position: "absolute", inset: 0, opacity: o, transform: `translateY(${lift}px) scale(${push * settle})`, filter: blur > 0.1 ? `blur(${blur}px)` : undefined }}>
            <GroupRow group={g} W={W} H={H} gap={28} captionH={captionH} />
          </div>
        );
      })}
    </div>
  );
};
