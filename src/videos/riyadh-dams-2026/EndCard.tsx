import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILIES } from "../../lib/fonts";
import { Logo } from "../../lib/Logo";
import { EASE, ramp } from "../../lib/motion";
import { SCENE_MEDIA, SOCIAL, type SceneMedia } from "./data";
import { clamp, Footage, type SceneProps } from "./shared";

// Scene 6 — SIO end card in the report's own look (9:16, navy over the lake), modelled on the official social outro:
// light burst behind the emblem → vertical white lockup → divider → social handles & website.
// The logo is the official file via Logo.tsx, animated only as a whole (fade + scale); the light stays behind it.

export type EndCardProps = SceneProps & { media?: SceneMedia; handle?: string; website?: string };

const S = 46; // icon size (px)
const XIcon = () => (
  <svg width={S * 0.82} height={S * 0.82} viewBox="0 0 24 24" fill="#fff">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);
const InIcon = () => (
  <svg width={S * 0.86} height={S * 0.86} viewBox="3 3 18 18" fill="#fff">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452z" />
  </svg>
);
const InstaIcon = () => (
  <svg width={S * 0.9} height={S * 0.9} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={2.2}>
    <rect x="2.5" y="2.5" width="19" height="19" rx="5.5" />
    <circle cx="12" cy="12" r="4.4" />
    <circle cx="17.6" cy="6.4" r="1.2" fill="#fff" stroke="none" />
  </svg>
);
const GlobeIcon = () => (
  <svg width={S * 0.86} height={S * 0.86} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={1.8}>
    <circle cx="12" cy="12" r="9.5" />
    <path d="M2.5 12h19M12 2.5c2.6 2.6 4 6 4 9.5s-1.4 6.9-4 9.5c-2.6-2.6-4-6-4-9.5s1.4-6.9 4-9.5z" />
  </svg>
);

export const EndCard: React.FC<EndCardProps> = ({ media = SCENE_MEDIA.endCard, handle = SOCIAL.handle, website = SOCIAL.website, transparent }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const burst = ramp(frame, 0, 34, EASE.out); // light opens
  const settle = interpolate(frame, [20, 70], [1, 0.45], clamp); // then calms down
  const logoT = ramp(frame, 10, 34, EASE.out);
  const lineT = ramp(frame, 40, 26, EASE.inOut);
  const item = (i: number) => ramp(frame, 50 + i * 6, 22, EASE.out);
  const out = 1 - ramp(frame, durationInFrames - 14, 14, EASE.in);
  const rot = interpolate(frame, [0, durationInFrames], [-8, 10]);
  const cy = 830; // centre of the emblem area

  const rise = (t: number): React.CSSProperties => ({ opacity: t, transform: `translateY(${(1 - t) * 22}px)` });

  return (
    <AbsoluteFill style={{ opacity: out }}>
      {!transparent && <Footage media={media} frames={durationInFrames} dim={0.74} blur={10} />}
      {!transparent && <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(0,40,80,0) 0%, rgba(1,14,30,0.55) 70%, rgba(0,8,18,0.85) 100%)" }} />}

      {/* light burst — behind the logo, never on it */}
      <div
        style={{
          position: "absolute",
          left: 540 - 900,
          top: cy - 900,
          width: 1800,
          height: 1800,
          borderRadius: "50%",
          opacity: burst * settle * 0.55,
          transform: `rotate(${rot}deg) scale(${0.6 + burst * 0.4})`,
          background:
            "repeating-conic-gradient(from 0deg, rgba(160,215,255,0.0) 0deg 7deg, rgba(160,215,255,0.22) 9deg, rgba(160,215,255,0.0) 11deg 22deg)",
          WebkitMaskImage: "radial-gradient(circle, #000 0%, rgba(0,0,0,0.6) 25%, transparent 62%)",
          maskImage: "radial-gradient(circle, #000 0%, rgba(0,0,0,0.6) 25%, transparent 62%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 540 - 420,
          top: cy - 420,
          width: 840,
          height: 840,
          borderRadius: "50%",
          opacity: burst * (0.35 + 0.65 * settle),
          background: "radial-gradient(circle, rgba(0,113,184,0.55) 0%, rgba(0,113,184,0.18) 45%, rgba(0,113,184,0) 70%)",
        }}
      />

      <AbsoluteFill style={{ alignItems: "center" }}>
        <div style={{ marginTop: cy - 330, opacity: logoT, transform: `scale(${0.9 + 0.1 * logoT})` }}>
          <Logo form="lockupVertical" variant="white" height={680} />
        </div>
        <div style={{ width: 760 * lineT, height: 3, marginTop: 56, background: "linear-gradient(to right, rgba(255,255,255,0), #fff 18%, #fff 82%, rgba(255,255,255,0))" }} />
        <div
          style={{
            marginTop: 52,
            direction: "ltr",
            display: "flex",
            alignItems: "center",
            gap: 24,
            fontFamily: FONT_FAMILIES.IBMPlexSansArabic,
            fontWeight: 600,
            fontSize: 42,
            color: "#fff",
          }}
        >
          <span style={rise(item(0))}><XIcon /></span>
          <span style={rise(item(1))}><InIcon /></span>
          <span style={rise(item(2))}><InstaIcon /></span>
          <span style={{ ...rise(item(3)), marginLeft: 4 }}>{handle}</span>
          <span style={{ ...rise(item(4)), width: 3, height: 54, background: "rgba(255,255,255,0.7)", margin: "0 14px" }} />
          <span style={rise(item(5))}><GlobeIcon /></span>
          <span style={rise(item(6))}>{website}</span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
