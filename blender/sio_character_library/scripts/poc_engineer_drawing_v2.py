"""PoC v2: improved engineer (groomed hair, symmetric beard with mouth clearance, natural seated posture,
corrective smoothing, focused expression, eye tracking + blinks). Reuses the v1 set/lights; v1 outputs are untouched.

Headless:  Blender -b -P scripts/poc_engineer_drawing_v2.py -- --render
"""
import sys, os, math, importlib.util
import bpy
from mathutils import Vector, Matrix

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else \
    "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
if LIB not in sys.path:
    sys.path.insert(0, LIB)
for m in [m for m in list(sys.modules) if m.startswith("sio_char")]:
    del sys.modules[m]
import sio_char
from sio_char import character, hair, rig as R, anim as A, render as RD

_spec = importlib.util.spec_from_file_location("poc_v1", os.path.join(LIB, "scripts", "poc_engineer_drawing.py"))
V1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V1)     # reuse set + lights (main() not run)

OUT = os.path.join(LIB, "tests", "poc_engineer_drawing_v2")
RENDER = globals().get("RENDER", "--render" in sys.argv)
# Version knobs (defaults = the approved v2 result; poc_engineer_drawing_v2_1.py overrides them)
CONFIG = dict(tag="v2", preset="engineer_m01_v2", pencil={}, grip={}, blinks=[22, 71],
              sit=dict(seat_y=0.04, spine_lean=(6, 9)), look=dict(strength=0.45, max_deg=24, neck_share=0.3),
              reach=0.0, resolve_contacts=False, left_hand_pose="relaxed", extra_cams={}, still_cams=["CAM_front", "CAM_side", "CAM_face", "CAM_seated"], after_build=None)
os.makedirs(OUT, exist_ok=True)
FPS, F0, F1 = 30, 1, 90


def hand_frame(fingers, palm, side):
    y = Vector(fingers).normalized(); pn = Vector(palm); pn = (pn - y * pn.dot(y)).normalized()
    x = -pn if side == "R" else pn
    return Matrix((x, y, x.cross(y).normalized())).transposed()


