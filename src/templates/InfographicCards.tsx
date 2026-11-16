// 3 ─ Animated infographic cards with icons & percentages
import React from "react";
import { AbsoluteFill } from "remotion";
import { useTemplate, riseStyle, type CommonProps } from "../lib/brand";
import { AnimatedNumber } from "../lib/AnimatedNumber";
import { Icon, type IconName } from "../lib/icons";
import { EASE, ramp } from "../lib/motion";
import { localizeDigits, percentSign } from "../lib/numbers";
import { ProgressRing } from "../lib/ProgressRing";

export type InfoCard = {
  icon: IconName;
  value: number; // the number shown
  isPercent?: boolean; // show ٪ and drive the ring/bar from value
  percent?: number; // ring/bar fill (0–100) when value isn't a percent
  suffix?: string;
  compact?: boolean;
  decimals?: number;
  label: string;
  description?: string;
};

export type InfographicCardsProps = CommonProps & {
  heading?: string;
  cards: InfoCard[];
  indicator: "ring" | "bar" | "none";
  columns?: number;
  cardWidth?: number;
};

export const InfographicCards: React.FC<InfographicCardsProps> = (props) => {
  const t = useTemplate(props);
  const { palette: c, font, digits, frame, s, out } = t;
  const cols = props.columns ?? Math.min(4, props.cards.length);
  const width = props.cardWidth ?? (cols >= 4 ? 370 : 430);
  const headIn = t.enter(0);

  return (
    <AbsoluteFill style={{ direction: t.dir, justifyContent: "center", alignItems: "center", fontFamily: font.body }}>
      {props.heading && (
        <div style={{ ...riseStyle(headIn, out, 18), fontFamily: font.display, fontSize: 56, fontWeight: 700, color: c.text, marginBottom: 56, lineHeight: 1.5, textShadow: `0 6px 30px ${c.shadow}` }}>
          {localizeDigits(props.heading, digits)}
        </div>
      )}
      <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, ${width}px)`, gap: 36 }}>
        {props.cards.map((card, i) => {
          const delay = 0.25 + i * t.timing.stagger * 1.8;
          const inT = t.enter(0, delay, t.timing.enter * 1.1);
          const fill = ramp(frame, s(delay + 0.35), s(1.8), EASE.count);
          const pct = (card.isPercent ? card.value : card.percent ?? 0) / 100;
          const suffix = card.isPercent ? percentSign(digits) : card.suffix;
          const number = (
            <AnimatedNumber value={card.value} progress={fill} digits={digits} decimals={card.decimals} compact={card.compact} suffix={suffix} suffixColor={c.accent} />
          );
          return (
            <div
              key={i}
              style={{
                opacity: inT * out,
                transform: `translateY(${(1 - inT) * 50 - (1 - out) * 20}px) scale(${0.96 + inT * 0.04})`,
                background: c.panel,
                border: `1px solid ${c.panelBorder}`,
                borderRadius: 28,
                padding: "38px 34px 36px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                textAlign: "center",
                boxShadow: `0 24px 60px ${c.shadow}`,
              }}
            >
              {props.indicator === "ring" ? (
                <ProgressRing size={190} stroke={9} progress={pct * fill} color={c.accent} track={c.track}>
                  <Icon name={card.icon} size={64} color={c.accent} />
                </ProgressRing>
              ) : (
                <div style={{ width: 104, height: 104, borderRadius: 52, background: c.track, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${0.7 + 0.3 * inT})` }}>
                  <Icon name={card.icon} size={54} color={c.accent} />
                </div>
              )}
              <div style={{ fontFamily: font.display, fontWeight: 700, fontSize: 76, color: c.text, lineHeight: 1.35, marginTop: 22 }}>{number}</div>
              <div style={{ fontSize: 32, fontWeight: 600, color: c.text, lineHeight: 1.5, marginTop: 4 }}>{localizeDigits(card.label, digits)}</div>
              {card.description && <div style={{ fontSize: 24, color: c.textMuted, lineHeight: 1.6, marginTop: 6 }}>{localizeDigits(card.description, digits)}</div>}
              {props.indicator === "bar" && (
                <div style={{ width: "100%", height: 8, borderRadius: 4, background: c.track, marginTop: 24, overflow: "hidden", display: "flex" }}>
                  <div style={{ width: `${pct * fill * 100}%`, background: c.accent, borderRadius: 4 }} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
