# نظام الصوت — SIO Audio Production System

ثلاثة مسارات اختيارية لكل مشروع: **تعليق صوتي · موسيقى · مؤثرات**، مع Ducking وFade ومستويات بالـ dB، وتصدير منفصل.
لا يعدّل أي قالب أو هوية. يعمل بـ Remotion + ffmpeg المرفق مع Remotion فقط.

## الملفات
| المسار | الغرض |
|---|---|
| `src/audio/AudioMix.tsx` | المكوّن: `<AudioMix mix={…} durationInFrames solo="all|vo|music|sfx" />` |
| `src/audio/presets.ts` | 5 إعدادات: institutional-documentary · corporate-presentation · technical-explainer · cinematic-showcase · social-short |
| `src/audio/tools/export.mjs` | تصدير Final MP4 · Clean ProRes 422 HQ (بلا صوت) · Stems WAV 24-bit/48k · `--alpha` ProRes 4444 + تقرير الصوت |
| `src/audio/tools/tts-piper.mjs` | تعليق عربي محلي (Piper عبر sherpa-onnx) — **مسودة توقيت فقط** |
| `src/audio/tools/gen-sfx.mjs` | يولّد مكتبة المؤثرات + موسيقى مؤقتة برمجيًا (ملكية كاملة، بلا ترخيص خارجي) |
| `public/audio/{vo,music,sfx}/` | الملفات الصوتية · `vo/imported/` للتسجيلات البشرية |
| `public/audio/LICENSES.json` | مصدر وترخيص وبصمة كل ملف — **لا يُستخدم ملف بلا قيد هنا** |

## إعداد الصوت لفيديو (ملف واحد)
مثال: `src/videos/hasad-2026/audio.trial.ts`
- `enabled`: تشغيل/إيقاف كل مسار.
- `vo[]`: `{ src, startSeconds, gainDb? }` — المدة تُقرأ من الملف تلقائيًا (لتوقيت الـ Ducking).
- `music`: `{ src, startSeconds?, trimBeforeSeconds?, gainDb?, loop? }`.
- `sfx[]`: `{ src, atSeconds, gainDb? }` — حد أقصى للمؤثرات في كل 10 ثوانٍ حسب الـ preset (الزائد يُحذف مع تحذير).
- استيراد تسجيل جاهز: ضعه في `public/audio/vo/imported/` واكتب مساره، وسجّل ترخيصه.

## الأوامر
```bash
node src/audio/tools/gen-sfx.mjs
node src/audio/tools/tts-piper.mjs <lines.json> public/audio/vo/<project>
node src/audio/tools/export.mjs --entry=src/videos/hasad-2026/entry.ts --id=Hasad-Audio-Trial-15s --name=hasad-2026-audio-trial --lufs=-16 --tp=-1 [--only=final,clean,stems] [--alpha]
```

## الصوت النهائي
- يُقاس الـ mix بـ loudnorm (EBU R128) ثم يُطبّق **ربح خطي واحد** على الـ mix وعلى كل stem (فمجموع الـ stems = الـ mix).
- لا ضاغط ولا limiter → لا تشويه. إن كان بلوغ الهدف سيتجاوز `tp` يُكتفى بأقصى ربح آمن (يظهر في `report.json`).

## أدوات خارج المشروع
أُزيلت أدوات TTS (sherpa-onnx + صوت kareem) في 2026-11-15 بعد رفض جودة التعليق المولّد. لإعادتها: أعد تنزيلها إلى `~/Library/Application Support/sio-audio/` ثم استخدم `tts-piper.mjs`. التعليق المعتمد = تسجيل بشري في `public/audio/vo/imported/`.
