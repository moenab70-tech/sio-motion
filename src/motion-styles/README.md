# Motion Styles Library — 20 styles (Phase 1 + Phase 2)

Isolated, reusable motion styles with their own Remotion entry point. **Production templates (`src/templates`, `src/fx`, `src/Root.tsx`), brand config, fonts, `package.json`, `remotion.config.ts` were not modified.**

```
src/motion-styles/
  entry.ts            isolated registerRoot (separate Studio / render entry)
  core/               shared API: types, brand-isolated tokens, useMotionStyle, Stage, text segmentation, SVG helpers
  styles/             7 styles (one file each)
  presets/            sample copy (AR/EN) + institutional / experimental / english presets
  registry/           central registry (registerStyle / getStyles)
  gallery/            Root (compositions) + StyleGallery (4-up comparison)
  tests/run.mjs       verification suite
```

## Run
- Studio: `npx remotion studio src/motion-styles/entry.ts`
- Render: `npx remotion render src/motion-styles/entry.ts <CompositionId> out/motion-styles/<name>.mov` (ProRes 4444 + alpha from the existing global config). Deliverables are stored in `outputs/` with SIO naming — see `OUTPUT_CATALOG.md`.
- Tests: `node src/motion-styles/tests/run.mjs`

Phase 2 presets: `presets/phase2.ts`, `presets/phase2b.ts`, `presets/phase2c.ts`. Tests: `node src/motion-styles/tests/run.mjs [StyleId …]` (limit render checks).

Compositions: `MS-Gallery-All`, `MS-Gallery-<Style>`, and per style `MS-<Style>-Institutional | -Experimental | -English`.

## Shared API (every style)
| prop | default | notes |
|---|---|---|
| `mode` | `"institutional"` | `"experimental"` = unapproved palette/fonts, never for production without approval |
| `lang` | `"ar"` | `"en"` supported |
| `direction` | `"auto"` | ar→rtl, en→ltr; or force `"rtl"`/`"ltr"` |
| `colors` | mode palette | `{ primary, secondary, accent, text, muted, background }` |
| `durationInFrames` | composition length | timings are fractions of this; seconds use the composition fps |
| `intensity` | `0.6` | 0–1 |
| `transparent` | `true` | `false` paints `colors.background` |
| `typography` | mode fonts | `{ display, body, weight, scale }` — FontName from `src/config/brand.ts` |
| `seed` | `"sio"` | deterministic variation |

### Brand isolation
- **Institutional** reads `defaultPalette` / `defaultFonts` from `src/config/brand.ts` read-only (those tokens are themselves provisional until the brand guide). Digits use the project font stack (Watad via `lib/fonts`). Restrained intensity in presets.
- **Experimental** palette (`core/tokens.ts`) and fonts are local to this library; the gallery tags them "غير معتمد مؤسسياً".
- The library never renders the official logo.

