# Study: tools for better environments in Blender (why the canal succeeded and the office didn't)

## Diagnosis: canal vs. office
| | Canal (succeeded) | Office (weak) |
|---|---|---|
| Elements | Natural: a palm studied in detail, grass from a scatter, sky, water | **Furniture made of boxes and tubes generated in code**, with no real modelling |
| Materials | Simple and fitting (green, water, sky) | **No real textures**: no wood grain, fabric or paper. Plaster with random blotches |
| Lighting | One strong source in the frame (the sun) + atmosphere | Cel bands only, with **no soft bounce light and no ambient occlusion (AO)**. Interiors in anime live on soft gradients |
| Composition | One-point perspective toward the sun | A 24 mm corner shot, crowded with no clear focal point |
| Story details | The palm, the dates, the water | Few, and their proportions are off (stool, table) |

**The root of the problem:** I'm building every object myself in code. Professionals in anime environments **use high-quality ready-made assets** and spend their effort on composition, lighting and colour.

## Free tools and libraries (studied)
### Asset libraries
- **Poly Haven** (CC0, free with no account): models, PBR textures and HDRIs. Commercial use with no conditions.
- **BlenderKit** (add-on + free tier): 45–48k assets (furniture, materials, HDRIs) under **CC0/RF** licences that allow commercial use. **Needs an account.**
- **Sketchfab**: huge, but the licences are mixed (CC0, CC-BY, NC...). Each model needs checking.

### Blender add-ons
- **Blender MCP** (most important): I work **inside an open Blender**, take viewport screenshots, and it **has a built-in Poly Haven integration** (search and download models, textures and HDRIs **with no key**) plus Sketchfab (with an account). Setup: an add-on in Blender + `claude mcp add blender uvx blender-mcp`.
- **Archimesh** (free, GPL): rooms, doors, windows, shelves and curtains. Official compatibility is 4.2+, with an unofficial Blender 5 version on GitHub.
- **Scattering:** KIRI Engine Scatter (free, 2026), OpenScatter (GPL, 4.2–5.0), GScatter (free, beta).
- **Trees:** Sapling Tree Gen **reportedly doesn't work in Blender 5.x**. Our palm is better for our purpose.
- **Hair/beards:** Blender's built-in Hair Curves + the built-in "Essentials" hair node groups.
- **Anime rendering:** Goo Engine (a Blender build for anime, behind on Blender versions), paid toon shaders. **Our cel shader is enough**, but it needs AO and per-collection Line Art outlines (the method taught in anime-room courses).

## What's missing (and the fix)
1. **High-quality ready-made assets** → Poly Haven (free, no account) + BlenderKit (optional, account).
2. **Real textures** (wood, fabric, plaster, paper) → Poly Haven textures turned into our cel shading while keeping the texture.
3. **Interior lighting:** a soft ambient light from an HDRI + **ambient occlusion** + window light with clear shafts.
4. **Composition:** a focal point (the desk lit by the window), a focal length closer to 35 mm, a cleaner foreground.
5. **Live work:** Blender MCP, so I see every step and you watch the work.

## Sources
cinevva.com (asset guides 2026, Sketchfab vs Poly Haven vs Kenney) · cgchannel.com (BlenderKit 48,000 free assets) · github.com/ahujasid/blender-mcp · extensions.blender.org (Archimesh, Sapling) · digitalproduction.com (KIRI Scatter) · superhivemarket.com (OpenScatter) · 80.lv (GScatter) · strayspark.studio (toon shaders 2026) · udemy/skillshare anime-room courses
