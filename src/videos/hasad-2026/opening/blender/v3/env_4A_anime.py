# v3 · 4A environment, ANIME style (Blender 5.x, EEVEE): cel-shaded 3D canal at golden hour.
# - Cel materials: light is read with Shader→RGB and snapped into 3 flat bands (cool shadow / warm mid / hot lit),
#   multiplied by the base colour, plus a gold rim on silhouettes. Real cast shadows from a low sun.
# - Anime sky in the world shader: gradient + drawn cumulus clouds + sun disc and halo (sky lights nothing).
# - Stylised water: deep teal → gold at grazing angles, animated sparkle glints along the sun path.
# - Date palms swaying, dust motes, light haze, Freestyle ink lines (not on leaves/water), bloom.
# Run: Blender -b --factory-startup -P env_4A_anime.py -- <out_dir> [frames=120] [still=0|frame] [percent=50]
import sys, math, os, random
import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/env4A_anime/"
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
sc.view_settings.view_transform = "Standard"  # flat anime colours, no filmic desaturation
ee = sc.eevee
for attr, val in [("taa_render_samples", 24), ("use_shadows", True), ("shadow_resolution_scale", 1.0),
                  ("volumetric_tile_size", "4"), ("volumetric_samples", 48), ("volumetric_end", 200.0)]:
    try: setattr(ee, attr, val)
    except Exception: pass

SUN_AZ, SUN_EL = math.radians(7), math.radians(4.0)
SUN_DIR = (math.sin(SUN_AZ) * math.cos(SUN_EL), math.cos(SUN_AZ) * math.cos(SUN_EL), math.sin(SUN_EL))  # toward the sun

# ---------- helpers ----------
def fcurves_of(action):
    if hasattr(action, "fcurves"): return list(action.fcurves)
    out = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []): out += list(bag.fcurves)
    return out

def link_obj(ob, coll=None):
    (coll or sc.collection).objects.link(ob)

NOINK = bpy.data.collections.new("NoInk"); sc.collection.children.link(NOINK)
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "palm_asset.py")).read())
exec(open(os.path.join(HERE, "toon_lib.py")).read())

def mesh_obj(name, verts, faces, coll=None):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); link_obj(ob, coll); return ob

def new_mat(name):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree; nt.nodes.clear()
    return m, nt, nt.nodes.new("ShaderNodeOutputMaterial")

