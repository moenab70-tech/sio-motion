// «بصمة إنجاز & نمو» (formerly «حصاد التميز 2026») — standalone composition. Content lives in ./config.ts (a list of scenes).
// Reuses: Motion Styles › KineticType (titles & goals), src/fx presentations (brandWipe / blurDissolve — built for
// scenes over a shared backdrop), src/fx Particles + LightLeak, lib/Logo, lib/motion, lib/fonts.
// No shared template/config is modified.
import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";
import { springTiming, TransitionSeries } from "@remotion/transitions";
import { KineticType } from "../../motion-styles/styles/KineticType";
import { blurDissolve, brandWipe } from "../../fx/presentations";
import { Logo } from "../../lib/Logo";
import { EASE, ramp } from "../../lib/motion";
import { sceneFrames, totalFrames, transitionFrames, type HasadConfig, type PhotoGroup, type Scene } from "./config";
import { Backdrop, C, FONT, Kicker, Leak, LOGO_ZONE, PhotoSequence, SAFE, WordReveal } from "./parts";

type Of<K extends Scene["kind"]> = Extract<Scene, { kind: K }>;
type SceneProps<K extends Scene["kind"]> = { data: Of<K>; dur: number; fps: number };

/** A KineticType line inside a fixed-height box, so stacked lines can never overlap. */
const KineticBox: React.FC<{ height: number; delay: number; dur: number; text: string; fontSize: number; weight?: number; color?: string; accent?: boolean; variant?: "rise" | "scale" | "mask" }> = ({ height, delay, dur, text, fontSize, weight = 700, color, accent = false, variant = "rise" }) => (
  <div data-hasad-text={text} style={{ position: "relative", width: 1660, height }}>
    <Sequence from={delay} layout="none">
      <KineticType lines={[text]} variant={variant} fontSize={fontSize} accentLine={accent} intensity={0.35} durationInFrames={dur - delay} typography={{ display: "NotoKufiArabic", weight }} colors={color ? { text: color } : undefined} />
    </Sequence>
  </div>
);

// ── Intro ─────────────────────────────────────────────
const Intro: React.FC<SceneProps<"intro"> & { leak: number }> = ({ data, dur, fps, leak }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Leak frame={frame} dur={dur} fps={fps} strength={leak} seed={3} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", direction: "rtl" }}>
        {/* +30 frames: the transition handles the exit, KineticType must not fade out on its own first */}
        <KineticBox height={250} delay={0} dur={dur + 30} text={data.title} fontSize={136} accent variant="scale" />
        <KineticBox height={110} delay={Math.round(0.9 * fps)} dur={dur + 30} text={data.subtitle} fontSize={58} weight={500} color={C.muted} />
        {data.showLogo && (
          <div style={{ marginTop: 36, height: data.logoHeight, display: "flex", justifyContent: "center" }}>
            <Logo form="lockupVertical" variant="white" background="dark" height={data.logoHeight} opacity={ramp(frame, Math.round(1.6 * fps), Math.round(0.9 * fps))} />
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ── About the initiative (Kinetic Typography, one line at a time) ────
const Goals: React.FC<SceneProps<"about">> = ({ data, dur }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      {/* kicker sits centred just above the lines — the top-right corner stays free for the logo */}
      <div style={{ position: "absolute", top: 382, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Kicker text={data.kicker} frame={frame} start={6} />
      </div>
      <div data-hasad-text={data.lines.join(" | ")} style={{ position: "absolute", inset: `300px ${SAFE.x}px 300px` }}>
        <KineticType lines={data.lines} variant="rise" fontSize={74} intensity={0.35} durationInFrames={dur + 30} />
      </div>
    </AbsoluteFill>
  );
};

// ── Section heading («منجزات دولية» / «منجزات محلية») ──
const Section: React.FC<SceneProps<"section">> = ({ data, dur, fps }) => (
  <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", direction: "rtl" }}>
    <KineticBox height={230} delay={0} dur={dur + 30} text={data.title} fontSize={120} accent variant="scale" />
    {data.subtitle && <KineticBox height={100} delay={Math.round(0.6 * fps)} dur={dur + 30} text={data.subtitle} fontSize={52} weight={500} color={C.muted} />}
  </AbsoluteFill>
);

// ── Award layout: text on the reading side (right), photos on the left; text-only → centred ──
const AwardScene: React.FC<{ kicker: string; title: string; items: string[]; photos: PhotoGroup[]; dur: number; fps: number }> = ({ kicker, title, items, photos, dur, fps }) => {
  const frame = useCurrentFrame();
  const solo = photos.length === 0;
  const t0 = kicker ? 10 : 4;
  const titleWords = title.split(/\s+/).length;
  const itemsStart = t0 + 14 + titleWords * 3 + 10;
  const line = ramp(frame, itemsStart - 12, 26, EASE.inOut);
  const align = solo ? "center" : "start";
  return (
    <AbsoluteFill style={{ direction: "rtl", padding: `${SAFE.y}px ${SAFE.x}px`, flexDirection: "row", alignItems: "center", justifyContent: solo ? "center" : undefined, gap: 60 }}>
      <div style={{ width: solo ? 1500 : 780, display: "flex", flexDirection: "column", alignItems: solo ? "center" : "flex-start", gap: solo ? 34 : 26 }}>
        <Kicker text={kicker} frame={frame} />
        <WordReveal text={title} frame={frame} start={t0 + 6} align={align} style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: solo ? 84 : 64, lineHeight: 1.5, color: C.text }} />
        <div style={{ height: 3, width: 140 * line, background: C.accent, borderRadius: 2 }} />
        {items.map((it, i) => {
          const s = itemsStart + i * Math.round(0.55 * fps);
          const p = ramp(frame, s, 18);
          return (
            <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 20 }}>
              {!solo && <span style={{ flexShrink: 0, width: 14, height: 14, marginTop: 26, background: C.accent, transform: `rotate(45deg) scale(${p})` }} />}
              <WordReveal text={it} frame={frame} start={s} align={align} style={{ fontFamily: FONT.body, fontWeight: 500, fontSize: solo ? 52 : 42, lineHeight: 1.6, color: solo ? C.muted : C.text }} />
            </div>
          );
        })}
      </div>
      {!solo && <PhotoSequence groups={photos} frame={frame} start={Math.round(0.35 * fps)} end={dur} W={820} H={800} />}
    </AbsoluteFill>
  );
};