def main():
    V1.clean_scene()
    sc = bpy.context.scene
    RD.setup("preview", sc, FPS)
    sc.frame_start, sc.frame_end = F0, F1
    set_coll = V1.build_set()
    bpy.data.objects["PH_dining_chair_02"].location = (0, 0.10, 0)

    ch = character.build(CONFIG["preset"])
    if CONFIG["after_build"]:
        CONFIG["after_build"](ch)
    for hp in ch.preset["hair"]:
        hair.apply_preset(ch, hp)
    rig = ch.rig

    dg = bpy.context.evaluated_depsgraph_get()
    owned = [o for o in bpy.data.objects if o.get("sio_owner")]
    for o in owned:
        o.hide_viewport = True
    _, loc, *_ = sc.ray_cast(dg, Vector((0, 0.06, 1.2)), Vector((0, 0, -1)))
    _, loc2, *_ = sc.ray_cast(dg, Vector((0, -0.45, 1.5)), Vector((0, 0, -1)))
    for o in owned:
        o.hide_viewport = False
    seat, desk_top = loc.z, loc2.z

    # 1. posture: pelvis on the seat, gradual spine lean, relaxed shoulders, planted asymmetric feet
    R.sit_natural(rig, seat_height=seat, **CONFIG["sit"])

    # 2. hands: paper closer to the body so the elbows bend ~100 deg; forearms near the desk edge
    paper_c = Vector((0.02, -0.34 - CONFIG["reach"], desk_top + 0.0006))
    A.make_paper(center=paper_c, rot_z=math.radians(-6), collection=set_coll)
    R.set_world(rig, "hand_ik.L", loc=(0.16, -0.30 - CONFIG["reach"], desk_top + 0.020), rot=hand_frame((-0.30, -0.93, -0.10), (0.1, 0, -1), "L"))
    R.hand_pose(rig, "L", CONFIG["left_hand_pose"])
    R.set_world(rig, "hand_ik.R", loc=(-0.11, -0.25 - CONFIG["reach"], desk_top + 0.085), rot=hand_frame((0.32, -0.84, -0.44), (0.85, 0.1, -0.45), "R"))
    R.hand_pose(rig, "R", "pencil")
    for s in ("L", "R"):
        R.arm_pole(rig, s, out=0.30, back=0.25, down=0.12)
    pencil = A.make_pencil(collection=set_coll, **CONFIG["pencil"])
    A.grip(rig, pencil, "R", **CONFIG["grip"])
    if CONFIG["resolve_contacts"]:
        # v2.2: no hand may sink into the desk; the writing hand is lifted by letting the pencil stick out further
        import numpy as np
        desk = bpy.data.objects["PH_metal_office_desk"]
        B = np.array([o.matrix_world @ Vector(c) for o in desk.children_recursive if o.type == 'MESH' for c in o.bound_box])
        lo, hi = B.min(0), B.max(0)
        fp = (lo[0], hi[0], lo[1], hi[1]); top = float(hi[2])
        dl = R.lay_hand_flat(rig, ch.body, "L", top + 0.0006, fp)          # paper top
        kw, dr = A.fit_writing_grip(rig, ch.body, pencil, "R", (paper_c.x, paper_c.y, desk_top + 0.0008), top, fp, CONFIG["grip"])
        print("contacts: left hand residual %.1f mm, writing hand residual %.1f mm, tip_out %.3f, roll %s deg" % (dl * 1000, dr * 1000, kw.get("tip_out", 0), kw.get("_roll_deg")))

    # 3. face: subtle focus
    R.expression(rig, "focused", 1.0)

    # 4. the concept on the paper (same design as v1, shifted with the paper)
    z = desk_top + 0.0008
    dy = paper_c.y - (-0.43)
    def canal(off, x0=-0.035, x1=0.075, y0=-0.455 + dy):
        return [Vector((x0 + (x1 - x0) * t, y0 + off + 0.018 * math.sin(t * math.pi * 1.6), z)) for t in [i / 24 for i in range(25)]]
    o = A._ink_curve("SIO_sketch_bank_A", canal(0.0), 0, 0, set_coll); o.data.animation_data_clear(); o.data.bevel_factor_end = 1
    for i, xx in enumerate((-0.02, 0.015, 0.05)):
        o = A._ink_curve(f"SIO_sketch_field_{i}", [Vector((xx, -0.505 + dy, z)), Vector((xx + 0.012, -0.485 + dy, z))], 0, 0, set_coll)
        o.data.animation_data_clear(); o.data.bevel_factor_end = 1

    # 5. animation
    rig.animation_data_create()
    A.key_pose(rig, ["torso", "chest", "hips", "foot_ik.L", "foot_ik.R", "hand_ik.L", "shoulder.L", "shoulder.R",
                     "upper_arm_ik_target.L", "upper_arm_ik_target.R"], F0)
    strokes = [canal(0.022), [Vector((0.028, -0.452 + dy, z)), Vector((0.030, -0.420 + dy, z))]]
    last, inks = A.draw_strokes(rig, pencil, strokes, frame_start=F0 + 2, fps=FPS, speed=0.075, lift=0.010,
                                hover_frames=5, side="R", ink_collection=set_coll, surface_z=z)
    tip = lambda f: (sc.frame_set(f), pencil.matrix_world.translation.copy())[1]
    A.look_follow(rig, lambda f: tip(f) + Vector((0, 0.03, 0)), F0, F1, lag=5, noise_deg=0.6, step=2, **CONFIG["look"])
    A.eyes_follow(rig, tip, F0, F1, lag=1, step=2)
    A.blinks(rig, CONFIG["blinks"])
    A.breathe(rig, F0, F1, amount_deg=0.8)
    sc.frame_set(F0)

    # 6. lights / cameras (v1 rig) + a medium shot for the seated pose
    V1.lights_and_cameras()
    sc.frame_set(45)
    eyes = (R.bone_head(rig, "DEF-eye.L") + R.bone_head(rig, "DEF-eye.R")) / 2
    cams = {
        "CAM_anim":  ((1.05, -1.75, 1.42), (0.0, -0.25, 1.0), 50),
        "CAM_front": ((0.0, -2.6, 1.20), (0.0, -0.05, 0.95), 50),
        "CAM_side":  ((-2.4, -0.2, 1.10), (0.0, -0.15, 0.85), 45),
        "CAM_face":  ((eyes.x + 0.36, eyes.y - 0.80, eyes.z - 0.13), (eyes.x, eyes.y + 0.02, eyes.z + 0.015), 85),
        "CAM_seated": ((-1.55, -1.05, 1.0), (0.0, -0.1, 0.78), 32),
    }
    for n, fn in CONFIG["extra_cams"].items():
        cams[n] = fn(rig, pencil, eyes)
    for n, (l, t, lens) in cams.items():
        c = bpy.data.objects.get(n)
        if not c:
            d = bpy.data.cameras.new(n); d.dof.use_dof = True; d.dof.aperture_fstop = 2.8
            c = bpy.data.objects.new(n, d); sc.collection.objects.link(c)
        c.data.lens = lens
        c.location = l; c.rotation_euler = (Vector(t) - Vector(l)).to_track_quat('-Z', 'Y').to_euler()
        c.data.dof.focus_distance = (Vector(t) - Vector(l)).length
    sc.camera = bpy.data.objects["CAM_anim"]
    sc.frame_set(F0)
    path = os.path.join(OUT, f"poc_engineer_drawing_{CONFIG['tag']}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    # textures live in MPFB / Poly Haven cache folders: store them absolute so a copied .blend keeps its links
    bpy.ops.file.make_paths_absolute()
    bpy.ops.wm.save_as_mainfile(filepath=path, relative_remap=False)
    print("saved", path, "strokes end", last)
    if RENDER:
        render_all()
    return ch


def render_all():
    sc = bpy.context.scene
    RD.setup("cinematic", sc, FPS)
    for cam in CONFIG["still_cams"]:
        sc.frame_set(40)
        RD.still(os.path.join(OUT, f"{cam.lower()}_{CONFIG['tag']}.png"), cam, sc)
    RD.setup("preview", sc, FPS)
    sc.render.resolution_percentage = 50
    sc.camera = bpy.data.objects["CAM_anim"]
    RD.animation_preview(os.path.join(OUT, f"poc_engineer_drawing_{CONFIG['tag']}_3s.mp4"), F0, F1, sc)


if __name__ == "__main__" or "__file__" not in dir():
    main()
