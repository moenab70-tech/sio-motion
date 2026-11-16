"""Hasad opening v6.3 = v6.2 (cameras + render quality) + irrigated canal vegetation from Poly Haven (sio_env.vegetation).
final_v6_2.blend stays untouched.
  Blender -b tests/final_v6_2/final_v6_2.blend -P scripts/final_v6_3.py -- --build [--previews]
  Blender -b tests/final_v6_3/final_v6_3.blend -P scripts/final_v6_3.py -- --previews
  Blender -b tests/final_v6_3/final_v6_3.blend -P scripts/final_v6_3.py -- --render [SLOT ...]
"""
import os, sys, importlib.util
import bpy
LIB = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
sys.path.insert(0, LIB)
OUT = os.path.join(LIB, "tests", "final_v6_3"); os.makedirs(os.path.join(OUT, "previews"), exist_ok=True)
_s = importlib.util.spec_from_file_location("v62", os.path.join(LIB, "scripts", "final_v6_2.py")); V62 = importlib.util.module_from_spec(_s); _s.loader.exec_module(V62)
V62.FRAMES_DIR = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/public/media/opening/blender_v6_3"


def build():
    from sio_env import vegetation
    info = vegetation.build()
    print("VEG", info)
    dg = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects["EXT_veg_scatter"].evaluated_get(dg)
    from collections import Counter
    cnt = Counter()
    for inst in dg.object_instances:
        if inst.is_instance and inst.parent and inst.parent.name == "EXT_veg_scatter":
            cnt[inst.object.users_collection[0].name if inst.object.users_collection else "?"] += 1
    print("INSTANCES", dict(cnt), "total", sum(cnt.values()))
    path = os.path.join(OUT, "final_v6_3.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, relative_remap=False); print("FINAL_V6_3 saved", path)


def previews(pct=50, samples=32):
    from sio_env import story
    from sio_char import render as RD
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    RD.setup("cinematic", sc, 30); V62.quality(sc); sc.render.resolution_percentage = pct; sc.eevee.taa_render_samples = samples
    im = sc.render.image_settings; im.media_type = 'IMAGE'; im.file_format = 'JPEG'; im.quality = 92
    for tag, ses, cam, f in (("3B_canal_bank_f01", "S3", "SHOT_J_canal", 1), ("3B_canal_bank_f60", "S3", "SHOT_J_canal", 60),
                             ("4A_canal_axis_f01", "S3", "SHOT_K3_canal_axis", 1), ("4A_canal_axis_f120", "S3", "SHOT_K3_canal_axis", 120),
                             ("1A_office_window_f45", "S1", "SHOT_A_establishing", 45), ("2B_profile_window_f51", "S3", "SHOT_G2_profile", 51)):
        story.apply(ses, rig); sc.camera = bpy.data.objects[cam]; sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, "previews", tag + ".jpg"); bpy.ops.render.render(write_still=True); print("PREV", tag)


if __name__ == "__main__" or "__file__" not in dir():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--build" in a: build()
    if "--previews" in a: previews()
    if "--render" in a:
        V62.render([x for x in a if x in V62.PLAN] or ["1A", "1B", "2A", "2B", "3B", "4A"])
