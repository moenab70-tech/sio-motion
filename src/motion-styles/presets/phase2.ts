// Phase 2 presets (batch 1: Flow, Network, Timeline, Process, Charts).
import type { FlowLinesProps } from "../styles/FlowLines";
import type { NetworkMapProps, NetNode } from "../styles/NetworkMap";
import type { TimelineProps } from "../styles/Timeline";
import type { ProcessFlowProps } from "../styles/ProcessFlow";
import type { ChartsProps } from "../styles/Charts";

const inst = { mode: "institutional" as const, intensity: 0.45 };
const exp = { mode: "experimental" as const, intensity: 0.9 };
const en = { mode: "institutional" as const, lang: "en" as const, intensity: 0.45 };

const flowAR = { title: "شبكة نقل المياه", gauges: [{ label: "المصدر", value: 4200, unit: "م³/س" }, { label: "نقطة التوزيع", value: 2650, unit: "م³/س" }, { label: "المخرج", value: 1480, unit: "م³/س" }] } as const;
export const flow = {
  institutional: { ...inst, ...flowAR } as FlowLinesProps,
  experimental: { ...exp, ...flowAR, flowSpeed: 1.6 } as FlowLinesProps,
  english: { ...en, title: "Water Transfer Network", gauges: [{ label: "Source", value: 4200, unit: "m³/h" }, { label: "Distribution", value: 2650, unit: "m³/h" }, { label: "Outlet", value: 1480, unit: "m³/h" }] } as FlowLinesProps,
};

const enNodes: NetNode[] = [
  { x: 0.5, y: 0.52, label: "Control centre", hub: true }, { x: 0.25, y: 0.3, label: "North station" }, { x: 0.22, y: 0.72, label: "West station" },
  { x: 0.75, y: 0.28, label: "East station" }, { x: 0.8, y: 0.7, label: "South station" }, { x: 0.38, y: 0.18 }, { x: 0.62, y: 0.82 }, { x: 0.1, y: 0.5 }, { x: 0.9, y: 0.48 },
];
export const network = {
  institutional: { ...inst, title: "شبكة المحطات الذكية" } as NetworkMapProps,
  experimental: { ...exp, title: "شبكة المحطات الذكية", pulses: 4 } as NetworkMapProps,
  english: { ...en, title: "Smart Station Network", nodes: enNodes } as NetworkMapProps,
};

const tlAR = [
  { year: "2020", label: "إطلاق برنامج التأهيل" }, { year: "2022", label: "ربط المحطات رقمياً" },
  { year: "2024", label: "تشغيل مركز التحكم" }, { year: "2026", label: "الإدارة الذكية للمياه" }, { year: "2030", label: "استدامة شاملة" },
];
export const timeline = {
  institutional: { ...inst, title: "مسيرة التحول", items: tlAR, currentIndex: 3 } as TimelineProps,
  experimental: { ...exp, title: "مسيرة التحول", items: tlAR, currentIndex: 3 } as TimelineProps,
  english: { ...en, title: "Transformation Journey", currentIndex: 3, items: [
    { year: "2020", label: "Rehabilitation launch" }, { year: "2022", label: "Stations digitally linked" },
    { year: "2024", label: "Control centre live" }, { year: "2026", label: "Smart water management" }, { year: "2030", label: "Full sustainability" },
  ] } as TimelineProps,
};

const stepsAR = [
  { icon: "water", title: "المصدر", desc: "رصد الموارد المائية" }, { icon: "factory", title: "المعالجة", desc: "رفع جودة المياه" },
  { icon: "energy", title: "الضخ", desc: "تشغيل عالي الكفاءة" }, { icon: "leaf", title: "الري", desc: "توزيع ذكي ومستدام" },
] as ProcessFlowProps["steps"];
export const process = {
  institutional: { ...inst, title: "دورة المياه التشغيلية", steps: stepsAR } as ProcessFlowProps,
  experimental: { ...exp, title: "دورة المياه التشغيلية", steps: stepsAR } as ProcessFlowProps,
  english: { ...en, title: "Operational Water Cycle", steps: [
    { icon: "water", title: "Source", desc: "Resource monitoring" }, { icon: "factory", title: "Treatment", desc: "Quality improvement" },
    { icon: "energy", title: "Pumping", desc: "High-efficiency operation" }, { icon: "leaf", title: "Irrigation", desc: "Smart distribution" },
  ] } as ProcessFlowProps,
};

const years = ["2021", "2022", "2023", "2024", "2025", "2026"];
export const charts = {
  institutional: { ...inst, chart: "area", title: "كفاءة استخدام المياه", labels: years, values: [61, 66, 70, 76, 83, 91], unit: "النسبة %" } as ChartsProps,
  experimental: { ...exp, chart: "bars", title: "كفاءة استخدام المياه", labels: years, values: [61, 66, 70, 76, 83, 91] } as ChartsProps,
  english: { ...en, chart: "donut", title: "Water Use by Sector", labels: ["Agriculture", "Urban", "Industry"], values: [62, 26, 12], unit: "%" } as ChartsProps,
};
