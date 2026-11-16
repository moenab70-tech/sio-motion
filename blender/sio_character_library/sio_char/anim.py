"""Procedural animation utilities for Rigify characters (no manual bone rotation per frame).

Main pieces
  make_pencil()                 hexagonal pencil, origin at the graphite tip, +Z toward the eraser
  grip(rig, pencil, side)       place the pencil between thumb and index (along the index finger) and parent it to the hand
  draw_strokes(...)             key the IK hand so the pencil TIP lands exactly on every stroke point (lifts between strokes),
                                and build an ink curve that is revealed in sync with the tip
  look_follow(...)              head (and a little neck) track a moving target with lag + subtle noise
  breathe(...)                  chest breathing cycle
  stash(rig, name)              push the current action to the NLA as a reusable strip
"""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix, Quaternion
from . import rig as R


# ------------------------------------------------------------------ props
def make_pencil(name="SIO_pencil", length=0.175, radius=0.0036, collection=None):
    if bpy.data.objects.get(name):
        return bpy.data.objects[name]
    bm = bmesh.new()
    cone = 0.022
    rings = [(0.0, 0.0002), (0.006, 0.0011), (cone, radius), (length - 0.012, radius), (length - 0.0115, radius * 0.97), (length, radius * 0.97)]
    prev = None
    verts_rings = []
    for z, r in rings:
        ring = [bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in [i * math.pi / 3 for i in range(6)]]
        verts_rings.append(ring)
    for a, b in zip(verts_rings[:-1], verts_rings[1:]):
        for i in range(6):
            bm.faces.new((a[i], a[(i + 1) % 6], b[(i + 1) % 6], b[i]))
    bm.faces.new(list(reversed(verts_rings[0])))
    bm.faces.new(verts_rings[-1])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    def mat(n, c, rough=0.5, metal=0.0):
        m = bpy.data.materials.get(n) or bpy.data.materials.new(n)
        m.use_nodes = True
        b = next(x for x in m.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
        b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
        return m
    for m in (mat("SIO_graphite", (0.03, 0.03, 0.035), 0.35, 0.3), mat("SIO_wood", (0.78, 0.58, 0.38), 0.6),
              mat("SIO_pencil_paint", (0.95, 0.72, 0.08), 0.35), mat("SIO_ferrule", (0.75, 0.72, 0.65), 0.25, 1.0),
              mat("SIO_eraser", (0.85, 0.42, 0.42), 0.8)):
        me.materials.append(m)
    for p in me.polygons:
        z = p.center.z
        p.material_index = 0 if z < 0.006 else 1 if z < cone else 2 if z < length - 0.012 else 3 if z < length - 0.0005 else 4
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    return ob


def make_paper(name="SIO_paper", center=(0, -0.4, 0.789), size=(0.297, 0.21), rot_z=0.0, collection=None):
    if bpy.data.objects.get(name):
        return bpy.data.objects[name]
    bpy.ops.mesh.primitive_plane_add(size=1, location=center)
    ob = bpy.context.active_object; ob.name = name
    ob.scale = (size[0], size[1], 1); ob.rotation_euler.z = rot_z
    m = bpy.data.materials.get("SIO_paper") or bpy.data.materials.new("SIO_paper"); m.use_nodes = True
    b = next(x for x in m.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (0.93, 0.92, 0.88, 1); b.inputs["Roughness"].default_value = 0.85
    ob.data.materials.append(m)
    if collection:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        collection.objects.link(ob)
    return ob


# ------------------------------------------------------------------ grip
def grip(rig, pencil, side="R", tip_out=0.028, tilt_to_thumb=0.25, mode="index", web_lift=0.014, pinch_mix=0.5):
    """Place the pencil in the hand and parent it to the hand deform bone.

    mode="index" (v1/v2): pencil along the proximal index phalanx.
    mode="web"   (v2.1): tripod grip - the pencil is pinched between the index pad and the thumb pad and rests
                 on the web between thumb and index, the eraser end rising above the back of the hand
                 (no part of the shaft runs through the palm).
    Returns the tip offset in hand-control space (used by draw_strokes to land the tip exactly)."""
    s = side
    i1, i3 = R.bone_head(rig, f"DEF-f_index.01.{s}"), R.bone_tail(rig, f"DEF-f_index.03.{s}")
    t1, t3 = R.bone_head(rig, f"DEF-thumb.01.{s}"), R.bone_tail(rig, f"DEF-thumb.03.{s}")
    m1 = R.bone_head(rig, f"DEF-f_middle.01.{s}")
    p1 = R.bone_head(rig, f"DEF-f_pinky.01.{s}")
    i2 = R.bone_head(rig, f"DEF-f_index.02.{s}")
    w2 = R.bone_head(rig, f"DEF-hand.{s}") if f"DEF-hand.{s}" in rig.pose.bones else i1
    if mode == "web":
        pinch = i3.lerp(t3, pinch_mix)                     # between the index and thumb pads
        # back of the hand: normal of the palm plane, oriented away from the thumb (which sits on the palm side)
        dorsal = (i1 - p1).cross(m1 - w2).normalized()
        if dorsal.dot(t3 - (i1 + p1 + w2) / 3) > 0:
            dorsal = -dorsal
        web = (i1 * 0.55 + t1 * 0.45) + dorsal * web_lift  # rests on the thumb-index web, above the skin
        axis = (pinch - web).normalized()                  # toward the tip
    else:
        # writing grip: the pencil runs along the proximal index phalanx and back over the thumb web
        axis = ((i2 - i1).normalized() * 0.7 + (i1 - w2).normalized() * 0.3).normalized()
        pinch = (i3 * 0.65 + t3 * 0.35)                     # where index tip and thumb meet
        axis = (axis + (t3 - i3).normalized() * tilt_to_thumb).normalized()
    tip = pinch + axis * tip_out
    up = (i1 - m1).normalized()
    z = -axis                                               # pencil +Z points back toward the eraser
    x = up.cross(z).normalized(); y = z.cross(x)
    M = Matrix((x, y, z)).transposed().to_4x4(); M.translation = tip
    pencil.parent = None
    pencil.matrix_world = M
    bone = f"DEF-hand.{s}" if f"DEF-hand.{s}" in rig.pose.bones else f"ORG-hand.{s}"
    pencil.parent = rig; pencil.parent_type = 'BONE'; pencil.parent_bone = bone
    pb = rig.pose.bones[bone]
    bone_world = rig.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))
    pencil.matrix_parent_inverse = bone_world.inverted()
    pencil.matrix_basis = M
    R.update()
    hand = R.world(rig, f"hand_ik.{s}")
    return hand.inverted() @ tip                            # tip in hand-control space


