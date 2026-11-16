---
name: sio-production
description: Use when producing an SIO video or scene (new production, scene changes, previews, exports, audio). Gives the scene-by-scene workflow, which tool/skill to use for each task, render/export commands and failure rules. Not needed for pure Q&A.
---

# SIO production workflow

## Per video
1. Read the request/scenario → list scenes (one message, title, stat, map, transition…).
2. Map each scene to an existing template id (`TEMPLATES.md`, read only the needed section) or a Motion Style (use skill `sio-motion-styles`). Build new code only if nothing fits — extend via props, never rebuild.
3. `npm run production:new -- <name>` → edit `productions/<name>/production.json` (shot = template id + partial props; nested objects written whole).
4. Preview only changed shots: `npm run still -- <Id> <frame>` (half-size JPEG) or `npm run production:preview -- <name> --only=<shot,…>`.
5. `npm run verify` after code edits (one line).
6. Export on request: `npm run production:render -- <name> [--only=…]` → `exports/<name>/prores-4444-alpha/`. Verify with `npm run check:alpha -- <files>`.
7. Full video only after approval. Never re-render approved shots whose inputs didn't change.
8. Deliverables: SIO naming + `OUTPUT_CATALOG.md`; update `SIO_PROJECT_STATUS.md` only on meaningful progress.

## Tool / skill routing (load only what the task needs; one is usually enough)
| Task | Use |
|---|---|
| Compositions, animation, rendering, transitions | This project's code first; Remotion API/technique questions (markup, maps, media, render flags) → skill `remotion-best-practices`. Never follow its “create a new project/video” scaffolding for SIO work — SIO videos go through this workflow |
| Choosing a visual style per scene | `sio-motion-styles` |
| Charts / stats / data visuals | Templates `Stat-*`, `Infographic-*`, `FX-Bars-3D`, Motion Styles `Charts`, `SplitFlap`, `DataStream`; chart-type choice → `ui-ux-pro-max` (`--domain chart`) or `dataviz` |
| Complex planning, architecture, debugging | Plan inline; plan mode only for multi-file architecture changes |
| Preview UI / galleries, layout & typography decisions | Existing `src/preview/*`, `src/motion-styles/gallery/*`; design research → skill `ui-ux-pro-max` (never for brand identity) |
| Word / PDF / slides deliverables | The matching Anthropic document skill, only if asked |
| Audio (VO, music, SFX) | **No audio workflow exists yet** — see Audio rules |

Installed: `remotion-best-practices` (official router, v4.0.543, no hooks), `ui-ux-pro-max` (main skill only, local Python search, patched — see its LOCAL_PATCH.md). Not installed (2026-11-15): Superpowers (declined), Graphify (needs Python ≥3.10; code-graph tool, not charts), Taste Skill (pending decision — now ships auto-running hook scripts, web-focused), audio tools (audio paused). Ask before installing anything.

## Rendering rules
- Default ProRes 4444 + alpha (`remotion.config.ts`); preview = `PREVIEW=1` H.264. Don't change global config.
- Long renders: run in background (`run_in_background`), don't poll; scenes export independently.
- 1920×1080 @ 30 fps everywhere; keep timing in frames from `durationInSeconds`.
- Keep VO / music / SFX as separate files, never baked into graphics overlays.

## Audio rules (when added)
- Check whether an existing TTS/audio tool works before installing or repairing anything.
- Prefer local processing; cache generated audio by text hash; never regenerate unchanged lines.
- Use only music/SFX with confirmed licences; store in `public/media/audio/`.

## Failure rule
If a tool or command fails twice for the same reason: stop, diagnose, report to the user before trying another approach. Log non-obvious fixes in `docs/TROUBLESHOOTING.md`.
