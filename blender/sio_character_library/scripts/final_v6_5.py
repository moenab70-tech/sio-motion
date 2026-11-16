"""Hasad opening v6.5 = v6.4 + landscape enrichment (sio_env.landscape): terrain relief, recessed canal channel,
layered Poly Haven vegetation (library v3), palms moved to the background, office window planters.
final_v6_4.blend stays untouched. Previews only - no full render.
  Blender -b tests/final_v6_4/final_v6_4.blend -P scripts/final_v6_5.py -- --build
  Blender -b tests/final_v6_5/final_v6_5.blend -P scripts/final_v6_5.py -- --previews [pct]
  Blender -b tests/final_v6_5/final_v6_5.blend -P scripts/final_v6_5.py -- --compare eevee|cycles office|canal <out.png>
"""
import os, sys, time, importlib.util
import bpy
LIB = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
sys.path.insert(0, LIB)
OUT = os.path.join(LIB, "tests", "final_v6_5")
_s = importlib.util.spec_from_file_location("v64", os.path.join(LIB, "scripts", "final_v6_4.py")); V64 = importlib.util.module_from_spec(_s); _s.loader.exec_module(V64)


def build():
    from sio_env import landscape
    info = landscape.build()
    for k, v in info.items():
        print("LAND", k, v)
    from collections import Counter
    dg = bpy.context.evaluated_depsgraph_get(); cnt = Counter()
    for inst in dg.object_instances:
        if inst.is_instance and inst.parent:
            cnt[inst.parent.name] += 1
    print("INSTANCES", dict(cnt))
    path = os.path.join(OUT, "final_v6_5.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, relative_remap=False); print("FINAL_V6_5 saved", path)


def preview_cams():
    from sio_env import shots as SH
    rig = bpy.data.objects["engineer_m01_rig"]; bpy.context.scene.frame_set(51)
    H = rig.matrix_world @ rig.pose.bones["DEF-spine.006"].head
    def cam(name, lens, fs, loc, tgt, focus=True):
        c = SH._cam(name, lens, fs); c.data.clip_end = 150000; c.animation_data_clear()
        SH._track(c, SH._target_empty(name + "_t", tgt), focus=focus); c.location = loc; return c
    return {
        "wide_landscape": cam("PV_wide", 24, 11, (-40.0, -100.0, 4.0), (120.0, -40.0, -9.0), False),
        "bank_greenery_rocks": cam("PV_bank", 35, 5.6, (-8.0, -50.5, -7.6), (6.0, -46.0, -8.7)),
        "canal_cross_section": cam("PV_section", 24, 8, (6.0, -46.8, -7.3), (6.0, -33.0, -9.7)),
        "ots_engineer_canal": cam("PV_ots", 32, 5.6, (H.x + 0.14, H.y + 0.52, H.z + 0.30), (-2.0, -38.0, -9.4)),
    }


def previews(pct=50, samples=32):
    from sio_env import story
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    cams = preview_cams()
    V64._eevee(sc, pct, samples)
    im = sc.render.image_settings; im.media_type = 'IMAGE'; im.file_format = 'JPEG'; im.quality = 92
    plan = [("3B_canal_bank_f45", "S3", "SHOT_J_canal", 45), ("4A_canal_axis_f60", "S3", "SHOT_K3_canal_axis", 60),
            ("4A_canal_axis_f120", "S3", "SHOT_K3_canal_axis", 120),
            ("1A_office_window_planters_f45", "S1", "SHOT_A_establishing", 45), ("2B_profile_window_f51", "S3", "SHOT_G2_profile", 51)]
    plan += [(k, "S3", c.name, 51) for k, c in cams.items()]
    for tag, ses, cam, f in plan:
        story.apply(ses, rig); sc.camera = bpy.data.objects[cam]; sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, "previews", tag + ".jpg"); t = time.time(); bpy.ops.render.render(write_still=True)
        print("PREV", tag, round(time.time() - t, 1))


CMP = {"office": ("S3", "SHOT_G2_profile", 51, "Engineering office"), "canal": ("S3", "SHOT_K3_canal_axis", 60, "Irrigation canal")}


def compare(engine, case, out):
    from sio_env import story
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    (V64._cycles if engine == "cycles" else V64._eevee)(sc)
    ses, cam, f, label = CMP[case]; story.apply(ses, rig); sc.camera = bpy.data.objects[cam]; sc.frame_set(f)
    r = sc.render; r.use_stamp = True
    for a in dir(r):
        if a.startswith("use_stamp_") and a != "use_stamp_note":
            try: setattr(r, a, False)
            except Exception: pass
    r.use_stamp_note = True; r.stamp_note_text = f"{label}  |  {'Cycles (Metal GPU)' if engine == 'cycles' else 'EEVEE'}  |  frame {f}  |  AgX"
    r.stamp_font_size = 30; r.stamp_background = (0, 0, 0, 0.6)
    im = r.image_settings; im.media_type = 'IMAGE'; im.file_format = 'PNG'; im.color_mode = 'RGB'
    r.filepath = out; t = time.time(); bpy.ops.render.render(write_still=True)
    print("COMPARE", engine, case, "seconds", round(time.time() - t, 1))


if __name__ == "__main__" or "__file__" not in dir():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--build" in a: build()
    if "--previews" in a:
        i = a.index("--previews"); previews(int(a[i + 1]) if len(a) > i + 1 and a[i + 1].isdigit() else 50)
    if "--compare" in a:
        i = a.index("--compare"); compare(a[i + 1], a[i + 2], a[i + 3])