def tip_world(pencil):
    return pencil.matrix_world.translation.copy()


# ------------------------------------------------------------------ strokes
def _key(pb, frame):
    pb.keyframe_insert("location", frame=frame)
    pb.keyframe_insert("rotation_quaternion", frame=frame)


def draw_strokes(rig, pencil, strokes, frame_start, fps=30, speed=0.06, lift=0.012, hover_frames=4,
                 side="R", ink_collection=None, surface_z=None, ink_name="SIO_ink"):
    """strokes: list of point lists (world). The hand keeps its current orientation (plus a tiny wrist roll),
    and is positioned every frame so the pencil tip is exactly on the stroke (or lifted between strokes).
    Returns (last_frame, ink_objects)."""
    hb = rig.pose.bones[f"hand_ik.{side}"]
    Hm = R.world(rig, f"hand_ik.{side}")
    rot0 = Hm.to_quaternion()
    tip_local = Hm.inverted() @ tip_world(pencil)
    f = frame_start
    inks = []

    def place(pt, frame, roll=0.0):
        q = rot0 @ Quaternion((0, 1, 0), roll) if roll else rot0
        loc = Vector(pt) - (q.to_matrix() @ (tip_local))
        R.set_world(rig, f"hand_ik.{side}", loc=loc, rot=q)
        _key(hb, frame)

    for si, pts in enumerate(strokes):
        pts = [Vector(p) for p in pts]
        if surface_z is not None:
            pts = [Vector((p.x, p.y, surface_z)) for p in pts]
        # approach: hover above the first point
        place(pts[0] + Vector((0, 0, lift)), f); f += hover_frames
        place(pts[0], f)
        start = f
        # resample by speed (m/s)
        seg = [0.0]
        for a, b in zip(pts[:-1], pts[1:]):
            seg.append(seg[-1] + (b - a).length)
        total = seg[-1]
        n = max(2, int(round(total / speed * fps)))
        for k in range(1, n + 1):
            d = total * k / n
            j = max(i for i in range(len(seg)) if seg[i] <= d) if d < total else len(seg) - 2
            j = min(j, len(pts) - 2)
            t = (d - seg[j]) / max(1e-6, seg[j + 1] - seg[j])
            p = pts[j].lerp(pts[j + 1], min(1, t))
            place(p, f + k, roll=0.04 * math.sin(k * 0.4))
        f += n
        inks.append(_ink_curve(f"{ink_name}_{si:02d}", pts, start, f, ink_collection))
        place(pts[-1] + Vector((0, 0, lift)), f + hover_frames); f += hover_frames
    # smooth interpolation for the in-between keys
    act = rig.animation_data.action if rig.animation_data else None
    _set_interp(act, f"hand_ik.{side}", 'LINEAR')
    return f, inks


