# SIO | تقرير سدود منطقة الرياض خلال الحالة المطرية (10–11 نوفمبر 2026م)

مدخل مستقل: `entry.ts` (لا يمس `src/Root.tsx` ولا قالب `dams-2026` المعتمد — يستورد منه الشعارات والمقاسات فقط).

## الملفات
- `data.ts` — **كل البيانات**: النصوص، الإحصائيات، السدود الـ13 (الترتيب، المحافظة، السعة، الوارد، المواد، المدة)، أطوال المشاهد، الصوت. عدّل هنا فقط.
- `RainfallIntro` · `RainfallStats` · `DamCapacityChart` · `DamProfile` · `RainfallOutro` — المكونات.
- `RiyadhDamsReport.tsx` — الفيديو الكامل (Intro → Stats → Chart → 13 سدًا → Outro).
- المواد الأصلية من العرض التقديمي: `public/media/riyadh-dams-2026/original/` (رقم = ترتيب السعة). الفحيحيل: نسخة 1080×1920 من أصل 4K، البرة: نسخة مصححة الاتجاه (الأصلان محفوظان).

## الأوامر (من جذر المشروع)
- Studio: `npx remotion studio src/videos/riyadh-dams-2026/entry.ts --port 3004`
- معاينة منخفضة: `PREVIEW=1 npx remotion render src/videos/riyadh-dams-2026/entry.ts RD-Master out/riyadh-dams/preview.mp4 --scale=0.5 --crf=26`
- النهائي: `PREVIEW=1 npx remotion render src/videos/riyadh-dams-2026/entry.ts RD-Master exports/riyadh-dams-2026/Riyadh_Dams_Rainfall_Report_Nov2026.mp4 --crf=16 --jpeg-quality=95`
- بدون موسيقى: `RD-Master-NoMusic` · مشاهد مستقلة: `RD-Intro`, `RD-Stats`, `RD-Chart`, `RD-Outro`, `RD-Dam-01`…`RD-Dam-13`
- شفاف Alpha (ProRes 4444، **بدون** PREVIEW=1): أضف `-Alpha` لأي معرّف مشهد، مثل `RD-Stats-Alpha`.
