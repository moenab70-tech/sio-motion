"""Three lighting states on the same scene (physically placed lights, cached Poly Haven skies):

  dusk  - low warm sun through the window, sunset sky, warm bounce, desk lamp off
  night - cool moonlit sky, desk lamp is the key (warm pool on the drawing), dim cool room fill
  dawn  - pale gold sun just above the horizon, soft volumetric light shafts, lamp still on (left on all night)

    lighting.set_state("night")                 # static
    lighting.key_state("dusk", frame); ...      # or keyframe several states for a time-lapse
"""
import math, os
import bpy
from mathutils import Vector
from . import exterior

HDRI_DIR = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/src/videos/hasad-2026/opening/blender/v3/polyhaven_cache/hdris"

STATES = {
    "dusk":  dict(hdri="industrial_sunset_puresky_2k.hdr", hdri_strength=0.9, hdri_rot=200,
                  sun_el=9, sun_az=20, sun_col=(1.0, 0.56, 0.30), sun_e=7.0,
                  lamp_e=0.0, lamp_col=(1.0, 0.78, 0.52), fill_e=14, fill_col=(1.0, 0.72, 0.50),
                  moon_e=0.0, haze=(0.96, 0.66, 0.48), haze_far=650, vol=0.0, exposure=-0.2),
    "night": dict(hdri="qwantani_night_puresky_2k.hdr", hdri_strength=0.10, hdri_rot=0,
                  sun_el=-10, sun_az=20, sun_col=(0.5, 0.6, 1.0), sun_e=0.0,
                  lamp_e=90, lamp_col=(1.0, 0.72, 0.44), fill_e=1.5, fill_col=(0.45, 0.55, 0.9),
                  moon_e=4, haze=(0.03, 0.05, 0.11), haze_far=560, vol=0.0, exposure=-0.1),
    "dawn":  dict(hdri="qwantani_sunrise_puresky_2k.hdr", hdri_strength=0.6, hdri_rot=150,
                  sun_el=8, sun_az=-20, sun_col=(1.0, 0.72, 0.48), sun_e=10.0,
                  lamp_e=10, lamp_col=(1.0, 0.78, 0.52), fill_e=12, fill_col=(0.75, 0.82, 1.0),
                  moon_e=0.0, haze=(0.95, 0.78, 0.70), haze_far=600, vol=0.004, exposure=-0.3),
}


def _light(name, kind):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, bpy.data.lights.new(name, kind))
        c = bpy.data.collections.get("ENV_lights") or bpy.data.collections.new("ENV_lights")
        if c.name not in [x.name for x in bpy.context.scene.collection.children]:
            bpy.context.scene.collection.children.link(c)
        c.objects.link(o)
    return o


