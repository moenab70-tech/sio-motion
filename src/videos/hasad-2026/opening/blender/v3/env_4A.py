# v3 · 4A environment: a real 3D canal at golden hour (Blender 5.x, EEVEE).
# Water with animated waves reflecting the low sun, sloped concrete banks, rows of procedural date palms
# swaying in the wind, volumetric haze with light shafts, floating dust motes, sun bloom, and a painterly
# Kuwahara pass so the 3D reads like the opening's hand-painted frames.
# Run: Blender -b --factory-startup -P env_4A.py -- <out_dir> [frames=120] [still=0|frame] [percent=50]
import sys, math, os, random
import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/env4A/"
FRAMES = int(argv[1]) if len(argv) > 1 else 120
STILL = int(argv[2]) if len(argv) > 2 else 0
PCT = int(argv[3]) if len(argv) > 3 else 50
os.makedirs(OUT, exist_ok=True)
random.seed(4)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, PCT
sc.render.fps = 30
sc.frame_start, sc.frame_end = 1, FRAMES
sc.render.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
ee = sc.eevee
for attr, val in [("taa_render_samples", 32), ("use_shadows", True), ("use_raytracing", True),
                  ("volumetric_tile_size", "4"), ("volumetric_samples", 64), ("volumetric_end", 260.0),
                  ("use_volumetric_shadows", True), ("volumetric_light_clamp", 0.0)]:
    try: setattr(ee, attr, val)
    except Exception: pass

TOON = os.environ.get("TOON", "0") == "1"

