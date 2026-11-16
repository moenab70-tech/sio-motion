# Study: how AI works better with Blender (after struggling with the character)

## Diagnosing the problem
I build the character with code and only see the result after a full render. Each fix exposes the next problem, because I can't see the model while I'm editing it. The model also takes manual modeling skill (sculpting the head, the garments) that code doesn't replace.

## Option 1: Blender MCP (live control, with eyes)
- An open-source project (ahujasid/blender-mcp): Claude runs Python inside an **open Blender session** and gets **viewport screenshots** after each step (`get_viewport_screenshot`, `return_screenshot=True`).
- It integrates directly with **Hyper3D Rodin** and **Hunyuan3D** to generate models from images inside Blender.
- Setup: an add-on in Blender, plus `claude mcp add blender uvx blender-mcp`.
- Benefit: faster iteration, and **you watch Blender live** while I work. It doesn't replace modeling skill on its own.

## Option 2: Image → 3D (generate the character from the character sheet)
| Tool | Where | Pros | Cons |
|---|---|---|---|
| **Tripo (P1)** | Cloud | The most balanced in comparisons; **convincing clothing and hair**; accepts **multiple views** (we have front/side/back); **automatic rig** | Needs an account; commercial use usually on a paid plan |
| **Hunyuan3D (V3 / 2.1)** | Open source / cloud | Strongest open option; clean body | Stiff facial expressions; the Mac port is unverified |
| **TRELLIS.2** | **Local on Mac** (trellis-mac port) | Free; about 3.5 min on an M4 Pro | Recommended **24 GB+** RAM (yours is 16); DINOv3/RMBG models restrict commercial use; needs retopology |
| **Rodin** | Cloud (through Blender MCP) | High mesh fidelity | Textures need work |

## Rigging
- **Tripo** auto-rig, **Mixamo** (free, humanoid, still works), **Rigify** in Blender (free, full control). AccuRIG is Windows only.

## My recommendation
1. **Generate the character model** from HERO_SHEET (front, side and back views) with **Tripo**, using its free credits as a test first.
2. **Import it into Blender** and apply our toon shading, inking and colour palette (so it matches the environments).
3. **Rig it** (Tripo's auto-rig or Rigify). The ends of the shemagh and the hem of the thobe sway with light bones instead of a full cloth simulation, which is a well-known approach in anime.
4. **Blender MCP** (optional, useful): you can watch the work live, and I can see the viewport at every step.

Honest trade-off: the generated model **fuses the garments into one mesh**, so we lose the shemagh's cloth simulation and use bone-driven sway instead. In return we get a character that matches the drawing at once, without dozens of attempts.

## Sources
github.com/ahujasid/blender-mcp · mcp.directory/blog/claude-blender-connector-guide · vitalify.asia (image-to-3D comparison, July 2026) · fuser.studio · krea.ai · github.com/shivampkumar/trellis-mac · lilting.ch (TRELLIS.2 on M1 Max) · app.cinevva.com (auto-rigging 2026) · strayspark.studio (AI auto-rigging showdown)
