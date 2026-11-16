"""Rigify control helpers: world-space control placement, IK/FK, hand poses, sitting, look-at.

All functions act on the generated Rigify rig (MPFB 'rigify.human'); the character faces -Y.
"""
import math
import bpy
from mathutils import Vector, Matrix, Quaternion, Euler

SIDES = ("L", "R")


def update():
    bpy.context.view_layer.update()


def reset(rig):
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)
    update()


def world(rig, bone):
    return rig.matrix_world @ rig.pose.bones[bone].matrix


def set_world(rig, bone, loc=None, rot=None):
    """Place a control in world space. rot: Quaternion/Matrix3 in world space (None keeps current)."""
    pb = rig.pose.bones[bone]
    M = world(rig, bone)
    l, r, s = M.decompose()
    if loc is not None:
        l = Vector(loc)
    if rot is not None:
        r = rot.to_quaternion() if hasattr(rot, "to_quaternion") else rot
    pb.matrix = rig.matrix_world.inverted() @ Matrix.LocRotScale(l, r, s)
    update()


def rotate_world(rig, bone, axis, deg, pivot=None):
    pb = rig.pose.bones[bone]
    M = world(rig, bone)
    p = M.translation if pivot is None else Vector(pivot)
    R = Matrix.Translation(p) @ Matrix.Rotation(math.radians(deg), 4, Vector(axis)) @ Matrix.Translation(-p)
    pb.matrix = rig.matrix_world.inverted() @ (R @ M)
    update()


def set_ik(rig, limb="arm", side="R", ik=True):
    parent = ("upper_arm_parent." if limb == "arm" else "thigh_parent.") + side
    rig.pose.bones[parent]["IK_FK"] = 0.0 if ik else 1.0
    update()


# ------------------------------------------------------------------ hands
FINGERS = ("f_index", "f_middle", "f_ring", "f_pinky")

HAND_POSES = {
    #             (index, middle, ring, pinky) curl degrees per phalanx, thumb (01,02,03)
    "relaxed":    dict(curl=(18, 24, 28, 32), thumb=(5, 10, 10), spread=4),
    "rest_flat":  dict(curl=(6, 8, 10, 12), thumb=(0, 5, 5), spread=3),
    "pencil":     dict(curl=(22, 52, 62, 70), thumb=(18, 22, 18), spread=-2, index_mid=(28, 20)),
    "point":      dict(curl=(0, 75, 80, 85), thumb=(20, 35, 25), spread=0),
    "fist":       dict(curl=(80, 85, 85, 85), thumb=(25, 40, 30), spread=0),
}


def hand_pose(rig, side, name):
    """Curl fingers with the Rigify finger controls (local X = curl)."""
    P = HAND_POSES[name]
    for f, c in zip(FINGERS, P["curl"]):
        for i, seg in enumerate(("01", "02", "03")):
            b = rig.pose.bones.get(f"{f}.{seg}.{side}")
            if not b:
                continue
            ang = c
            if f == "f_index" and "index_mid" in P and i > 0:
                ang = P["index_mid"][i - 1]
            b.rotation_mode = 'XYZ'
            b.rotation_euler = (math.radians(ang), 0, 0)
        m = rig.pose.bones.get(f"{f}.01_master.{side}")
        if m:
            m.rotation_mode = 'XYZ'
            sp = P["spread"] * (FINGERS.index(f) - 1.5)
            m.rotation_euler = (0, 0, math.radians(sp if side == "L" else -sp))
    for i, seg in enumerate(("01", "02", "03")):
        b = rig.pose.bones.get(f"thumb.{seg}.{side}")
        if b:
            b.rotation_mode = 'XYZ'
            b.rotation_euler = (math.radians(P["thumb"][i]), 0, 0)
    update()


def bone_head(rig, name):
    return rig.matrix_world @ rig.pose.bones[name].head


def bone_tail(rig, name):
    return rig.matrix_world @ rig.pose.bones[name].tail