# ---------- helpers ----------
def toonize(nt, shader_out, steps=0.25, sat=1.15):
    """Anime cel look: shader → RGB → snap brightness into flat bands → emission."""
    s2r = nt.nodes.new("ShaderNodeShaderToRGB"); nt.links.new(shader_out, s2r.inputs[0])
    hsv = nt.nodes.new("ShaderNodeSeparateColor"); hsv.mode = "HSV"; nt.links.new(s2r.outputs["Color"], hsv.inputs[0])
    lift = nt.nodes.new("ShaderNodeMath"); lift.operation = "POWER"; lift.inputs[1].default_value = 0.6
    nt.links.new(hsv.outputs[2], lift.inputs[0])
    snap = nt.nodes.new("ShaderNodeMath"); snap.operation = "SNAP"; snap.inputs[1].default_value = steps
    nt.links.new(lift.outputs[0], snap.inputs[0])
    floor = nt.nodes.new("ShaderNodeMath"); floor.operation = "MAXIMUM"; floor.inputs[1].default_value = 0.22
    nt.links.new(snap.outputs[0], floor.inputs[0])
    sm = nt.nodes.new("ShaderNodeMath"); sm.operation = "MULTIPLY"; sm.inputs[1].default_value = sat
    nt.links.new(hsv.outputs[1], sm.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineColor"); comb.mode = "HSV"
    nt.links.new(hsv.outputs[0], comb.inputs[0]); nt.links.new(sm.outputs[0], comb.inputs[1]); nt.links.new(floor.outputs[0], comb.inputs[2])
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(comb.outputs[0], em.inputs["Color"])
    return em.outputs[0]

def finish(nt, shader_out, out):
    nt.links.new(toonize(nt, shader_out) if TOON else shader_out, out.inputs[0])

def fcurves_of(action):
    """F-curves for both legacy and layered (Blender 4.4+/5.x) actions."""
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    out = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                out += list(bag.fcurves)
    return out

def mat(name, build):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    build(nt, out); return m

def bsdf(nt, color, rough=0.8, spec=0.3):
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    try: b.inputs["Specular IOR Level"].default_value = spec
    except Exception: pass
    return b

def noise_color(nt, b, c1, c2, scale=6.0, detail=6):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
    nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(n.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return n

def link_obj(ob):
    if ob.name not in sc.collection.objects: sc.collection.objects.link(ob)

def mesh_obj(name, verts, faces):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); link_obj(ob); return ob

# ---------- materials ----------
def m_concrete(nt, out):
    b = bsdf(nt, (0.55, 0.47, 0.38), 0.85); noise_color(nt, b, (0.42, 0.35, 0.28), (0.66, 0.57, 0.46), 3.0)
    finish(nt, b.outputs[0], out)
M_CONC = mat("Concrete", m_concrete)

def m_ground(nt, out):
    b = bsdf(nt, (0.3, 0.19, 0.1), 0.95, 0.1); noise_color(nt, b, (0.22, 0.13, 0.06), (0.42, 0.28, 0.14), 0.6, 4)
    finish(nt, b.outputs[0], out)
M_GROUND = mat("Ground", m_ground)

def m_water(nt, out):
    b = bsdf(nt, (0.05, 0.12, 0.14), 0.04, 0.6)
    try: b.inputs["Transmission Weight"].default_value = 0.0
    except Exception: pass
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    # flow toward the camera: animate location along Y
    mp.inputs["Scale"].default_value = (1.0, 0.35, 1.0)
    mp.inputs["Location"].default_value = (0, 0, 0)
    mp.inputs["Location"].keyframe_insert("default_value", frame=1)
    mp.inputs["Location"].default_value = (0, 3.5 * FRAMES / 120, 0.6)
    mp.inputs["Location"].keyframe_insert("default_value", frame=FRAMES)
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 2.2; n.inputs["Detail"].default_value = 8
    try: n.noise_dimensions = "4D"
    except Exception: pass
    w = n.inputs.get("W")
    if w is not None:
        w.default_value = 0; w.keyframe_insert("default_value", frame=1)
        w.default_value = 1.2 * FRAMES / 120; w.keyframe_insert("default_value", frame=FRAMES)
    nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.55; bump.inputs["Distance"].default_value = 0.08
    nt.links.new(n.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    finish(nt, b.outputs[0], out)
    if nt.animation_data and nt.animation_data.action:
        for f in fcurves_of(nt.animation_data.action):
            for k in f.keyframe_points: k.interpolation = "LINEAR"
M_WATER = mat("Water", m_water)

def m_trunk(nt, out):
    b = bsdf(nt, (0.28, 0.18, 0.1), 0.9, 0.1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 6; wv.wave_type = "BANDS"; wv.bands_direction = "Z"
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.12, 0.075, 0.04, 1); ramp.color_ramp.elements[1].color = (0.2, 0.13, 0.07, 1)
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    finish(nt, b.outputs[0], out)
M_TRUNK = mat("Trunk", m_trunk)

def m_frond(nt, out):
    # leaflets: stripes across the frond's width, alpha-cut; translucent so the backlight glows through
    b = bsdf(nt, (0.06, 0.09, 0.025), 0.7, 0.2)
    try:
        b.inputs["Subsurface Weight"].default_value = 0.0
    except Exception: pass
    tl = nt.nodes.new("ShaderNodeBsdfTranslucent"); tl.inputs["Color"].default_value = (0.45, 0.32, 0.05, 1)
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.inputs["Fac"].default_value = 0.35
    nt.links.new(b.outputs[0], mix.inputs[1]); nt.links.new(tl.outputs[0], mix.inputs[2])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["UV"], sep.inputs[0])
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"; wv.inputs["Scale"].default_value = 18
    wv.inputs["Distortion"].default_value = 1.5
    nt.links.new(tc.outputs["UV"], wv.inputs["Vector"])
    # taper: leaflets shorter near the tip (u→1) and a gap along the rib (v≈0.5)
    edge = nt.nodes.new("ShaderNodeMath"); edge.operation = "ABSOLUTE"
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = 0.5
    nt.links.new(sep.outputs["Y"], sub.inputs[0]); nt.links.new(sub.outputs[0], edge.inputs[0])
    lim = nt.nodes.new("ShaderNodeMath"); lim.operation = "MULTIPLY_ADD"
    nt.links.new(sep.outputs["X"], lim.inputs[0]); lim.inputs[1].default_value = -0.38; lim.inputs[2].default_value = 0.5
    inside = nt.nodes.new("ShaderNodeMath"); inside.operation = "LESS_THAN"
    nt.links.new(edge.outputs[0], inside.inputs[0]); nt.links.new(lim.outputs[0], inside.inputs[1])
    stripe = nt.nodes.new("ShaderNodeMath"); stripe.operation = "GREATER_THAN"; stripe.inputs[1].default_value = 0.35
    nt.links.new(wv.outputs["Fac"], stripe.inputs[0])
    rib = nt.nodes.new("ShaderNodeMath"); rib.operation = "LESS_THAN"; rib.inputs[1].default_value = 0.03
    nt.links.new(edge.outputs[0], rib.inputs[0])
    either = nt.nodes.new("ShaderNodeMath"); either.operation = "MAXIMUM"
    nt.links.new(stripe.outputs[0], either.inputs[0]); nt.links.new(rib.outputs[0], either.inputs[1])
    alpha = nt.nodes.new("ShaderNodeMath"); alpha.operation = "MULTIPLY"
    nt.links.new(inside.outputs[0], alpha.inputs[0]); nt.links.new(either.outputs[0], alpha.inputs[1])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    cut = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(alpha.outputs[0], cut.inputs["Fac"]); nt.links.new(tr.outputs[0], cut.inputs[1]); nt.links.new(toonize(nt, mix.outputs[0]) if TOON else mix.outputs[0], cut.inputs[2])
    nt.links.new(cut.outputs[0], out.inputs[0])
M_FROND = mat("Frond", m_frond)
try:
    M_FROND.surface_render_method = "DITHERED"
except Exception: pass

def m_emit(color, strength):
    def f(nt, out):
        e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*color, 1); e.inputs["Strength"].default_value = strength
        nt.links.new(e.outputs[0], out.inputs[0])
    return f