// ── Text cards (kept for future use): two text cards, no images ──
const More: React.FC<SceneProps<"cards">> = ({ data, fps }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ direction: "rtl", padding: `${LOGO_ZONE.bottom + 20}px ${SAFE.x}px ${SAFE.y}px`, justifyContent: "flex-start", gap: 50 }}>
      <Kicker text={data.kicker} frame={frame} start={4} />
      <div style={{ display: "flex", gap: 60, alignItems: "stretch" }}>
        {data.cards.map((card, i) => {
          const s = Math.round((0.45 + i * 1.4) * fps);
          const p = ramp(frame, s, 30);
          return (
            <div key={i} style={{ flex: 1, minWidth: 0, opacity: Math.min(1, p * 1.2), transform: `translateY(${(1 - p) * 60}px) scale(${0.97 + 0.03 * p})`, background: C.panel, border: `1px solid ${C.border}`, borderTop: `4px solid ${C.accent}`, borderRadius: 18, padding: "46px 46px 52px", display: "flex", flexDirection: "column", gap: 24, boxShadow: "0 30px 70px rgba(0,0,0,0.35)" }}>
              <div style={{ fontFamily: FONT.display, fontSize: 72, lineHeight: 1, color: C.accent, direction: "ltr", textAlign: "right" }}>{String(i + 1).padStart(2, "0")}</div>
              <WordReveal text={card.title} frame={frame} start={s + 10} style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 42, lineHeight: 1.55, color: C.text }} />
              <WordReveal text={card.body} frame={frame} start={s + 26} style={{ fontFamily: FONT.body, fontWeight: 500, fontSize: 38, lineHeight: 1.6, color: C.muted }} />
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ── Outro: title, tagline, optional official logo (whole-logo fade only) ──
const Outro: React.FC<SceneProps<"outro"> & { leak: number }> = ({ data, dur, fps, leak }) => {
  const frame = useCurrentFrame();
  const logoIn = ramp(frame, Math.round(1.4 * fps), Math.round(0.8 * fps));
  const endFade = 1 - ramp(frame, dur - Math.round(1.2 * fps), Math.round(1.2 * fps), EASE.inOut);
  return (
    <>
    <AbsoluteFill style={{ opacity: endFade }}>
      <Leak frame={frame} dur={dur} fps={fps} strength={leak} seed={7} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", direction: "rtl", gap: 10 }}>
        <KineticBox height={210} delay={0} dur={dur + 30} text={data.title} fontSize={112} accent variant="scale" />
        <KineticBox height={100} delay={Math.round(0.7 * fps)} dur={dur + 30} text={data.tagline} fontSize={54} weight={500} color={C.muted} />
        {data.showLogo && (
          <div style={{ marginTop: 40, height: data.logoHeight, display: "flex", justifyContent: "center" }}>
            <Logo form="lockupVertical" variant="white" background="dark" height={data.logoHeight} opacity={logoIn} />
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
    {data.brandOutro && (
      <Sequence from={dur} name="Official outro">
        <OffthreadVideo src={staticFile(data.brandOutro.src)} muted transparent style={{ width: "100%", height: "100%" }} />
      </Sequence>
    )}
    </>
  );
};

/** Delays a scene's content by `lead` frames (module-level so it never remounts). */
const Lead: React.FC<{ lead: number; children: React.ReactNode }> = ({ lead, children }) => <Sequence from={lead} name="content">{children}</Sequence>;

/** Renders one scene of any kind. `dur` = frames available to the content (excluding the outro's clean hold). */
export const SceneView: React.FC<{ scene: Scene; dur: number; fps: number; leak: number }> = ({ scene, dur, fps, leak }) => {
  switch (scene.kind) {
    case "intro": return <Intro data={scene} dur={dur} fps={fps} leak={leak} />;
    case "about": return <Goals data={scene} dur={dur} fps={fps} />;
    case "section": return <Section data={scene} dur={dur} fps={fps} />;
    case "award": return <AwardScene {...scene} dur={dur} fps={fps} />;
    case "cards": return <More data={scene} dur={dur} fps={fps} />;
    case "outro": return <Outro data={scene} dur={dur} fps={fps} leak={leak} />;
  }
};

const contentFrames = (s: Scene, fps: number) => Math.round(s.seconds * fps);

export const HasadVideo: React.FC<HasadConfig> = (cfg) => {
  const frame = useCurrentFrame();
  const frames = sceneFrames(cfg);
  const fps = cfg.fps;
  const tf = transitionFrames(cfg);
  // Critically-damped spring, stretched to exactly `tf` frames → soft start and a long, gentle settle.
  const timing = springTiming({ config: { damping: 200 }, durationInFrames: tf, durationRestThreshold: 0.001 });
  // The incoming scene's content waits until the outgoing one has mostly cleared,
  // so two scenes' text/photos never animate on top of each other during a transition.
  const lead = Math.round(tf * 0.6);
  return (
    <AbsoluteFill data-hasad-root style={{ background: C.background }}>
      <Backdrop frame={frame} total={totalFrames(cfg)} particles={cfg.particles} />
      <TransitionSeries>
        {cfg.scenes.flatMap((s, i) => {
          const seq = (
            <TransitionSeries.Sequence key={s.id} durationInFrames={frames[i]} name={s.name}>
              {i === 0 ? <SceneView scene={s} dur={contentFrames(s, fps)} fps={fps} leak={cfg.lightLeak} /> : (
                <Lead lead={lead}><SceneView scene={s} dur={contentFrames(s, fps) - lead} fps={fps} leak={cfg.lightLeak} /></Lead>
              )}
            </TransitionSeries.Sequence>
          );
          if (i === 0) return [seq];
          const t = (s.transition ?? "blur") === "wipe" ? (
            <TransitionSeries.Transition key={`${s.id}-t`} presentation={brandWipe({ rtl: true, feather: 26, intensity: 0.45 })} timing={timing} />
          ) : (
            <TransitionSeries.Transition key={`${s.id}-t`} presentation={blurDissolve({ intensity: 0.45 })} timing={timing} />
          );
          return [t, seq];
        })}
      </TransitionSeries>
      {cfg.cornerLogo.show && (
        <div style={{ position: "absolute", top: 60, right: 100 }}>
          <Logo form="lockupVertical" variant="white" background="dark" height={cfg.cornerLogo.height} />
        </div>
      )}
    </AbsoluteFill>
  );
};

/** One scene on its own (for the separate per-scene export to Premiere): same backdrop, no transitions. */
export type SceneClipProps = { cfg: HasadConfig; index: number };
export const SceneClip: React.FC<SceneClipProps> = ({ cfg, index }) => {
  const frame = useCurrentFrame();
  const s = cfg.scenes[index];
  const total = sceneFrames(cfg)[index];
  return (
    <AbsoluteFill style={{ background: C.background }}>
      <Backdrop frame={frame} total={total} particles={cfg.particles} />
      <SceneView scene={s} dur={contentFrames(s, cfg.fps)} fps={cfg.fps} leak={cfg.lightLeak} />
      {cfg.cornerLogo.show && (
        <div style={{ position: "absolute", top: 60, right: 100 }}>
          <Logo form="lockupVertical" variant="white" background="dark" height={cfg.cornerLogo.height} />
        </div>
      )}
    </AbsoluteFill>
  );
};
