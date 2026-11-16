"""Proof of concept: an engineer sits at a desk and draws an irrigation-channel concept (3 s @ 30 fps).

Headless:
  /Applications/Blender.app/Contents/MacOS/Blender -b -P scripts/poc_engineer_drawing.py -- [--render]
Inside a live Blender (MCP):
  exec(open(".../scripts/poc_engineer_drawing.py").read())   (set RENDER = True/False first)

Everything comes from the sio_char library; only scene layout lives here.
"""
import sys, os, math
import bpy
from mathutils import Vector, Matrix

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else \
    "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
if LIB not in sys.path:
    sys.path.insert(0, LIB)
for m in [m for m in list(sys.modules) if m.startswith("sio_char")]:
    del sys.modules[m]
import sio_char
from sio_char import character, hair, rig as R, anim as A, render as RD, util

OUT = os.path.join(LIB, "tests", "poc_engineer_drawing")
OFFICE = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/src/videos/hasad-2026/opening/blender/v3/office_polyhaven.blend"
RENDER = globals().get("RENDER", "--render" in sys.argv)
os.makedirs(OUT, exist_ok=True)
FPS, F0, F1 = 30, 1, 90


def clean_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.actions, bpy.data.armatures, bpy.data.curves,
                  bpy.data.hair_curves, bpy.data.images, bpy.data.lights, bpy.data.cameras):
        for d in list(block):
            if d.users == 0:
                block.remove(d)


def build_set():
    coll = util.ensure_collection("SET_desk")
    with bpy.data.libraries.load(OFFICE, link=False) as (a, b):
        b.collections = ["Office_Props"]
    keep = {"PH_metal_office_desk", "PH_dining_chair_02"}
    def under(o):
        while o:
            if o.name in keep:
                return True
            o = o.parent
        return False
    for c in b.collections:
        for o in list(c.objects):
            if under(o):
                coll.objects.link(o)
        bpy.data.collections.remove(c)
    for o in [o for o in bpy.data.objects if o.users == 0]:
        bpy.data.objects.remove(o)
    desk = bpy.data.objects["PH_metal_office_desk"]; desk.location = (0, -0.62, 0); desk.rotation_euler = (0, 0, math.pi)
    chair = bpy.data.objects["PH_dining_chair_02"]; chair.location = (0, 0.12, 0); chair.rotation_euler = (0, 0, 0)
    # clean studio backdrop: floor + soft warm wall
    for name, size, loc, rot, col in (("SET_floor", 12, (0, 0, 0), (0, 0, 0), (0.30, 0.27, 0.24)),
                                      ("SET_wall", 12, (0, 1.6, 3), (math.pi / 2, 0, 0), (0.42, 0.40, 0.37))):
        bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
        o = bpy.context.active_object; o.name = name
        m = bpy.data.materials.new(name); m.use_nodes = True
        bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bs.inputs["Base Color"].default_value = (*col, 1); bs.inputs["Roughness"].default_value = 0.9
        o.data.materials.append(m)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    return coll


def lights_and_cameras():
    sc = bpy.context.scene
    w = bpy.data.worlds.new("SIO_world"); sc.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.32, 0.34, 0.38, 1); bg.inputs[1].default_value = 0.35
    def light(name, kind, loc, target, energy, color, size=1.0):
        d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color
        if kind == 'AREA':
            d.size = size
        o = bpy.data.objects.new(name, d); sc.collection.objects.link(o)
        o.location = loc; o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        return o
    light("KEY_window", 'AREA', (1.6, -1.2, 1.9), (0, -0.3, 1.0), 170, (1.0, 0.86, 0.70), 1.4)   # warm window key
    light("FILL", 'AREA', (-1.8, -1.6, 1.4), (0, -0.2, 1.1), 60, (0.85, 0.9, 1.0), 2.0)
    light("RIM", 'AREA', (-0.8, 1.3, 2.0), (0, 0, 1.3), 140, (0.80, 0.86, 1.0), 0.8)
    light("DESK_lamp", 'SPOT', (-0.35, -0.55, 1.35), (0.0, -0.42, 0.79), 12, (1.0, 0.82, 0.6))
    cams = {}
    def cam(name, loc, target, lens):
        d = bpy.data.cameras.new(name); d.lens = lens
        d.dof.use_dof = True; d.dof.aperture_fstop = 2.8
        o = bpy.data.objects.new(name, d); sc.collection.objects.link(o)
        o.location = loc; o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        cams[name] = o
        return o
    return cams


