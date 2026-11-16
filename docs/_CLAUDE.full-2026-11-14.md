# SIO Motion Graphics — تعليمات المشروع

مكتبة موشن جرافيك عربية (Remotion 4 + React + TypeScript) للمؤسسة العامة للري، تُصدّر طبقات شفافة لـ Adobe Premiere Pro.

- **تواصل مع المستخدم بالعربية.** المستخدم محرر فيديو ومصمم موشن (Premiere / After Effects) ويفضّل العمل عبر Claude Desktop لا الطرفية.
- المواصفات الثابتة: **1920×1080 · 30fps · RTL · خلفية شفافة · ProRes 4444 + Alpha**.

## قواعد لا تُكسر

1. **لا تُعِد بناء القوالب من الصفر.** عدّل عبر الخصائص (props) أو أضف خيارات جديدة للقوالب الموجودة.
2. **الشعارات** (`public/brand/logos/`): لا تعدّل، لا تقص، لا تعِد تلوين، لا تعِد رسم، لا تولّد بالذكاء الاصطناعي، لا ظلال ولا فلاتر، لا تحريك لأجزاء الشعار. المسموح فقط: ظهور/اختفاء الشعار كاملاً بالشفافية، وتغيير حجمه بنسبته الأصلية. استخدم دائماً المكوّن `src/lib/Logo.tsx`. أي نسخة جديدة تُضاف كما هي وتُسجَّل في `src/config/logos.ts` مع بصمتها في `public/brand/logos/README.md`.
3. **الهوية المعتمدة** (لا تغيّرها دون طلب صريح):
   - الشعار الافتراضي على الخلفيات الداكنة: **العمودي الأبيض** (`DEFAULT_FORM` في `logos.ts`).
   - **الأرقام كلها إنجليزية** (`defaultDigits = "latin"`) وبخط **Watad Regular** عبر `numberFont` في `src/config/brand.ts` (يطبَّق على 0–9 % + , - . فقط).
4. **لا تستنتج ألوان أو خطوط الهوية من الشعار.** الألوان الحالية في `defaultPalette` **مؤقتة** إلى أن يزوّد المستخدم دليل الهوية الرسمي.
5. **لا تحذف ملفات أو مشاريع سابقة** (بما فيها `out/_old-v1/` و`productions/*`) دون طلب صريح.
6. في النص العربي: لا `letterSpacing`، ولا تحريك حرفاً حرفاً (يكسر اتصال الحروف) — التحريك كلمةً كلمة.
7. لا تقل إن شيئاً اكتمل قبل أن ينجح `npm run typecheck` ويُصدَّر المقطع فعلاً وتُراجع إطاراته.

## نظام المؤثرات (FX)

- الكود في `src/fx/`، الإعدادات في `src/config/fx.ts` (الشدة/السرعة/التفعيل)، المحتوى في `src/config/fxDefaults.ts`. الفهرس في `TEMPLATES.md`.
- **مبدأ:** المؤثرات تخدم المعلومة ولا تنافسها. لا مؤثرات فوق الأرقام أو النصوص تعيق القراءة؛ طبقات العمق (3D/جزيئات) خلف المحتوى وبعيدة عن منطقة المعلومات.
- **الشعار:** لا ضبابية حركة ولا توهج ولا مرور ضوئي على الشعار — يبقى خارج طبقات المؤثرات (ظهور بالشفافية فقط).
- **ضبابية الحركة:** استخدم `DirectionalBlur` + `velocityBlur()` (SVG، تحافظ على Alpha). **لا تستخدم `@remotion/motion-blur`** — اختُبرت ولم تنتج أي ضبابية في هذا الإعداد وأزيلت.
- **3D:** `@remotion/three` + React Three Fiber؛ دائماً `gl={{ alpha: true, premultipliedAlpha: false }}`. المواد المعدنية تظهر داكنة بدون Environment map — استخدم `emissive` ومعدنية منخفضة. الأرقام والنصوص HTML فوق المشهد (حادة)، تُسقط بنفس رياضيات الكاميرا.
- **الانتقالات:** `@remotion/transitions` مع العروض المخصصة في `src/fx/presentations.tsx` (تُخفي المشهد الخارج بقناع مكمّل لأن المشاهد شفافة). من المدمجة استخدم فقط ما لا يحتاج HTML-in-Canvas: `fade`، `slide`، `wipe`، `iris`، `clockWipe`، `flip`. **لا تستخدم** `blurSlide`، `dissolve`، `filmBurn`، `zoomBlur`، `crossZoom`… (تتطلب Chrome 149+ مع علم تجريبي).
- **`@remotion/effects`:** يعمل فقط على `<Solid>`/`<Img>` (WebGL). مؤثراته على HTML تتطلب HTML-in-Canvas التجريبي — لا تعتمد عليها. التسرّب الضوئي طبقة منفصلة بوضع Screen.
- **Lottie:** غير مثبت (لا ملفات Lottie). عند الحاجة: `@remotion/lottie@4.0.543` + `lottie-web`.
- عند إضافة مكتبة `@remotion/*`: نفس إصدار `remotion` بالضبط (4.0.543) وبـ `--save-exact`.

## الهيكل

