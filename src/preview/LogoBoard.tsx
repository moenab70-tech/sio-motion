// Preview board: every official logo file on the background it is meant for.
import React from "react";
import { AbsoluteFill } from "remotion";
import { LOGOS, type LogoForm, type LogoVariant } from "../config/logos";
import { FONT_FAMILIES } from "../lib/fonts";
import { Logo } from "../lib/Logo";

const LIGHT = "#F4F6F8";
const DARK = "#0C1626";
const font = FONT_FAMILIES.IBMPlexSansArabic;

const Tile: React.FC<{ form: LogoForm; variant: LogoVariant; bg: string; caption: string }> = ({ form, variant, bg, caption }) => {
  const available = Boolean(LOGOS[form][variant]);
  const ink = bg === LIGHT ? "#3A4655" : "rgba(255,255,255,0.75)";
  const size = form === "lockup" ? { width: 520 } : form === "lockupVertical" ? { height: 300 } : { height: 240 };
  return (
    <div style={{ background: bg, borderRadius: 24, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 24, border: "1px solid rgba(128,128,128,0.25)" }}>
      <div style={{ height: 310, display: "flex", alignItems: "center" }}>
        {available ? (
          <Logo form={form} variant={variant} {...size} />
        ) : (
          <div style={{ width: 380, height: 220, border: `2px dashed ${ink}`, borderRadius: 18, display: "flex", alignItems: "center", justifyContent: "center", color: ink, fontSize: 28, textAlign: "center", lineHeight: 1.6 }}>
            لا يوجد ملف رسمي
          </div>
        )}
      </div>
      <div style={{ fontSize: 24, color: ink }}>{caption}</div>
    </div>
  );
};

export const LogoBoard: React.FC = () => (
  <AbsoluteFill style={{ background: "#DDE2E8", padding: 50, direction: "rtl", fontFamily: font }}>
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gridTemplateRows: "1fr 1fr", gap: 26, height: "100%" }}>
      <Tile form="lockup" variant="color" bg={LIGHT} caption="أفقي · ملون · sio-lockup-color" />
      <Tile form="lockup" variant="blue" bg={LIGHT} caption="أفقي · أزرق · sio-lockup-blue" />
      <Tile form="lockupVertical" variant="black" bg={LIGHT} caption="عمودي · أسود · sio-lockup-vertical-black" />
      <Tile form="lockupVertical" variant="white" bg={DARK} caption="عمودي · أبيض · sio-lockup-vertical-white" />
      <Tile form="emblem" variant="color" bg={DARK} caption="الرمز · ملون · sio-emblem-color" />
      <Tile form="emblem" variant="white" bg={DARK} caption="الرمز منفرداً · أبيض" />
    </div>
  </AbsoluteFill>
);