def ramp(nt, stops, interp="CONSTANT"):
    r = nt.nodes.new("ShaderNodeValToRGB"); r.color_ramp.interpolation = interp
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], (*stops[0][1], 1)
    els[1].position, els[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        e = els.new(p); e.color = (*c, 1)
    return r

def cel_output(nt, out, base_socket, shadow=(0.46, 0.4, 0.62), mid=(0.78, 0.64, 0.56), lit=(1.22, 1.04, 0.82),
               t1=0.03, t2=0.14, rim=(1.0, 0.72, 0.38), rim_amt=0.55, alpha_socket=None):
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse"); dif.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB"); nt.links.new(dif.outputs[0], s2r.inputs[0])
    bands = ramp(nt, [(0.0, shadow), (t1, mid), (t2, lit)])
    nt.links.new(s2r.outputs["Color"], bands.inputs["Fac"])
    mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1.0
    nt.links.new(bands.outputs["Color"], mul.inputs[6]); nt.links.new(base_socket, mul.inputs[7])
    col = mul.outputs[2]
    if rim_amt > 0:
        lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
        rr = ramp(nt, [(0.0, (0, 0, 0)), (0.72, (rim_amt, rim_amt, rim_amt))])
        nt.links.new(lw.outputs["Facing"], rr.inputs["Fac"])
        rc = nt.nodes.new("ShaderNodeMix"); rc.data_type = "RGBA"; rc.blend_type = "MULTIPLY"; rc.inputs["Factor"].default_value = 1.0
        nt.links.new(rr.outputs["Color"], rc.inputs[6]); rc.inputs[7].default_value = (*rim, 1)
        add = nt.nodes.new("ShaderNodeMix"); add.data_type = "RGBA"; add.blend_type = "ADD"; add.inputs["Factor"].default_value = 1.0
        nt.links.new(col, add.inputs[6]); nt.links.new(rc.outputs[2], add.inputs[7]); col = add.outputs[2]
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(col, em.inputs["Color"])
    shader = em.outputs[0]
    if alpha_socket is not None:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(alpha_socket, mx.inputs["Fac"]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(shader, mx.inputs[2])
        shader = mx.outputs[0]
    nt.links.new(shader, out.inputs["Surface"])

def flat(nt, c):
    rgb = nt.nodes.new("ShaderNodeRGB"); rgb.outputs[0].default_value = (*c, 1); return rgb.outputs[0]

def two_tone(nt, c1, c2, scale, coord="Object", thresh=0.55, detail=3):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
    nt.links.new(tc.outputs[coord], n.inputs["Vector"])
    r = ramp(nt, [(0.0, c1), (thresh, c2)]); nt.links.new(n.outputs["Fac"], r.inputs["Fac"])
    return r.outputs["Color"]

# ---------- materials ----------
M_CONC, nt, out = new_mat("Concrete")
_base = two_tone(nt, (0.8, 0.68, 0.52), (0.72, 0.6, 0.46), 1.4)
_geo = nt.nodes.new("ShaderNodeNewGeometry"); _sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(_geo.outputs["Position"], _sp.inputs[0])
_jy = nt.nodes.new("ShaderNodeMath"); _jy.operation = "WRAP"; _jy.inputs[1].default_value = 0; _jy.inputs[2].default_value = 3.0
nt.links.new(_sp.outputs["Y"], _jy.inputs[0])
_jr = ramp(nt, [(0.0, (0.55, 0.5, 0.48)), (0.03, (1, 1, 1)), (0.985, (0.55, 0.5, 0.48))])
_jn = nt.nodes.new("ShaderNodeMath"); _jn.operation = "DIVIDE"; _jn.inputs[1].default_value = 3.0
nt.links.new(_jy.outputs[0], _jn.inputs[0]); nt.links.new(_jn.outputs[0], _jr.inputs["Fac"])
_wl = nt.nodes.new("ShaderNodeMapRange"); _wl.inputs["From Min"].default_value = -0.5; _wl.inputs["From Max"].default_value = -0.2
nt.links.new(_sp.outputs["Z"], _wl.inputs["Value"])
_wr = ramp(nt, [(0.0, (0.5, 0.48, 0.5)), (0.5, (0.72, 0.68, 0.66)), (0.75, (1, 1, 1))])
nt.links.new(_wl.outputs["Result"], _wr.inputs["Fac"])
_m1 = nt.nodes.new("ShaderNodeMix"); _m1.data_type = "RGBA"; _m1.blend_type = "MULTIPLY"; _m1.inputs["Factor"].default_value = 1
nt.links.new(_base, _m1.inputs[6]); nt.links.new(_jr.outputs["Color"], _m1.inputs[7])
_m2 = nt.nodes.new("ShaderNodeMix"); _m2.data_type = "RGBA"; _m2.blend_type = "MULTIPLY"; _m2.inputs["Factor"].default_value = 1
nt.links.new(_m1.outputs[2], _m2.inputs[6]); nt.links.new(_wr.outputs["Color"], _m2.inputs[7])
cel_output(nt, out, _m2.outputs[2])
M_COPE, nt, out = new_mat("Coping"); cel_output(nt, out, flat(nt, (0.9, 0.8, 0.64)))
M_GROUND, nt, out = new_mat("Ground"); cel_output(nt, out, two_tone(nt, (0.62, 0.38, 0.2), (0.4, 0.44, 0.16), 0.09, thresh=0.6), shadow=(0.5, 0.42, 0.62), mid=(0.8, 0.62, 0.52), lit=(1.08, 0.92, 0.74))
M_TRUNK, nt, out = new_mat("Trunk")
tc = nt.nodes.new("ShaderNodeTexCoord")
wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Z"; wv.inputs["Scale"].default_value = 5
nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
tr_r = ramp(nt, [(0.0, (0.4, 0.27, 0.17)), (0.7, (0.3, 0.2, 0.13))]); nt.links.new(wv.outputs["Fac"], tr_r.inputs["Fac"])
cel_output(nt, out, tr_r.outputs["Color"], rim_amt=0.7)

# fronds: leaflet alpha cut-out (UV u = along the frond, v = across)
M_FROND, nt, out = new_mat("Frond")
tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["UV"], sep.inputs[0])
wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"
wv.inputs["Scale"].default_value = 16; wv.inputs["Distortion"].default_value = 0.8
nt.links.new(tc.outputs["UV"], wv.inputs["Vector"])
def M(op, a, b=None, v=None):
    m = nt.nodes.new("ShaderNodeMath"); m.operation = op
    for i, x in enumerate([a, b] if b is not None or v is not None else [a]):
        if x is None: m.inputs[i].default_value = v
        elif isinstance(x, (int, float)): m.inputs[i].default_value = x
        else: nt.links.new(x, m.inputs[i])
    return m.outputs[0]
across = M("ABSOLUTE", M("SUBTRACT", sep.outputs["Y"], 0.5))
limit = M("MULTIPLY_ADD", sep.outputs["X"], -0.4, None) if False else None
lm = nt.nodes.new("ShaderNodeMath"); lm.operation = "MULTIPLY_ADD"
nt.links.new(sep.outputs["X"], lm.inputs[0]); lm.inputs[1].default_value = -0.42; lm.inputs[2].default_value = 0.5
inside = M("LESS_THAN", across, lm.outputs[0])
stripe = M("GREATER_THAN", wv.outputs["Fac"], 0.3)
rib = M("LESS_THAN", across, 0.035)
alpha = M("MULTIPLY", inside, M("MAXIMUM", stripe, rib))
fr_col = two_tone(nt, (0.27, 0.44, 0.13), (0.36, 0.5, 0.15), 3.0, coord="UV", thresh=0.5)
cel_output(nt, out, fr_col, shadow=(0.42, 0.42, 0.6), lit=(1.3, 1.15, 0.7), rim=(1.0, 0.82, 0.3), rim_amt=0.6, alpha_socket=alpha)
try: M_FROND.surface_render_method = "DITHERED"
except Exception: pass

