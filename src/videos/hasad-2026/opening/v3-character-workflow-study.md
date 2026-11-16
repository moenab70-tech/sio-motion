# Study: how professionals build an anime character in Blender

## What I got wrong
I was building the body from primitives (spheres, tubes, a skin skeleton) and fixing them through trial and error. Professionals don't work that way. They start from a **base mesh with sound topology** and then apply a known workflow.

## The professional workflow (Blender Studio: "Toon Character Workflow", Dillon Gu)
1. Body → 2. Head and headwear (head, hat, scarf) → 3. Face → 4. Mouth shape keys
5. Rigging with **Rigify** → 6. Weight painting → 7. Face rig
8. **Toon shader + outline** → 9. Tune-up and render

## Lessons that apply directly to us
| Problem we hit | The professional solution |
|---|---|
| Claw-like hands and a boxy body | **A ready base mesh with sound topology**: Blender Studio "Human Base Meshes" (**CC0**, v1.4.1, Blender 4.2+, ~49 MB) with realistic and stylized men and women, or **MPFB2** (MakeHuman; GPL code, **CC0 output**) which generates a person with an automatic **Rigify** rig |
| Blotchy shadows on the face | The **Normal Edit** modifier / transferring normals from a sphere onto the face → clean, flat shading like anime |
| Jagged, noisy outlines (Sobel in the compositor) | **Inverted hull**: a copy of the mesh pushed outward with flipped normals, backface culling, and a dark colour. Thickness is controllable, the line is clean, and it works per object |
| Thobe as a stiff tube | **Model the garment close to its final shape** over the body, then run the cloth simulation with the **rigged body as the collider**, and simulate only the parts that move (do not build it from flat pieces) |
| Expressions | **Mouth shape keys** + eye and brow textures (the hybrid anime method) |
| Toon shading | Shader to RGB → ColorRamp, with the shadow hue shifted toward violet or blue (we already do this) |

## The new plan
1. **Base mesh:** the stylized man from Blender Studio's "Human Base Meshes" (CC0), adjusted to 7.5 heads and 1.78 m, with a slim build.
2. **Rig:** Rigify fitted to the body, then generated, with automatic weights.
3. **Head and face:** the base head with lightly adjusted anime proportions, normals transferred from a sphere, and the drawn face (eyes, brows, beard) as a texture. That part is already built and works.
4. **Thobe:** modelled close to its final shape from the body (offset outward + the skirt down to the ankle), with the details (collar, placket, pocket, cuffs), then a short cloth simulation over the body.
5. **Shemagh:** the current method (a folded triangle draped by simulation), which now works, plus the agal.
6. **Outline:** inverted hull for the character.
7. Then turnaround renders matching the character sheet.

## Sources
- Blender Studio, Toon Character Workflow: studio.blender.org/training/toon-character-workflow/
- Human Base Meshes (CC0): blender.org/download/demo (asset bundles) · cgchannel.com/2023/06/download-blender-studios-free-human-base-meshes · 80.lv
- MPFB2: extensions.blender.org/add-ons/mpfb/ · cgchannel.com/2025/03/check-out-open-source-blender-character-generation-plugin-mpfb-2
- Toon shading / outline: strayspark.studio (anime look in Blender) · note.com/m_0039 (outline tips) · blenderdeluxe.com (cel shading in 5.2)
- Garments: blendernation.com (dress simulation for beginners) · docs.blender.org (cloth)
