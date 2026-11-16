"""Hasad opening - FINAL v6 (engineer only). Built from office_v5.blend (untouched): removes every supporting
character, keeps engineer V2.3 + office + story sessions, adds the two exterior canal shots, and renders the
seven storyboard slots (frame counts from opening/timing.ts) as 1920x1080 PNG sequences.

  Blender -b tests/office_v5/office_v5.blend -P scripts/final_v6.py -- --build
  Blender -b tests/final_v6/final_v6.blend   -P scripts/final_v6.py -- --render [SHOT ...] [--pct 100]
"""
import os, sys, math
import bpy
from mathutils import Vector

LIB = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
sys.path.insert(0, LIB)
OUT = os.path.join(LIB, "tests", "final_v6"); os.makedirs(OUT, exist_ok=True)
FRAMES_DIR = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/public/media/opening/blender_v6"

# slot -> list of segments (camera, session, first blender frame, number of frames); lengths match timing.ts
PLAN = {
    "1A": [("SHOT_A_establishing", "S1", 1, 90)],
    "1B": [("SHOT_D_pencil", "S1", 1, 96)],
    "2A": [("SHOT_H_calendar", "S2", 1, 22), ("SHOT_E_overhead", "S2", 20, 44)],
    "2B": [("SHOT_G_dawn_reveal", "S3", 1, 102)],
    "3A": [("SHOT_C_eyes", "S3", 1, 84)],
    "3B": [("SHOT_J_canal", "S3", 1, 90)],
    "4A": [("SHOT_K_rise", "S3", 1, 120)],
}


def build():
    from sio_env import shots, story
    # 1. remove every supporting character and everything they own
    gone = [o for o in bpy.data.objects if o.get("sio_owner") in ("engineer_m02", "engineer_f02")]
    n = len(gone)
    for o in gone:
        bpy.data.objects.remove(o)
    for c in [c for c in bpy.data.collections if c.name in ("CHR_engineer_m02", "CHR_engineer_f02")]:
        bpy.data.collections.remove(c)
    for o in ("SHOT_I_collab", "SHOT_I_target"):
        if bpy.data.objects.get(o):
            bpy.data.objects.remove(bpy.data.objects[o])
    story.SESSIONS.pop("COLLAB", None)
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    owners = sorted({o.get("sio_owner") for o in bpy.data.objects if o.get("sio_owner")})
    print("REMOVED", n, "objects; remaining characters:", owners)
    # 2. exterior shots over the irrigation canal (ground z=-9, canal along X at y=-38)
    c = shots._cam("SHOT_J_canal", 28, 8)
    shots._track(c, shots._target_empty("SHOT_J_target", (40.0, -38.0, -8.6)), focus=True)
    shots._move(c, [(-38.0, -33.5, -6.9), (-14.0, -34.5, -7.1)], 1, 90)
    c = shots._cam("SHOT_K_rise", 24, 11)
    tgt = shots._target_empty("SHOT_K_target", (90.0, -40.0, -8.5))     # far end of the canal: stays in frame
    shots._track(c, tgt, focus=False)
    shots._move(c, [(0.0, -28.0, -6.8), (0.0, -24.0, 9.0)], 1, 120)       # rises from the bank to an aerial view
    for f, z in ((1, -7.5), (120, -9.0)):
        tgt.location.z = z; tgt.keyframe_insert("location", index=2, frame=f)
    bpy.context.scene.camera = bpy.data.objects["SHOT_A_establishing"]
    path = os.path.join(OUT, "final_v6.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.file.make_paths_absolute(); bpy.ops.wm.save_as_mainfile(filepath=path, relative_remap=False)
    print("FINAL_V6 saved", path)


def render(slots, pct=100, samples=64):
    from sio_env import story
    from sio_char import render as RD
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    RD.setup("cinematic", sc, 30)
    sc.render.resolution_percentage = pct
    try:
        sc.eevee.taa_render_samples = samples
    except Exception:
        pass
    sc.render.film_transparent = False
    im = sc.render.image_settings
    if hasattr(im, "media_type"):
        im.media_type = 'IMAGE'
    im.file_format = 'PNG'; im.color_mode = 'RGB'; im.compression = 30
    for slot in slots:
        d = os.path.join(FRAMES_DIR, slot); os.makedirs(d, exist_ok=True)
        idx = 1
        for cam, ses, f0, n in PLAN[slot]:
            story.apply(ses, rig)
            sc.camera = bpy.data.objects[cam]
            for f in range(f0, f0 + n):
                p = os.path.join(d, f"f_{idx:04d}.png")
                if not os.path.exists(p):
                    sc.frame_set(f)
                    sc.render.filepath = p
                    bpy.ops.render.render(write_still=True)
                idx += 1
        print("SLOT_DONE", slot, idx - 1, "frames")


if __name__ == "__main__" or "__file__" not in dir():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--build" in a:
        build()
    if "--render" in a:
        pct = int(a[a.index("--pct") + 1]) if "--pct" in a else 100
        slots = [x for x in a if x in PLAN] or list(PLAN)
        render(slots, pct)
