# Export & verification

| preset (`export-presets.json`) | codec | pixels | use |
|---|---|---|---|
| `prores-4444-alpha` (default) | ProRes 4444, PNG frames | `yuva444p10le` (stored as `yuva444p12le`) | delivery to Premiere |
| `preview-h264` (`PREVIEW=1`) | H.264 CRF 18 | `yuv420p` | review only, no alpha |

`remotion.config.ts` applies ProRes 4444 globally; `PREVIEW=1` switches to H.264 (passing `--codec=h264` alone fails because the ProRes profile is set).

## Verify (quiet commands)
- `npm run verify` — typecheck + bundle + list compositions (one line each).
- `npm run check:alpha -- <files…>` — codec/pix_fmt + % transparent/opaque/semi of one frame per file.
- `npm run still -- <CompositionId> <frame>` — half-size JPEG into `.cache/stills/` for visual review.
- Expected probe: `prores,4,…,yuva444p12le,30/1`.

## Premiere notes
- Transitions (`Transition-*`): put the clip on V2 with its **midpoint** on the cut (100% cover there).
- `FX-LightLeak`: blend mode Screen/Add.
- Dark fringes → Interpret Footage → Alpha (premultiplied/straight).
- Not yet tested inside Premiere itself.
