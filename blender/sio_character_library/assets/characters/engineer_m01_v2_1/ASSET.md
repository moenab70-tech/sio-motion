# engineer_m01 · v2.1 — baseline SIO engineer

**Status: Ready for User Approval** (not yet approved for production; do not start the Hasad full production with it until the user approves).

## Contents
| File | What |
|---|---|
| `engineer_m01_v2_1.blend` | Editable scene: character (MPFB body + Rigify rig + Hair Curves hair/beard + polished materials), desk set, pencil in tripod grip, 3 s drawing animation (frames 1–90 @ 30 fps), cameras `CAM_front/side/threequarter/face/grip/seated/anim` |
| `previews/` | Final-quality stills + `engineer_m01_v2_1_3s.mp4` (Eevee preview, 50 %) |
| `status.json` | Version, status, presets used |

Rebuildable from code at any time (no manual steps):
```bash
/Applications/Blender.app/Contents/MacOS/Blender -b -P scripts/poc_engineer_drawing_v2_1.py -- --render
```

## Presets that define this character
- Character: `presets/characters/engineer_m01_v2_1.json` (MPFB macro, skin, clothes, Rigify, corrective smooth, material polish)
- Hair: `presets/hair/short_side_part_v2.json` · Beard: `presets/hair/beard_short_v2.json`

## Controls you will use (Rigify)
- Body: `torso`, `hips`, `chest`, `shoulder.L/R`, `neck`, `head`
- Arms (IK by default): `hand_ik.L/R`, elbow poles `upper_arm_ik_target.L/R` (`upper_arm_parent.*["pole_vector"] = True`)
- Legs (IK): `foot_ik.L/R`
- Fingers: `f_*.01/02/03.L/R` (curl = local X) — presets in `rig.HAND_POSES` (`relaxed`, `rest_flat`, `pencil`, `point`, `fist`)
- Face: `eye_common` (gaze target, lids follow), `lid.T.*` (blink), `brow.*`, `lip.*`; expression presets `rig.EXPRESSIONS`

## Re-using it in a new shot (Python / MCP)
```python
import sys; sys.path.insert(0, "<repo>/blender/sio_character_library")
from sio_char import character, hair, rig as R, anim as A, render
ch = character.build("engineer_m01_v2_1")
for h in ch.preset["hair"]: hair.apply_preset(ch, h)
R.sit_natural(ch.rig, seat_height=0.455)                 # or keep standing
R.expression(ch.rig, "focused")
pencil = A.make_pencil(length=0.19, radius=0.0042)
R.hand_pose(ch.rig, "R", "pencil"); A.grip(ch.rig, pencil, "R", mode="web")
A.draw_strokes(ch.rig, pencil, strokes, frame_start=1)   # hand solved from the pencil tip every frame
A.eyes_follow(ch.rig, lambda f: pencil.matrix_world.translation, 1, 90); A.blinks(ch.rig, [64])
```
Or append the character from `engineer_m01_v2_1.blend` (collection `CHR_engineer_m01` + `SIO_rig_widgets`).

## Known limitations
- Hair/beard follow the head bone rigidly (no secondary motion; EXea Jiggle is available for future hair bones).
- Long jeans/shirt are MPFB proxy clothes (no cloth simulation).
- The face rig is Rigify's; dialogue/lip-sync not set up.