# stylised water
M_WATER, nt, out = new_mat("Water")
lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.2
wcol = ramp(nt, [(0.0, (0.07, 0.3, 0.36)), (0.35, (0.2, 0.45, 0.48)), (0.75, (0.95, 0.66, 0.36)), (0.92, (1.0, 0.85, 0.55))], "LINEAR")
nt.links.new(lw.outputs["Facing"], wcol.inputs["Fac"])
tc = nt.nodes.new("ShaderNodeTexCoord"); geo = nt.nodes.new("ShaderNodeNewGeometry"); mp = nt.nodes.new("ShaderNodeMapping"); nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])
mp.inputs["Scale"].default_value = (1.6, 0.35, 1.6)
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"; nz.inputs["Scale"].default_value = 9; nz.inputs["Detail"].default_value = 2
nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
nz.inputs["W"].default_value = 0; nz.inputs["W"].keyframe_insert("default_value", frame=1)
nz.inputs["W"].default_value = 2.0 * FRAMES / 120; nz.inputs["W"].keyframe_insert("default_value", frame=FRAMES)
mp.inputs["Location"].default_value = (0, 0, 0); mp.inputs["Location"].keyframe_insert("default_value", frame=1)
mp.inputs["Location"].default_value = (0, -1.5 * FRAMES / 120, 0); mp.inputs["Location"].keyframe_insert("default_value", frame=FRAMES)
gl = ramp(nt, [(0.0, (0, 0, 0)), (0.66, (1, 1, 1))]); nt.links.new(nz.outputs["Fac"], gl.inputs["Fac"])
# glints only along the sun path (|x| small in object space) and stronger far away (grazing)
sepw = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sepw.inputs[0])
path = nt.nodes.new("ShaderNodeMapRange"); nt.links.new(sepw.outputs["X"], path.inputs["Value"])
path.inputs["From Min"].default_value = -1.9; path.inputs["From Max"].default_value = 1.9
pr = ramp(nt, [(0.0, (0.25, 0.25, 0.25)), (0.3, (1, 1, 1)), (0.7, (0.25, 0.25, 0.25))], "LINEAR")
nt.links.new(path.outputs["Result"], pr.inputs["Fac"])
gm = nt.nodes.new("ShaderNodeMix"); gm.data_type = "RGBA"; gm.blend_type = "MULTIPLY"; gm.inputs["Factor"].default_value = 1
nt.links.new(gl.outputs["Color"], gm.inputs[6]); nt.links.new(pr.outputs["Color"], gm.inputs[7])
gstr = nt.nodes.new("ShaderNodeMix"); gstr.data_type = "RGBA"; gstr.blend_type = "MULTIPLY"; gstr.inputs["Factor"].default_value = 1
nt.links.new(gm.outputs[2], gstr.inputs[6]); gstr.inputs[7].default_value = (3.2, 2.7, 1.9, 1)
wadd = nt.nodes.new("ShaderNodeMix"); wadd.data_type = "RGBA"; wadd.blend_type = "ADD"; wadd.inputs["Factor"].default_value = 1
nt.links.new(wcol.outputs["Color"], wadd.inputs[6]); nt.links.new(gstr.outputs[2], wadd.inputs[7])
# ripple bands (lighter strokes) for a drawn feel
rb = ramp(nt, [(0.0, (0, 0, 0)), (0.56, (0.12, 0.12, 0.1)), (0.6, (0, 0, 0))])
nt.links.new(nz.outputs["Fac"], rb.inputs["Fac"])
wadd2 = nt.nodes.new("ShaderNodeMix"); wadd2.data_type = "RGBA"; wadd2.blend_type = "ADD"; wadd2.inputs["Factor"].default_value = 1
nt.links.new(wadd.outputs[2], wadd2.inputs[6]); nt.links.new(rb.outputs["Color"], wadd2.inputs[7])
wem = nt.nodes.new("ShaderNodeEmission"); nt.links.new(wadd2.outputs[2], wem.inputs["Color"]); nt.links.new(wem.outputs[0], out.inputs["Surface"])
if nt.animation_data and nt.animation_data.action:
    for f in fcurves_of(nt.animation_data.action):
        for k in f.keyframe_points: k.interpolation = "LINEAR"

M_DUST, nt, out = new_mat("Dust")
e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (1, 0.85, 0.55, 1); e.inputs["Strength"].default_value = 3
nt.links.new(e.outputs[0], out.inputs["Surface"])

M_WALK, nt, out = new_mat("Walkway"); cel_output(nt, out, two_tone(nt, (0.72, 0.52, 0.32), (0.64, 0.45, 0.27), 0.6, thresh=0.55))
M_FARM, nt, out = new_mat("Farm")
_g = two_tone(nt, (0.23, 0.38, 0.11), (0.31, 0.46, 0.14), 0.25, thresh=0.5)
_soil = two_tone(nt, (0, 0, 0), (1, 1, 1), 0.06, thresh=0.74)
_mx = nt.nodes.new("ShaderNodeMix"); _mx.data_type = "RGBA"
_sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(_soil, _sep.inputs[0])
nt.links.new(_sep.outputs[0], _mx.inputs["Factor"]); nt.links.new(_g, _mx.inputs[6]); _mx.inputs[7].default_value = (0.42, 0.3, 0.17, 1)
cel_output(nt, out, _mx.outputs[2], shadow=(0.45, 0.45, 0.62), lit=(1.15, 1.02, 0.78))

def grass_clump_mesh():
    vs, fs, cs = [], [], []
    rnd = random.Random(2)
    for b in range(16):
        a = rnd.uniform(0, 2 * math.pi); lean = rnd.uniform(0.35, 0.95); h = rnd.uniform(0.06, 0.16); w = 0.014
        ox, oy = rnd.uniform(-0.06, 0.06), rnd.uniform(-0.06, 0.06)
        dx, dy = math.cos(a), math.sin(a); px, py = -dy, dx
        base = len(vs)
        for q in range(4):
            t = q / 3; ww = w * (1 - t)
            cx, cy, cz = ox + dx * lean * h * t * t, oy + dy * lean * h * t * t, h * t
            vs += [(cx - px * ww, cy - py * ww, cz), (cx + px * ww, cy + py * ww, cz)]
            col = (0.2 + 0.16 * t, 0.33 + 0.18 * t, 0.1 + 0.05 * t); cs += [col, col]
        for q in range(3):
            i0 = base + 2 * q; fs.append((i0, i0 + 1, i0 + 3, i0 + 2))
    me = bpy.data.meshes.new("GrassClump"); me.from_pydata(vs, [], fs); me.update()
    attr = me.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
    for i, c in enumerate(cs): attr.data[i].color = (*c, 1)
    return me