M_SUN = mat("SunDisc", m_emit((1.0, 0.82, 0.5), 60.0))
M_DUST = mat("Dust", m_emit((1.0, 0.8, 0.45), 6.0))

# ---------- world: golden sky gradient + thin haze ----------
world = bpy.data.worlds.new("Golden"); sc.world = world; world.use_nodes = True
wn = world.node_tree; wn.nodes.clear()
wout = wn.nodes.new("ShaderNodeOutputWorld")
bg = wn.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = 1.1
tc = wn.nodes.new("ShaderNodeTexCoord"); sep = wn.nodes.new("ShaderNodeSeparateXYZ")
wn.links.new(tc.outputs["Generated"], sep.inputs[0])
ramp = wn.nodes.new("ShaderNodeValToRGB")
els = ramp.color_ramp.elements
els[0].position = 0.0; els[0].color = (1.0, 0.86, 0.58, 1)
els[1].position = 0.45; els[1].color = (0.62, 0.42, 0.24, 1)
e = els.new(0.08); e.color = (1.0, 0.7, 0.32, 1)
wn.links.new(sep.outputs["Z"], ramp.inputs["Fac"]); wn.links.new(ramp.outputs["Color"], bg.inputs["Color"])
wn.links.new(bg.outputs[0], wout.inputs["Surface"])
vol = wn.nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Color"].default_value = (1.0, 0.8, 0.55, 1); vol.inputs["Density"].default_value = 0.006
try: vol.inputs["Anisotropy"].default_value = 0.6
except Exception: pass
# EEVEE treats world volumes as infinite (they swallow the sky and the sun), so the haze lives in a finite box instead.
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 60, 6))
haze = bpy.context.active_object; haze.name = "Haze"; haze.scale = (80, 150, 12)
hm = bpy.data.materials.new("Haze"); hm.use_nodes = True; hn = hm.node_tree; hn.nodes.clear()
hout = hn.nodes.new("ShaderNodeOutputMaterial")
hv = hn.nodes.new("ShaderNodeVolumePrincipled")
hv.inputs["Color"].default_value = (1.0, 0.8, 0.55, 1); hv.inputs["Density"].default_value = 0.0035
try: hv.inputs["Anisotropy"].default_value = 0.65
except Exception: pass
hn.links.new(hv.outputs[0], hout.inputs["Volume"]); haze.data.materials.append(hm)
wn.nodes.remove(vol)

# ---------- sun ----------
sun_dir_az = math.radians(8)  # sun slightly right of the canal axis
bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
sun = bpy.context.active_object; sun.name = "Sun"
sun.data.energy = 4.5; sun.data.color = (1.0, 0.72, 0.42); sun.data.angle = math.radians(1.5)
# light travels from far +Y (sun) toward the camera, very low elevation (5°)
sun.rotation_euler = (math.radians(-85), 0, sun_dir_az)
try: sun.data.use_shadow = True
except Exception: pass
bpy.ops.mesh.primitive_uv_sphere_add(radius=7, location=(math.sin(sun_dir_az) * 420, 420, 16))
disc = bpy.context.active_object; disc.name = "SunDisc"; disc.data.materials.append(M_SUN)
try: disc.visible_shadow = False
except Exception: pass
# soft fill from the sky side
bpy.ops.object.light_add(type="AREA", location=(-6, -14, 9))
fill = bpy.context.active_object; fill.data.energy = 350; fill.data.size = 14; fill.data.color = (0.75, 0.82, 1.0)
fill.rotation_euler = (math.radians(55), 0, math.radians(-25))

# ---------- terrain: canal channel along +Y ----------
L0, L1 = -20, 320
W_TOP, W_BOT, DEPTH, WATER_Z = 2.4, 1.4, 1.3, -0.55
# banks: left walkway (where the hero stands), right bank, both sloping into the channel
v = [(-W_TOP, L0, 0), (-W_BOT, L0, -DEPTH), (W_BOT, L0, -DEPTH), (W_TOP, L0, 0),
     (-W_TOP, L1, 0), (-W_BOT, L1, -DEPTH), (W_BOT, L1, -DEPTH), (W_TOP, L1, 0)]
