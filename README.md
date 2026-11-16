# مكتبة موشن جرافيك عربية — Remotion

قوالب احترافية للفيديو المؤسسي بدقة 1920×1080 و30 إطاراً في الثانية، تدعم العربية واتجاه RTL، بخلفية شفافة (ProRes 4444 + Alpha) جاهزة لـ Premiere Pro.

## القوالب

| # | القالب | التكوينات في Studio | الملف |
|---|---|---|---|
| 1 | الإحصائيات والعدّادات | `Stat-Single`، `Stat-Row` | `src/templates/StatCounter.tsx` |
| 2 | العناوين السينمائية وشريط الاسم | `Title-Cinematic`، `LowerThird-Panel`، `LowerThird-Minimal` | `CinematicTitle.tsx`، `LowerThird.tsx` |
| 3 | بطاقات الإنفوغرافيك | `Infographic-Rings`، `Infographic-Bars` | `InfographicCards.tsx` |
| 4 | بطاقة معلومات المشروع | `Project-Card`، `Project-Wide` | `ProjectCard.tsx` |
| 5 | الانتقالات بين الأقسام | `Transition-Panels`، `Transition-Sweep`، `Transition-Shutter` | `SectionTransition.tsx` |
| — | معاينة شاملة | `Showreel` | `src/preview/Showreel.tsx` |

## أين أعدّل؟

| ماذا | أين |
|---|---|
| ألوان الهوية، الخطوط، نوع الأرقام، توقيت الحركة | `src/config/brand.ts` (يسري على كل القوالب) |
| النصوص والأرقام الافتراضية لكل قالب | `src/config/defaults.ts` |
| تعديل سريع ومعاينة فورية | لوحة Props على يمين Studio |
| نسخة مخصصة بدون تعديل الكود | ملف JSON في `props/` ثم `--props=` (انظر المثال) |

### خصائص مشتركة في كل القوالب
- `durationInSeconds`: مدة المقطع (طول التكوين يتبعها تلقائياً).
- `digits`: الافتراضي `"latin"` (0123)، أي الأرقام الإنجليزية في كل القوالب. يمكن تغييره إلى `"arabic"` (٠١٢٣) لقالب بعينه.
- `rtl`: الاتجاه، الافتراضي `true`.
- `colors`: لتغيير أي لون لهذا القالب فقط، مثل `{ "accent": "#2BB673" }`.
- `fonts`: `{ "display": "NotoKufiArabic", "body": "IBMPlexSansArabic" }`، والخيارات المتاحة: `NotoKufiArabic`، `IBMPlexSansArabic`، `Tajawal`، `Cairo`.
- `timing`: `{ "enter": 0.9, "exit": 0.6, "stagger": 0.12 }` بالثواني.

### أيقونات متاحة للإنفوغرافيك
`users, growth, building, leaf, target, award, globe, partnership, education, factory, shield, briefcase, energy, water, calendar, percent, location, clock, wallet`

## التصدير

| الأمر | النتيجة |
|---|---|
| `npm run studio` | فتح المعاينة |
| `npm run render:all` | تصدير القوالب الاثني عشر بصيغة ProRes 4444 + Alpha إلى `out/` |
| `npm run render:all -- Stat-Row Project-Card` | تصدير قوالب محددة فقط |
| `npm run render:preview` | معاينة شاملة بصيغة MP4 صغيرة (بدون شفافية) |
| `npm run render:preview-alpha` | المعاينة الشاملة بصيغة ProRes 4444 شفافة |
| `npm run render:example` | مثال على تصدير قالب بإعدادات من ملف JSON |

### استخدام الانتقالات في Premiere
ضع ملف الانتقال على مسار V2 فوق نقطة القطع بحيث يقع **منتصف** المقطع على القطع تماماً. الإطار يكون مغطى بالكامل في المنتصف، فيختفي القطع. في `Transition-Shutter` يمتد التغطية الكاملة طوال `holdSeconds` مع عنوان القسم.

