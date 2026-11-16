# افتتاحية «من فكرة إلى إنجاز» — 20 ثانية

تركيبات مستقلة داخل `src/videos/hasad-2026/entry.ts` (الفيلم المعتمد لم يُعدَّل):
- `Hasad-Opening-20s` — الافتتاحية وحدها (صورة + موسيقى + مؤثرات).
- `Hasad-Opening-Plus-Film` — الافتتاحية ثم الفيلم المعتمد مباشرة (نفس الخلفية الكحلية في نقطة الوصل).

## خط الإنتاج
| المرحلة | الأداة | الملفات |
|---|---|---|
| رسم الأصول | FLUX.1-schnell محليًا (Apache-2.0) عبر mflux | `production-assets.json` → `public/media/opening/assets/` |
| فصل الطبقات + إعادة بناء الخلفية | BiRefNet (MIT) | `tools/prep_layers.py` → `public/media/opening/layers/` |
| التحريك (Puppet Warp + كاميرا + عمق ميدان) | Blender 5.3 | `blender/puppet.py` + `blender/shots/*.json` → `public/media/opening/render/<shot>/` |
| التركيب والانتقالات والإضاءة والصوت | Remotion | `OpeningFilm.tsx`, `shots/`, `timing.ts`, `audio.ts` |
| الموسيقى والمؤثرات | توليد داخلي (ملك المؤسسة) | `src/audio/tools/gen-opening-audio.mjs` |

## التعديل
- **مدد اللقطات والانتقالات:** `timing.ts`.
- **حركة الشخصيات والكاميرا:** `blender/shots/<shot>.json` (مقابض: موضع u/v، نصف قطر r، مفاتيح dx/dy/rot، موجة wave)، ثم:
  `/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P src/videos/hasad-2026/opening/blender/puppet.py -- src/videos/hasad-2026/opening/blender/shots/1A.json`
- **رسومات القلم والأوراق والرمز الذهبي:** `shots/Shot1B.tsx`, `Shot2B.tsx`, `Shot3B.tsx`, `Shot4B.tsx`.
- **الصوت:** `audio.ts` (توقيت ومستوى كل مؤثر بالثواني والـ dB).
- **إعادة توليد أصل:** احذف ملفه من `public/media/opening/assets/` ثم:
  `node src/videos/hasad-2026/opening/tools/gen-frames.mjs src/videos/hasad-2026/opening/production-assets.json public/media/opening/assets <id>`

## التصدير
`node src/audio/tools/export.mjs --entry=src/videos/hasad-2026/entry.ts --id=Hasad-Opening-20s --name=<اسم> --lufs=-16 --only=final,clean,stems --stems=music,sfx`

## ملاحظات صريحة
- الحركة «أداء هادئ» بتشويه أجزاء الرسم (رأس، يد، تنفّس، ميل جذع، حركة قماش) مع كاميرا وعمق ميدان — وليست رسمًا يدويًا إطارًا بإطار.
- المهندس الأقدم في 4A مُركَّب من صورة مستقلة بالشماغ فوق الشخص الأصلي (الذي حُذف وأُعيد بناء ما خلفه).
- إطار 2A رُسم بإضاءة دافئة؛ لون الليل مضاف بالتدرّج في Remotion.
