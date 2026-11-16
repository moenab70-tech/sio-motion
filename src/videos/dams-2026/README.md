# فيديوهات السدود 2026 — `DamRainfallReport`

فيديو عمودي مستقل لكل سد: 1080×1920 · 30fps · H.264.

## سد جديد
أضف كائناً في `config.ts` بنفس الحقول ثم سجّله في `Root.tsx` (سطر Composition واحد):
`damName` · `governorate` · `storageCapacity` (م³) · `incomingWater` (م³) · `videoSources` · `duration` (ثوانٍ) · `music` (اختياري، مرخّص).

كل لقطة في `videoSources`: `src` (داخل public) · `from` (ثانية البداية) · `focusX/focusY` (إعادة التأطير 0–1) · `panToX` (تحريك أفقي هادئ) · `zoom` · `weight` · `volume`.
المدد تتوزع تلقائياً لتملأ `duration` مع انتقالات تلاشٍ (18 إطاراً).

## اختيار اللقطات
ورقة لقطات لأي مقاطع: Composition `Dam-ContactSheet` مع `--props` (انظر `ContactSheet.tsx`).

## الملاحظات
- المقاطع الأصلية: `public/media/video/dams/<dam>/` (من Google Drive «سدود منطقة الرياض»، HEVC 1080p 60fps **بدون صوت**). harimla_5/6/7 ملف واحد مكرر.
- الشعارات: المؤسسة (`lib/Logo`، أفقي ملوّن) يساراً، الوزارة (`PartnerLogo`) يميناً، الدائرتان فقط (`logoMode: "emblem"`) بقطر موحّد، بدون خلفية.
- المساحات الآمنة في `DAM_LAYOUT` (أعلى 150، أسفل 400، جوانب 64).

## التشغيل
- Studio: `npx remotion studio src/videos/dams-2026/entry.ts --port 3003`
- معاينة: `PREVIEW=1 npx remotion render src/videos/dams-2026/entry.ts Dam-Harimla out/dams-2026/Harimla_preview.mp4`
- نهائي: `PREVIEW=1 npx remotion render src/videos/dams-2026/entry.ts Dam-Harimla exports/dams-2026/Harimla_Dam_Final.mp4 --crf=16 --jpeg-quality=95`
