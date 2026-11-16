# Output Catalog — SIO Motion Graphics

Last updated: 2026-11-14. Naming: `SIO_<StyleName>_<Version>_<Resolution+fps>_<Format>.ext` — `Alpha` only when an alpha channel was verified (pix_fmt `yuva444p12le` + fully transparent pixels measured).

**Approval:** nothing is institutionally approved yet. *Candidate* = technically verified render awaiting your explicit approval; on approval it is moved to `outputs/final/`.

## Folders

| Folder | Content |
|---|---|
| `outputs/final/` | Approved deliverables only (empty until approval) |
| `outputs/candidates/` | Technically verified renders awaiting approval |
| `outputs/previews/` | Review copies (galleries, showreels, boards) |
| `outputs/archive/` | Superseded but kept (not reproducible) |
| `out/` | Development renders of production templates (reproducible) |
| `exports/<production>/` | Production deliveries from `npm run production:render` |

## Export settings

| Code | Settings |
|---|---|
| ProRes4444Alpha | Apple ProRes 4444, `yuva444p10le` → stored 12-bit, PNG frames, 1920×1080, 30 fps, transparent |
| Preview | H.264, `yuv420p`, CRF 18, 1920×1080, 30 fps, no alpha |

## Motion Styles (20)

Shared preview for all styles: `outputs/previews/SIO_MotionStylesGallery_v01_1080p30_Preview.mp4` · per-style gallery composition `MS-Gallery-<Id>` (entry `src/motion-styles/entry.ts`).

| # | Style | Source | Preview composition | Final / candidate file | Version | Export | Status |
|---|---|---|---|---|---|---|---|
| 1 | Kinetic Typography | `src/motion-styles/styles/KineticType.tsx` | `MS-Gallery-KineticType` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 2 | Blueprint | `src/motion-styles/styles/Blueprint.tsx` | `MS-Gallery-Blueprint` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 3 | Isometric | `src/motion-styles/styles/Isometric.tsx` | `MS-Gallery-Isometric` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 4 | Holographic | `src/motion-styles/styles/Holographic.tsx` | `MS-Gallery-Holographic` | `outputs/candidates/SIO_Holographic_v01_1080p30_ProRes4444Alpha.mov` | v01 | ProRes4444Alpha (institutional) | Candidate |
| 5 | Particles | `src/motion-styles/styles/ParticleText.tsx` | `MS-Gallery-Particles` | `outputs/candidates/SIO_Particles_v01_1080p30_ProRes4444Alpha.mov` | v01 | ProRes4444Alpha (institutional) | Candidate |
| 6 | Liquid Morph | `src/motion-styles/styles/LiquidMorph.tsx` | `MS-Gallery-LiquidMorph` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 7 | Split-Flap | `src/motion-styles/styles/SplitFlap.tsx` | `MS-Gallery-SplitFlap` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 8 | Flow Lines | `src/motion-styles/styles/FlowLines.tsx` | `MS-Gallery-FlowLines` | `outputs/candidates/SIO_FlowLines_v01_1080p30_ProRes4444Alpha.mov` | v01 | ProRes4444Alpha (institutional) | Candidate |
| 9 | Network Map | `src/motion-styles/styles/NetworkMap.tsx` | `MS-Gallery-NetworkMap` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 10 | Timeline | `src/motion-styles/styles/Timeline.tsx` | `MS-Gallery-Timeline` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 11 | Process Flow | `src/motion-styles/styles/ProcessFlow.tsx` | `MS-Gallery-ProcessFlow` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 12 | Charts | `src/motion-styles/styles/Charts.tsx` | `MS-Gallery-Charts` | `outputs/candidates/SIO_Charts_v01_1080p30_ProRes4444Alpha.mov` | v01 | ProRes4444Alpha (institutional) | Candidate |
| 13 | Split Compare | `src/motion-styles/styles/SplitCompare.tsx` | `MS-Gallery-SplitCompare` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 14 | Line Art | `src/motion-styles/styles/LineArt.tsx` | `MS-Gallery-LineArt` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 15 | Geometric Patterns | `src/motion-styles/styles/GeometricPattern.tsx` | `MS-Gallery-GeometricPattern` | `outputs/candidates/SIO_GeometricPatterns_v01_1080p30_ProRes4444Alpha.mov` | v01 | ProRes4444Alpha (institutional) | Candidate |
| 16 | Topographic | `src/motion-styles/styles/Topographic.tsx` | `MS-Gallery-Topographic` | `outputs/candidates/SIO_Topographic_v01_1080p30_ProRes4444Alpha.mov` | v01 | ProRes4444Alpha (institutional) | Candidate |
| 17 | Radar Scan | `src/motion-styles/styles/RadarScan.tsx` | `MS-Gallery-RadarScan` | `outputs/candidates/SIO_RadarScan_v01_1080p30_ProRes4444Alpha.mov` | v01 | ProRes4444Alpha (institutional) | Candidate |
| 18 | Data Stream | `src/motion-styles/styles/DataStream.tsx` | `MS-Gallery-DataStream` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 19 | Parallax Layers | `src/motion-styles/styles/ParallaxLayers.tsx` | `MS-Gallery-ParallaxLayers` | — (not rendered yet) | v01 | — | Source ready · not rendered |
| 20 | Swiss Grid | `src/motion-styles/styles/SwissGrid.tsx` | `MS-Gallery-SwissGrid` | `outputs/candidates/SIO_SwissGrid_v01_1080p30_ProRes4444Alpha.mov` | v01 | ProRes4444Alpha (institutional) | Candidate |