# ------------------------------------------------------------------ body
def sit(rig, seat_height, feet_forward=0.42, feet_apart=0.11, lean_deg=8):
    """Seated pose with IK legs: lower the torso to the seat, plant the feet in front."""
    reset_body = ("torso", "chest", "hips", "foot_ik.L", "foot_ik.R")
    for b in reset_body:
        pb = rig.pose.bones[b]; pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.rotation_euler = (0, 0, 0)
    update()
    hip = (bone_head(rig, "DEF-thigh.L") + bone_head(rig, "DEF-thigh.R")) / 2
    drop = hip.z - (seat_height + 0.09)
    t = world(rig, "torso").translation
    set_world(rig, "torso", loc=(t.x, t.y + 0.04, t.z - drop))
    for s, sx in (("L", 1), ("R", -1)):
        f = world(rig, f"foot_ik.{s}").translation
        set_world(rig, f"foot_ik.{s}", loc=(sx * feet_apart, f.y - feet_forward, f.z))
        set_ik(rig, "leg", s, True)
    rotate_world(rig, "chest", (1, 0, 0), -lean_deg)
    update()


def look_quat(rig, target, base=None):
    """World rotation for the head control so the face (-Y in rest) points at target."""
    hm = world(rig, "head")
    eye = (bone_head(rig, "DEF-eye.L") + bone_head(rig, "DEF-eye.R")) / 2 if "DEF-eye.L" in rig.pose.bones else hm.translation
    cur_fwd = (base or hm).to_3x3() @ (rig.matrix_world.to_3x3().inverted() @ Vector((0, -1, 0))).normalized()
    want = (Vector(target) - eye).normalized()
    return want, cur_fwd


# ------------------------------------------------------------------ v2: anatomy-aware seated pose + face
def offset_world(rig, bone, delta):
    """Translate a control by a world-space vector (keeps rotation)."""
    M = world(rig, bone)
    set_world(rig, bone, loc=M.translation + Vector(delta))


def sit_natural(rig, seat_height, seat_y=0.06, feet=((0.13, -0.40), (-0.12, -0.36)), pelvis_tilt=4,
                spine_lean=(5, 7), shoulder_drop=4, forward=False):
    """Relaxed working posture: pelvis on the seat with a slight backward tilt, the spine bending gradually
    forward (lower + upper), shoulders dropped/forward a little, feet flat and slightly asymmetric.
    The lean comes from the spine so the neck can stay moderate (avoids the stretched-neck look)."""
    for b in ("torso", "chest", "hips", "foot_ik.L", "foot_ik.R", "shoulder.L", "shoulder.R"):
        pb = rig.pose.bones[b]; pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0)
    for b in ("spine_fk", "spine_fk.001", "spine_fk.002", "spine_fk.003", "tweak_spine.001", "tweak_spine.002"):
        if b in rig.pose.bones:
            rig.pose.bones[b].rotation_quaternion = (1, 0, 0, 0)
    update()
    hip = (bone_head(rig, "DEF-thigh.L") + bone_head(rig, "DEF-thigh.R")) / 2
    t = world(rig, "torso").translation
    set_world(rig, "torso", loc=(t.x, t.y + (seat_y - hip.y), t.z - (hip.z - (seat_height + 0.085))))
    sg = 1 if forward else -1
    # NOTE v1-v2.2 used forward=False, which (rotation about +X) tilts the trunk BACK; kept for reproducibility.
    # forward=True: positive rotation about +X moves the top of the spine toward -Y (toward the desk).
    rotate_world(rig, "hips", (1, 0, 0), pelvis_tilt if not forward else -pelvis_tilt)
    for (fx, fy), s in zip(feet, ("L", "R")):
        f = world(rig, f"foot_ik.{s}").translation
        set_world(rig, f"foot_ik.{s}", loc=(fx, fy, f.z))
        set_ik(rig, "leg", s, True)
    rotate_world(rig, "torso", (1, 0, 0), sg * spine_lean[0])          # hinge at the hips (lower back)
    rotate_world(rig, "chest", (1, 0, 0), sg * spine_lean[1])          # upper back
    for s, sg in (("L", 1), ("R", -1)):
        rotate_world(rig, f"shoulder.{s}", (0, 1, 0), sg * shoulder_drop)   # drop
        rotate_world(rig, f"shoulder.{s}", (0, 0, 1), -sg * 3)              # roll slightly forward
    update()


