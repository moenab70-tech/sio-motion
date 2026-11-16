# SIO Motion Graphics

Remotion 4.0.543 + React 19 + TS library of Arabic motion graphics for the Saudi Irrigation Organization, delivered as transparent ProRes 4444 overlays for Premiere Pro.

**Talk to the user in Arabic.** User = video editor / motion designer (Premiere, After Effects), works in Claude Desktop, not the terminal.

## Hard rules
1. Never rebuild templates from scratch; extend via props/options. Never delete files, productions or renders without explicit approval — then use `/usr/bin/trash`, never `rm`.
2. Logos: use `src/lib/Logo.tsx` only; files in `public/brand/` are read-only — no edits, crops, recolours, effects, part animation. Details: `docs/BRAND.md`.
3. Approved identity: dark-bg default logo = vertical white lockup; all digits Latin in Watad Regular. Palette is provisional — never infer brand colours/fonts from the logo.
4. Arabic text: no letter-spacing; animate per word.
5. Effects never cover information or touch the logo (`docs/FX.md`).
6. "Done" only after `npm run verify`, a real render, and a look at frames (`npm run still`).

## Specs
1920×1080 · 30fps · RTL · transparent · ProRes 4444 + alpha (default). Presets: `export-presets.json`, details `docs/EXPORT.md`.

## Layout
- `src/config/` — `brand.ts` (palette, fonts, digits, number font, timing), `logos.ts`, `fx.ts`, `defaults.ts`, `fxDefaults.ts`
- `src/templates/` — StatCounter, CinematicTitle, LowerThird, InfographicCards, ProjectCard, SectionTransition
- `src/fx/` — FxTitle, Bars3D, Depth3D, Particles, LightLeak, FxEnhanced, FxScenes, presentations
- `src/lib/` — Logo, AnimatedNumber, motion, numbers, fonts, icons · `src/preview/` — Showreel, LogoBoard, FxCompare
- `productions/<name>/production.json` → `exports/<name>/` · `public/media/` assets · `out/` dev renders · `outputs/` (final/candidates/previews/archive, see `OUTPUT_CATALOG.md`)
- Template catalogue (ids + props): `TEMPLATES.md` — read only the section you need.
- Motion Styles (20 experimental/institutional styles, isolated entry `src/motion-styles/entry.ts`, own Studio; never imported by production): `src/motion-styles/README.md`, tests `node src/motion-styles/tests/run.mjs`.

## Commands
`npm run verify` · `npm run still -- <Id> <frame>` · `npm run check:alpha -- <files>` · `npm run studio` (production workflow commands: skill `sio-production`)

## Skills & continuity
- Project skills (load on demand): `sio-production` (video workflow, routing, render/failure rules), `sio-motion-styles` (content → style), `remotion-best-practices` (official Remotion reference router — techniques only, SIO workflow takes precedence), `ui-ux-pro-max` (UI/layout/typography/chart research — never brand identity). Don't load other skills unless the task needs them.
- Session start: if the project is a Git repo, `git pull` first; then read `SIO_PROJECT_STATUS.md` (current task, pending, known issues).
- After every task that changes anything (code, renders, decisions, approvals): update `SIO_PROJECT_STATUS.md` with a dated one-line entry, then — if the project is a Git repo with a remote — commit and push (code/docs only; heavy files stay out per `.gitignore`). The user works from several devices (laptop, office PC, phone); this file is the shared memory between them.

## Docs (read on demand)
`docs/BRAND.md` · `docs/EXPORT.md` · `docs/FX.md` · `docs/DECISIONS.md` · `docs/TROUBLESHOOTING.md` · `docs/LICENSING.md`

## Context hygiene
- `.claude/settings.json` denies Read on `node_modules/`, `out/`, `exports/`, `package-lock.json` (Bash scripts like `check:alpha` still work). Don't open `public/**` binaries.
- Pipe long command output through `tail`/`grep`; renders use `--log=error`.
- Review stills at half scale; prefer `check:alpha` numbers over opening many images.
- When fixing a new non-obvious problem, add one line to `docs/TROUBLESHOOTING.md`; new technical decisions go to `docs/DECISIONS.md`.