def main():
    clean_scene()
    sc = bpy.context.scene
    RD.setup("preview", sc, FPS)
    sc.frame_start, sc.frame_end = F0, F1
    set_coll = build_set()

    # 1. character + hair (library presets)
    ch = character.build("engineer_m01")
    for hp in ch.preset["hair"]:
        hair.apply_preset(ch, hp)
    rig = ch.rig

    # 2. seated pose with IK legs; chair seat height measured from the set
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.get("sio_owner"):
            o.hide_viewport = True
    hit, loc, *_ = sc.ray_cast(dg, Vector((0, 0.08, 1.2)), Vector((0, 0, -1)))
    hit2, loc2, *_ = sc.ray_cast(dg, Vector((0, -0.45, 1.5)), Vector((0, 0, -1)))
    for o in bpy.data.objects:
        if o.get("sio_owner"):
            o.hide_viewport = False
    seat, desk_top = loc.z, loc2.z
    R.sit(rig, seat_height=seat, lean_deg=16)

    # 3. hands: left holds the paper, right writes
    def hand_frame(fingers, palm, side):
        y = Vector(fingers).normalized(); pn = Vector(palm); pn = (pn - y * pn.dot(y)).normalized()
        x = -pn if side == "R" else pn
        return Matrix((x, y, x.cross(y).normalized())).transposed()
    paper = A.make_paper(center=(0.02, -0.43, desk_top + 0.0006), rot_z=math.radians(-6), collection=set_coll)
    R.set_world(rig, "hand_ik.L", loc=(0.17, -0.40, desk_top + 0.022), rot=hand_frame((-0.25, -0.95, -0.12), (0, 0, -1), "L"))
    R.hand_pose(rig, "L", "rest_flat")
    R.set_world(rig, "hand_ik.R", loc=(-0.12, -0.33, desk_top + 0.097), rot=hand_frame((0.30, -0.85, -0.45), (0.85, 0.1, -0.45), "R"))
    R.hand_pose(rig, "R", "pencil")
    pencil = A.make_pencil(collection=set_coll)
    A.grip(rig, pencil, "R")

    # 4. the concept already on the paper: first canal bank + field grid (static ink)
    z = desk_top + 0.0008
    def canal(off, x0=-0.035, x1=0.075, y0=-0.455):
        return [Vector((x0 + (x1 - x0) * t, y0 + off + 0.018 * math.sin(t * math.pi * 1.6), z)) for t in [i / 24 for i in range(25)]]
    A._ink_curve("SIO_sketch_bank_A", canal(0.0), 0, 0, set_coll).data.bevel_factor_end = 1.0
    sk = bpy.data.objects["SIO_sketch_bank_A"].data
    sk.animation_data_clear(); sk.bevel_factor_end = 1.0
    for i, xx in enumerate((-0.02, 0.015, 0.05)):
        o = A._ink_curve(f"SIO_sketch_field_{i}", [Vector((xx, -0.505, z)), Vector((xx + 0.012, -0.485, z))], 0, 0, set_coll)
        o.data.animation_data_clear(); o.data.bevel_factor_end = 1.0

    # 5. animation: draw the second canal bank, then a sluice-gate tick
    rig.animation_data_create()
    key_bones = ["torso", "chest", "foot_ik.L", "foot_ik.R", "hand_ik.L"]
    A.key_pose(rig, key_bones, F0)
    strokes = [canal(0.022), [Vector((0.028, -0.452, z)), Vector((0.030, -0.420, z))]]
    last, inks = A.draw_strokes(rig, pencil, strokes, frame_start=F0 + 2, fps=FPS, speed=0.075, lift=0.010,
                                hover_frames=5, side="R", ink_collection=set_coll, surface_z=z)
    A.look_follow(rig, lambda f: (sc.frame_set(f), pencil.matrix_world.translation.copy())[1] + Vector((0, 0.02, 0)),
                  F0, F1, strength=0.5, lag=4, noise_deg=0.8, step=2)
    A.breathe(rig, F0, F1)
    sc.frame_set(F0)

    # 6. cameras
    cams = lights_and_cameras()
    sc.frame_set(45)
    eyes = (R.bone_head(rig, "DEF-eye.L") + R.bone_head(rig, "DEF-eye.R")) / 2
    cams_def = {
        "CAM_anim":  ((1.05, -1.75, 1.42), (0.0, -0.30, 1.02), 50),
        "CAM_front": ((0.0, -2.6, 1.20), (0.0, -0.1, 0.95), 50),
        "CAM_side":  ((-2.4, -0.25, 1.15), (0.0, -0.25, 0.95), 50),
        "CAM_face":  ((eyes.x + 0.36, eyes.y - 0.80, eyes.z - 0.13), (eyes.x, eyes.y + 0.02, eyes.z + 0.015), 85),
    }
    for n, (l, t, lens) in cams_def.items():
        c = bpy.data.objects.get(n)
        if not c:
            d = bpy.data.cameras.new(n); d.lens = lens; d.dof.use_dof = True; d.dof.aperture_fstop = 2.8
            c = bpy.data.objects.new(n, d); sc.collection.objects.link(c)
        c.location = l; c.rotation_euler = (Vector(t) - Vector(l)).to_track_quat('-Z', 'Y').to_euler()
        c.data.dof.focus_distance = (Vector(t) - Vector(l)).length
    sc.camera = bpy.data.objects["CAM_anim"]

    path = os.path.join(OUT, "poc_engineer_drawing.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("saved", path, "strokes end frame", last)
    if RENDER:
        render_all()
    return ch


def render_all():
    sc = bpy.context.scene
    RD.setup("cinematic", sc, FPS)
    for cam, f in (("CAM_front", 40), ("CAM_side", 40), ("CAM_face", 40)):
        sc.frame_set(f)
        RD.still(os.path.join(OUT, f"{cam.lower()}.png"), cam, sc)
    RD.setup("preview", sc, FPS)
    sc.render.resolution_percentage = 50
    sc.camera = bpy.data.objects["CAM_anim"]
    RD.animation_preview(os.path.join(OUT, "poc_engineer_drawing_3s.mp4"), F0, F1, sc)


if __name__ == "__main__" or "__file__" not in dir():
    main()
