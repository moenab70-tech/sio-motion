"""Multi-session storytelling for the office: persistence across several WORKDAYS (not one sleepless night).

Cues that a new day has started (all switchable per session, applied between cuts):
  - daylight state (afternoon / morning / late afternoon) - never night
  - wall calendar date (12 -> 13 -> 14)
  - the engineer's shirt colour (tinted on the shirt only; trousers unchanged)
  - desk clutter grows only between sessions (clean -> early -> attempts -> late_night)
  - posture: session 3 sits a touch more upright (refreshed, focused - not exhausted)
Collaboration: two colleagues (MPFB presets) stand at the desk looking at the drawing.

    story.setup(ch)            # once: lights, calendar, shirt tint node
    story.apply("S2")          # switch everything to a session
"""
import math
import bpy
from mathutils import Vector
from . import lighting, clutter

lighting.STATES.update({
    "afternoon": dict(hdri="qwantani_afternoon_puresky_2k.hdr", hdri_strength=0.8, hdri_rot=200,
                      sun_el=32, sun_az=25, sun_col=(1.0, 0.93, 0.84), sun_e=5.5,
                      lamp_e=0.0, lamp_col=(1.0, 0.78, 0.52), fill_e=30, fill_col=(1.0, 0.96, 0.92),
                      moon_e=0.0, haze=(0.84, 0.84, 0.82), haze_far=700, vol=0.0, exposure=0.1),
    "morning":   dict(hdri="qwantani_morning_puresky_2k.hdr", hdri_strength=0.8, hdri_rot=150,
                      sun_el=17, sun_az=-30, sun_col=(1.0, 0.89, 0.76), sun_e=6.0,
                      lamp_e=0.0, lamp_col=(1.0, 0.78, 0.52), fill_e=15, fill_col=(0.86, 0.91, 1.0),
                      moon_e=0.0, haze=(0.86, 0.88, 0.92), haze_far=650, vol=0.003, exposure=-0.4),
    "late_afternoon": dict(hdri="qwantani_late_afternoon_puresky_2k.hdr", hdri_strength=0.75, hdri_rot=210,
                      sun_el=13, sun_az=30, sun_col=(1.0, 0.74, 0.50), sun_e=7.0,
                      lamp_e=8.0, lamp_col=(1.0, 0.78, 0.52), fill_e=12, fill_col=(1.0, 0.82, 0.66),
                      moon_e=0.0, haze=(0.94, 0.78, 0.62), haze_far=650, vol=0.0, exposure=-0.3),
})

SESSIONS = {
    "S1": dict(light="afternoon", clutter="early", day=12, shirt="blue", upright=0.0),
    "S2": dict(light="morning", clutter="attempts", day=13, shirt="white", upright=0.0),
    "S3": dict(light="late_afternoon", clutter="late_night", day=14, shirt="navy", upright=4.0),
    "COLLAB": dict(light="late_afternoon", clutter="late_night", day=14, shirt="navy", upright=4.0, collaborators=True),
}
SHIRTS = {"blue": (0.5, 1.0, 1.0), "white": (0.5, 0.12, 1.75), "navy": (0.5, 1.05, 0.62)}   # (hue, sat, value)