def _ink_curve(name, pts, f0, f1, coll):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old)
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z + 0.0004, 1)
    cu.bevel_depth = 0.00045; cu.bevel_resolution = 1
    cu.use_fill_caps = True
    m = bpy.data.materials.get("SIO_ink") or bpy.data.materials.new("SIO_ink"); m.use_nodes = True
    b = next(x for x in m.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (0.06, 0.06, 0.07, 1); b.inputs["Roughness"].default_value = 0.6
    cu.materials.append(m)
    ob = bpy.data.objects.new(name, cu)
    (coll or bpy.context.scene.collection).objects.link(ob)
    cu.bevel_factor_end = 0.0; cu.keyframe_insert("bevel_factor_end", frame=f0)
    cu.bevel_factor_end = 1.0; cu.keyframe_insert("bevel_factor_end", frame=f1)
    _set_interp(cu.animation_data.action, None, 'LINEAR')
    return ob


def _fcurves(action):
    """Blender 5 layered actions and legacy actions."""
    if action is None:
        return []
    if hasattr(action, "layers") and action.layers:
        out = []
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out.extend(cb.fcurves)
        return out
    return list(getattr(action, "fcurves", []))


def _set_interp(action, bone, mode):
    for fc in _fcurves(action):
        if bone is None or f'"{bone}"' in fc.data_path:
            for kp in fc.keyframe_points:
                kp.interpolation = mode


# ------------------------------------------------------------------ head / body
def look_follow(rig, target_fn, f0, f1, strength=0.85, lag=3, noise_deg=1.2, seed=2, step=1, max_deg=38, neck_share=0.25):
    """Rotate head (and 30% neck) so the face tracks target_fn(frame) -> world point."""
    rng = random.Random(seed)
    head = rig.pose.bones["head"]; neck = rig.pose.bones["neck"]
    rest_fwd = Vector((0, -1, 0))
    nx = [rng.uniform(-1, 1) for _ in range(8)]
    for fr in range(f0, f1 + 1, step):
        bpy.context.scene.frame_set(fr)
        head.rotation_quaternion = (1, 0, 0, 0); neck.rotation_quaternion = (1, 0, 0, 0)
        R.update()
        tgt = Vector(target_fn(max(f0, fr - lag)))
        eye = (R.bone_head(rig, "DEF-eye.L") + R.bone_head(rig, "DEF-eye.R")) / 2
        Hw = R.world(rig, "head")
        fwd = (Hw.to_3x3() @ rig.pose.bones["head"].bone.matrix_local.to_3x3().inverted() @ rig.matrix_world.to_3x3().inverted() @ rest_fwd).normalized()
        want = (tgt - eye).normalized()
        q = fwd.rotation_difference(want)
        ax, ang = q.to_axis_angle()
        ang = min(ang, math.radians(max_deg))
        t = fr * 0.06
        wob = math.radians(noise_deg) * math.sin(t * 1.7 + nx[0]) * math.sin(t * 0.63 + nx[1])
        R.rotate_world(rig, "neck", ax, math.degrees(ang) * strength * neck_share)
        R.rotate_world(rig, "head", ax, math.degrees(ang) * strength * (1 - neck_share))
        R.rotate_world(rig, "head", (0, 0, 1), math.degrees(wob))
        head.keyframe_insert("rotation_quaternion", frame=fr)
        neck.keyframe_insert("rotation_quaternion", frame=fr)


def breathe(rig, f0, f1, period_s=3.6, fps=30, amount_deg=1.2):
    chest = rig.pose.bones["chest"]
    base = chest.rotation_quaternion.copy()
    for fr in range(f0, f1 + 1, 3):
        a = math.radians(amount_deg) * math.sin(2 * math.pi * (fr - f0) / (period_s * fps))
        chest.rotation_quaternion = base @ Quaternion((1, 0, 0), -a)
        chest.keyframe_insert("rotation_quaternion", frame=fr)
    chest.rotation_quaternion = base


def key_pose(rig, bones, frame):
    for b in bones:
        pb = rig.pose.bones[b]
        pb.keyframe_insert("location", frame=frame)
        if pb.rotation_mode == 'QUATERNION':
            pb.keyframe_insert("rotation_quaternion", frame=frame)
        else:
            pb.keyframe_insert("rotation_euler", frame=frame)


def stash(rig, name):
    """Rename the active action and push it to the NLA so it can be reused / layered."""
    ad = rig.animation_data
    if not ad or not ad.action:
        return None
    act = ad.action; act.name = name; act.use_fake_user = True
    tr = ad.nla_tracks.new(); tr.name = name
    tr.strips.new(name, int(act.frame_range[0]), act)
    ad.action = None
    return act


# ------------------------------------------------------------------ v2: eyes
def eyes_follow(rig, target_fn, f0, f1, lag=2, step=2, distance=0.45):
    """Move the Rigify 'eye_common' target so both eyes track target_fn(frame); lids follow (lid_follow)."""
    pb = rig.pose.bones["eye_common"]
    for fr in range(f0, f1 + 1, step):
        bpy.context.scene.frame_set(fr)
        pb.location = (0, 0, 0); R.update()
        eye = (R.bone_head(rig, "DEF-eye.L") + R.bone_head(rig, "DEF-eye.R")) / 2
        tgt = Vector(target_fn(max(f0, fr - lag)))
        d = (tgt - eye)
        R.set_world(rig, "eye_common", loc=eye + d.normalized() * min(distance, d.length))
        pb.keyframe_insert("location", frame=fr)


def blink(rig, frame, close=2, hold=1, open_=4, amount=0.95):
    """One natural blink: the upper-lid controls drop to the lower lid fast (close), hold, open slower.
    Keys only lid.T.* location, on top of whatever expression offset they already have."""
    sc = bpy.context.scene
    for t in [b.name for b in rig.pose.bones if b.name.startswith("lid.T.")]:
        pb = rig.pose.bones[t]
        side = "L" if ".L" in t else "R"
        sc.frame_set(frame); R.update()
        base = pb.location.copy()
        top = R.bone_head(rig, t)
        bot = R.bone_head(rig, f"lid.B.{side}.002")
        drop_world = Vector((0, 0, (bot.z - top.z) * amount))
        drop_local = pb.bone.matrix_local.to_3x3().inverted() @ (rig.matrix_world.to_3x3().inverted() @ drop_world)
        for f, k in ((frame, 0.0), (frame + close, 1.0), (frame + close + hold, 1.0), (frame + close + hold + open_, 0.0)):
            pb.location = base + drop_local * k
            pb.keyframe_insert("location", frame=f)
        pb.location = base


def blinks(rig, frames, **kw):
    for f in frames:
        blink(rig, f, **kw)


# ------------------------------------------------------------------ v2.2: writing-hand clearance
def fit_writing_grip(rig, body, pencil, side, surface_point, top_z, footprint, grip_kw, clearance=0.0015,
                     rolls=(0, 4, 8, 12, 16, -4, -8), max_tip_out=0.045, iters=4):
    """Make the writing hand clear the table while the pencil tip stays on surface_point.
    1) roll the hand about the PENCIL AXIS (tip fixed) to lift the curled pinky/ring side;
    2) only if still needed, let the pencil stick out further (capped at max_tip_out).
    The chosen roll is kept in the hand's base rotation (draw_strokes reuses it). Returns (grip kwargs, depth)."""
    kw = dict(grip_kw)
    Hm0 = R.world(rig, f"hand_ik.{side}")

    def place_and_measure(roll_deg):
        R.set_world(rig, f"hand_ik.{side}", loc=Hm0.translation, rot=Hm0.to_quaternion())
        grip(rig, pencil, side, **kw)
        Hm = R.world(rig, f"hand_ik.{side}")
        tip_local = Hm.inverted() @ tip_world(pencil)
        q = Hm.to_quaternion()
        R.set_world(rig, f"hand_ik.{side}", loc=Vector(surface_point) - (q.to_matrix() @ tip_local), rot=q)
        if roll_deg:
            ax = (pencil.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
            R.rotate_world(rig, f"hand_ik.{side}", ax, roll_deg, pivot=tip_world(pencil))
        return R.hand_contact_depth(body, side, top_z, footprint), R.world(rig, f"hand_ik.{side}").to_quaternion()

    best = None
    for _ in range(iters):
        for r in rolls:
            d, q = place_and_measure(r)
            if best is None or d < best[0]:
                best = (d, r, q, dict(kw))
            if d <= 0.0:
                break
        if best[0] <= 0.0 or kw.get("tip_out", 0.028) >= max_tip_out:
            break
        ax = (pencil.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
        kw["tip_out"] = min(max_tip_out, kw.get("tip_out", 0.028) + (best[0] + clearance) / max(0.2, ax.z))
    depth, roll, q, kw = best
    # keep the roll in the base rotation, restore the base position (draw_strokes positions the hand from the tip)
    R.set_world(rig, f"hand_ik.{side}", loc=Hm0.translation, rot=q)
    grip(rig, pencil, side, **kw)
    kw["_roll_deg"] = roll
    return kw, depth
