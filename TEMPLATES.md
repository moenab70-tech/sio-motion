# فهرس القوالب — SIO Motion Graphics

كل القوالب: **1920×1080 · 30fps · خلفية شفافة · RTL**. تُستخدم في `productions/<اسم>/production.json` عبر `template` (المعرّف) و`props` (ما تريد تغييره فقط — الباقي يأخذ القيم الافتراضية من `src/config/defaults.ts`).

> **قاعدة الدمج:** القيم في `props` تستبدل القيم الافتراضية على المستوى الأول. الكائنات المتداخلة (`items`، `cards`، `budget`، `colors`…) تُكتب **كاملة** عند تغييرها.

## الخصائص المشتركة (كل القوالب)

| الخاصية | النوع | الافتراضي | الوصف |
|---|---|---|---|
| `durationInSeconds` | رقم | حسب القالب | مدة المقطع؛ طول التكوين يتبعها تلقائياً |
| `digits` | `"latin"` \| `"arabic"` | `"latin"` | شكل الأرقام (المعتمد: إنجليزي) |
| `rtl` | منطقي | `true` | اتجاه التخطيط |
| `colors` | كائن | من `brand.ts` | تجاوز ألوان لهذا المقطع فقط: `text, textMuted, accent, secondary, panel, panelBorder, track, shadow` |
| `fonts` | كائن | `{display:"NotoKufiArabic", body:"IBMPlexSansArabic"}` | الخيارات: `NotoKufiArabic`، `IBMPlexSansArabic`، `Tajawal`، `Cairo` |
| `timing` | كائن | `{enter:0.9, exit:0.6, stagger:0.12}` | بالثواني: مدة الدخول، مدة الخروج، الفاصل بين العناصر |

---

## 1 · الإحصائيات والعدّادات — `StatCounter`

| المعرّف | الوظيفة | المدة |
|---|---|---|
| `Stat-Single` | رقم رئيسي واحد كبير مع وصف | 6 ث |
| `Stat-Row` | صف من 2–4 مؤشرات مع عنوان | 6 ث |

| الخاصية | الوصف |
|---|---|
| `layout` | `"single"` أو `"row"` |
| `heading` | عنوان صغير فوق الصف (row فقط) |
| `items[]` | **حد أقصى 4** (1 في single). لكل عنصر: `value` (رقم)، `label`، `sublabel`، `prefix` (مثل `"+"`)، `suffix` (`"%"` أو كلمة مثل `"مليار"`)، `decimals`، `compact` (1250000 ← 1.25 مليون) |
| `countSeconds` | مدة العدّ (افتراضي 2.2) |
| `numberSize` | حجم الرقم بالبكسل |
| `verticalPosition` | `"center"` أو `"lower"` |

## 2 · العناوين وشريط الاسم

| المعرّف | الوظيفة | المدة |
|---|---|---|
| `Title-Cinematic` | عنوان سينمائي يظهر كلمة كلمة | 6 ث |
| `Title-WithLogo` | نفسه مع الشعار العمودي الأبيض | 6 ث |
| `LowerThird-Panel` | شريط اسم على لوحة داكنة | 6 ث |
| `LowerThird-Minimal` | شريط اسم بدون لوحة | 6 ث |
| `LowerThird-WithLogo` | شريط اسم مع الشعار | 6 ث |

**`CinematicTitle`:** `eyebrow` (سطر صغير)، `title`، `subtitle`، `align` (`"center"`/`"start"`)، `titleSize`، `pushIn` (تكبير بطيء، افتراضي مفعّل)، `logo`.

**`LowerThird`:** `name`، `role`، `organization`، `variant` (`"panel"`/`"minimal"`)، `side` (`"start"` = يمين، `"end"` = يسار)، `marginX`، `marginBottom`، `logo`.

## 3 · بطاقات الإنفوغرافيك — `InfographicCards`

| المعرّف | الوظيفة | المدة |
|---|---|---|
| `Infographic-Rings` | بطاقات بأيقونة داخل حلقة نسبة | 7 ث |
| `Infographic-Bars` | بطاقات بأيقونة وشريط نسبة | 7 ث |

