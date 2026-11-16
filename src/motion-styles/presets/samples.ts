// Representative sample copy (infrastructure, irrigation, efficiency, digital transformation).
export const AR = {
  headline: "نحو إدارة ذكية لموارد المياه",
  lines: ["كفاءة تشغيلية أعلى", "بنية تحتية مستدامة", "تحول رقمي شامل"],
  blueprintTitle: "مقطع عرضي — قناة ري رئيسية",
  callouts: ["جسم القناة", "محطة الضخ", "منسوب المياه"] as [string, string, string],
  dims: ["العرض 12.5 م", "العمق 4.2 م"] as [string, string],
  isoTitle: "منظومة الري المتكاملة",
  holoTitle: "لوحة التشغيل الرقمية",
  holoRows: [
    { label: "كفاءة الري", value: 92.4, suffix: "%", decimals: 1 },
    { label: "التدفق اليومي", value: 18450, suffix: "م³" },
    { label: "المحطات المتصلة", value: 126 },
    { label: "خفض الفاقد", value: 37, suffix: "%" },
  ],
  gauge: { label: "جاهزية التحول الرقمي", value: 78 },
  particle: "مياه مستدامة",
  liquidTitle: "الري الذكي",
  liquidSub: "حلول مرنة لمستقبل مستدام",
  flapRows: ["التحول الرقمي", "كفاءة التشغيل"],
  counter: { from: 0, to: 2450, suffix: "كم", label: "شبكات ري مؤهلة" },
};

export const EN = {
  headline: "Smart Water Infrastructure",
  lines: ["Higher Operational Efficiency", "Sustainable Infrastructure", "Digital Transformation"],
  blueprintTitle: "Cross-section — Main Irrigation Canal",
  callouts: ["Canal body", "Pump station", "Water level"] as [string, string, string],
  dims: ["Width 12.5 m", "Depth 4.2 m"] as [string, string],
  isoTitle: "Integrated Irrigation System",
  holoTitle: "Digital Operations Panel",
  holoRows: [
    { label: "Irrigation efficiency", value: 92.4, suffix: "%", decimals: 1 },
    { label: "Daily flow", value: 18450, suffix: "m³" },
    { label: "Connected stations", value: 126 },
    { label: "Loss reduction", value: 37, suffix: "%" },
  ],
  gauge: { label: "Digital readiness", value: 78 },
  particle: "WATER",
  liquidTitle: "Smart Irrigation",
  liquidSub: "Fluid solutions for a sustainable future",
  flapRows: ["DIGITAL 2026", "EFFICIENCY"],
  counter: { from: 0, to: 2450, suffix: "km", label: "Rehabilitated networks" },
};