| المسار | المحتوى |
|---|---|
| `src/config/brand.ts` | **نظام الهوية المركزي**: الألوان، الخطوط، الأرقام، خط الأرقام، التوقيت |
| `src/config/logos.ts` | سجل الشعارات الرسمية والافتراضيات |
| `src/config/defaults.ts` | المحتوى الافتراضي لكل قالب |
| `src/templates/` | القوالب الخمسة (انظر `TEMPLATES.md`) |
| `src/lib/` | مكوّنات مشتركة: `Logo`، `AnimatedNumber`، `ProgressRing`، الحركة (`motion.ts`)، الأرقام (`numbers.ts`)، الخطوط، الأيقونات |
| `src/preview/` | `Showreel` و`Logo-Board` (للمعاينة فقط) |
| `src/Root.tsx` | تسجيل التكوينات (المجلدات في Studio) |
| `public/brand/` | ملفات الهوية الرسمية (شعارات + خط Watad) — للقراءة فقط |
| `public/media/` | الأصول الإعلامية للإنتاج (video / images / audio / documents) |
| `productions/<name>/production.json` | تعريف كل إنتاج: قائمة لقطات (قالب + props) |
| `productions/_template/` | قالب إنتاج جديد — لا تعدّله إلا لتحسين البداية الافتراضية |
| `exports/<name>/` | **المخرجات النهائية** (`prores-4444-alpha/`، `preview-h264/`، `render-report.json`) |
| `out/` | مخرجات التطوير واختبار القوالب |
| `export-presets.json` | **إعدادات التصدير المعتمدة** |
| `remotion.config.ts` | الافتراضي: ProRes 4444 + Alpha؛ `PREVIEW=1` ← H.264 |

## سير عمل إنتاج جديد (بدون إعادة تصميم)

```
npm run production:new -- <name>            # ينشئ productions/<name>/production.json
# عدّل اللقطات: template = معرّف من TEMPLATES.md، props = ما يتغيّر فقط
npm run production:preview -- <name>        # MP4 للمراجعة → exports/<name>/preview-h264/
npm run production:render -- <name>         # ProRes 4444 + Alpha → exports/<name>/prores-4444-alpha/
npm run production:render -- <name> --only=01-title,03-stats   # لقطات محددة
```

- `props` تُدمج سطحياً مع الافتراضيات: الكائنات/المصفوفات المتداخلة تُكتب كاملة.
- السكربت يتحقق من وجود القوالب ومن تكرار المعرّفات قبل التصدير.

## أوامر أخرى

| الأمر | الغرض |
|---|---|
| `npm run studio` | المعاينة والتعديل الحي (Studio على المنفذ 3000؛ يوجد `.claude/launch.json`) |
| `npm run typecheck` | فحص الأنواع — شغّله بعد كل تعديل للكود |
| `npm run render:all [-- <ids>]` | تصدير القوالب الافتراضية إلى `out/` |
| `npm run render:preview` / `render:preview-alpha` | المعاينة الشاملة MP4 / ProRes شفاف |

## إعدادات التصدير المعتمدة

| الإعداد | القيمة |
|---|---|
| الترميز | Apple ProRes 4444 (`--prores-profile=4444`) |
| البكسل | `yuva444p10le` (يخزّنه ProRes داخلياً 12-bit: `yuva444p12le`) |
| الإطارات | PNG (لحفظ الشفافية) |
| الدقة/المعدل | 1920×1080 · 30fps |
| المعاينة | H.264 · yuv420p · CRF 18 (بدون شفافية) |

**التحقق من الشفافية:** `npx remotion ffprobe` يجب أن يعرض `prores,4,…,yuva444p12le`. الـ FFmpeg المضمّن في Remotion مبني بحد أدنى (لا `overlay` ولا `rawvideo`)؛ لاستخراج إطار: `npx remotion ffmpeg -ss 3 -i file.mov -frames:v 1 -pix_fmt rgba frame.png`.

## الترخيص

- **Remotion** (ومنه `@remotion/transitions` و`@remotion/effects`) تحت "Remotion License": مجاني للأفراد، والشركات الربحية حتى 3 موظفين، والجهات غير الربحية. غير ذلك يتطلب **Company License** مدفوعة (remotion.dev/docs/license). وضع جهة حكومية حالة تحتاج تأكيداً من Remotion.
- Three.js، React Three Fiber، lucide-react: MIT. خطوط Google: OFL. خط Watad: ترخيص المستخدم.

## مشكلات وقيود معروفة

- الخطوط العربية (Noto Kufi Arabic / IBM Plex Sans Arabic) تُحمَّل من Google Fonts وقت التصدير ← يلزم اتصال بالإنترنت.
- Watad وزن واحد (Regular)؛ لا يُسمَّك صناعياً.
- لا توجد نسخة رسمية بيضاء للرمز منفرداً ولا للشعار الأفقي.
- في الأحجام الصغيرة (≤190px) يصغر السطر الإنجليزي داخل الشعار العمودي (~12px).
- ضبابية الخلفية (glass) لا تنتقل عبر Alpha؛ اللوحات شبه شفافة.
- لا يوجد Git (أدوات Apple للمطورين غير مثبتة) ← لا تاريخ نسخ.
- خطوط GE Dinar One موجودة على جهاز المستخدم لكنها غير معتمدة في المشروع بعد.