def scatter_patch(name, xr, yr, density):
    """Geometry-nodes scatter of grass clumps over a rectangle (instanced, randomised)."""
    global GRASS_OB, GRASS_NG
    if "GRASS_OB" not in globals():
        me = grass_clump_mesh(); me.materials.append(palm_material("GrassToon"))
        GRASS_OB = bpy.data.objects.new("GrassClump", me); NOINK.objects.link(GRASS_OB); GRASS_OB.hide_render = True; GRASS_OB.location = (0, 0, -50)
        ng = bpy.data.node_groups.new("GrassScatter", "GeometryNodeTree")
        ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        dsock = ng.interface.new_socket("Density", in_out="INPUT", socket_type="NodeSocketFloat")
        gi, go = ng.nodes.new("NodeGroupInput"), ng.nodes.new("NodeGroupOutput")
        dist = ng.nodes.new("GeometryNodeDistributePointsOnFaces")
        oi = ng.nodes.new("GeometryNodeObjectInfo"); oi.inputs["As Instance"].default_value = True; oi.inputs["Object"].default_value = GRASS_OB
        inst = ng.nodes.new("GeometryNodeInstanceOnPoints")
        rr = ng.nodes.new("FunctionNodeRandomValue"); rr.data_type = "FLOAT_VECTOR"
        rr.inputs["Min"].default_value = (0, 0, 0); rr.inputs["Max"].default_value = (0.25, 0.25, 6.28)
        rs = ng.nodes.new("FunctionNodeRandomValue"); rs.data_type = "FLOAT"
        _f = [i for i in rs.inputs if i.type == "VALUE" and i.name in ("Min", "Max")]
        _f[0].default_value = 0.7; _f[1].default_value = 1.35
        ng.links.new(gi.outputs[0], dist.inputs["Mesh"]); ng.links.new(gi.outputs[1], dist.inputs["Density"])
        ng.links.new(dist.outputs["Points"], inst.inputs["Points"]); ng.links.new(oi.outputs["Geometry"], inst.inputs["Instance"])
        ng.links.new([o for o in rr.outputs if o.type == "VECTOR"][0], inst.inputs["Rotation"]); ng.links.new([o for o in rs.outputs if o.type == "VALUE"][0], inst.inputs["Scale"])
        ng.links.new(inst.outputs[0], go.inputs[0])
        GRASS_NG = ng
    v = [(xr[0], yr[0], 0.03), (xr[1], yr[0], 0.03), (xr[1], yr[1], 0.03), (xr[0], yr[1], 0.03)]
    if xr[1] < xr[0]: v = [v[1], v[0], v[3], v[2]]
    ob = mesh_obj(name, v, [(0, 1, 2, 3)], NOINK)
    ng = GRASS_NG.copy(); ng.interface.items_tree["Density"].default_value = density   # one group per density
    mod = ob.modifiers.new("Grass", "NODES"); mod.node_group = ng

