// Phase 2 presets (batch 3: Radar, DataStream, Parallax, SwissGrid).
import type { RadarScanProps } from "../styles/RadarScan";
import type { DataStreamProps } from "../styles/DataStream";
import type { ParallaxLayersProps } from "../styles/ParallaxLayers";
import type { SwissGridProps } from "../styles/SwissGrid";

const inst = { mode: "institutional" as const, intensity: 0.45 };
const exp = { mode: "experimental" as const, intensity: 0.9 };
const en = { mode: "institutional" as const, lang: "en" as const, intensity: 0.45 };

const statusAR = [{ label: "المحطات النشطة", value: "126 / 128" }, { label: "ضغط الشبكة", value: "4.2 bar" }, { label: "تنبيهات", value: "1", alert: true }];
export const radar = {
  institutional: { ...inst, title: "مراقبة الشبكة لحظياً", status: statusAR } as RadarScanProps,
  experimental: { ...exp, title: "مراقبة الشبكة لحظياً", status: statusAR, rpm: 3.5 } as RadarScanProps,
  english: { ...en, title: "Real-time Network Monitoring", status: [{ label: "Active stations", value: "126 / 128" }, { label: "Network pressure", value: "4.2 bar" }, { label: "Alerts", value: "1", alert: true }],
    blips: [{ angle: 35, dist: 0.55, label: "Station 12" }, { angle: 110, dist: 0.8 }, { angle: 160, dist: 0.35, label: "Station 07" }, { angle: 215, dist: 0.7, label: "Possible leak", alert: true }, { angle: 290, dist: 0.5 }, { angle: 320, dist: 0.85, label: "Station 21" }] } as RadarScanProps,
};

const kpiAR = [{ label: "قراءة يومية", value: 1.2, suffix: "مليون", decimals: 1 }, { label: "دقة التنبؤ", value: 96, suffix: "%" }, { label: "زمن الاستجابة", value: 8, suffix: "دقائق" }];
export const stream = {
  institutional: { ...inst, title: "البيانات تقود القرار", kpis: kpiAR } as DataStreamProps,
  experimental: { ...exp, title: "البيانات تقود القرار", kpis: kpiAR, columns: 56 } as DataStreamProps,
  english: { ...en, title: "Data-Driven Decisions", kpis: [{ label: "Daily readings", value: 1.2, suffix: "M", decimals: 1 }, { label: "Forecast accuracy", value: 96, suffix: "%" }, { label: "Response time", value: 8, suffix: "min" }] } as DataStreamProps,
};

export const parallax = {
  institutional: { ...inst, title: "أرض تنبض بالحياة", subtitle: "مياه مستدامة لزراعة مزدهرة" } as ParallaxLayersProps,
  experimental: { ...exp, title: "أرض تنبض بالحياة", subtitle: "مياه مستدامة لزراعة مزدهرة", camera: "push" } as ParallaxLayersProps,
  english: { ...en, title: "Land Full of Life", subtitle: "Sustainable water for thriving agriculture" } as ParallaxLayersProps,
};

export const swiss = {
  institutional: { ...inst, kicker: "مؤشر الأداء 2026", bigNumber: { value: 92, suffix: "%" }, title: "كفاءة تشغيل المحطات", body: "ارتفاع مستمر في كفاءة التشغيل نتيجة الربط الرقمي والصيانة التنبؤية.", caption: "المصدر: بيانات تشغيلية" } as SwissGridProps,
  experimental: { ...exp, kicker: "مؤشر الأداء 2026", bigNumber: { value: 92, suffix: "%" }, title: "كفاءة تشغيل المحطات", body: "ارتفاع مستمر في كفاءة التشغيل نتيجة الربط الرقمي والصيانة التنبؤية.", caption: "المصدر: بيانات تشغيلية" } as SwissGridProps,
  english: { ...en, kicker: "Performance 2026", bigNumber: { value: 92, suffix: "%" }, title: "Station Operating Efficiency", body: "Steady gains driven by digital connectivity and predictive maintenance.", caption: "Source: operational data" } as SwissGridProps,
};