def _aim(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()


def rig_lights(lamp_head=(-0.50, -0.80, 1.22), paper=(0.02, -0.34, 0.79), window=(0.0, -1.10, 1.8)):
    """Create the light objects once (positions in the v4 room)."""
    sun = _light("L_sun", 'SUN'); sun.data.angle = math.radians(1.2)
    lamp = _light("L_desk_lamp", 'SPOT'); lamp.location = lamp_head; _aim(lamp, paper)
    lamp.data.spot_size = math.radians(70); lamp.data.spot_blend = 0.6; lamp.data.shadow_soft_size = 0.02
    bulb = _light("L_lamp_bulb", 'POINT'); bulb.location = Vector(lamp_head) + Vector((0, 0, 0.03)); bulb.data.shadow_soft_size = 0.01
    fill = _light("L_room_fill", 'AREA'); fill.location = (1.2, 2.2, 2.85); fill.data.size = 2.5; _aim(fill, (0, 0, 0.5))
    moon = _light("L_window_moon", 'AREA'); moon.location = Vector(window) + Vector((0, -0.25, 0)); moon.data.size = 1.6
    moon.data.size_y = 1.9; moon.data.shape = 'RECTANGLE'; _aim(moon, (0, 1.5, 0.6))
    return dict(sun=sun, lamp=lamp, bulb=bulb, fill=fill, moon=moon)


def room_haze(density, bounds=((-2.35, 3.55), (-1.08, 3.82), (0.02, 2.98))):
    """Volumetric haze limited to the room interior (the exterior stays clear; light shafts through the window)."""
    o = bpy.data.objects.get("ENV_room_haze")
    if o is None:
        (x0, x1), (y0, y1), (z0, z1) = bounds
        bpy.ops.mesh.primitive_cube_add(location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        o = bpy.context.active_object; o.name = "ENV_room_haze"; o.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
        m = bpy.data.materials.new("ENV_room_haze"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial"); sc_ = nt.nodes.new("ShaderNodeVolumeScatter"); sc_.name = "scatter"
        sc_.inputs["Anisotropy"].default_value = 0.65
        nt.links.new(sc_.outputs[0], out.inputs["Volume"]); o.data.materials.append(m)
        o.visible_shadow = False
        c = bpy.data.collections.get("ENV_lights")
        if c:
            for cc in list(o.users_collection):
                cc.objects.unlink(o)
            c.objects.link(o)
    o.data.materials[0].node_tree.nodes["scatter"].inputs["Density"].default_value = density
    o.hide_render = density <= 0
    return o


def _world(state):
    P = STATES[state]
    sc = bpy.context.scene
    w = bpy.data.worlds.get("SIO_world_v4") or bpy.data.worlds.new("SIO_world_v4")
    sc.world = w; w.use_nodes = True; nt = w.node_tree
    env = nt.nodes.get("env")
    if env is None:
        nt.nodes.clear()
        tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.name = "map"
        env = nt.nodes.new("ShaderNodeTexEnvironment"); env.name = "env"
        bg = nt.nodes.new("ShaderNodeBackground"); bg.name = "bg"
        out = nt.nodes.new("ShaderNodeOutputWorld")
        nt.links.new(tc.outputs["Generated"], mp.inputs[0]); nt.links.new(mp.outputs[0], env.inputs[0])
        nt.links.new(env.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs["Surface"])
    env.image = bpy.data.images.load(os.path.join(HDRI_DIR, P["hdri"]), check_existing=True)
    return w


def set_state(state):
    P = STATES[state]
    L = {k: bpy.data.objects.get(n) for k, n in (("sun", "L_sun"), ("lamp", "L_desk_lamp"), ("bulb", "L_lamp_bulb"),
                                                  ("fill", "L_room_fill"), ("moon", "L_window_moon"))}
    if not all(L.values()):
        L = rig_lights()
    w = _world(state); nt = w.node_tree
    nt.nodes["bg"].inputs["Strength"].default_value = P["hdri_strength"]
    nt.nodes["map"].inputs["Rotation"].default_value[2] = math.radians(P["hdri_rot"])
    room_haze(P["vol"])
    el, az = math.radians(P["sun_el"]), math.radians(P["sun_az"])
    toward_sun = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))  # sun outside the window (-Y)
    L["sun"].rotation_euler = (-toward_sun).to_track_quat('-Z', 'Y').to_euler()
    L["sun"].data.energy = P["sun_e"]; L["sun"].data.color = P["sun_col"]; L["sun"].hide_render = P["sun_e"] <= 0
    L["lamp"].data.energy = P["lamp_e"]; L["lamp"].data.color = P["lamp_col"]; L["lamp"].hide_render = P["lamp_e"] <= 0
    L["bulb"].data.energy = P["lamp_e"] * 0.25; L["bulb"].data.color = P["lamp_col"]; L["bulb"].hide_render = P["lamp_e"] <= 0
    L["fill"].data.energy = P["fill_e"]; L["fill"].data.color = P["fill_col"]
    L["moon"].data.energy = P["moon_e"]; L["moon"].data.color = (0.55, 0.65, 1.0); L["moon"].hide_render = P["moon_e"] <= 0
    ov = bpy.context.scene.get("sio_haze_override")          # optional per-file override (v6.5+): (r, g, b, far, amount)
    if ov:
        exterior.set_haze(tuple(ov[:3]), far=ov[3], amount=ov[4])
    else:
        exterior.set_haze(P["haze"], far=P["haze_far"])
    sc = bpy.context.scene
    sc.view_settings.exposure = P["exposure"]
    try:
        sc.eevee.volumetric_end = 12.0; sc.eevee.volumetric_tile_size = '8'
    except Exception:
        pass
    return L


def key_state(state, frame):
    """Keyframe every light/world value of a state at `frame` (for time-lapse transitions)."""
    L = set_state(state)
    for o in L.values():
        o.data.keyframe_insert("energy", frame=frame); o.data.keyframe_insert("color", frame=frame)
        o.keyframe_insert("rotation_euler", frame=frame)
    w = bpy.context.scene.world; nt = w.node_tree
    nt.nodes["bg"].inputs["Strength"].keyframe_insert("default_value", frame=frame)
    vb = bpy.data.objects.get("ENV_room_haze")
    if vb:
        vb.data.materials[0].node_tree.nodes["scatter"].inputs["Density"].keyframe_insert("default_value", frame=frame)
    bpy.context.scene.view_settings.keyframe_insert("exposure", frame=frame)