# ------------------------------------------------------------------ calendar
def calendar(loc=(-2.385, 2.42, 1.55), facing=(1, 0, 0)):
    """Paper wall calendar (header band + big day number, Latin digits) under the wall clock."""
    if bpy.data.objects.get("STORY_calendar"):
        return bpy.data.objects["STORY_calendar"]
    coll = bpy.data.collections.get("ENV_story") or bpy.data.collections.new("ENV_story")
    if coll.name not in [c.name for c in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(coll)
    root = bpy.data.objects.new("STORY_calendar", None); coll.objects.link(root)
    root.location = loc
    root.rotation_euler = (math.pi / 2, 0, math.atan2(facing[1], facing[0]) + math.pi / 2)

    def mat(name, rgb, rough=0.8):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
        return m
    def plane(name, w, h, z, y, m):
        bpy.ops.mesh.primitive_plane_add(size=1)
        o = bpy.context.active_object; o.name = name; o.scale = (w, h, 1)
        o.location = (0, y, z); o.parent = root
        o.data.materials.append(m)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
        return o
    plane("STORY_cal_sheet", 0.30, 0.40, 0.0, 0.0, mat("STORY_cal_paper", (0.92, 0.91, 0.87)))
    plane("STORY_cal_header", 0.30, 0.08, 0.001, 0.16, mat("STORY_cal_red", (0.55, 0.08, 0.07), 0.6))
    cu = bpy.data.curves.new("STORY_cal_day", 'FONT'); cu.body = "12"; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    cu.size = 0.2; cu.extrude = 0.0005
    t = bpy.data.objects.new("STORY_cal_day", cu); coll.objects.link(t); t.parent = root
    t.location = (0, -0.03, 0.002); cu.materials.append(mat("STORY_cal_ink", (0.05, 0.05, 0.06), 0.7))
    # small date strip under the number (lines suggest the week grid)
    for i in range(3):
        plane(f"STORY_cal_line_{i}", 0.22, 0.004, 0.0015, -0.13 - i * 0.02, mat("STORY_cal_grey", (0.55, 0.55, 0.55)))
    return root


def set_day(n):
    t = bpy.data.objects.get("STORY_cal_day")
    if t:
        t.data.body = str(n)


# ------------------------------------------------------------------ shirt tint (shirt only)
def shirt_tint_setup(ch, waist_z=None):
    suit = next((o for o in ch.parts.values() if "suit" in o.name), None)
    if not suit:
        return None
    m = suit.material_slots[0].material; nt = m.node_tree
    if nt.nodes.get("story_shirt_hsv"):
        return nt.nodes["story_shirt_hsv"]
    tex = next(n for n in nt.nodes if n.type == 'TEX_IMAGE' and "diffuse" in n.name.lower())
    link = tex.outputs["Color"].links[0]; dst = link.to_socket
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.name = "story_shirt_hsv"
    # mask: only above the waist, using rest-shape (Generated) coordinates so it does not slide when seated
    me = suit.data
    zs = [v.co.z for v in me.vertices]; zmin, zmax = min(zs), max(zs)
    if waist_z is None:
        waist_z = zmin + 0.6 * (zmax - zmin)
    t = (waist_z - zmin) / (zmax - zmin)
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = t - 0.01; mr.inputs["From Max"].default_value = t + 0.01
    nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.name = "story_shirt_mix"
    nt.links.new(tex.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(mr.outputs[0], mix.inputs["Factor"]); nt.links.new(tex.outputs["Color"], mix.inputs[6]); nt.links.new(hsv.outputs[0], mix.inputs[7])
    nt.links.new(mix.outputs[2], dst)
    return hsv


def set_shirt(name):
    h = next((m.node_tree.nodes.get("story_shirt_hsv") for m in bpy.data.materials if m.use_nodes and m.node_tree.nodes.get("story_shirt_hsv")), None)
    if h:
        hue, sat, val = SHIRTS[name]
        h.inputs["Hue"].default_value = hue; h.inputs["Saturation"].default_value = sat; h.inputs["Value"].default_value = val


# ------------------------------------------------------------------ posture offset per session
def set_upright(rig, degrees, frame=1):
    """Sit a few degrees more upright for the whole clip (keyed on 'chest' at `frame`, constant)."""
    from sio_char import rig as R
    pb = rig.pose.bones["torso"]
    base = pb.get("story_base_q")
    if base is None:
        pb["story_base_q"] = list(pb.rotation_quaternion); base = pb["story_base_q"]
    pb.rotation_quaternion = base
    R.update()
    if degrees:
        R.rotate_world(rig, "torso", (1, 0, 0), -degrees)
    pb.keyframe_insert("rotation_quaternion", frame=frame)


# ------------------------------------------------------------------ collaborators
def _face(rig, target):
    d = Vector(target) - rig.location
    rig.rotation_euler.z = math.atan2(d.x, -d.y)


def stand(ch, loc, look_at, hands=("side", "side"), lean=6, desk_hand=None, point_at=None):
    """Standing colleague: feet on the floor (MPFB rest height), turned toward look_at, relaxed arms,
    optional right hand resting on the desk, optional left hand pointing at the drawing."""
    from sio_char import rig as R
    rig = ch.rig
    rig.location = (loc[0], loc[1], 0.0); _face(rig, look_at)
    R.update()
    R.rotate_world(rig, "chest", rig.matrix_world.to_3x3() @ Vector((1, 0, 0)), lean)
    for s, sx in (("L", 1), ("R", -1)):
        sh = R.bone_head(rig, f"DEF-upper_arm.{s}")
        side = rig.matrix_world.to_3x3() @ Vector((sx * 0.06, 0.02, 0))
        R.set_world(rig, f"hand_ik.{s}", loc=sh + side + Vector((0, 0, -0.56)))
        R.hand_pose(rig, s, "relaxed")
    if desk_hand:
        R.set_world(rig, "hand_ik.R", loc=desk_hand); R.hand_pose(rig, "R", "rest_flat")
    if point_at:
        R.set_world(rig, "hand_ik.L", loc=point_at); R.hand_pose(rig, "L", "point")
    # head toward the drawing
    head = rig.pose.bones["head"]
    eye = (R.bone_head(rig, "DEF-eye.L") + R.bone_head(rig, "DEF-eye.R")) / 2
    fwd = (rig.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    want = (Vector(look_at) - eye).normalized()
    ax, ang = fwd.rotation_difference(want).to_axis_angle()
    R.rotate_world(rig, "head", ax, math.degrees(ang) * 0.6)
    R.rotate_world(rig, "neck", ax, math.degrees(ang) * 0.3)
    bones = ["root", "chest", "head", "neck", "hand_ik.L", "hand_ik.R"] + [b.name for b in rig.pose.bones if b.name.startswith(("f_", "thumb"))]
    for b in bones:
        pb = rig.pose.bones.get(b)
        if pb:
            pb.keyframe_insert("location", frame=1)
            if pb.rotation_mode == 'QUATERNION':
                pb.keyframe_insert("rotation_quaternion", frame=1)
            else:
                pb.keyframe_insert("rotation_euler", frame=1)
    return rig


def collaborators(paper=(0.02, -0.41, 0.79)):
    """Build the two colleagues (senior engineer + female engineer) beside the desk, hidden until COLLAB."""
    from sio_char import character, hair
    out = []
    for preset, hp, loc, kw in (
        ("engineer_m02", ["short_side_part_v3", "beard_short_v3"], (0.62, 0.22), dict(desk_hand=(0.45, -0.22, 0.80), lean=14)),
        ("engineer_f02", ["ponytail"], (-0.72, -0.02), dict(point_at=(-0.08, -0.36, 0.84), lean=12)),
    ):
        c = character.build(preset)
        for h in hp:
            hair.apply_preset(c, h)
        stand(c, loc, paper, **kw)
        out.append(c)
    return out


def _collab_objects():
    return [o for o in bpy.data.objects if o.get("sio_owner") in ("engineer_m02", "engineer_f02")]


def show_collaborators(on):
    for o in _collab_objects():
        if o.name.startswith("WGT-"):
            continue
        o.hide_render = not on; o.hide_viewport = not on


# ------------------------------------------------------------------ session switch
def setup(ch):
    lighting.rig_lights()
    calendar()
    shirt_tint_setup(ch)


def apply(session, rig=None):
    S = SESSIONS[session]
    lighting.set_state(S["light"])
    clutter.show(S["clutter"])
    set_day(S["day"])
    set_shirt(S["shirt"])
    if rig is not None:
        set_upright(rig, S["upright"])
    show_collaborators(S.get("collaborators", False))
    return S