| الخاصية | الوصف |
|---|---|
| `heading` | عنوان فوق البطاقات |
| `indicator` | `"ring"` أو `"bar"` أو `"none"` |
| `columns`، `cardWidth` | التخطيط (افتراضي حتى 4 أعمدة) |
| `cards[]` | `icon`، `value`، `isPercent` (يعرض % ويملأ الحلقة)، `percent` (نسبة الملء إن لم تكن القيمة نسبة)، `suffix`، `compact`، `decimals`، `label`، `description` |

**الأيقونات:** `users, growth, building, leaf, target, award, globe, partnership, education, factory, shield, briefcase, energy, water, calendar, percent, location, clock, wallet`

## 4 · بطاقة معلومات المشروع — `ProjectCard`

| المعرّف | الوظيفة | المدة |
|---|---|---|
| `Project-Card` | بطاقة عمودية | 7 ث |
| `Project-Wide` | شريط عريض أسفل الشاشة | 7 ث |
| `Project-WithLogo` | بطاقة عمودية مع الشعار | 7 ث |
| `Project-Wide-WithLogo` | شريط عريض مع الشعار | 7 ث |

| الخاصية | الوصف |
|---|---|
| `projectName`، `tag`، `status` | اسم المشروع، التصنيف، الحالة |
| `location`، `duration` | نص حر (الأرقام داخله تتحول تلقائياً) |
| `budget` | `{ value, currency, compact, decimals }` — يُكتب كاملاً |
| `progress` | نسبة الإنجاز 0–100 |
| `labels` | تغيير العناوين: `{location, duration, budget, progress}` |
| `layout` | `"card"` أو `"wide"` |
| `side` | `"start"` / `"center"` / `"end"` (للبطاقة) |
| `logo` | الشعار |

## 5 · الانتقالات — `SectionTransition`

| المعرّف | الوظيفة | المدة |
|---|---|---|
| `Transition-Panels` | شرائح متتابعة | 1.6 ث |
| `Transition-Sweep` | مسح مائل بطبقات | 1.4 ث |
| `Transition-Shutter` | ستارة تُغلق مع عنوان القسم ثم تُفتح | 3 ث |

**الاستخدام في Premiere:** ضع المقطع على V2 بحيث يقع **منتصفه** على نقطة القطع؛ الإطار مغطى 100% في المنتصف (وطوال `holdSeconds` في Shutter).

| الخاصية | الوصف |
|---|---|
| `variant` | `"panels"` / `"sweep"` / `"shutter"` |
| `layers` | ألوان الطبقات (الأمامية آخراً) |
| `panelCount` | عدد الشرائح |
| `holdSeconds` | مدة التغطية الكاملة |
| `label`، `sublabel` | عنوان القسم أثناء التغطية |

---

## الشعار — خاصية `logo` (في `CinematicTitle`، `LowerThird`، `ProjectCard`)

`{ "background": "dark", "height": 250 }` — بدون `form` يُستخدم الافتراضي المعتمد (العمودي الأبيض على الداكن).

| `form` | `variant` المتوفرة |
|---|---|
| `emblem` (الرمز) | `color` |
| `lockup` (أفقي) | `color`، `blue` |
| `lockupVertical` (عمودي) | `white`، `black` |

أحجام مقترحة للعمودي: 250 للعنوان، 190 لشريط الاسم، 170 للبطاقة.

## تكوينات المعاينة (ليست للتسليم)

| المعرّف | الوظيفة |
|---|---|
| `Showreel` | عرض شامل لكل القوالب (`showBackground: true/false`) |
| `Logo-Board` | لوحة جميع الشعارات الرسمية |

---

# نظام المؤثرات المتقدم (مجلد FX في Studio)

القوالب السابقة لم تتغيّر. المؤثرات إما قوالب جديدة، أو طبقات منفصلة، أو غلاف (`FxEnhanced`) يضيف عمقاً **خلف** قالب قديم دون تعديله.

## التحكم المشترك — خاصية `fx` (الافتراضي في `src/config/fx.ts`)

