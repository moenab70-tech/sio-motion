// 1 ─ Animated statistics & counters (Arabic number formatting)
import React from "react";
import { AbsoluteFill } from "remotion";
import { useTemplate, riseStyle, type CommonProps } from "../lib/brand";
import { AnimatedNumber } from "../lib/AnimatedNumber";
import { EASE, ramp } from "../lib/motion";
import { localizeDigits, percentSign } from "../lib/numbers";

export type StatItem = {
  value: number;
  label: string;
  sublabel?: string;
  prefix?: string; // e.g. "+"
  suffix?: string; // e.g. "مليون", "ريال" — use "%" for a localized percent sign
  decimals?: number;
  compact?: boolean; // 1250000 → ١٫٢٥ مليون
};

export type StatCounterProps = CommonProps & {
  layout: "single" | "row"; // one hero number, or a row of 2–4 stats
  items: StatItem[];
  heading?: string; // optional small heading above the row
  countSeconds?: number; // how long numbers take to count up
  numberSize?: number; // px
  verticalPosition?: "center" | "lower";
};

export const StatCounter: React.FC<StatCounterProps> = (props) => {
  const t = useTemplate(props);
  const { palette: c, font, digits, frame, s, out } = t;
  const countDur = s(props.countSeconds ?? 2.2);
  const single = props.layout === "single";
  const size = props.numberSize ?? (single ? 210 : 128);
  const items = single ? props.items.slice(0, 1) : props.items.slice(0, 4);
  const headIn = t.enter(0);

  return (
    <AbsoluteFill
      style={{
        direction: t.dir,
        justifyContent: props.verticalPosition === "lower" ? "flex-end" : "center",
        alignItems: "center",
        paddingBottom: props.verticalPosition === "lower" ? 150 : 0,
        fontFamily: font.body,
      }}
    >
      {props.heading && !single && (
        <div style={{ ...riseStyle(headIn, out), fontSize: 34, letterSpacing: 0, color: c.accent, fontWeight: 500, marginBottom: 46, display: "flex", alignItems: "center", gap: 18 }}>
          <span style={{ width: 60 * headIn, height: 2, background: c.accent }} />
          {localizeDigits(props.heading, digits)}
          <span style={{ width: 60 * headIn, height: 2, background: c.accent }} />
        </div>
      )}
      <div style={{ display: "flex", alignItems: "stretch", justifyContent: "center" }}>
        {items.map((it, i) => {
          const delay = 0.15 + i * (t.timing.stagger * 2.5);
          const inT = t.enter(0, delay);
          const count = ramp(frame, s(delay + 0.1), countDur, EASE.count);
          const line = ramp(frame, s(delay + 0.35), s(0.9), EASE.out);
          const labelIn = t.enter(0, delay + 0.45);
          const suffix = it.suffix === "%" ? percentSign(digits) : it.suffix;
          return (
            <React.Fragment key={i}>
              {i > 0 && (
                <div style={{ width: 1.5, margin: "10px 70px", background: c.panelBorder, transform: `scaleY(${line * out})` }} />
              )}
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: single ? 0 : 300 }}>
                <div
                  style={{
                    ...riseStyle(inT, out, 40),
                    fontFamily: font.display,
                    fontWeight: 700,
                    fontSize: size,
                    lineHeight: 1.25,
                    color: c.text,
                    textShadow: `0 8px 40px ${c.shadow}`,
                  }}
                >
                  <AnimatedNumber value={it.value} progress={count} digits={digits} decimals={it.decimals} compact={it.compact} prefix={it.prefix} suffix={suffix} suffixColor={c.accent} />
                </div>
                <div style={{ height: 3, width: (single ? 220 : 90) * line, background: c.accent, borderRadius: 2, margin: single ? "18px 0 26px" : "12px 0 22px", opacity: out }} />
                <div style={{ ...riseStyle(labelIn, out, 16), fontSize: single ? 52 : 38, fontWeight: 600, color: c.text, textShadow: `0 4px 24px ${c.shadow}`, textAlign: "center", lineHeight: 1.5 }}>
                  {localizeDigits(it.label, digits)}
                </div>
                {it.sublabel && (
                  <div style={{ ...riseStyle(t.enter(0, delay + 0.6), out, 12), fontSize: single ? 32 : 26, fontWeight: 400, color: c.textMuted, marginTop: 6, textAlign: "center", lineHeight: 1.5 }}>
                    {localizeDigits(it.sublabel, digits)}
                  </div>
                )}
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