# ---------- anime sky (seen by the camera only; lights nothing) ----------
world = bpy.data.worlds.new("AnimeSky"); sc.world = world
try: world.use_nodes = True
except Exception: pass
wn = world.node_tree; wn.nodes.clear()
wout = wn.nodes.new("ShaderNodeOutputWorld")
tc = wn.nodes.new("ShaderNodeTexCoord")
dirv = wn.nodes.new("ShaderNodeVectorMath"); dirv.operation = "NORMALIZE"; wn.links.new(tc.outputs["Generated"], dirv.inputs[0])
sepd = wn.nodes.new("ShaderNodeSeparateXYZ"); wn.links.new(dirv.outputs[0], sepd.inputs[0])
def wramp(stops, interp="LINEAR"):
    r = wn.nodes.new("ShaderNodeValToRGB"); r.color_ramp.interpolation = interp
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], (*stops[0][1], 1)
    els[1].position, els[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        x = els.new(p); x.color = (*c, 1)
    return r
skyr = wramp([(0.0, (1.0, 0.82, 0.5)), (0.05, (1.0, 0.64, 0.32)), (0.16, (0.96, 0.52, 0.38)), (0.38, (0.55, 0.42, 0.62)), (0.75, (0.24, 0.3, 0.58))])
wn.links.new(sepd.outputs["Z"], skyr.inputs["Fac"])
# drawn clouds: project direction onto a plane above (x/z, y/z) → noise → hard threshold
dz = wn.nodes.new("ShaderNodeMath"); dz.operation = "MAXIMUM"; dz.inputs[1].default_value = 0.04; wn.links.new(sepd.outputs["Z"], dz.inputs[0])
proj = wn.nodes.new("ShaderNodeVectorMath"); proj.operation = "DIVIDE"; wn.links.new(dirv.outputs[0], proj.inputs[0])
cz = wn.nodes.new("ShaderNodeCombineXYZ"); wn.links.new(dz.outputs[0], cz.inputs[0]); wn.links.new(dz.outputs[0], cz.inputs[1]); wn.links.new(dz.outputs[0], cz.inputs[2])
wn.links.new(cz.outputs[0], proj.inputs[1])
def cnoise(vec):
    n = wn.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 0.42; n.inputs["Detail"].default_value = 6
    n.inputs["Roughness"].default_value = 0.58; wn.links.new(vec, n.inputs["Vector"]); return n.outputs["Fac"]
cn_fac = cnoise(proj.outputs[0])
_l = math.hypot(SUN_DIR[0], SUN_DIR[1])
shift = wn.nodes.new("ShaderNodeVectorMath"); shift.operation = "ADD"; wn.links.new(proj.outputs[0], shift.inputs[0])
shift.inputs[1].default_value = (0.1 * SUN_DIR[0] / _l, 0.1 * SUN_DIR[1] / _l, 0)
cn2_fac = cnoise(shift.outputs[0])
diff = wn.nodes.new("ShaderNodeMath"); diff.operation = "SUBTRACT"; wn.links.new(cn_fac, diff.inputs[0]); wn.links.new(cn2_fac, diff.inputs[1])
lmap = wn.nodes.new("ShaderNodeMath"); lmap.operation = "MULTIPLY_ADD"; wn.links.new(diff.outputs[0], lmap.inputs[0])
lmap.inputs[1].default_value = 5.0; lmap.inputs[2].default_value = 0.5
cshade = wramp([(0.0, (0.74, 0.5, 0.62)), (0.42, (0.95, 0.72, 0.66)), (0.6, (1.0, 0.88, 0.76))], "CONSTANT")
wn.links.new(lmap.outputs[0], cshade.inputs["Fac"])
# thicker cores a touch darker (volume), thin edges softly transparent-ish
cmask = wramp([(0.0, (0, 0, 0)), (0.555, (0.55, 0.55, 0.55)), (0.575, (1, 1, 1))], "CONSTANT"); wn.links.new(cn_fac, cmask.inputs["Fac"])
hband = wramp([(0.0, (0, 0, 0)), (0.06, (0, 0, 0)), (0.16, (1, 1, 1)), (0.5, (1, 1, 1)), (0.7, (0.3, 0.3, 0.3))])
wn.links.new(sepd.outputs["Z"], hband.inputs["Fac"])
cm2 = wn.nodes.new("ShaderNodeMix"); cm2.data_type = "RGBA"; cm2.blend_type = "MULTIPLY"; cm2.inputs["Factor"].default_value = 1
wn.links.new(cmask.outputs["Color"], cm2.inputs[6]); wn.links.new(hband.outputs["Color"], cm2.inputs[7])
sepm = wn.nodes.new("ShaderNodeSeparateColor"); wn.links.new(cm2.outputs[2], sepm.inputs[0])
skyc = wn.nodes.new("ShaderNodeMix"); skyc.data_type = "RGBA"
wn.links.new(sepm.outputs[0], skyc.inputs["Factor"]); wn.links.new(skyr.outputs["Color"], skyc.inputs[6])
# sun disc + halo
dot = wn.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; wn.links.new(dirv.outputs[0], dot.inputs[0])
dot.inputs[1].default_value = SUN_DIR
halo = wramp([(0.0, (0, 0, 0)), (0.99, (0, 0, 0)), (0.9982, (0.4, 0.22, 0.07)), (0.99955, (0.85, 0.55, 0.25)), (0.9996, (3.0, 2.6, 1.9))])
wn.links.new(dot.outputs["Value"], halo.inputs["Fac"])
skyadd = wn.nodes.new("ShaderNodeMix"); skyadd.data_type = "RGBA"; skyadd.blend_type = "ADD"; skyadd.inputs["Factor"].default_value = 1
wn.links.new(skyc.outputs[2], skyadd.inputs[6]); wn.links.new(halo.outputs["Color"], skyadd.inputs[7])
prox = wramp([(0.0, (0, 0, 0)), (0.6, (0, 0, 0)), (0.99, (0.75, 0.75, 0.75))])
wn.links.new(dot.outputs["Value"], prox.inputs["Fac"])
psep = wn.nodes.new("ShaderNodeSeparateColor"); wn.links.new(prox.outputs["Color"], psep.inputs[0])
cgold = wn.nodes.new("ShaderNodeMix"); cgold.data_type = "RGBA"
wn.links.new(psep.outputs[0], cgold.inputs["Factor"]); wn.links.new(cshade.outputs["Color"], cgold.inputs[6]); cgold.inputs[7].default_value = (1.0, 0.8, 0.46, 1)
wn.links.new(cgold.outputs[2], skyc.inputs[7])
warmc = skyadd
bg_cam = wn.nodes.new("ShaderNodeBackground"); wn.links.new(warmc.outputs[2], bg_cam.inputs["Color"])
bg_amb = wn.nodes.new("ShaderNodeBackground"); bg_amb.inputs["Color"].default_value = (1, 0.8, 0.6, 1); bg_amb.inputs["Strength"].default_value = 0.02
lp = wn.nodes.new("ShaderNodeLightPath")
wmix = wn.nodes.new("ShaderNodeMixShader"); wn.links.new(lp.outputs["Is Camera Ray"], wmix.inputs["Fac"])
wn.links.new(bg_amb.outputs[0], wmix.inputs[1]); wn.links.new(bg_cam.outputs[0], wmix.inputs[2])
wn.links.new(wmix.outputs[0], wout.inputs["Surface"])

# ---------- sun light (travels from the sun toward the camera) ----------
bpy.ops.object.light_add(type="SUN", location=(0, 0, 20))
sun = bpy.context.active_object; sun.name = "Sun"
sun.data.energy = 3.0; sun.data.color = (1.0, 0.9, 0.75); sun.data.angle = math.radians(0.6)
dx, dy, dz_ = (-SUN_DIR[0], -SUN_DIR[1], -SUN_DIR[2])  # light direction
sun.rotation_euler = (math.atan2(math.hypot(dx, dy), -dz_), 0, math.atan2(dy, dx) + math.pi / 2)
# light haze for depth
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 70, 7))
haze = bpy.context.active_object; haze.name = "Haze"; haze.scale = (90, 170, 14)
for c in list(haze.users_collection): c.objects.unlink(haze)
NOINK.objects.link(haze)
hm, hn, hout = new_mat("Haze")
hv = hn.nodes.new("ShaderNodeVolumePrincipled"); hv.inputs["Color"].default_value = (1.0, 0.78, 0.55, 1); hv.inputs["Density"].default_value = 0.0012
try: hv.inputs["Anisotropy"].default_value = 0.7
except Exception: pass
hn.links.new(hv.outputs[0], hout.inputs["Volume"]); haze.data.materials.append(hm)

