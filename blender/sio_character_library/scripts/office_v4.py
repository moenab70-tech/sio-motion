"""Hasad opening - engineering office v4 (cinematic): approved engineer V2.2 + v3 office + dressing + 3D exterior
+ dusk/night/dawn lighting + paper clutter + camera shot library. Previews only (no final renders).

  Blender -b -P scripts/office_v4.py -- --previews
Outputs: tests/office_v4/office_v4.blend, tests/office_v4/previews/*.png
"""
import os, sys, importlib.util
import bpy

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else \
    "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
if LIB not in sys.path:
    sys.path.insert(0, LIB)
OUT = os.path.join(LIB, "tests", "office_v4"); os.makedirs(os.path.join(OUT, "previews"), exist_ok=True)
PREVIEWS = globals().get("PREVIEWS", "--previews" in sys.argv)

# 1. approved character + drawing animation (V2.2 config), written to the office_v4 folder (V2.2 files untouched)
_spec = importlib.util.spec_from_file_location("poc_v2_2", os.path.join(LIB, "scripts", "poc_engineer_drawing_v2_2.py"))
V22 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V22)
V2 = V22.V2
V2.OUT = OUT; V2.RENDER = False
V2.CONFIG.update(tag="office_v4_character")


def build():
    ch = V2.main()
    for m in [m for m in list(sys.modules) if m.startswith("sio_env")]:
        del sys.modules[m]
    from sio_env import office, exterior, lighting, clutter, shots
    from sio_char import render as RD
    # remove the studio backdrop + studio lights/cameras of the character test
    for n in ("SET_floor", "SET_wall", "KEY_window", "FILL", "RIM", "DESK_lamp"):
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o)
    for o in [o for o in bpy.data.objects if o.type == 'CAMERA' and o.name.startswith("CAM_")]:
        bpy.data.objects.remove(o)
    desk_top = 0.7875
    office.append_office()
    office.dress(desk_top=desk_top)
    office.facade()
    ext, n_palms = exterior.build()
    veg = exterior.poly_haven_vegetation()
    print("POLYHAVEN_VEG", veg)
    lighting.rig_lights()
    lighting.set_state("dusk")
    clutter.build(desk_top=desk_top, desk_area=((0.25, 0.66), (-0.62, -0.2)))
    pencil = bpy.data.objects["SIO_pencil"]
    cams = shots.all_shots(ch.rig, pencil)
    sc = bpy.context.scene
    sc.camera = cams["A"]
    RD.setup("preview", sc, 30)
    sc.frame_start, sc.frame_end = 1, 150
    path = os.path.join(OUT, "office_v4.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.file.make_paths_absolute(); bpy.ops.wm.save_as_mainfile(filepath=path, relative_remap=False)
    print("OFFICE_V4 saved", path, "palms", n_palms)
    return ch, cams


def previews(pct=50, samples=32):
    from sio_env import lighting, clutter
    from sio_char import render as RD
    sc = bpy.context.scene
    RD.setup("preview", sc, 30); sc.render.resolution_percentage = pct
    try:
        sc.eevee.taa_render_samples = samples
    except Exception:
        pass
    P = os.path.join(OUT, "previews")
    plan = [  # (file, state, clutter, camera, frame)
        ("01_wide_dusk", "dusk", "early", "SHOT_A_establishing", 60),
        ("02_wide_night", "night", "late_night", "SHOT_A_establishing", 60),
        ("03_wide_dawn", "dawn", "dawn", "SHOT_G_dawn_reveal", 100),
        ("04_exterior_window", "dusk", "early", "SHOT_B_exterior_in", 70),
        ("05_eyes_closeup_night", "night", "late_night", "SHOT_C_eyes", 40),
        ("06_pencil_closeup_night", "night", "late_night", "SHOT_D_pencil", 40),
        ("07_overhead_clean_dusk", "dusk", "clean", "SHOT_E_overhead", 40),
        ("08_overhead_late_night", "night", "late_night", "SHOT_E_overhead", 40),
    ]
    for name, state, cl, cam, f in plan:
        lighting.set_state(state); clutter.show(cl)
        sc.frame_set(f)
        RD.still(os.path.join(P, name + ".png"), cam, sc)
        print("PREVIEW", name)


if __name__ == "__main__" or "__file__" not in dir():
    build()
    if PREVIEWS:
        previews()