canal = mesh_obj("CanalBed", v, [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6)]); canal.data.materials.append(M_CONC)
# concrete coping strips on both edges
for sx in (-1, 1):
    x0 = sx * W_TOP
    cv = [(x0, L0, 0), (x0 + sx * 0.45, L0, 0), (x0 + sx * 0.45, L1, 0), (x0, L1, 0)]
    c = mesh_obj(f"Coping{sx}", [(a, b, z + 0.06) for a, b, z in cv], [(0, 1, 2, 3)]); c.data.materials.append(M_CONC)
# ground planes outside the canal
for sx in (-1, 1):
    x0 = sx * (W_TOP + 0.45)
    gv = [(x0, L0, 0.02), (sx * 400, L0, 0.02), (sx * 400, 600, 0.02), (x0, 600, 0.02)]
    g = mesh_obj(f"Ground{sx}", gv, [(0, 1, 2, 3)]); g.data.materials.append(M_GROUND)
# water surface, subdivided for gentle real displacement near the camera
bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=400, size=1, location=(0, (L0 + L1) / 2, WATER_Z))
water = bpy.context.active_object; water.name = "Water"
wwidth = W_BOT + (W_TOP - W_BOT) * (1 - (-WATER_Z) / DEPTH)
water.scale = (2 * wwidth, L1 - L0, 1)
water.data.materials.append(M_WATER)

# ---------- procedural date palm (shared meshes, instanced) ----------
def make_frond_mesh():
    # strip along +X, width along Y, UV u=length, v=width; bent downward with a curve
    segs, verts, faces, uvs = 14, [], [], []
    for i in range(segs + 1):
        u = i / segs; x = u * 3.2; droop = -1.4 * u * u; half = 0.55 * (1 - 0.35 * u)
        verts += [(x, -half, droop), (x, half, droop)]
    for i in range(segs):
        a = 2 * i; faces.append((a, a + 2, a + 3, a + 1))
    me = bpy.data.meshes.new("Frond"); me.from_pydata(verts, [], faces); me.update()
    uvl = me.uv_layers.new(name="UV")
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index; i, side = divmod(vi, 2)
            uvl.data[li].uv = (i / segs, float(side))
    me.materials.append(M_FROND); return me
FROND = make_frond_mesh()
bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.22, depth=1, location=(0, 0, 0))
trunk_proto = bpy.context.active_object; TRUNK = trunk_proto.data; TRUNK.materials.append(M_TRUNK)
bpy.data.objects.remove(trunk_proto)

def palm(x, y, h, seed):
    rnd = random.Random(seed)
    root = bpy.data.objects.new("Palm", None); link_obj(root); root.location = (x, y, 0)
    t = bpy.data.objects.new("Trunk", TRUNK); link_obj(t); t.parent = root
    t.scale = (1, 1, h); t.location = (0, 0, h / 2)
    crown = bpy.data.objects.new("Crown", None); link_obj(crown); crown.parent = root; crown.location = (0, 0, h)
    n = rnd.randint(13, 17)
    for k in range(n):
        f = bpy.data.objects.new("Fr", FROND); link_obj(f); f.parent = crown
        up = rnd.uniform(-0.15, 0.55)
        f.rotation_euler = (rnd.uniform(-0.2, 0.2), -up, 2 * math.pi * k / n + rnd.uniform(-0.2, 0.2))
        s = rnd.uniform(0.85, 1.15); f.scale = (s, s, s)
    # wind sway on the crown: slow noise-like sine keys (stop-motion friendly, stepped later in Remotion)
    ph, amp = rnd.uniform(0, 6.28), rnd.uniform(0.03, 0.06)
    for fr in range(1, FRAMES + 1, 6):
        crown.rotation_euler = (amp * math.sin(fr / 30 * 1.7 + ph), amp * 0.6 * math.sin(fr / 30 * 1.1 + ph * 1.3), 0)
        crown.keyframe_insert("rotation_euler", frame=fr)
    return root

pid = 0
for sx in (-1, 1):
    for row in range(4):
        xoff = sx * (W_TOP + 5.0 + row * 6.5)
        y = 6 + row * 3.0
        while y < 300:
            pid += 1
            palm(xoff + random.uniform(-1.2, 1.2), y + random.uniform(-1.5, 1.5), random.uniform(6.5, 9.5), pid)
            y += random.uniform(7.0, 9.5)