# ---------- terrain ----------
L0, L1 = -20, 320
W_TOP, W_BOT, DEPTH, WATER_Z = 2.4, 1.4, 1.3, -0.5
v = [(-W_TOP, L0, 0), (-W_BOT, L0, -DEPTH), (W_BOT, L0, -DEPTH), (W_TOP, L0, 0),
     (-W_TOP, L1, 0), (-W_BOT, L1, -DEPTH), (W_BOT, L1, -DEPTH), (W_TOP, L1, 0)]
canal = mesh_obj("CanalBed", v, [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6)]); canal.data.materials.append(M_CONC)
for sx in (-1, 1):
    x0 = sx * W_TOP
    cv = [(x0, L0, 0.08), (x0 + sx * 0.45, L0, 0.08), (x0 + sx * 0.45, L1, 0.08), (x0, L1, 0.08)]
    c = mesh_obj(f"Coping{sx}", cv, [(0, 1, 2, 3)]); c.data.materials.append(M_COPE)
    # a small vertical face so the edge reads (and gets an ink line)
    fv = [(x0, L0, 0.08), (x0, L1, 0.08), (x0, L1, -0.1), (x0, L0, -0.1)]
    f = mesh_obj(f"CopingFace{sx}", fv, [(0, 1, 2, 3)]); f.data.materials.append(M_COPE)
    x1 = sx * (W_TOP + 0.45); x2 = sx * (W_TOP + 3.2)
    wv_ = [(x1, L0, 0.03), (x2, L0, 0.03), (x2, 600, 0.03), (x1, 600, 0.03)]
    w_ = mesh_obj(f"Walkway{sx}", wv_, [(0, 1, 2, 3)]); w_.data.materials.append(M_WALK)
    gv = [(x2, L0, 0.02), (sx * 400, L0, 0.02), (sx * 400, 600, 0.02), (x2, 600, 0.02)]
    g = mesh_obj(f"Farm{sx}", gv, [(0, 1, 2, 3)]); g.data.materials.append(M_FARM)
    # grass scatter patches: farmland near the camera + a tuft line along the walkway edges
    scatter_patch(f"GrassNear{sx}", (x2, sx * 22), (L0, 40), 55.0)
    scatter_patch(f"GrassMid{sx}", (x2, sx * 38), (40, 90), 20.0)
    scatter_patch(f"GrassEdge{sx}", (x2 - sx * 0.12, x2 + sx * 0.3), (L0, 90), 45.0)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, (L0 + L1) / 2, WATER_Z))
water = bpy.context.active_object; water.name = "Water"
wwidth = W_BOT + (W_TOP - W_BOT) * (1 - (-WATER_Z) / DEPTH)
water.scale = (2 * wwidth, L1 - L0, 1); water.data.materials.append(M_WATER)
for c in list(water.users_collection): c.objects.unlink(water)
NOINK.objects.link(water)

# ---------- date palms: one detailed asset, a few variants, instanced ----------
exec(open(os.path.join(HERE, "toon_lib.py")).read())
M_PTRUNK, M_PLEAF = palm_material("PalmTrunk", leaf=False), palm_material("PalmLeaf")
VARIANTS = []
for k, (seed, hgt, lod) in enumerate([(3, 7.6, 1.0), (7, 8.4, 1.0), (11, 6.9, 1.0), (5, 8.0, 0.45), (9, 7.2, 0.45)]):
    tm, cm = build_palm(seed=seed, height=hgt, lod=lod, dates=lod > 0.5, name=f"PalmV{k}")
    tm.materials.append(M_PTRUNK); cm.materials.append(M_PLEAF); VARIANTS.append((tm, cm, lod))
NEAR = [v for v in VARIANTS if v[2] > 0.5]; FAR = [v for v in VARIANTS if v[2] <= 0.5]
basin_me = None
def basin(x, y):
    """Dark wet irrigation basin under each palm (a soft irregular disc)."""
    global basin_me
    if basin_me is None:
        vs, fs = [(0, 0, 0.045)], []
        for k in range(20):
            a = 2 * math.pi * k / 20; r = 1.15 * (1 + 0.08 * math.sin(a * 3))
            vs.append((r * math.cos(a), r * math.sin(a), 0.045))
        for k in range(20): fs.append((0, 1 + k, 1 + (k + 1) % 20))
        basin_me = bpy.data.meshes.new("Basin"); basin_me.from_pydata(vs, [], fs); basin_me.update()
        mb, nt, out = new_mat("Basin"); cel_output(nt, out, flat(nt, (0.36, 0.24, 0.14)), rim_amt=0)
        basin_me.materials.append(mb)
    ob = bpy.data.objects.new("Basin", basin_me); NOINK.objects.link(ob); ob.location = (x, y, 0)
    ob.rotation_euler = (0, 0, random.uniform(0, 6.28))