def arm_pole(rig, side, out=0.25, back=0.15, down=0.10):
    """Place the IK elbow pole outward/back/down of the elbow so elbows point naturally (not up/inward)."""
    pb = rig.pose.bones[f"upper_arm_parent.{side}"]
    pb["pole_vector"] = True
    update()
    elbow = bone_tail(rig, f"DEF-upper_arm.{side}.001") if f"DEF-upper_arm.{side}.001" in rig.pose.bones else bone_head(rig, f"DEF-forearm.{side}")
    sx = 1 if side == "L" else -1
    set_world(rig, f"upper_arm_ik_target.{side}", loc=elbow + Vector((sx * out, back, -down)))


# facial expressions as small world offsets (metres, character faces -Y), applied on top of the rest face
EXPRESSIONS = {
    "neutral": {},
    "focused": {
        # brows drawn slightly down and toward the nose; lower lids raised a touch (concentration)
        "brow.T.L.001": (-0.0008, 0, -0.0012), "brow.T.L.002": (-0.0006, 0, -0.0014), "brow.T.L.003": (0, 0, -0.0008),
        "brow.T.R.001": (0.0008, 0, -0.0012), "brow.T.R.002": (0.0006, 0, -0.0014), "brow.T.R.003": (0, 0, -0.0008),
        "brow.B.L.001": (-0.0005, 0, -0.0009), "brow.B.L.002": (0, 0, -0.0009),
        "brow.B.R.001": (0.0005, 0, -0.0009), "brow.B.R.002": (0, 0, -0.0009),
        "lid.B.L.002": (0, 0, 0.0009), "lid.B.R.002": (0, 0, 0.0009),
        "lip.T": (0, 0, -0.0003), "lip.B": (0, 0, 0.0004),               # lips gently pressed
    },
}


def expression(rig, name="focused", amount=1.0):
    for b, d in EXPRESSIONS[name].items():
        if b in rig.pose.bones:
            offset_world(rig, b, Vector(d) * amount)


# ------------------------------------------------------------------ v2.2: contact checks (hands vs a table top)
def _hand_vertex_sets(body):
    names = {g.index: g.name for g in body.vertex_groups}
    skin = body.vertex_groups["body"].index if "body" in body.vertex_groups else None
    sets = {"R": [], "L": []}
    for v in body.data.vertices:
        if skin is not None and not any(g.group == skin for g in v.groups):
            continue                       # skip MPFB helper geometry (hidden by masks, but weighted to the hands)
        gs = [(g.weight, names[g.group]) for g in v.groups if names[g.group].startswith("DEF-")]
        if gs:
            n = max(gs)[1]
            if any(k in n for k in ("hand", "f_", "thumb", "palm")):
                sets["R" if ".R" in n else "L"].append(v.index)
    return sets


def hand_contact_depth(body, side, top_z, footprint):
    """Deepest penetration (m) of the hand mesh below a table top inside footprint=(xmin,xmax,ymin,ymax).
    Mask modifiers are bypassed during the measurement so vertex indices stay 1:1."""
    import numpy as np
    masks = [m for m in body.modifiers if m.type == 'MASK' and m.show_viewport]
    for m in masks:
        m.show_viewport = False
    try:
        dg = bpy.context.evaluated_depsgraph_get()
        ev = body.evaluated_get(dg); me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", co); ev.to_mesh_clear()
    finally:
        for m in masks:
            m.show_viewport = True
    W = np.array(body.matrix_world)
    P = co.reshape(-1, 3) @ W[:3, :3].T + W[:3, 3]
    key = "_sio_hand_sets"
    sets = _hand_vertex_sets(body)
    Q = P[sets[side]]
    x0, x1, y0, y1 = footprint
    inb = (Q[:, 0] > x0) & (Q[:, 0] < x1) & (Q[:, 1] > y0) & (Q[:, 1] < y1) & (Q[:, 2] > top_z - 0.08)
    if not inb.any():
        return 0.0
    return float(max(0.0, (top_z - Q[inb, 2]).max()))


