"""Headless functional test of the installed third-party extensions (EXea Jiggle, Brushstroke Tools).

  Blender -b -P scripts/test_extensions.py
Writes tests/extensions/report.json and a painterly test render. Nothing here touches production files.
"""
import os, sys, json, math, importlib, traceback
import bpy
from mathutils import Vector

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(LIB, "tests", "extensions"); os.makedirs(OUT, exist_ok=True)
report = {"blender": bpy.app.version_string, "background": bpy.app.background}


def fresh():
    bpy.ops.wm.read_homefile(use_empty=True)


# ---------------------------------------------------------------- EXea Jiggle
def test_jiggle():
    r = {}
    fresh()
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, 40
    arm = bpy.data.armatures.new("chain"); ob = bpy.data.objects.new("chain", arm); sc.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    prev = None
    for i in range(4):
        b = arm.edit_bones.new(f"tail.{i:03d}"); b.head = (0, 0, 1 - i * 0.15); b.tail = (0, 0, 1 - (i + 1) * 0.15)
        if prev: b.parent = prev; b.use_connect = True
        prev = b
    bpy.ops.object.mode_set(mode='POSE')
    # drive the object: a quick side move then stop, so secondary motion should overshoot and settle
    for f, x in ((1, 0.0), (10, 0.4), (40, 0.4)):
        ob.location.x = x; ob.keyframe_insert("location", frame=f)
    core = importlib.import_module("bl_ext.user_default.exea_jiggle.core")
    root = ob.pose.bones["tail.000"]
    chain = core.setup_chain(root, 0.85, layer_name="Test")
    r["chain_bones"] = len(chain)
    tip = ob.pose.bones["tail.003"]
    samples = []
    for f in range(1, 41):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        samples.append(round((ob.matrix_world @ tip.tail).x - ob.location.x, 4))
    r["tip_lag_x"] = samples[::5]
    r["secondary_motion"] = max(abs(s) for s in samples) > 0.005
    # bake through the add-on operator (needs pose mode + selected bones; works without a window)
    for pb in ob.pose.bones:
        if hasattr(pb, "select"):
            pb.select = True                     # Blender 5: selection lives on the pose bone
        else:
            pb.bone.select = True
    try:
        with bpy.context.temp_override(object=ob, active_object=ob, selected_pose_bones=list(ob.pose.bones)):
            res = bpy.ops.jiggle.bake()
        act = ob.animation_data.action if ob.animation_data else None
        r["bake"] = str(res)
        r["baked_action"] = act.name if act else None
    except Exception as e:
        r["bake"] = "ERROR " + str(e)
    return r


# ---------------------------------------------------------------- Brushstroke Tools
def test_brushstrokes():
    r = {}
    fresh()
    sc = bpy.context.scene
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, 0.5), segments=48, ring_count=24)
    surf = bpy.context.active_object; surf.name = "paint_surface"
    m = bpy.data.materials.new("surf"); m.use_nodes = True
    next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs["Base Color"].default_value = (0.2, 0.45, 0.35, 1)
    surf.data.materials.append(m)
    before = set(bpy.data.objects)
    with bpy.context.temp_override(object=surf, active_object=surf, selected_objects=[surf]):
        res = bpy.ops.brushstroke_tools.new_brushstrokes(method='SURFACE_FILL')
    new = [o for o in bpy.data.objects if o not in before]
    r["operator"] = str(res)
    # Surface Fill needs flow guide curves: add a few horizontal guides on the sphere (what a user would draw)
    flow = next((o for o in new if o.name.endswith("-FLOW")), None)
    if flow:
        n, K = 6, 16
        flow.data.add_curves([K] * n)
        pts = []
        for i in range(n):
            z = 0.12 + 0.76 * i / (n - 1); rr = math.sqrt(max(0.0, 0.25 - (z - 0.5) ** 2)) + 0.002
            for k in range(K):
                a = -math.pi * 0.9 + 1.8 * math.pi * k / (K - 1)
                pts += [rr * math.cos(a), rr * math.sin(a), z]
        flow.data.attributes["position"].data.foreach_set("vector", pts)
        flow.data.surface = surf
        flow.data.surface_uv_map = surf.data.uv_layers[0].name
        try:
            with bpy.context.temp_override(object=flow, active_object=flow, selected_objects=[flow], selected_editable_objects=[flow]):
                r["snap"] = str(bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST'))
        except Exception as e:
            r["snap"] = "ERROR " + str(e)[:200]
        flow.data.update_tag()
    r["new_objects"] = [(o.name, o.type, [md.type for md in o.modifiers]) for o in new]
    dg = bpy.context.evaluated_depsgraph_get()
    for o in new:
        if o.type == 'CURVES':
            ev = o.evaluated_get(dg)
            r.setdefault("evaluated", []).append((o.name, len(ev.data.curves) if hasattr(ev.data, "curves") else None))
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    cam.location = (0, -2.2, 0.8); cam.rotation_euler = (Vector((0, 0, 0.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", 'SUN')); sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30)); sun.data.energy = 3
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = sc.render.resolution_y = 512
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = os.path.join(OUT, "brushstroke_test.png")
    bpy.ops.render.render(write_still=True)
    r["render"] = sc.render.filepath
    return r


for name, fn in (("exea_jiggle", test_jiggle), ("brushstroke_tools", test_brushstrokes)):
    try:
        report[name] = fn()
    except Exception:
        report[name] = {"error": traceback.format_exc()[-1500:]}
json.dump(report, open(os.path.join(OUT, "report.json"), "w"), indent=2)
print("EXT_REPORT", json.dumps(report))
