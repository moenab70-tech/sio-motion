// Phase 2 presets (batch 2: Compare, LineArt, Geometric, Topographic).
import type { SplitCompareProps } from "../styles/SplitCompare";
import type { LineArtProps } from "../styles/LineArt";
import type { GeometricPatternProps } from "../styles/GeometricPattern";
import type { TopographicProps } from "../styles/Topographic";

const inst = { mode: "institutional" as const, intensity: 0.45 };
const exp = { mode: "experimental" as const, intensity: 0.9 };
const en = { mode: "institutional" as const, lang: "en" as const, intensity: 0.45 };

const cmpAR = { title: "أثر تأهيل القنوات على الفاقد", before: { label: "قبل التأهيل", value: 38, unit: "%", caption: "نسبة فاقد المياه" }, after: { label: "بعد التأهيل", value: 12, unit: "%", caption: "نسبة فاقد المياه" }, lowerIsBetter: true };
export const compare = {
  institutional: { ...inst, ...cmpAR } as SplitCompareProps,
  experimental: { ...exp, ...cmpAR } as SplitCompareProps,
  english: { ...en, title: "Canal Rehabilitation Impact on Losses", before: { label: "Before", value: 38, unit: "%", caption: "Water loss rate" }, after: { label: "After", value: 12, unit: "%", caption: "Water loss rate" }, lowerIsBetter: true } as SplitCompareProps,
};

const laAR = [
  { icon: "water", label: "موارد مائية" }, { icon: "factory", label: "محطات ضخ" }, { icon: "energy", label: "طاقة" },
  { icon: "leaf", label: "زراعة مستدامة" }, { icon: "globe", label: "تحول رقمي" },
] as LineArtProps["items"];
export const lineArt = {
  institutional: { ...inst, title: "منظومة متكاملة", items: laAR } as LineArtProps,
  experimental: { ...exp, title: "منظومة متكاملة", items: laAR, strokeWidth: 1.8 } as LineArtProps,
  english: { ...en, title: "An Integrated System", items: [
    { icon: "water", label: "Water resources" }, { icon: "factory", label: "Pump stations" }, { icon: "energy", label: "Energy" },
    { icon: "leaf", label: "Sustainable farming" }, { icon: "globe", label: "Digital" },
  ] } as LineArtProps,
};

export const geometric = {
  institutional: { ...inst, title: "رؤية مستدامة", subtitle: "إدارة متكاملة للمياه" } as GeometricPatternProps,
  experimental: { ...exp, title: "رؤية مستدامة", subtitle: "إدارة متكاملة للمياه", cell: 96 } as GeometricPatternProps,
  english: { ...en, title: "A Sustainable Vision", subtitle: "Integrated water management" } as GeometricPatternProps,
};

export const topo = {
  institutional: { ...inst, title: "تضاريس حوض التجميع", levelLabel: "منسوب المياه" } as TopographicProps,
  experimental: { ...exp, title: "تضاريس حوض التجميع", levelLabel: "منسوب المياه", levels: 20 } as TopographicProps,
  english: { ...en, title: "Catchment Terrain", levelLabel: "Water level" } as TopographicProps,
};
