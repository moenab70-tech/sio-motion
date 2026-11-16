# FX system rules (`src/fx/`, settings `src/config/fx.ts`, content `src/config/fxDefaults.ts`)

- Effects support information, never compete: depth layers (3D, particles) sit behind content and away from the information area; nothing over numbers.
- Logo never receives blur/glow/sweep.
- Motion blur: `DirectionalBlur` + `velocityBlur()` (SVG, alpha-safe). `@remotion/motion-blur` was removed — no visible effect here (see TROUBLESHOOTING).
- 3D: `@remotion/three` + R3F, `gl={{ alpha:true, premultipliedAlpha:false }}`; use `emissive` + low metalness (metal is black without env map); numbers/labels as HTML projected with the same camera maths.
- Transitions: custom presentations in `src/fx/presentations.tsx` mask the exiting scene (scenes are transparent). Built-ins allowed: fade, slide, wipe, iris, clockWipe, flip. Not allowed (need HTML-in-Canvas, Chrome 149+ flag): blurSlide, dissolve, filmBurn, zoomBlur, crossZoom, dreamyZoom, crosswarp, ripple, swap, linearBlur, bookFlip, zoomInOut.
- `@remotion/effects`: only on `<Solid>`/`<Img>` (WebGL). Light leak = separate layer (Screen).
- Lottie not installed. New `@remotion/*` packages must match `remotion` exactly (4.0.543), `--save-exact`.
- Controls: `fx = { intensity 0–1, speed, motionBlur, glow, lightSweep, particles }`.
