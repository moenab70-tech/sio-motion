# Technical decisions log (newest last)

| date | decision | why |
|---|---|---|
| 2026-11-14 | Remotion 4.0.543 + React 19.3 + TS, manual setup (no create-video) | deterministic, minimal |
| 2026-11-14 | Default render = ProRes 4444 + alpha via `remotion.config.ts` | Premiere overlay workflow |
| 2026-11-14 | 1920×1080 @ 30fps, RTL default | user requirement |
| 2026-11-14 | Duration from `durationInSeconds` prop + `calculateMetadata`; templates read it from props, not `useVideoConfig` | `useVideoConfig` inside `<Sequence>` returns composition length |
| 2026-11-14 | Arabic text animated per word, no letter-spacing | per-letter breaks Arabic joining |
| 2026-11-14 | Fonts: Noto Kufi Arabic (display), IBM Plex Sans Arabic (body) | provisional, until brand guide |
| 2026-11-14 | Icons: lucide-react 1.59.0 (pinned, ≥2 weeks old) | clean, MIT |
| 2026-11-14 | Logos stored byte-identical + SHA-256 manifest; `Logo` component locks aspect ratio, blocks inherited effects | brand compliance |
| 2026-11-14 | Missing logo variants throw; never derived from other files | no unofficial artwork |
| 2026-11-14 | All digits Latin, Watad Regular via `unicode-range` | user requirement |
| 2026-11-14 | Default dark-bg logo = vertical white lockup | user approval |
| 2026-11-14 | Productions = `productions/<name>/production.json` (shot = template id + partial props) rendered by `scripts/render-production.mjs` to `exports/` | reuse without code edits |
| 2026-11-14 | Props merge is shallow (Remotion default) — nested objects written whole | documented in TEMPLATES.md |
| 2026-11-14 | Removed `@remotion/motion-blur`; own SVG directional blur | library produced no blur in tests |
| 2026-11-14 | FX enhancements wrap old templates (`FxEnhanced`) instead of editing them | keep templates stable |
| 2026-11-14 | Custom transitions mask the exiting scene | transparent scenes would otherwise overlap |
| 2026-11-14 | Lottie not installed | no Lottie assets yet |
| 2026-11-14 | Project docs in English (except TEMPLATES/README for the user) | Arabic costs ~2–3× more tokens in context |
| 2026-11-14 | Project `.claude/settings.json` denies Read on node_modules/out/exports/package-lock | save context; renders checked via scripts |
| 2026-11-14 | Motion Styles library isolated under `src/motion-styles/` with its own entry point; production Root/config untouched | keep experimental work separate from approved templates |
| 2026-11-15 | Project skills `sio-production` + `sio-motion-styles` in `.claude/skills/`; `SIO_PROJECT_STATUS.md` for continuity | on-demand loading instead of growing CLAUDE.md; named third-party skills are not installed |
| 2026-11-15 | Installed official `remotion-best-practices` router only (not all 13 Remotion skills); Superpowers declined; Taste/UI UX Pro Max/Graphify not installed | one startup description instead of 13; no auto-running hooks; no Python available |
| 2026-11-15 | Installed `ui-ux-pro-max` main skill only (sub-skills incl. `brand` excluded); patched script path to `python3` + project-relative | avoid identity conflicts; plugin path variable unset for project skills |
| 2026-11-15 | Blender characters: MPFB 2 + bundled Rigify + Python-generated native Hair Curves (`blender/sio_character_library/`); GBH Tool & Hair Tool rejected | GBH free build is education-only and targets 4.2–4.3; Hair Tool is paid; native curves are scriptable/headless |
| 2026-11-15 | Installed EXea Jiggle 1.1.0 + Brushstroke Tools 1.2.3 (GPL, code reviewed, headless-tested); rejected Eye Animation 2.0.0 (naming incompatible with Rigify/MPFB) and HiFi Builder 4.6.7 (GTA V asset payload) | only scriptable, licence-clean tools; eye/blink done natively on Rigify face controls |
