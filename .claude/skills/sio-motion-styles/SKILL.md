---
name: sio-motion-styles
description: Use when choosing or configuring an SIO Motion Style for a scene (titles, engineering, facilities, digital, data, transitions, maps, timelines). Maps content to the 20 styles and gives the institutional-first rules.
---

# Choosing a Motion Style

Library: `src/motion-styles/` (isolated entry `src/motion-styles/entry.ts`). Props per style: `src/motion-styles/README.md` (read only the needed row). Composition ids: `MS-<Id>-Institutional | -Experimental | -English`.

## Content → style
| Scene content | First choice | Alternative |
|---|---|---|
| Title / key message | KineticType | SwissGrid (big number + statement) |
| Engineering / canal / dam cross-section | Blueprint | Topographic (terrain, water level) |
| Facilities / systems overview | Isometric | ProcessFlow (sequence of steps) |
| Digital transformation / control room | Holographic | DataStream (data → KPIs), RadarScan (monitoring, alerts) |
| Atmosphere / transition between parts | Particles | LiquidMorph (organic), GeometricPattern (identity-rich opener) |
| Numbers changing / counters | SplitFlap | Charts (bars/line/area/donut) |
| Before vs after | SplitCompare | Charts |
| Water network / flows | FlowLines | NetworkMap (stations, geographic — never mirrored) |
| History / roadmap | Timeline | — |
| Icons overview | LineArt | ProcessFlow |
| Landscape / agriculture mood | ParallaxLayers | — |

## Rules
- Default `mode: "institutional"`; experimental only on request and labelled unapproved.
- Recommend 1 style per scene (2 options max); keep 2–3 styles per video for consistency.
- Arabic: whole-word animation only; numeric values force LTR; check SVG text anchors under RTL.
- File-size heavy on ProRes: GeometricPattern, Holographic, SwissGrid with grid — mention when exporting.
- Logo is never rendered inside Motion Styles; use production templates for logo scenes.
- Production templates (`src/templates`, `src/fx`) are preferred for approved deliverables; Motion Styles outputs are candidates until the user approves (`OUTPUT_CATALOG.md`).