# ---------- floating dust motes in the light ----------
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.012)
mote = bpy.context.active_object; mote.data.materials.append(M_DUST); MOTE = mote.data
bpy.data.objects.remove(mote)
rnd = random.Random(11)
for i in range(160):
    d = bpy.data.objects.new("Mote", MOTE); link_obj(d)
    base = (rnd.uniform(-5, 4), rnd.uniform(0, 16), rnd.uniform(0.3, 3.2))
    ph = rnd.uniform(0, 6.28)
    for fr in range(1, FRAMES + 1, 4):
        tt = fr / 30
        d.location = (base[0] + 0.25 * math.sin(tt * 0.7 + ph) + 0.12 * tt, base[1] + 0.2 * math.cos(tt * 0.5 + ph), base[2] + 0.15 * math.sin(tt * 0.9 + ph * 2))
        d.keyframe_insert("location", frame=fr)

# ---------- camera: behind the hero on the left walkway, low, looking down the canal toward the sun ----------
bpy.ops.object.camera_add(location=(-3.6, -5.5, 1.55))
cam = bpy.context.active_object; sc.camera = cam
cam.data.lens = 32; cam.data.sensor_width = 36; cam.data.clip_end = 1500
cam.rotation_euler = (math.radians(88.5), 0, math.radians(-6))
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 7.0; cam.data.dof.aperture_fstop = 5.6
# slow push-in (~0.6 m over the shot)
cam.keyframe_insert("location", frame=1)
cam.location = (-3.6, -4.9, 1.58); cam.keyframe_insert("location", frame=FRAMES)
# hero marker (where the rigged hero will stand) — hidden in renders, for blocking only
bpy.ops.object.empty_add(type="SINGLE_ARROW", location=(-3.3, 1.5, 0.06)); bpy.context.active_object.name = "HeroMark"

# ---------- compositor: bloom + painterly Kuwahara + gentle vignette ----------
def setup_compositor():
    tree = None
    if hasattr(sc, "compositing_node_group"):
        tree = bpy.data.node_groups.new("Comp4A", "CompositorNodeTree"); sc.compositing_node_group = tree
        gi = tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        out = tree.nodes.new("NodeGroupOutput")
        out_in = out.inputs[0]
    else:
        sc.use_nodes = True; tree = sc.node_tree; tree.nodes.clear()
        out = tree.nodes.new("CompositorNodeComposite"); out_in = out.inputs["Image"]
    rl = tree.nodes.new("CompositorNodeRLayers")
    glare = tree.nodes.new("CompositorNodeGlare")
    def setin(node, names, val):
        for n in names:
            if n in node.inputs:
                try: node.inputs[n].default_value = val; return True
                except Exception: pass
            if hasattr(node, n.lower().replace(" ", "_")):
                try: setattr(node, n.lower().replace(" ", "_"), val); return True
                except Exception: pass
        return False
    if not setin(glare, ["Type"], "Bloom"): setin(glare, ["glare_type"], "BLOOM")
    setin(glare, ["Threshold", "threshold"], 1.2)
    setin(glare, ["Strength"], 0.45)
    setin(glare, ["Size", "size"], 0.6)
    kuw = tree.nodes.new("CompositorNodeKuwahara")
    setin(kuw, ["Type"], "Anisotropic")
    setin(kuw, ["Size", "size"], 6 if PCT >= 100 else 3)
    setin(kuw, ["Sharpness", "sharpness"], 0.6)
    tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
    if TOON:
        tree.links.new(glare.outputs["Image"], out_in)
    else:
        tree.links.new(glare.outputs["Image"], kuw.inputs["Image"])
        tree.links.new(kuw.outputs["Image"], out_in)
try: setup_compositor()
except Exception as ex: print("COMPOSITOR WARN:", ex)

if TOON:
    # anime ink lines: silhouettes, borders and creases, thin warm-dark strokes
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"; sc.render.line_thickness = 1.1 if PCT < 100 else 1.6
    vl = sc.view_layers[0]; vl.use_freestyle = True
    fs = vl.freestyle_settings
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("Ink")
    ls.select_by_visibility = True; ls.select_silhouette = True; ls.select_border = True; ls.select_crease = True
    if ls.linestyle is None: ls.linestyle = bpy.data.linestyles.new("Ink")
    ls.linestyle.color = (0.18, 0.09, 0.04); ls.linestyle.thickness = 1.0
    try: hv.inputs["Density"].default_value = 0.0018
    except Exception: pass
sc.render.filepath = os.path.join(OUT, "4A_env_")
if STILL:
    sc.frame_set(STILL); sc.render.filepath = os.path.join(OUT, f"still_{STILL:04d}{'_toon' if TOON else ''}.png")
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "env_4A.blend"))
print("ENV4A DONE", OUT)
