// ─────────────────────────────────────────────────────────────
// Default content for each template. Edit here, in Studio's
// right-hand "Props" panel, or pass a JSON file with --props.
// ─────────────────────────────────────────────────────────────
import type { StatCounterProps } from "../templates/StatCounter";
import type { CinematicTitleProps } from "../templates/CinematicTitle";
import type { LowerThirdProps } from "../templates/LowerThird";
import type { InfographicCardsProps } from "../templates/InfographicCards";
import type { ProjectCardProps } from "../templates/ProjectCard";
import type { SectionTransitionProps } from "../templates/SectionTransition";

export const statSingle: StatCounterProps = {
  durationInSeconds: 6,
  layout: "single",
  items: [{ value: 1250000, compact: true, decimals: 2, prefix: "+", label: "مستفيد من برامج التنمية", sublabel: "خلال عام 2026" }],
};

export const statRow: StatCounterProps = {
  durationInSeconds: 6,
  layout: "row",
  heading: "أبرز المؤشرات",
  items: [
    { value: 87, suffix: "%", label: "رضا المستفيدين" },
    { value: 342, label: "مشروعاً منجزاً" },
    { value: 4.8, decimals: 1, suffix: "مليار", label: "حجم الاستثمار", sublabel: "ريال سعودي" },
  ],
};

export const cinematicTitle: CinematicTitleProps = {
  durationInSeconds: 6,
  eyebrow: "التقرير السنوي 2026",
  title: "نحو مستقبل أكثر استدامة",
  subtitle: "إنجازات تُبنى على رؤية واضحة",
  align: "center",
};

export const lowerThird: LowerThirdProps = {
  durationInSeconds: 6,
  name: "د. أحمد السالم",
  role: "الرئيس التنفيذي",
  organization: "هيئة التنمية الوطنية",
  variant: "panel",
  side: "start",
};

export const infographic: InfographicCardsProps = {
  durationInSeconds: 7,
  heading: "أثر البرامج في أرقام",
  indicator: "ring",
  cards: [
    { icon: "users", value: 92, isPercent: true, label: "نسبة التوظيف", description: "من خريجي البرامج" },
    { icon: "leaf", value: 64, isPercent: true, label: "خفض الانبعاثات", description: "مقارنة بعام 2020" },
    { icon: "education", value: 18500, percent: 74, label: "متدرب", description: "في 12 مدينة" },
    { icon: "partnership", value: 140, percent: 56, label: "شريكاً استراتيجياً" },
  ],
};

export const projectCard: ProjectCardProps = {
  durationInSeconds: 7,
  layout: "card",
  side: "start",
  tag: "بنية تحتية",
  status: "قيد التنفيذ",
  projectName: "مشروع تطوير الواجهة البحرية",
  location: "جدة، المملكة العربية السعودية",
  duration: "36 شهراً (2025 – 2028)",
  budget: { value: 2400000000, currency: "ريال", compact: true, decimals: 1 },
  progress: 68,
};

export const transitionPanels: SectionTransitionProps = {
  durationInSeconds: 1.6,
  variant: "panels",
};

export const transitionSweep: SectionTransitionProps = {
  durationInSeconds: 1.4,
  variant: "sweep",
};

export const transitionShutter: SectionTransitionProps = {
  durationInSeconds: 3,
  variant: "shutter",
  holdSeconds: 1.4,
  sublabel: "الفصل 02",
  label: "المشاريع الكبرى",
};

// ── Same templates with the official logo (Brand folder in Studio) ──
// No "form" given → central default for dark backgrounds (vertical white lockup).
export const titleWithLogo: CinematicTitleProps = { ...cinematicTitle, titleSize: 104, logo: { background: "dark", height: 250 } };
export const lowerThirdWithLogo: LowerThirdProps = { ...lowerThird, organization: undefined, logo: { background: "dark", height: 190 } };
export const projectWithLogo: ProjectCardProps = { ...projectCard, logo: { background: "dark", height: 170 } };
export const projectWideWithLogo: ProjectCardProps = { ...projectCard, layout: "wide", logo: { background: "dark", height: 160 } };