def palm(x, y, seed):
    rnd = random.Random(seed)
    tm, cm, _ = rnd.choice(NEAR if y < 90 else FAR)
    root = bpy.data.objects.new("Palm", None); link_obj(root); root.location = (x, y, 0)
    root.rotation_euler = (0, 0, rnd.uniform(0, 6.28)); s = rnd.uniform(0.9, 1.12); root.scale = (s, s, s)
    t = bpy.data.objects.new("Trunk", tm); link_obj(t); t.parent = root
    c = bpy.data.objects.new("Crown", cm); NOINK.objects.link(c); c.parent = root
    if y < 90: basin(x, y)
    # wind: the whole palm sways from its foot (small, slow), crown adds a little flutter
    ph, amp = rnd.uniform(0, 6.28), rnd.uniform(0.006, 0.012)
    for fr in range(1, FRAMES + 1, 4):
        tt = fr / 30
        root.rotation_euler = (amp * math.sin(tt * 1.3 + ph), amp * 0.7 * math.sin(tt * 0.9 + ph * 1.7), root.rotation_euler[2])
        root.keyframe_insert("rotation_euler", frame=fr)
        c.rotation_euler = (0.012 * math.sin(tt * 2.6 + ph), 0.01 * math.sin(tt * 2.1 + ph), 0)
        c.keyframe_insert("rotation_euler", frame=fr)

pid = 0
for sx in (-1, 1):
    for row in range(5):
        xoff = sx * (W_TOP + 6.5 + row * 7.0); y = 4 + (row % 2) * 4.0
        while y < 260:
            pid += 1
            palm(xoff + random.uniform(-0.8, 0.8), y + random.uniform(-1.0, 1.0), pid)
            y += random.uniform(7.5, 9.0)

# ---------- dust motes ----------
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.014)
mo = bpy.context.active_object; mo.data.materials.append(M_DUST); MOTE = mo.data
for c in list(mo.users_collection): c.objects.unlink(mo)
bpy.data.objects.remove(mo)
rnd = random.Random(11)
for i in range(140):
    d = bpy.data.objects.new("Mote", MOTE); NOINK.objects.link(d)
    base = (rnd.uniform(-5, 4), rnd.uniform(0, 16), rnd.uniform(0.3, 3.2)); ph = rnd.uniform(0, 6.28)
    for fr in range(1, FRAMES + 1, 4):
        tt = fr / 30
        d.location = (base[0] + 0.25 * math.sin(tt * 0.7 + ph) + 0.12 * tt, base[1] + 0.2 * math.cos(tt * 0.5 + ph), base[2] + 0.15 * math.sin(tt * 0.9 + ph * 2))
        d.keyframe_insert("location", frame=fr)

# ---------- camera ----------
bpy.ops.object.camera_add(location=(-3.6, -5.5, 1.55))
cam = bpy.context.active_object; sc.camera = cam
cam.data.lens = 30; cam.data.clip_end = 1500
cam.rotation_euler = (math.radians(91.5), 0, math.radians(-6))
cam.keyframe_insert("location", frame=1)
cam.location = (-3.6, -4.9, 1.58); cam.keyframe_insert("location", frame=FRAMES)
bpy.ops.object.empty_add(type="SINGLE_ARROW", location=(-3.3, 1.5, 0.08)); bpy.context.active_object.name = "HeroMark"

# ---------- ink lines (Freestyle), everything except leaves / water / haze / motes ----------
sc.render.use_freestyle = False  # Freestyle is single-threaded: too slow for hundreds of palms → compositor ink below
sc.render.line_thickness_mode = "ABSOLUTE"; sc.render.line_thickness = 1.0 if PCT < 100 else 1.5
vl = sc.view_layers[0]; vl.use_freestyle = False
fs = vl.freestyle_settings
ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("Ink")
ls.select_by_visibility = True; ls.select_silhouette = True; ls.select_border = True; ls.select_crease = False
ls.select_by_collection = True; ls.collection = NOINK; ls.collection_negation = "EXCLUSIVE"
if ls.linestyle is None: ls.linestyle = bpy.data.linestyles.new("Ink")
ls.linestyle.color = (0.24, 0.12, 0.08); ls.linestyle.thickness = 1.0
try: ls.linestyle.alpha = 0.85
except Exception: pass

# ---------- prototype hero (HERO=1): standing on the walkway, back to camera, looking down the canal at the sun ----------
if os.environ.get("HERO") == "1":
    exec(open(os.path.join(HERE, "hero_asset.py")).read())
    hero, shem = build_hero(loc=(-3.3, 1.5, 0.04), yaw=math.pi + math.radians(8), frames=FRAMES, wind=(1.0, 0.35, 0.0), noink=None)
    # closer camera: behind-left three-quarter, low, the sun beyond him
    cam.animation_data_clear()
    cam.location = (-4.35, -1.55, 1.5); cam.data.lens = 40
    tgt = mathutils.Vector((-3.1, 2.6, 1.45)) if "mathutils" in globals() else None
    import mathutils
    tgt = mathutils.Vector((-3.05, 2.8, 1.42))
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = hero; cam.data.dof.aperture_fstop = 2.8
    for f in range(1, (STILL or FRAMES) + 1): sc.frame_set(f)     # run the cloth simulation up to the rendered frame