## قيود معروفة
- **الخطوط تُحمَّل من Google Fonts** وقت المعاينة والتصدير، فيلزم اتصال بالإنترنت. لاستخدام خط الهوية الرسمي أو العمل دون اتصال، أضف ملفات الخط داخل المشروع.
- **ضبابية الخلفية (glass blur)** لا يمكن نقلها عبر قناة Alpha، لذلك اللوحات شبه شفافة بدلاً منها.
- **حجم الملفات كبير** في ProRes 4444 (من 3 إلى 150 ميغابايت لكل قالب بين 1.5 و7 ثوانٍ)، وهذا طبيعي لهذه الصيغة.
- **عمق الألوان:** يظهر في Premiere كـ 12-bit (`yuva444p12le`)، وهذا هو التخزين الداخلي القياسي لـ ProRes 4444.
- **حواف داكنة حول النص:** إذا ظهرت في Premiere، اضغط بالزر الأيمن على المقطع ← Modify ← Interpret Footage، ثم جرّب خيار Alpha المناسب (Premultiplied/Straight).
- **الأرقام العربية** تستخدم الفاصلة العشرية العربية (٫) وفاصل الآلاف (٬)، وشكلهما يعتمد على الخط المستخدم.

## الشعار الرسمي (المؤسسة العامة للري)

- **الملفات:** في `public/brand/logos/`، منسوخة كما هي دون أي تعديل (البصمات موثّقة في `README.md` داخل المجلد).
- **السجل المركزي:** `src/config/logos.ts`.

| الشكل (`form`) | النسخ المتوفرة (`variant`) |
|---|---|
| `emblem`: الرمز وحده | `color` |
| `lockup`: أفقي | `color`، `blue` |
| `lockupVertical`: عمودي | `white`، `black` |

- **المكوّن:** `src/lib/Logo.tsx`، ومثال الاستخدام: `<Logo form="lockupVertical" variant="auto" background="dark" height={250} />`.
  - **الشعار الافتراضي (معتمد):** إذا لم يُحدَّد `form`، يُستخدم **العمودي الأبيض** على الخلفيات الداكنة، والأفقي الملون على الفاتحة. الإعداد في `DEFAULT_FORM`.
  - **`variant: "auto"`:** على الخلفيات الداكنة يجرّب الأبيض ثم الملون. على الفاتحة يجرّب الملون ثم الأزرق ثم الأسود.
  - **طلب نسخة غير موجودة:** يُظهر خطأ واضحاً، ولا يُولّد بديلاً.
  - **الحفاظ على الشعار:** النسبة الأصلية ثابتة، ولا ظلال ولا فلاتر، والحركة الوحيدة ظهور الشعار كاملاً بالشفافية.
- **في القوالب:** خاصية `logo` متاحة في `CinematicTitle` و`LowerThird` و`ProjectCard`.
- **في Studio:** مجلد **Brand** يضم لوحة الشعارات ونسخاً من القوالب مع الشعار.

## خط الأرقام
- **الخط:** جميع الأرقام تُعرض بخط **Watad Regular**، وملفه في `public/brand/fonts/Watad-Regular.otf`. يشمل ذلك العدّادات والنسب والتواريخ والأرقام داخل النصوص.
- **طريقة التطبيق:** الخط مقصور على الرموز 0–9 و% + , - . عبر `unicode-range`، فتبقى الحروف العربية بخطوطها.
- **الإعداد:** في `numberFont` داخل `src/config/brand.ts`. لإيقافه، اجعل قيمته `null`.
- **الوزن:** للخط وزن واحد (Regular)، ويُعرض كما هو دون تسميك صناعي، حتى في العناوين العريضة.

## الإنتاج الفعلي
- **الدليل الكامل:** `CLAUDE.md`. **فهرس القوالب:** `TEMPLATES.md`.
- **إنشاء إنتاج جديد:** `npm run production:new -- <name>`، ثم عدّل `productions/<name>/production.json`.
- **المعاينة:** `npm run production:preview -- <name>`.
- **التسليم النهائي:** `npm run production:render -- <name>`، والملفات تُحفظ في `exports/<name>/prores-4444-alpha/`.
- **الأصول الإعلامية:** ضعها في `public/media/`. إعدادات التصدير المعتمدة في `export-presets.json`.

## نظام المؤثرات (FX)
- **التفاصيل:** في `TEMPLATES.md` و`CLAUDE.md`.
- **المعاينة:** مجلد **FX** في Studio. للمقارنة بين القالب قبل المؤثرات وبعدها، افتح `FX-Compare` أو `outputs/previews/SIO_FXCompare_v01_1080p30_Preview.mp4`.
- **التحكم:** عبر خاصية `fx`، وتشمل `intensity` (الشدة) و`speed` (السرعة) و`motionBlur` و`glow` و`lightSweep` و`particles`.