| الخاصية | الافتراضي | الوصف |
|---|---|---|
| `intensity` | `0.5` | شدة المؤثرات 0–1 (الضبابية، التوهج، الجزيئات، الضوء) |
| `speed` | `1` | سرعة الحركة (0.8 أبطأ، 1.2 أسرع)؛ المدة تبقى `durationInSeconds` |
| `motionBlur` | `true` | ضبابية حركة اتجاهية من سرعة العنصر الفعلية |
| `glow` | `true` | توهج ذهبي خفيف حول النص الكبير (لا يطبَّق على الشعار أبداً) |
| `lightSweep` | `true` | مرور ضوئي واحد على العنوان بعد استقراره |
| `particles` | `false` | جزيئات عمق خلف المحتوى |

## القوالب

| المعرّف | الفئة | الوظيفة | المدة |
|---|---|---|---|
| `FX-Title-Rise` | Typography + Motion Blur | كلمات تصعد من قناع مع ضبابية حركة عمودية | 6 ث |
| `FX-Title-Focus` | Typography + Depth | كلمات تدخل من خارج التركيز (عمق ميدان) + الشعار العمودي + جزيئات | 6 ث |
| `FX-Title-Sweep` | Typography + Light | كلمات تنزلق أفقياً بضبابية حركة + مرور ضوئي ذهبي | 6 ث |
| `FX-Bars-3D` | 3D + Infographic | رسم أعمدة ثلاثي الأبعاد مع حركة كاميرا وأرقام عدّادة حادة | 8 ث |
| `FX-Stat-Row` | Depth | `Stat-Row` الأصلي + حلقات 3D وجزيئات خلفه | 6 ث |
| `FX-Infographic` | Particles | `Infographic-Rings` الأصلي + جزيئات خلفه | 7 ث |
| `FX-Scenes` | Transitions | تسلسل مشاهد من القوالب الحالية بانتقالات سينمائية | ~24 ث |
| `FX-Depth-3D` | طبقة 3D | حلقات وكرات ثلاثية الأبعاد مع حركة كاميرا — تحت العناوين | 8 ث |
| `FX-Particles` | طبقة | جزيئات عمق شفافة | 8 ث |
| `FX-LightLeak` | طبقة ضوء | تسرّب ضوئي — **ضعه في Premiere بوضع Screen أو Add** | 4 ث |
| `FX-Compare` | معرض | مقارنة قبل/بعد (للمراجعة فقط) | 30 ث |

### `FxTitle` (FX-Title-*)
`eyebrow`، `title`، `subtitle`، `style` (`"rise"` / `"focus"` / `"sweep"`)، `align`، `titleSize`، `logo`، `fx`.

### `Bars3D` (FX-Bars-3D)
`heading`، `items[]` (2–7: `label`، `value`، `suffix`، `decimals`، `compact`)، `camera` (`"push"` / `"orbit"` / `"static"`)، `highlightIndex` (العمود الذهبي؛ افتراضياً الأكبر)، `fx`.

### `FxEnhanced` (FX-Stat-Row، FX-Infographic)
`scene: { template, props }` — `template` أحد: `CinematicTitle`، `StatCounter`، `InfographicCards`، `ProjectCard`، `LowerThird`، `FxTitle`، `Bars3D`. و`layers: { depth3D, particles }`، و`fx`.

### `FxScenes` (FX-Scenes)
`scenes[]` (نفس صيغة `scene`)، `transition`: `"brandWipe"` (مسح ناعم بخط ذهبي من جهة القراءة) / `"blurDissolve"` (خروج عن التركيز ودخول إليه) / `"slide"` / `"fade"` — قيمة واحدة أو قائمة لكل فاصل، `transitionSeconds`، `fx`. المدة الكلية = مجموع المشاهد − التداخلات.

### الطبقات
- `FX-Depth-3D`: `rings`، `spheres`، `colors`، `fx`.
- `FX-Particles`: `count`، `colors`، `seed`، `fx`.
- `FX-LightLeak`: `hueShift` (0–360)، `seed`، `fx`.