def rest_hand_on_table(rig, body, side, top_z, footprint, clearance=0.0015, iters=4):
    """Lift a resting hand (IK) until no part of it is below the table top."""
    for _ in range(iters):
        d = hand_contact_depth(body, side, top_z, footprint)
        if d <= 0.0:
            break
        offset_world(rig, f"hand_ik.{side}", (0, 0, d + clearance))
    return hand_contact_depth(body, side, top_z, footprint)


def lay_hand_flat(rig, body, side, top_z, footprint, finger_drop=0.15, clearance=0.001):
    """Resting hand on a table: level the palm (pitch + roll from the actual finger geometry), bring the thumb
    into the palm plane, then make sure nothing is below the table top. Use after hand_pose(..., "rest_flat")."""
    s = side
    def tips():
        return [bone_tail(rig, f"DEF-{b}.{s}") for b in ("f_index.03", "f_middle.03", "f_ring.03", "f_pinky.03")]
    for _ in range(3):
        w = bone_head(rig, f"DEF-hand.{s}"); m = sum(tips(), Vector()) / 4
        v = m - w
        target = (Vector((v.x, v.y, 0)).normalized() * v.length + Vector((0, 0, -finger_drop * v.length))).normalized()
        ax, ang = v.normalized().rotation_difference(target).to_axis_angle()
        rotate_world(rig, f"hand_ik.{s}", ax, math.degrees(ang))
        a = bone_head(rig, f"DEF-f_index.01.{s}") - bone_head(rig, f"DEF-f_pinky.01.{s}")
        roll = math.degrees(math.atan2(a.z, Vector((a.x, a.y, 0)).length))
        fwd = (sum(tips(), Vector()) / 4 - bone_head(rig, f"DEF-hand.{s}")).normalized()
        rotate_world(rig, f"hand_ik.{s}", fwd, roll if s == "L" else -roll)
    t = rig.pose.bones[f"thumb.01.{s}"]; t.rotation_mode = 'XYZ'
    goal = tips()[0].z + 0.005; best = None
    for ax_ in range(-50, 51, 10):
        for az in range(-50, 51, 10):
            t.rotation_euler = (math.radians(ax_), 0, math.radians(az)); update()
            z = bone_tail(rig, f"DEF-thumb.03.{s}").z
            if best is None or abs(z - goal) < best[0]:
                best = (abs(z - goal), ax_, az)
    t.rotation_euler = (math.radians(best[1]), 0, math.radians(best[2])); update()
    # rest on the surface: lowest point of the hand 'clearance' above the top
    for _ in range(4):
        d = hand_contact_depth(body, s, top_z, footprint)
        if d > 0:
            offset_world(rig, f"hand_ik.{s}", (0, 0, d + clearance))
        else:
            break
    return hand_contact_depth(body, s, top_z, footprint)


# ------------------------------------------------------------------ v2.3: rigid skull skin
def rigid_skull(body, hair_preset, head="DEF-spine.006", neck=("DEF-spine.005", "DEF-spine.004")):
    """MPFB weights the skin at the back of the skull partly to the neck (~20 %), so when the head bows the
    occipital skin lags behind the skull and head-parented hair sinks into it. Move the neck share of every
    scalp vertex onto the head bone, weighted by the hair region (soft taper at the nape)."""
    from mathutils import Vector
    from . import hair, util
    L = hair.landmarks(body)
    H = util.load_preset("hair", hair_preset)
    co = util.rest_coords(body)
    vg = {g.name: g for g in body.vertex_groups}
    gh = vg[head]; gn = [vg[n] for n in neck if n in vg]
    idx = {g.index: g for g in [gh] + gn}
    changed = 0
    for v in body.data.vertices:
        c = co[v.index]
        if c[2] < L["ear_bot"] - 0.08 or c[1] < L["ear_front"]:
            continue
        f = hair.region_scalp(Vector(c), L, H["region"])
        if f <= 0.0:
            continue
        w = {g.group: g.weight for g in v.groups if g.group in idx}
        moved = sum(w.get(g.index, 0.0) for g in gn) * f
        if moved < 1e-4:
            continue
        for g in gn:
            if g.index in w:
                g.add([v.index], w[g.index] * (1 - f), 'REPLACE')
        gh.add([v.index], w.get(gh.index, 0.0) + moved, 'REPLACE')
        changed += 1
    return changed
