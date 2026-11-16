"""Thin, tested wrappers around the third-party extensions that passed review (2026-11-15).

EXea Jiggle 1.1.0 (GPL-3, github.com/asnise/EXeaJiggle) - bone-chain secondary motion.
    Simulation runs in a frame_change_post handler, so it also works in background (-b) renders;
    bake to keyframes for final renders (deterministic, no handler needed).
Brushstroke Tools 1.2.3 (GPL-3, Blender Studio) - painterly geometry-nodes brushstrokes on a surface.

Rejected (not installed): Eye Animation 2.0.0 (expects eye_r/eye_l bones + blink_r/blink_l shape keys;
Rigify/MPFB use eye.R and lid controls -> use anim.eyes_follow / anim.blink instead) and
HiFi Builder 4.6.7 (architecture/GTA-V modding tool that embeds a GTA V character mesh; not usable in production).
"""
import importlib
import bpy


def _ext(mod):
    for k in bpy.context.preferences.addons.keys():
        if k.endswith(mod):
            return importlib.import_module(k)
    raise RuntimeError(f"extension '{mod}' is not enabled")


# ------------------------------------------------------------------ EXea Jiggle
def jiggle_chain(rig, root_bone, falloff=0.85, layer="Secondary", stiffness=None, damping=None, gravity=None):
    """Add jiggle physics to the chain that starts at root_bone. Returns the chain bone names."""
    core = importlib.import_module(_ext("exea_jiggle").__name__ + ".core")
    chain = core.setup_chain(rig.pose.bones[root_bone], falloff, layer_name=layer)
    for pb in chain:
        for key, val in (("jiggle_stiffness", stiffness), ("jiggle_damping", damping), ("jiggle_gravity", gravity)):
            if val is not None and key in pb:
                pb[key] = val
    return [pb.name for pb in chain]


def jiggle_bake(rig, bones, frame_start=None, frame_end=None):
    """Bake the jiggle of `bones` to keyframes (removes the physics constraints). Works headless."""
    sc = bpy.context.scene
    if frame_start is not None:
        sc.frame_start, sc.frame_end = frame_start, frame_end
    bpy.context.view_layer.objects.active = rig
    if rig.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    sel = [rig.pose.bones[b] for b in bones]
    for pb in rig.pose.bones:
        pb.select = pb in sel
    with bpy.context.temp_override(object=rig, active_object=rig, selected_pose_bones=sel):
        res = bpy.ops.jiggle.bake()
    bpy.ops.object.mode_set(mode='OBJECT')
    return res


# ------------------------------------------------------------------ Brushstroke Tools
def brushstrokes(surface, flow_curves, method='SURFACE_FILL'):
    """Painterly strokes on `surface`, following `flow_curves` (list of point lists in world space).
    Returns (brushstrokes_object, flow_object). Strokes are geometry-nodes instances (render in Eevee/Cycles)."""
    before = set(bpy.data.objects)
    with bpy.context.temp_override(object=surface, active_object=surface, selected_objects=[surface]):
        bpy.ops.brushstroke_tools.new_brushstrokes(method=method)
    new = [o for o in bpy.data.objects if o not in before]
    flow = next(o for o in new if o.name.endswith("-FLOW"))
    strokes = next(o for o in new if o.name.endswith("Brushstrokes"))
    K = max(len(c) for c in flow_curves)
    flow.data.add_curves([K] * len(flow_curves))
    inv = flow.matrix_world.inverted()
    pts = []
    for c in flow_curves:
        c = list(c) + [c[-1]] * (K - len(c))
        for p in c:
            q = inv @ p
            pts += [q.x, q.y, q.z]
    flow.data.attributes["position"].data.foreach_set("vector", pts)
    if surface.data.uv_layers:
        flow.data.surface = surface
        flow.data.surface_uv_map = surface.data.uv_layers[0].name
        with bpy.context.temp_override(object=flow, active_object=flow, selected_objects=[flow], selected_editable_objects=[flow]):
            bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST')
    flow.data.update_tag()
    return strokes, flow