To render a missing candidate: `npx remotion render src/motion-styles/entry.ts MS-<Id>-Institutional outputs/candidates/SIO_<StyleName>_v01_1080p30_ProRes4444Alpha.mov` then verify with `npm run check:alpha -- <file>`.

## Other outputs

| File | Type | Status |
|---|---|---|
| `outputs/previews/SIO_FXCompare_v01_1080p30_Preview.mp4` | Preview | Review copy |
| `outputs/previews/SIO_LogoBoard_v01_1080p_Preview.png` | Preview | Review copy |
| `outputs/previews/SIO_MotionStylesGallery_v01_1080p30_Preview.mp4` | Preview | Review copy |
| `outputs/previews/SIO_TemplatesShowreel_v01_1080p30_Preview.mp4` | Preview | Review copy |
| `outputs/previews/SIO_TemplatesShowreel_v01_1080p30_ProRes4444Alpha.mov` | Preview | Review copy |
| `outputs/archive/SIO_LegacyAnimatedStat_v00_1080p25_ProRes4444Alpha.mov` | Archive | Superseded v1 template (25 fps), kept |
| `outputs/archive/SIO_LegacyBarChart_v00_1080p25_ProRes4444Alpha.mov` | Archive | Superseded v1 template (25 fps), kept |
| `outputs/archive/SIO_LegacyLowerThird_v00_1080p25_ProRes4444Alpha.mov` | Archive | Superseded v1 template (25 fps), kept |
| `outputs/archive/SIO_LegacyTitleCard_v00_1080p25_ProRes4444Alpha.mov` | Archive | Superseded v1 template (25 fps), kept |
| `out/*.mov` (26 files) | Template & FX dev renders | Moved to Trash 2026-11-14 (approved) — re-create with `npm run render:all` |
| `exports/sample-test/` | Workflow test production | Moved to Trash 2026-11-14 (approved); source kept in `productions/sample-test/` |

## dams-2026 (2026-11-16)
| File | Spec | Source |
|---|---|---|
| exports/dams-2026/Harimla_Dam_Final.mp4 | H.264 CRF16 + AAC · 1080×1920 · 30fps · 20 s · in-house music + water ambience, -15 LUFS | `src/videos/dams-2026` → Dam-Harimla |
| exports/dams-2026/Sulbukh_Dam_Final.mp4 | H.264 CRF16 + AAC · 1080×1920 · 30fps · 18 s · in-house music + water ambience, -15 LUFS | `src/videos/dams-2026` → Dam-Sulbukh |