# ---------- compositor: bloom ----------
try:
    tree = bpy.data.node_groups.new("CompAnime", "CompositorNodeTree"); sc.compositing_node_group = tree
    tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    vl.use_pass_z = True; vl.use_pass_normal = True
    # EEVEE has no object-index pass → an AOV "ink" = 1 on materials of inked objects
    if "ink" not in vl.aovs: a_ = vl.aovs.add(); a_.name = "ink"; a_.type = "VALUE"
    inked = set()
    for ob in sc.objects:
        if ob.type == "MESH" and NOINK not in ob.users_collection:
            for ms in ob.material_slots:
                if ms.material: inked.add(ms.material)
    for m_ in inked:
        aov = m_.node_tree.nodes.new("ShaderNodeOutputAOV"); aov.aov_name = "ink"; aov.inputs["Value"].default_value = 1.0
    if "geo" not in vl.aovs: a2 = vl.aovs.add(); a2.name = "geo"; a2.type = "VALUE"
    for m_ in bpy.data.materials:
        if m_.node_tree and m_.name != "Haze":
            g_ = m_.node_tree.nodes.new("ShaderNodeOutputAOV"); g_.aov_name = "geo"; g_.inputs["Value"].default_value = 1.0
    gout = tree.nodes.new("NodeGroupOutput"); rl = tree.nodes.new("CompositorNodeRLayers")
    print("RL outputs:", [o.name for o in rl.outputs if o.enabled])
    glare = tree.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = "Bloom"; glare.inputs["Threshold"].default_value = 1.6
    glare.inputs["Strength"].default_value = 0.35; glare.inputs["Size"].default_value = 0.55
    from bpy_extras.object_utils import world_to_camera_view
    sc.frame_set(STILL or 1)
    sp = world_to_camera_view(sc, cam, cam.location + __import__("mathutils").Vector(SUN_DIR) * 1000)
    beams = tree.nodes.new("CompositorNodeGlare")
    beams.inputs["Type"].default_value = "Sun Beams"; beams.inputs["Threshold"].default_value = 1.3
    beams.inputs["Strength"].default_value = 0.55; beams.inputs["Size"].default_value = 0.4
    beams.inputs["Sun Position"].default_value = (sp.x, sp.y)
    tree.links.new(rl.outputs["Image"], glare.inputs["Image"]); tree.links.new(glare.outputs["Image"], beams.inputs["Image"])
    # ---- compositor ink: edges from inverse depth + normals, only on inked objects (pass index 1) ----
    def mnode(op, a=None, b=None):
        n = tree.nodes.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: tree.links.new(x, n.inputs[i])
        return n.outputs[0]
    inv = mnode("MULTIPLY", mnode("DIVIDE", 1.0, rl.outputs["Depth"]), 12.0)
    sob_d = tree.nodes.new("CompositorNodeFilter"); sob_d.inputs["Type"].default_value = "Sobel"
    tree.links.new(inv, sob_d.inputs["Image"])
    sd = tree.nodes.new("CompositorNodeSeparateColor"); tree.links.new(sob_d.outputs[0], sd.inputs[0])
    e_d = mnode("GREATER_THAN", sd.outputs["Red"], 0.35)
    sob_n = tree.nodes.new("CompositorNodeFilter"); sob_n.inputs["Type"].default_value = "Sobel"
    tree.links.new(rl.outputs["Normal"], sob_n.inputs["Image"])
    sn = tree.nodes.new("CompositorNodeSeparateColor"); tree.links.new(sob_n.outputs[0], sn.inputs[0])
    e_n = mnode("GREATER_THAN", mnode("ADD", mnode("ADD", sn.outputs["Red"], sn.outputs["Green"]), sn.outputs["Blue"]), 1.6)
    ink = mnode("MULTIPLY", mnode("MAXIMUM", e_d, e_n), rl.outputs["ink"])
    ink = mnode("MULTIPLY", ink, 0.8)
    mix = tree.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    tree.links.new(ink, mix.inputs["Factor"]); tree.links.new(beams.outputs["Image"], mix.inputs[6]); mix.inputs[7].default_value = (0.22, 0.11, 0.07, 1)
    # aerial perspective: far palms melt into the warm haze (no detail needed far away)
    dmap = tree.nodes.new("ShaderNodeMapRange"); tree.links.new(rl.outputs["Depth"], dmap.inputs["Value"])
    dmap.inputs["From Min"].default_value = 12.0; dmap.inputs["From Max"].default_value = 170.0
    fog = mnode("MULTIPLY", mnode("POWER", dmap.outputs["Result"], 0.75), 0.88)
    fog = mnode("MULTIPLY", fog, rl.outputs["geo"])
    fmix = tree.nodes.new("ShaderNodeMix"); fmix.data_type = "RGBA"
    tree.links.new(fog, fmix.inputs["Factor"]); tree.links.new(mix.outputs[2], fmix.inputs[6]); fmix.inputs[7].default_value = (1.0, 0.8, 0.64, 1)
    tree.links.new(fmix.outputs[2], gout.inputs[0])
except Exception as ex:
    print("COMPOSITOR WARN:", ex)

if STILL:
    sc.frame_set(STILL); sc.render.filepath = os.path.join(OUT, f"anime_{STILL:04d}{'_hero' if os.environ.get('HERO') == '1' else ''}.png")
    bpy.ops.render.render(write_still=True)
else:
    if os.environ.get("HERO") == "1":
        try: sc.render.image_settings.media_type = "VIDEO"     # Blender 5.x: video output is a media type
        except Exception: pass
        sc.render.image_settings.file_format = "FFMPEG"; sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"
        sc.render.ffmpeg.constant_rate_factor = "HIGH"
        sc.render.filepath = os.path.join(OUT, "hero_test_.mp4")
    else:
        sc.render.filepath = os.path.join(OUT, "4A_anime_")
    bpy.ops.render.render(animation=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "env_4A_anime.blend"))
print("ANIME4A DONE", OUT)
