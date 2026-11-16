# SIO Project Status

_Last updated: 2026-11-15 (skills installed)_

## Current production task
None in progress — system ready for the first real production.

## Completed
- Production templates (5 families, 18 compositions) + FX system (11) + logo integration; ProRes 4444 + alpha verified.
- Motion Styles library: 20 styles, isolated entry, gallery, registry, tests (77 checks passing on 2026-11-14).
- Production workflow (`productions/` → `exports/`), outputs structure (`outputs/`), `OUTPUT_CATALOG.md`.
- Storage cleanup: 2.96 GB moved to macOS Trash (approved; `outputs/TRASH_LOG.md`). Project ≈ 4.0 GB.
- Project skills `sio-production`, `sio-motion-styles`; CLAUDE.md slimmed.

## Pending
- Official brand guide (colours/fonts) → replace provisional `defaultPalette`.
- Approval of Motion Style candidates (8 rendered in `outputs/candidates/`, 12 not rendered).
- Official white emblem (alone) — not supplied.
- Audio: paused by the user (previous voice-over results were poor).
- Test inside Premiere Pro itself (never done).

## Known issues
- Google Fonts load at render time → internet required.
- Motion Styles test "baseline unchanged" check reports 3 intended edits (CLAUDE.md, docs/DECISIONS.md, README.md) until the baseline is refreshed.
- Large ProRes files: GeometricPattern (~720 MB/8 s), Holographic (~440 MB/8 s).
- Git repository since 2026-11-16 → see «المزامنة» below.
- Remotion licence: confirm Free vs Company licence for the organisation (`docs/LICENSING.md`).

## المزامنة
- **المستودع:** https://github.com/moenab70-tech/sio-motion (عام / Public منذ 2026-11-16، الفرع `main`). أُنشئ ورُفع أول commit في 2026-11-16.
- **GitHub = الكود والقوالب والوثائق والإعدادات فقط** (≈ 20MB). الملفات الثقيلة مكانها **Google Drive، مو GitHub**:
  - ملفات بلندر `.blend` / `.blend1`، وكاش Poly Haven (`**/polyhaven_cache/`)، ورندرات بلندر.
  - الوسائط الخام: `public/media/`، `public/audio/`، وأي `.mp4/.mov/.wav/.mp3/.aep`.
  - المخرجات: `out/`، `outputs/`، `exports/`، `backups/`.
- على جهاز جديد: `git clone` ← `npm install` ← انسخ المجلدات الثقيلة أعلاه من Drive لنفس المسارات.
- القواعد في `.gitignore`؛ لا يُرفع أي ملف أكبر من 50MB ولا أي `.env`.

## Skills
| Skill | Scope | Purpose |
|---|---|---|
| `sio-production` | project | Video workflow, tool routing, render/audio/failure rules |
| `sio-motion-styles` | project | Map scene content → Motion Style |
| `remotion-best-practices` | project (official, v4.0.543) | Remotion techniques: markup, maps, media, render/studio — router to 12 references |
| `ui-ux-pro-max` | project (main skill only, MIT) | UI/layout/typography/chart-type research via local `python3` search (stdlib only, no network) |
| Anthropic skills (docx, pdf, pptx, xlsx, dataviz…) | app-provided | Only when a task needs that format |
Not installed: Superpowers (declined), Graphify (needs Python ≥3.10; not a charts tool), Taste Skill (pending — auto-running hook scripts), audio tools (audio paused by user).

## Last verified configuration (2026-11-15)
Remotion 4.0.543 · React 19.3.1 · Node 26 · Python 3.9.6 + Git 2.39.5 (Apple CLT) · macOS 15.3.2 (arm64) · `npm run verify` ✓ (29 compositions) · Motion Styles entry ✓ (81 compositions).

## Recommended next action
Start the first production: send the scenario/script → `npm run production:new -- <name>`.

## Blender character library (2026-11-15)
- `blender/sio_character_library/`: MPFB + Rigify + Python Hair Curves; presets engineer_m01/f01, hair short_side_part/beard_short/long_center_part/ponytail; PoC `scripts/poc_engineer_drawing.py` (headless OK, outputs in `tests/poc_engineer_drawing/`).
- Pending: toon style polish (hairline cap edge), secondary motion for long hair, neck crease when the head bows, thobe/shemagh garments. Approved Hasad opening untouched.

- 2026-11-15: engineer_m01 **v2.1 = Ready for User Approval** → `blender/sio_character_library/assets/characters/engineer_m01_v2_1/`. Full Hasad production not started (awaiting approval).
- 2026-11-15: engineer_m01 **v2.2** (V2.1 + hand/desk contact fixes) in `blender/sio_character_library/tests/poc_engineer_drawing_v2_2/` — Ready for User Approval. Poly Haven MCP verified (per-scene switch, see library README).
- 2026-11-15: office v4 previews (dusk/night/dawn, shots A–G, clutter presets) in `blender/sio_character_library/tests/office_v4/`; no final renders, storyboard untouched.
- 2026-11-15: engineer v2.3 + office v5 multi-day story previews (tests/office_v5) — awaiting approval; final 20 s not started.
- 2026-11-16: **Dams 2026** — `DamRainfallReport` (vertical 9:16, isolated entry `src/videos/dams-2026/entry.ts`). Harimla + Sulbukh finals approved & exported to `exports/dams-2026/`. Logos = circles only, equal diameter, no plate; MEWA logo added in `public/brand/partners/`. Source clips (HEVC 1080p, no audio) in `public/media/video/dams/`.
