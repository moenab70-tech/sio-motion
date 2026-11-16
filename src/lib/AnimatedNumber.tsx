import React from "react";
import type { Digits } from "../config/brand";
import { formatNumber } from "./numbers";

/** A number that counts from 0 to `value` as `progress` goes 0 → 1. Isolated for correct RTL ordering. */
export const AnimatedNumber: React.FC<{
  value: number;
  progress: number;
  digits: Digits;
  decimals?: number;
  compact?: boolean;
  prefix?: string;
  suffix?: string;
  suffixScale?: number;
  suffixColor?: string;
}> = ({ value, progress, digits, decimals = 0, compact, prefix = "", suffix = "", suffixScale = 0.55, suffixColor }) => {
  const shown = progress >= 1 ? value : value * progress;
  return (
    <bdi style={{ fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }}>
      {prefix && <span style={{ fontSize: `${suffixScale}em`, color: suffixColor, marginInlineEnd: "0.15em" }}>{prefix}</span>}
      {formatNumber(shown, { digits, decimals, compact })}
      {suffix && <span style={{ fontSize: `${suffixScale}em`, color: suffixColor, marginInlineStart: suffix.length > 1 ? "0.3em" : "0.08em" }}>{suffix}</span>}
    </bdi>
  );
};