## Styles
| id | component | specific props |
|---|---|---|
| KineticType | `KineticType` | `lines[]`, `variant` rise/slide/mask/scale, `unit` word/char (char = English only), `fontSize`, `align`, `accentLine` |
| Blueprint | `Blueprint` | `title`, `drawingNo`, `callouts[3]`, `dimensions[2]`, `gridOpacity` |
| Isometric | `Isometric` | `title`, `blocks[]` ({x,y,w,d,h,role,label}), `camera` push/pan/static |
| Holographic | `Holographic` | `title`, `rows[]` ({label,value,suffix,decimals}), `gauge` {label,value}, `series[]` |
| Particles | `ParticleText` | `text`, `fontSize`, `maxParticles` (2200), `density` (5 px), `path` swirl/rise/explode, `particleSize` |
| LiquidMorph | `LiquidMorph` | `title`, `subtitle`, `shapes` (2–6), `blobScale`, `fontSize` |
| SplitFlap | `SplitFlap` | `rows[]`, `counter` {from,to,suffix,label}, `pool[]` (Arabic filler words), `fontSize`, `flips` |
| FlowLines | `FlowLines` | `title`, `gauges[3]` ({label,value,unit}), `flowSpeed` — layout mirrors in RTL (flow follows reading direction) |
| NetworkMap | `NetworkMap` | `title`, `nodes[]` ({x,y 0–1, label, hub}), `links[]` ([a,b]), `pulses` — positions are geographic, never mirrored |
| Timeline | `Timeline` | `title`, `items[]` ({year,label}, 3–7), `currentIndex` |
| ProcessFlow | `ProcessFlow` | `title`, `steps[]` ({icon,title,desc}, 3–5; icons from `src/lib/icons`) |
| Charts | `Charts` | `chart` line/area/bars/donut, `title`, `labels[]`, `values[]`, `unit`, `mirrorX` |
| SplitCompare | `SplitCompare` | `title`, `before`/`after` ({label,value,unit,caption,decimals}), `showDelta`, `lowerIsBetter` |
| LineArt | `LineArt` | `title`, `items[]` ({icon,label}, 3–6), `strokeWidth`, `iconSize` |
| GeometricPattern | `GeometricPattern` | `title`, `subtitle`, `cell` (px, default 120), `lineWidth`, `clearCenter` |
| Topographic | `Topographic` | `title`, `levelLabel`, `minElevation`/`maxElevation` (m), `waterTo` (0–1), `levels` |
| RadarScan | `RadarScan` | `title`, `blips[]` ({angle°,dist 0–1,label,alert}), `status[]` ({label,value,alert}), `rpm` |
| DataStream | `DataStream` | `title`, `kpis[]` ({label,value,suffix,decimals}, 2–4), `columns`, `glyphs` |
| ParallaxLayers | `ParallaxLayers` | `title`, `subtitle`, `camera` pan/push, `depth` |
| SwissGrid | `SwissGrid` | `kicker`, `bigNumber` {value,suffix,decimals}, `title`, `body`, `caption`, `showGrid` |

### Example
```tsx
import { KineticType } from "./motion-styles/styles/KineticType";
<KineticType lines={["كفاءة تشغيلية أعلى", "تحول رقمي شامل"]} variant="mask" intensity={0.4} transparent />
```

## Adding a style (Phase 2+)
1. `styles/<Name>.tsx` using `useMotionStyle` + `Stage`.
2. Presets in `presets/index.ts`.
3. `registerStyle({...})` in `registry/index.ts` → compositions + gallery appear automatically.

## Arabic handling
- Arabic is never split per letter: Kinetic/SplitFlap animate whole words; Particles rasterise the shaped string once with the real font (`document.fonts.load` + `delayRender`) then sample points.
- SVG text: `text-anchor` flips under RTL, so Blueprint maps physical edges (`anchorFor`).

## Limitations / notes
- Particle text: sampling waits for fonts; ~2,200 SVG circles per frame (≈1.8 s/still at 25% scale in tests). Raise `density` / lower `maxParticles` for speed.
- Holographic panels are semi-transparent by design → large ProRes files (≈440 MB / 8 s). Scanlines are confined to panels for this reason.
- Geometric Patterns: thin lines across the whole frame → large ProRes (≈720 MB / 8 s). Larger `cell` or `clearCenter` reduces it.
- Swiss Grid: column guides make the frame ~26% transparent — use `showGrid:false` for clean overlays.
- Parallax Layers: lower half mostly opaque by design (landscape).
- Numeric values that mix digits and Latin units ("126 / 128", "4.2 bar") force `direction:ltr` so they never flip in Arabic.
- Network map positions are geographic and never mirrored; Flow Lines mirror so water follows the reading direction.
- Split Compare: numeric badges force `direction:ltr` so “-68%” never flips in Arabic.
- Liquid Morph uses pure geometry (no blur/goo filters) for identical rendering everywhere.
- Split-Flap uses CSS 3D `rotateX` (supported by the bundled Chromium); filler words for Arabic come from `pool`.
- Experimental output is not institutionally approved.
