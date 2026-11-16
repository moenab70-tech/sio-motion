# Brand system (SIO — المؤسسة العامة للري)

## Logos — `public/brand/logos/` (read-only)
Never edit, crop, recolour, redraw, AI-generate, add shadow/filter/glow/blur, or animate parts. Allowed: whole-logo opacity fade and uniform scaling. Always render via `src/lib/Logo.tsx`. Hashes: `public/brand/logos/README.md`.

| form | variants | file |
|---|---|---|
| `emblem` | color | sio-emblem-color.png |
| `lockup` (horizontal) | color, blue | sio-lockup-color.webp, sio-lockup-blue.webp |
| `lockupVertical` | white, black | sio-lockup-vertical-white.png, sio-lockup-vertical-black.png |

- Approved default: **dark bg → `lockupVertical`/white**, light bg → `lockup`/color (`DEFAULT_FORM` in `src/config/logos.ts`).
- `variant:"auto"` order — dark: white→color; light: color→blue→black. Missing combos throw (never synthesize).
- Not supplied: white emblem alone, white/black horizontal lockup, colour vertical lockup.
- Legibility: the English line inside the vertical lockup is ~12px at ≤190px height.

## Typography
- Display: Noto Kufi Arabic; body: IBM Plex Sans Arabic (Google Fonts, loaded at render → needs internet).
- **All digits Latin** (`defaultDigits = "latin"`), rendered in **Watad Regular** (`public/brand/fonts/Watad-Regular.otf`) via `numberFont` + `unicode-range` (0-9 % + , - .). Single weight; no faux bold.
- Arabic text: no `letterSpacing`, animate by word never by letter.
- GE Dinar One exists on the user's Mac but is NOT adopted.

## Colours
`defaultPalette` in `src/config/brand.ts` is **provisional** (gold #C8A45D / blue #3B82C4) until the official brand guide is supplied. Do not infer brand colours from the logo.

## Partner logos
Official partner logos (e.g. MEWA) live in `public/brand/partners/` (read-only, hashes in its README) and render via `src/videos/dams-2026/PartnerLogo.tsx` with the same rules as SIO logos.
