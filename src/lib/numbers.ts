import type { Digits } from "../config/brand";

export type NumberFormat = {
  digits: Digits;
  decimals?: number;
  compact?: boolean; // 1,250,000 → ١٫٢٥ مليون
  grouping?: boolean; // thousands separators
};

/** Arabic-aware number formatting (Arabic-Indic or Latin digits, Arabic separators & compact words). */
export const formatNumber = (value: number, { digits, decimals = 0, compact = false, grouping = true }: NumberFormat) => {
  const locale = digits === "arabic" ? "ar-u-nu-arab" : "ar-u-nu-latn";
  return new Intl.NumberFormat(locale, {
    notation: compact ? "compact" : "standard",
    compactDisplay: "long",
    minimumFractionDigits: compact ? 0 : decimals,
    maximumFractionDigits: decimals,
    useGrouping: grouping,
  })
    .format(value)
    .replace(/[؜‎‏]/g, ""); // strip invisible bidi marks Intl may insert
};

export const percentSign = (digits: Digits) => (digits === "arabic" ? "٪" : "%");

/** Converts digits inside free text (e.g. "18 شهراً" / "١٨ شهراً") to the chosen digit style, both ways. */
export const localizeDigits = (text: string, digits: Digits) =>
  digits === "arabic"
    ? text.replace(/[0-9]/g, (d) => "٠١٢٣٤٥٦٧٨٩"[Number(d)])
    : text.replace(/[٠-٩]/g, (d) => String(d.charCodeAt(0) - 0x0660)).replace(/٪/g, "%");
