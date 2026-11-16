"""Camera shot library for the office (v4 room coordinates, engineer at the desk facing the window, -Y).

Each function creates (or updates) one camera, keys its move over [f0, f1] and returns it.
Shots are a library: the edit picks the strongest ones for the 20 s / 8-shot storyboard.
"""
import math
import bpy
from mathutils import Vector


def _cam(name, lens, fstop=2.8, sensor=36):
    c = bpy.data.objects.get(name)
    if c is None:
        d = bpy.data.cameras.new(name); c = bpy.data.objects.new(name, d)
        coll = bpy.data.collections.get("ENV_cameras") or bpy.data.collections.new("ENV_cameras")
        if coll.name not in [x.name for x in bpy.context.scene.collection.children]:
            bpy.context.scene.collection.children.link(coll)
        coll.objects.link(c)
    c.data.lens = lens; c.data.sensor_width = sensor
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = fstop
    c.data.clip_start = 0.01; c.data.clip_end = 2000
    return c


def _look(c, target):
    c.rotation_euler = (Vector(target) - c.location).to_track_quat('-Z', 'Y').to_euler()


def _target_empty(name, loc=None, parent=None, bone=None):
    e = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if e.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(e)
    e.empty_display_size = 0.03
    if parent is not None:
        mw = e.matrix_world.copy() if loc is None else None
        e.parent = parent
        if bone:
            e.parent_type = 'BONE'; e.parent_bone = bone
        bpy.context.view_layer.update()
        if loc is not None:
            from mathutils import Matrix
            e.matrix_world = Matrix.Translation(loc)
    elif loc is not None:
        e.location = loc
    return e


def _track(c, target_obj, focus=True):
    for con in list(c.constraints):
        c.constraints.remove(con)
    t = c.constraints.new('TRACK_TO'); t.target = target_obj; t.track_axis = 'TRACK_NEGATIVE_Z'; t.up_axis = 'UP_Y'
    if focus:
        c.data.dof.focus_object = target_obj


def _move(c, path, f0, f1, ease=True):
    for i, p in enumerate(path):
        f = round(f0 + (f1 - f0) * i / max(1, len(path) - 1))
        c.location = p; c.keyframe_insert("location", frame=f)
    if c.animation_data and c.animation_data.action and not ease:
        from sio_char.anim import _set_interp
        _set_interp(c.animation_data.action, None, 'LINEAR')


def shot_A_establishing(f0=1, f1=150, target=(0.0, -0.35, 1.0)):
    """Wide: office layout, engineer at the desk, plants, window. Slow lateral dolly + slight push."""
    c = _cam("SHOT_A_establishing", 24, 5.6)
    _track(c, _target_empty("SHOT_A_target", target))
    _move(c, [(3.15, 3.35, 1.75), (2.55, 3.55, 1.68)], f0, f1)
    return c


def shot_B_exterior_in(f0=1, f1=150, head=(0.0, -0.12, 1.25)):
    """From outside the building through the arched window toward the engineer (real geometry -> parallax)."""
    c = _cam("SHOT_B_exterior_in", 35, 8)
    _track(c, _target_empty("SHOT_B_target", head))
    _move(c, [(0.6, -9.0, 2.6), (0.15, -3.2, 1.95), (0.0, -1.45, 1.62)], f0, f1)
    return c


def shot_C_eyes(rig, f0=1, f1=150):
    """Close-up of eyes/upper face, from the window side (low, slightly off-axis), tracks a head-bone target."""
    eyes = (rig.matrix_world @ rig.pose.bones["DEF-eye.L"].head + rig.matrix_world @ rig.pose.bones["DEF-eye.R"].head) / 2
    tgt = _target_empty("SHOT_C_eyes_target", eyes, parent=rig, bone="DEF-spine.006")
    c = _cam("SHOT_C_eyes", 100, 2.0)
    _track(c, tgt)
    _move(c, [(eyes.x + 0.16, eyes.y - 0.62, eyes.z - 0.20), (eyes.x + 0.13, eyes.y - 0.58, eyes.z - 0.19)], f0, f1)
    return c


def shot_D_pencil(pencil, f0=1, f1=150):
    """Macro on the pencil tip and the drawing; target follows the tip."""
    tgt = _target_empty("SHOT_D_tip_target")
    for con in list(tgt.constraints):
        tgt.constraints.remove(con)
    cl = tgt.constraints.new('COPY_LOCATION'); cl.target = pencil
    c = _cam("SHOT_D_pencil", 90, 2.8)
    _track(c, tgt)
    p = pencil.matrix_world.translation
    # low and in front of the tip (the tip points away from the hand toward -Y), slightly to his right:
    # the drawing is in the foreground, the pencil and fingers behind it, the resting left hand out of frame
    _move(c, [(p.x - 0.07, p.y - 0.24, p.z + 0.10), (p.x - 0.06, p.y - 0.21, p.z + 0.09)], f0, f1)
    return c


def shot_E_overhead(desk_center=(0.1, -0.55, 0.79), f0=1, f1=150):
    """Top-down desk shot (ceiling at 3 m); a tiny rotation keeps it alive."""
    c = _cam("SHOT_E_overhead", 30, 5.6)
    for con in list(c.constraints):
        c.constraints.remove(con)
    c.location = (desk_center[0], desk_center[1], 2.35)
    for f, rz in ((f0, 0.0), (f1, math.radians(3))):
        c.rotation_euler = (0, 0, rz); c.keyframe_insert("rotation_euler", frame=f)
    c.keyframe_insert("location", frame=f0)
    c.data.dof.focus_distance = 2.35 - desk_center[2]
    return c


def shot_F_timelapse(f0=1, f1=240, target=(0.05, -0.45, 0.95)):
    """Locked-off medium-wide for the time-passing beat (light, clock, clutter change while the camera holds)."""
    c = _cam("SHOT_F_timelapse", 32, 5.6)
    _track(c, _target_empty("SHOT_F_target", target))
    c.location = (2.25, 1.95, 1.55); c.keyframe_insert("location", frame=f0)
    return c


def shot_G_dawn_reveal(f0=1, f1=150, target=(0.0, -0.4, 0.95)):
    """Slow push from behind the engineer's shoulder toward the bright dawn window."""
    c = _cam("SHOT_G_dawn_reveal", 28, 4)
    _track(c, _target_empty("SHOT_G_target", target))
    _move(c, [(-1.55, 1.75, 1.55), (-1.05, 1.15, 1.45)], f0, f1)
    return c


def all_shots(rig, pencil):
    return dict(A=shot_A_establishing(), B=shot_B_exterior_in(), C=shot_C_eyes(rig), D=shot_D_pencil(pencil),
                E=shot_E_overhead(), F=shot_F_timelapse(), G=shot_G_dawn_reveal())
