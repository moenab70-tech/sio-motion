import type { Lang } from "./types";

/**
 * Splits text into animation units WITHOUT breaking Arabic shaping:
 * Arabic → whole words (letters must stay joined); English → words or grapheme clusters.
 */
export const segment = (text: string, lang: Lang, unit: "word" | "char" = "word"): string[] => {
  if (lang === "ar" || unit === "word") return text.split(/\s+/).filter(Boolean);
  const seg = new Intl.Segmenter("en", { granularity: "grapheme" });
  return [...seg.segment(text)].map((s) => s.segment);
};

/** Mixed-direction safety: numbers/latin inside Arabic stay isolated. */
export const bidiIsolate: React.CSSProperties = { unicodeBidi: "isolate" };
