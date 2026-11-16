# v3 · The engineer's office — 3D anime (cel) environment, built from v3-office-study.md.
# Al-Ahsa: the window (pointed arch + mashrabiya lattice) looks over a sea of date palms toward the flat-topped
# Jabal Al-Qarah mesas. Drafting table with a parallel bar, triangles, scale ruler, pencils, architect lamp; plan chest
# with rolled blueprints; Arabic coffee (dallah, finjan, dates); Sadu-pattern rug; round wall clock; canal map;
# split AC; waste basket with crumpled sheets. TOD=sunset|night|dawn sets sun, lamp, sky and the cel palette.
# Run: TOD=sunset Blender -b --factory-startup -P env_office.py -- <out_dir> [frames=120] [still=0|frame] [percent=50] [cam=wide|top]
import sys, os, math, random
import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/office/"
FRAMES = int(argv[1]) if len(argv) > 1 else 120
STILL = int(argv[2]) if len(argv) > 2 else 0
PCT = int(argv[3]) if len(argv) > 3 else 50
CAM = argv[4] if len(argv) > 4 else "wide"
TOD = os.environ.get("TOD", "sunset")
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, PCT
sc.render.fps = 30; sc.frame_start, sc.frame_end = 1, FRAMES
sc.render.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "Standard"
for attr, val in [("taa_render_samples", 24), ("use_shadows", True), ("volumetric_tile_size", "4"),
                  ("volumetric_samples", 48), ("volumetric_end", 40.0)]:
    try: setattr(sc.eevee, attr, val)
    except Exception: pass

NOINK = bpy.data.collections.new("NoInk"); sc.collection.children.link(NOINK)
exec(open(os.path.join(HERE, "toon_lib.py")).read())
exec(open(os.path.join(HERE, "palm_asset.py")).read())
exec(open(os.path.join(HERE, "office_assets.py")).read())

# ---------- time-of-day palette ----------
TODS = {
    "sunset": dict(sun_el=16, sun_az=-62, sun_col=(1.0, 0.72, 0.42), sun_e=3.2, lamp=0.0, fill=(1.0, 0.75, 0.6), fill_e=0, amb=0.06,
                   shadow=(0.42, 0.32, 0.52), mid=(0.8, 0.64, 0.58), lit=(1.25, 1.0, 0.76), rim=(1.0, 0.78, 0.45), rim_amt=0.35,
                   sky=[(0.0, (1.0, 0.8, 0.48)), (0.05, (1.0, 0.6, 0.32)), (0.16, (0.95, 0.5, 0.42)), (0.4, (0.55, 0.42, 0.65)), (0.8, (0.25, 0.3, 0.58))],
                   fog=(1.0, 0.76, 0.6), city=0.0, stars=0.0, ink=(0.2, 0.11, 0.08)),
    "night": dict(sun_el=-20, sun_az=-75, sun_col=(0.4, 0.5, 1.0), sun_e=0.0, lamp=1.0, fill=(0.35, 0.45, 0.9), fill_e=0, amb=0.012,
                  shadow=(0.045, 0.055, 0.13), mid=(0.3, 0.22, 0.24), lit=(1.35, 1.0, 0.68), rim=(0.25, 0.32, 0.6), rim_amt=0.12,
                  sky=[(0.0, (0.2, 0.25, 0.45)), (0.08, (0.1, 0.14, 0.32)), (0.4, (0.04, 0.06, 0.18)), (0.9, (0.02, 0.03, 0.1))],
                  fog=(0.12, 0.15, 0.3), city=1.0, stars=1.0, ink=(0.02, 0.02, 0.05)),
    "dawn": dict(sun_el=2.5, sun_az=105, sun_col=(1.0, 0.82, 0.62), sun_e=0.0, lamp=0.55, fill=(0.62, 0.7, 1.0), fill_e=0, amb=0.032,
                 shadow=(0.24, 0.28, 0.46), mid=(0.62, 0.6, 0.72), lit=(1.18, 1.02, 0.88), rim=(0.85, 0.75, 0.9), rim_amt=0.25,
                 sky=[(0.0, (1.0, 0.78, 0.6)), (0.04, (0.98, 0.66, 0.62)), (0.14, (0.62, 0.62, 0.82)), (0.45, (0.32, 0.42, 0.72)), (0.9, (0.18, 0.24, 0.5))],
                 fog=(0.85, 0.78, 0.82), city=0.4, stars=0.15, ink=(0.12, 0.1, 0.14)),
}
P = TODS[TOD]
el, az = math.radians(P["sun_el"]), math.radians(P["sun_az"])
SUN_DIR = (math.cos(el) * math.sin(az), math.cos(el) * math.cos(az), math.sin(el))   # toward the sun (west = -x)

def cel(nt, out, base, rim_amt=0.35, **kw):
    cel_output(nt, out, base, shadow=P["shadow"], mid=P["mid"], lit=P["lit"], rim=P["rim"], rim_amt=rim_amt * P["rim_amt"] / 0.35, **kw)

def palm_mat(name, leaf=True):
    m, nt, out = new_mat(name)
    ca = nt.nodes.new("ShaderNodeVertexColor"); ca.layer_name = "Col"
    cel(nt, out, ca.outputs["Color"], rim_amt=0.6 if leaf else 0.5)
    return m

def mat_flat(name, c, rim=0.3):
    m, nt, out = new_mat(name); cel(nt, out, flat(nt, c), rim_amt=rim); return m

def mat_tone(name, c1, c2, scale, thresh=0.55, coord="Object", rim=0.3):
    m, nt, out = new_mat(name); cel(nt, out, two_tone(nt, c1, c2, scale, coord, thresh), rim_amt=rim); return m

def mat_emit(name, c, s):
    m, nt, out = new_mat(name)
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*c, 1); e.inputs["Strength"].default_value = s
    nt.links.new(e.outputs[0], out.inputs["Surface"]); return m

def into(ob, coll):
    for c in list(ob.users_collection): c.objects.unlink(ob)
    coll.objects.link(ob); return ob

def mesh(name, V, F, mat=None, coll=None, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if mat: me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); (coll or sc.collection).objects.link(ob); return ob

# ---------- materials ----------
M_PLASTER = mat_tone("Plaster", (0.93, 0.85, 0.72), (0.915, 0.835, 0.705), 2.5)
M_CEIL = mat_flat("Ceiling", (0.95, 0.9, 0.8), 0)
M_WOOD = mat_tone("Wood", (0.42, 0.26, 0.15), (0.36, 0.21, 0.12), 6, coord="Object")
M_WOOD_L = mat_tone("WoodLight", (0.66, 0.47, 0.29), (0.6, 0.42, 0.25), 6)
M_BOARD = mat_flat("BoardLaminate", (0.88, 0.9, 0.86))
M_PAPER = mat_flat("Paper", (0.97, 0.95, 0.88), 0.2)
M_TAPE = mat_flat("MaskingTape", (0.93, 0.84, 0.6))
M_ALU = mat_flat("Aluminium", (0.72, 0.74, 0.78), 0.6)
M_DARK = mat_flat("DarkMetal", (0.15, 0.16, 0.19), 0.5)
M_LAMPGREEN = mat_flat("LampShade", (0.16, 0.3, 0.27), 0.6)
M_BRASS = mat_tone("Brass", (0.86, 0.62, 0.24), (0.7, 0.48, 0.16), 4, rim=0.8)
M_FINJAN = mat_flat("Finjan", (0.96, 0.95, 0.92), 0.4)
M_DATE = mat_flat("Date", (0.42, 0.18, 0.08), 0.5)
M_BLUEPRINT = mat_flat("Blueprint", (0.18, 0.34, 0.6), 0.3)
M_ACRYLIC = mat_flat("Triangle", (0.95, 0.55, 0.3), 0.6)
M_PENCIL = mat_flat("Pencil", (0.95, 0.75, 0.2), 0.4)
M_LEATHER = mat_flat("Leather", (0.32, 0.17, 0.1), 0.4)
M_AC = mat_flat("SplitAC", (0.96, 0.96, 0.95), 0.2)
M_FRAME = mat_flat("Frame", (0.25, 0.16, 0.1), 0.4)
M_BULB = mat_emit("Bulb", (1.0, 0.86, 0.6), 12 * P["lamp"] + 0.2)
M_BINDERS = [mat_flat(f"Binder{i}", c) for i, c in enumerate([(0.15, 0.3, 0.55), (0.62, 0.16, 0.12), (0.2, 0.42, 0.3), (0.88, 0.75, 0.4), (0.3, 0.3, 0.34)])]
M_PLANT = mat_tone("Plant", (0.2, 0.38, 0.14), (0.3, 0.48, 0.16), 3)
M_POT = mat_flat("Pot", (0.68, 0.38, 0.24))
M_CRUMPLE = mat_flat("Crumple", (0.96, 0.94, 0.86), 0.3)
M_BASKET = mat_tone("Wicker", (0.62, 0.45, 0.25), (0.5, 0.35, 0.18), 30)
M_SAND = mat_tone("Mesa", (0.82, 0.6, 0.4), (0.72, 0.5, 0.32), 0.05)
M_OASIS_GROUND = mat_tone("OasisGround", (0.28, 0.36, 0.16), (0.36, 0.42, 0.2), 0.04)
M_CITY = mat_flat("CityBlock", (0.82, 0.74, 0.62))
M_CITY_LIGHT = mat_emit("CityLight", (1.0, 0.82, 0.5), 6 * P["city"])

# floor tiles: 60 cm porcelain with grout lines
M_FLOOR, nt, out = new_mat("FloorTiles")
geo = nt.nodes.new("ShaderNodeNewGeometry"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sp.inputs[0])
def grout(sock):
    w = nt.nodes.new("ShaderNodeMath"); w.operation = "WRAP"; w.inputs[1].default_value = 0; w.inputs[2].default_value = 0.6
    nt.links.new(sock, w.inputs[0]); r = ramp(nt, [(0.0, (0.72, 0.68, 0.62)), (0.015, (1, 1, 1)), (0.985, (0.72, 0.68, 0.62))])
    d = nt.nodes.new("ShaderNodeMath"); d.operation = "DIVIDE"; d.inputs[1].default_value = 0.6
    nt.links.new(w.outputs[0], d.inputs[0]); nt.links.new(d.outputs[0], r.inputs["Fac"]); return r.outputs["Color"]
gx, gy = grout(sp.outputs["X"]), grout(sp.outputs["Y"])
gm = nt.nodes.new("ShaderNodeMix"); gm.data_type = "RGBA"; gm.blend_type = "MULTIPLY"; gm.inputs["Factor"].default_value = 1
nt.links.new(gx, gm.inputs[6]); nt.links.new(gy, gm.inputs[7])
tile = two_tone(nt, (0.86, 0.79, 0.68), (0.82, 0.75, 0.64), 3.0)
gm2 = nt.nodes.new("ShaderNodeMix"); gm2.data_type = "RGBA"; gm2.blend_type = "MULTIPLY"; gm2.inputs["Factor"].default_value = 1
nt.links.new(tile, gm2.inputs[6]); nt.links.new(gm.outputs[2], gm2.inputs[7])
cel(nt, out, gm2.outputs[2], rim_amt=0)

# Al Sadu rug: red field, black/white bands, a zigzag (triangle) border — Saudi Bedouin weaving
M_SADU, nt, out = new_mat("SaduRug")
tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["UV"], sp.inputs[0])
# distance to the long edges (v) → bands; zigzag in the border from |frac(u*k)-.5| vs band position
v_edge = nt.nodes.new("ShaderNodeMath"); v_edge.operation = "PINGPONG"; v_edge.inputs[1].default_value = 0.5
nt.links.new(sp.outputs["Y"], v_edge.inputs[0])
zz = nt.nodes.new("ShaderNodeMath"); zz.operation = "PINGPONG"; zz.inputs[1].default_value = 0.5
uk = nt.nodes.new("ShaderNodeMath"); uk.operation = "MULTIPLY"; uk.inputs[1].default_value = 22
nt.links.new(sp.outputs["X"], uk.inputs[0]); nt.links.new(uk.outputs[0], zz.inputs[0])
zsc = nt.nodes.new("ShaderNodeMath"); zsc.operation = "MULTIPLY_ADD"; zsc.inputs[1].default_value = 0.16; zsc.inputs[2].default_value = 0.06
nt.links.new(zz.outputs[0], zsc.inputs[0])
tri = nt.nodes.new("ShaderNodeMath"); tri.operation = "LESS_THAN"; nt.links.new(v_edge.outputs[0], tri.inputs[0]); nt.links.new(zsc.outputs[0], tri.inputs[1])
bands = ramp(nt, [(0.0, (0.08, 0.06, 0.06)), (0.05, (0.92, 0.88, 0.8)), (0.08, (0.08, 0.06, 0.06)), (0.24, (0.62, 0.1, 0.07)), (0.34, (0.92, 0.88, 0.8)), (0.36, (0.62, 0.1, 0.07)), (0.45, (0.1, 0.07, 0.07)), (0.47, (0.62, 0.1, 0.07))])
nt.links.new(v_edge.outputs[0], bands.inputs["Fac"])
rmix = nt.nodes.new("ShaderNodeMix"); rmix.data_type = "RGBA"
nt.links.new(tri.outputs[0], rmix.inputs["Factor"]); nt.links.new(bands.outputs["Color"], rmix.inputs[6]); rmix.inputs[7].default_value = (0.92, 0.88, 0.8, 1)
cel(nt, out, rmix.outputs[2], rim_amt=0)

# mashrabiya lattice: diagonal grid of thin wooden strips (alpha cut-out → patterned shadows)
M_LATTICE, nt, out = new_mat("Mashrabiya")
tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
def diag(sign):
    a = nt.nodes.new("ShaderNodeMath"); a.operation = "ADD" if sign > 0 else "SUBTRACT"
    nt.links.new(sp.outputs["Y"], a.inputs[0]); nt.links.new(sp.outputs["Z"], a.inputs[1])
    w = nt.nodes.new("ShaderNodeMath"); w.operation = "PINGPONG"; w.inputs[1].default_value = 0.06
    nt.links.new(a.outputs[0], w.inputs[0])
    l = nt.nodes.new("ShaderNodeMath"); l.operation = "LESS_THAN"; l.inputs[1].default_value = 0.012
    nt.links.new(w.outputs[0], l.inputs[0]); return l.outputs[0]
both = nt.nodes.new("ShaderNodeMath"); both.operation = "MAXIMUM"; nt.links.new(diag(1), both.inputs[0]); nt.links.new(diag(-1), both.inputs[1])
cel(nt, out, flat(nt, (0.34, 0.2, 0.11)), rim_amt=0.2, alpha_socket=both.outputs[0])
try: M_LATTICE.surface_render_method = "DITHERED"
except Exception: pass

# canal-network map in a frame (blue canals over beige, a few branches)
M_MAP, nt, out = new_mat("CanalMap")
tc = nt.nodes.new("ShaderNodeTexCoord"); vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = "DISTANCE_TO_EDGE"
vor.inputs["Scale"].default_value = 5; nt.links.new(tc.outputs["UV"], vor.inputs["Vector"])
mr = ramp(nt, [(0.0, (0.2, 0.4, 0.7)), (0.025, (0.93, 0.88, 0.74))])
nt.links.new(vor.outputs["Distance"], mr.inputs["Fac"])
cel(nt, out, mr.outputs["Color"], rim_amt=0)

# ---------- room shell (x: -2.6..2.6, y: -2.4..2.8, z: 0..3.2); window in the LEFT wall (x = -2.6) ----------
X0, X1, Y0, Y1, H = -2.6, 2.6, -2.4, 2.8, 3.2
GROUND = -9.0                                               # 3rd floor: look over the palm crowns
WY0, WY1, WZ0, WZS, WZT = -0.35, 1.75, 0.85, 2.25, 2.85      # window: y range, sill, arch spring, arch apex
mesh("Floor", [(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0)], [(0, 1, 2, 3)], M_FLOOR)
mesh("Ceiling", [(X0, Y0, H), (X0, Y1, H), (X1, Y1, H), (X1, Y0, H)], [(0, 1, 2, 3)], M_CEIL)
mesh("WallBack", [(X0, Y1, 0), (X1, Y1, 0), (X1, Y1, H), (X0, Y1, H)], [(0, 1, 2, 3)], M_PLASTER)
mesh("WallRight", [(X1, Y1, 0), (X1, Y0, 0), (X1, Y0, H), (X1, Y1, H)], [(0, 1, 2, 3)], M_PLASTER)
# left wall around the arched opening
mesh("WallL_below", [(X0, Y0, 0), (X0, Y1, 0), (X0, Y1, WZ0), (X0, Y0, WZ0)], [(0, 1, 2, 3)], M_PLASTER)
mesh("WallL_front", [(X0, Y0, WZ0), (X0, WY0, WZ0), (X0, WY0, H), (X0, Y0, H)], [(0, 1, 2, 3)], M_PLASTER)
mesh("WallL_back", [(X0, WY1, WZ0), (X0, Y1, WZ0), (X0, Y1, H), (X0, WY1, H)], [(0, 1, 2, 3)], M_PLASTER)
arch = []
half = (WY1 - WY0) / 2; cy = (WY0 + WY1) / 2; R = half * 1.55
c1, c2 = WY0 + R, WY1 - R                                  # each half's centre sits on the other side
th_apex = math.acos((cy - c1) / R)                          # left arc ends at the apex (y = cy)
for i in range(13):                                          # left arc: from the spring point up to the apex
    th = math.pi - (math.pi - th_apex) * i / 12
    arch.append((X0, c1 + R * math.cos(th), WZS + R * math.sin(th)))
for i in range(1, 13):                                       # right arc: mirror
    th = th_apex - th_apex * i / 12
    th2 = math.pi - th
    arch.append((X0, c2 - R * math.cos(th2) * -1 if False else c2 + R * math.cos(th), WZS + R * math.sin(th)))
apex = max(p[2] for p in arch)
AV, AF = [], []
for k, p_ in enumerate(arch):
    AV += [p_, (X0, p_[1], H)]
for k in range(len(arch) - 1):
    a = 2 * k; AF.append((a, a + 1, a + 3, a + 2))
mesh("WallL_arch", AV, AF, M_PLASTER)
# deep window reveal (wall thickness 0.3) so the opening reads as masonry
T = 0.3
mesh("RevealSill", [(X0, WY0, WZ0), (X0 - T, WY0, WZ0), (X0 - T, WY1, WZ0), (X0, WY1, WZ0)], [(0, 1, 2, 3)], M_PLASTER)
mesh("RevealL", [(X0, WY0, WZ0), (X0, WY0, WZS), (X0 - T, WY0, WZS), (X0 - T, WY0, WZ0)], [(0, 1, 2, 3)], M_PLASTER)
mesh("RevealR", [(X0, WY1, WZ0), (X0 - T, WY1, WZ0), (X0 - T, WY1, WZS), (X0, WY1, WZS)], [(0, 1, 2, 3)], M_PLASTER)
RV, RF = [], []
for i, p in enumerate(arch):
    RV += [p, (X0 - T, p[1], p[2])]
for i in range(len(arch) - 1):
    a = 2 * i; RF.append((a, a + 2, a + 3, a + 1))
mesh("RevealArch", RV, RF, M_PLASTER)
# wooden window frame + mullions + a marble sill
rbox("Sill", (0.42, WY1 - WY0 + 0.2, 0.05), (X0 - 0.08, (WY0 + WY1) / 2, WZ0 - 0.02), bevel=0.012, mat=mat_flat("Marble", (0.95, 0.93, 0.88), 0.4))
for yy in (WY0 + 0.03, (WY0 + WY1) / 2, WY1 - 0.03):
    rbox("Mullion", (0.06, 0.06, WZS - WZ0), (X0 - 0.2, yy, (WZ0 + WZS) / 2), bevel=0.008, mat=M_WOOD)
for zz in (WZ0 + 0.03, 1.55, WZS):
    rbox("Transom", (0.06, WY1 - WY0, 0.05), (X0 - 0.2, (WY0 + WY1) / 2, zz), bevel=0.008, mat=M_WOOD)
tube("ArchFrame", [(X0 - 0.2, p[1], p[2] - 0.02) for p in arch], 0.03, mat=M_WOOD)
# mashrabiya lattice over the lower half of the back sash (casts patterned light)
lat = mesh("Mashrabiya", [(X0 - 0.16, (WY0 + WY1) / 2 + 0.03, WZ0 + 0.05), (X0 - 0.16, WY1 - 0.05, WZ0 + 0.05),
                          (X0 - 0.16, WY1 - 0.05, 1.53), (X0 - 0.16, (WY0 + WY1) / 2 + 0.03, 1.53)], [(0, 1, 2, 3)], M_LATTICE)
into(lat, NOINK)
# curtains: heavy cream fabric, deep folds, tied back
def curtain(name, y0, y1, side):
    V, F = [], []
    nx, nz = 28, 18
    for j in range(nz + 1):
        z = 0.12 + (H - 0.25) * j / nz
        tie = 1.0 - 0.55 * math.exp(-((z - 1.25) / 0.35) ** 2)   # gathered at the tie-back height
        for i in range(nx + 1):
            u = i / nx
            yy = y0 + (y1 - y0) * u * tie if side < 0 else y1 - (y1 - y0) * u * tie
            fold = 0.05 * math.sin(u * math.pi * 9) * (0.6 + 0.4 * tie)
            V.append((X0 + 0.12 + fold, yy, z))
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
    return mesh(name, V, F, mat_tone("Curtain", (0.93, 0.86, 0.72), (0.88, 0.8, 0.66), 3, rim=0.5), coll=NOINK, smooth=True)
# heavy drapes (muted teal, contrasts with the cream wall) + a white voile sheer drawn partly across the window
M_DRAPE, nt, out = new_mat("Drape"); _dc = nt.nodes.new("ShaderNodeVertexColor"); _dc.layer_name = "Col"
cel(nt, out, _dc.outputs["Color"], rim_amt=0.5, translucent=0.25)
M_SHEER, nt, out = new_mat("Sheer"); _sc = nt.nodes.new("ShaderNodeVertexColor"); _sc.layer_name = "Col"
_sv = nt.nodes.new("ShaderNodeValue"); _sv.outputs[0].default_value = 0.55
cel(nt, out, _sc.outputs["Color"], rim_amt=0.6, translucent=0.9, alpha_socket=_sv.outputs[0])
try: M_SHEER.surface_render_method = "DITHERED"
except Exception: pass
TEAL, TEAL_BAND = (0.2, 0.38, 0.4), (0.13, 0.26, 0.28)
ROD_X = X0 + 0.24
drape("DrapeL", X0 + 0.15, WY0 - 0.85, WY0 + 0.12, H - 0.16, 0.01, M_DRAPE, coll=NOINK, tie_z=1.12, tie_w=0.2, base_col=TEAL, band_col=TEAL_BAND, seed=1, rings_mat=M_BRASS, rod_x=ROD_X)
drape("DrapeR", X0 + 0.15, WY1 + 0.85, WY1 - 0.12, H - 0.16, 0.01, M_DRAPE, coll=NOINK, tie_z=1.12, tie_w=0.2, base_col=TEAL, band_col=TEAL_BAND, seed=2, rings_mat=M_BRASS, rod_x=ROD_X)
drape("Sheer", X0 + 0.07, WY1 + 0.05, (WY0 + WY1) / 2 - 0.05, H - 0.2, WZ0 - 0.04, M_SHEER, coll=NOINK, fullness=3.0, pleat=0.1,
      base_col=(0.97, 0.96, 0.92), band_col=(0.93, 0.92, 0.88), seed=3)
tube("SheerRod", [(X0 + 0.1, WY0 - 0.9, H - 0.17), (X0 + 0.1, WY1 + 0.9, H - 0.17)], 0.008, mat=M_BRASS)
for yy in (WY0 - 0.72, WY1 + 0.72):                      # tasselled tie-backs
    tube("TieBack", [(X0 + 0.02, yy, 1.12), (X0 + 0.2, yy + (0.08 if yy > 0 else -0.08), 1.12), (X0 + 0.26, yy, 1.1)], 0.011, mat=M_BRASS, segs=6)
tube("CurtainRod", [(ROD_X, WY0 - 1.0, H - 0.13), (ROD_X, WY1 + 1.0, H - 0.13)], 0.017, mat=M_BRASS)
for yy in (WY0 - 1.0, WY1 + 1.0):                        # finials
    lathe("Finial", [(0.0, -0.05), (0.03, -0.035), (0.035, 0.0), (0.02, 0.03), (0.008, 0.05), (0.0, 0.06)], 16, mat=M_BRASS).location = (ROD_X, yy, H - 0.13)
# skirting board
for nm, a, b in [("SkirtB", (X0, Y1 - 0.01), (X1, Y1 - 0.01)), ("SkirtR", (X1 - 0.01, Y0), (X1 - 0.01, Y1))]:
    rbox(nm, (abs(b[0] - a[0]) + 0.02, abs(b[1] - a[1]) + 0.02, 0.1), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.05), bevel=0.005, mat=M_WOOD)

# ---------- drafting table (board 1.2 × 0.9, tilted 15°) ----------
DX, DY = -1.35, 0.7                 # centre of the table, close to the window
tilt = math.radians(15)
board_z = 0.95
for sy in (-0.52, 0.52):            # A-frame legs (dark wood) + feet
    tube("Leg", [(DX - 0.35, DY + sy, 0.02), (DX - 0.05, DY + sy, board_z - 0.06)], 0.03, mat=M_WOOD)
    tube("Leg", [(DX + 0.35, DY + sy, 0.02), (DX + 0.05, DY + sy, board_z - 0.06)], 0.03, mat=M_WOOD)
    rbox("Foot", (0.8, 0.07, 0.04), (DX, DY + sy, 0.02), bevel=0.01, mat=M_WOOD)
tube("Stretcher", [(DX, DY - 0.52, 0.35), (DX, DY + 0.52, 0.35)], 0.022, mat=M_WOOD)
# board faces the engineer (he sits on +x side, looking toward the window / -x)
board = rbox("Board", (0.9, 1.2, 0.035), (DX, DY, board_z), rot=(0, tilt, 0), bevel=0.008, mat=M_BOARD)
def on_board(u, v, h=0.02):
    """Point on the board surface: u along the slope (−0.45..0.45, + = far/high edge), v across (−0.6..0.6)."""
    return (DX - u * math.cos(tilt) + 0.0, DY + v, board_z + u * math.sin(tilt) + h * math.cos(tilt))
rbox("BoardEdge", (0.04, 1.22, 0.05), on_board(-0.46, 0, 0.0), rot=(0, tilt, 0), bevel=0.01, mat=M_WOOD_L)
rbox("PencilLedge", (0.07, 1.2, 0.02), on_board(-0.49, 0, 0.03), rot=(0, tilt, 0), bevel=0.006, mat=M_WOOD_L)
sheet = rbox("DrawingSheet", (0.6, 0.84, 0.002), on_board(0.02, 0.0, 0.019), rot=(0, tilt, 0), bevel=0, mat=M_PAPER)
for (u, v) in [(-0.27, -0.4), (-0.27, 0.4), (0.31, -0.4), (0.31, 0.4)]:
    rbox("Tape", (0.05, 0.07, 0.002), on_board(u, v, 0.021), rot=(0, tilt, math.radians(random.uniform(-25, 25))), bevel=0, mat=M_TAPE)
# parallel bar across the board + its cables and end caps
pb = rbox("ParallelBar", (0.055, 1.18, 0.018), on_board(-0.12, 0, 0.032), rot=(0, tilt, 0), bevel=0.004, mat=M_ALU)
for v in (-0.6, 0.6):
    rbox("BarCap", (0.07, 0.03, 0.03), on_board(-0.12, v, 0.032), rot=(0, tilt, 0), bevel=0.006, mat=M_DARK)
    tube("Cable", [on_board(-0.45, v, 0.025), on_board(0.45, v, 0.025)], 0.0015, mat=M_DARK, segs=4)
# triangles (45° and 30/60°), with cut-out centre
def triangle(name, pts, u0, v0, rotz):
    V, F = [], []
    cx = sum(p[0] for p in pts) / 3; cy = sum(p[1] for p in pts) / 3
    inner = [(cx + (p[0] - cx) * 0.45, cy + (p[1] - cy) * 0.45) for p in pts]
    ring = pts + inner
    c, s = math.cos(rotz), math.sin(rotz)
    for (a, b) in ring:
        a2, b2 = a * c - b * s, a * s + b * c
        V.append(on_board(u0 + a2, v0 + b2, 0.026))
    F = [(0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    return mesh(name, V, F, M_ACRYLIC)
triangle("Set45", [(0, 0), (0.22, 0), (0, 0.22)], -0.08, 0.05, 0.2)
triangle("Set3060", [(0, 0), (0.3, 0), (0, 0.17)], 0.05, -0.32, -0.4)
# triangular scale ruler and pencils on the ledge
tube("ScaleRuler", [on_board(-0.5, -0.45, 0.06), on_board(-0.5, -0.15, 0.06)], 0.014, mat=M_ALU, segs=3)
for k in range(3):
    tube("Pencil", [on_board(-0.5, 0.05 + 0.07 * k, 0.05), on_board(-0.5, 0.2 + 0.07 * k, 0.05)], 0.0045, mat=M_PENCIL, segs=6,
         taper=lambda t: 1.0 if t < 0.9 else max(0.1, (1 - t) * 10))
tube("Compass", [on_board(-0.1, 0.32, 0.03), on_board(0.02, 0.36, 0.09), on_board(0.1, 0.4, 0.03)], 0.004, mat=M_ALU, segs=6)
# architect lamp clamped on the board's high-left corner, shade over the sheet
lamp_base = on_board(0.46, 0.55, 0.03)
j1 = (lamp_base[0] + 0.05, lamp_base[1] - 0.05, lamp_base[2] + 0.45)
j2 = (j1[0] + 0.38, j1[1] - 0.22, j1[2] + 0.12)
rbox("LampClamp", (0.06, 0.05, 0.08), lamp_base, bevel=0.008, mat=M_DARK)
for off in (-0.012, 0.012):
    tube("LampArm1", [(lamp_base[0], lamp_base[1] + off, lamp_base[2]), (j1[0], j1[1] + off, j1[2])], 0.006, mat=M_DARK, segs=6)
    tube("LampArm2", [(j1[0], j1[1] + off, j1[2]), (j2[0], j2[1] + off, j2[2])], 0.006, mat=M_DARK, segs=6)
spring = [(lamp_base[0] + 0.02 + 0.03 * math.cos(t * 0.8) * 0, lamp_base[1] + 0.012 * math.cos(t), lamp_base[2] + 0.1 + 0.25 * t / 40 + 0.006 * math.sin(t)) for t in range(0, 41)]
tube("LampSpring", spring, 0.0018, mat=M_ALU, segs=4)
shade = lathe("LampShade", [(0.012, 0.0), (0.03, -0.01), (0.05, -0.06), (0.09, -0.15), (0.095, -0.155)], 32, mat=M_LAMPGREEN)
shade.location = j2; shade.rotation_euler = (0, math.radians(-30), 0)
bulb = lathe("Bulb", [(0.0, -0.06), (0.03, -0.07), (0.035, -0.1), (0.0, -0.125)], 16, mat=M_BULB, cap_bottom=False)
bulb.location = j2; bulb.rotation_euler = shade.rotation_euler
into(bulb, NOINK)
bpy.ops.object.light_add(type="SPOT", location=(j2[0], j2[1], j2[2] - 0.06))
lamp = bpy.context.active_object; lamp.name = "LampLight"
lamp.data.energy = 320 * P["lamp"]; lamp.data.color = (1.0, 0.82, 0.58); lamp.data.spot_size = math.radians(80)
lamp.data.spot_blend = 0.6; lamp.data.shadow_soft_size = 0.04
import mathutils
aim = mathutils.Vector(on_board(0.0, 0.05, 0.02)) - mathutils.Vector(lamp.location)
lamp.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
shade.rotation_euler = lamp.rotation_euler; bulb.rotation_euler = lamp.rotation_euler
lamp.location = mathutils.Vector(j2) + aim.normalized() * 0.11          # just inside the shade's mouth
for o_ in (shade, bulb):
    try: o_.visible_shadow = False
    except Exception: pass
lamp.data.spot_size = math.radians(62)
# drafting stool (engineer's seat, +x side of the table)
SX, SY = DX + 0.75, DY
lathe("StoolSeat", [(0.0, 0.66), (0.2, 0.66), (0.21, 0.69), (0.2, 0.72), (0.0, 0.72)], 32, mat=M_LEATHER).location = (SX, SY, 0)
tube("StoolPost", [(SX, SY, 0.08), (SX, SY, 0.66)], 0.025, mat=M_ALU)
tube("StoolRing", [(SX + 0.22 * math.cos(a), SY + 0.22 * math.sin(a), 0.3) for a in [i * math.pi / 12 for i in range(25)]], 0.009, mat=M_ALU, segs=6)
for k in range(5):
    a = 2 * math.pi * k / 5
    tube("StoolStar", [(SX, SY, 0.08), (SX + 0.3 * math.cos(a), SY + 0.3 * math.sin(a), 0.05)], 0.018, mat=M_DARK, segs=6)

# ---------- side table with Arabic coffee (dallah, finjan, dates) ----------
TX, TY = DX + 0.2, DY + 1.0
lathe("SideTableTop", [(0.0, 0.58), (0.28, 0.58), (0.29, 0.6), (0.28, 0.62), (0.0, 0.62)], 32, mat=M_WOOD).location = (TX, TY, 0)
tube("SideTableLeg", [(TX, TY, 0.0), (TX, TY, 0.58)], 0.03, mat=M_WOOD)
lathe("SideTableBase", [(0.0, 0.0), (0.18, 0.0), (0.16, 0.03), (0.0, 0.03)], 24, mat=M_WOOD).location = (TX, TY, 0)
lathe("Tray", [(0.0, 0.62), (0.2, 0.62), (0.215, 0.645), (0.22, 0.65)], 40, mat=M_BRASS).location = (TX, TY, 0)
# dallah: belly, waist, tall neck, crown lid with finial, beak spout, handle (Gulf dallah silhouette)
dprof = [(0.0, 0.0), (0.05, 0.0), (0.07, 0.03), (0.075, 0.07), (0.062, 0.11), (0.038, 0.15), (0.03, 0.2), (0.034, 0.24),
         (0.05, 0.26), (0.045, 0.27), (0.028, 0.3), (0.012, 0.33), (0.008, 0.36), (0.0, 0.37)]
dl = lathe("Dallah", dprof, 36, mat=M_BRASS, cap_top=False); dl.location = (TX - 0.06, TY + 0.05, 0.65)
sp0 = (TX - 0.06 + 0.06, TY + 0.05, 0.65 + 0.08)
spout = [sp0, (sp0[0] + 0.05, sp0[1], sp0[2] + 0.06), (sp0[0] + 0.09, sp0[1], sp0[2] + 0.14), (sp0[0] + 0.12, sp0[1], sp0[2] + 0.2), (sp0[0] + 0.17, sp0[1], sp0[2] + 0.22)]
tube("DallahSpout", spout, 0.014, mat=M_BRASS, taper=lambda t: 1 - 0.55 * t)
hb = (TX - 0.06 - 0.06, TY + 0.05, 0.65)
tube("DallahHandle", [(hb[0] + 0.01, hb[1], hb[2] + 0.06), (hb[0] - 0.05, hb[1], hb[2] + 0.1), (hb[0] - 0.06, hb[1], hb[2] + 0.18), (hb[0] - 0.03, hb[1], hb[2] + 0.25), (hb[0] + 0.03, hb[1], hb[2] + 0.255)], 0.007, mat=M_BRASS)
for k, (ox, oy) in enumerate([(0.1, -0.08), (0.12, 0.02), (0.06, -0.14)]):
    f = lathe("Finjan", [(0.0, 0.0), (0.017, 0.0), (0.021, 0.012), (0.027, 0.04), (0.028, 0.045)], 24, mat=M_FINJAN, cap_bottom=True)
    f.location = (TX + ox, TY + oy, 0.65)
plate = lathe("DatesPlate", [(0.0, 0.0), (0.07, 0.0), (0.1, 0.015), (0.105, 0.018)], 32, mat=M_FINJAN); plate.location = (TX - 0.02, TY - 0.13, 0.65)
rnd = random.Random(3)
for k in range(9):
    a = rnd.uniform(0, 6.28); r = rnd.uniform(0, 0.055)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.012, location=(TX - 0.02 + r * math.cos(a), TY - 0.13 + r * math.sin(a), 0.675))
    d = bpy.context.active_object; d.scale = (1.0, 0.7, 0.65); d.rotation_euler = (0, 0, rnd.uniform(0, 3)); d.data.materials.append(M_DATE)
    for p in d.data.polygons: p.use_smooth = True
    into(d, NOINK)

# ---------- plan chest with rolled blueprints (right of the window, against the back wall) ----------
PCX, PCY = -1.6, Y1 - 0.45
rbox("PlanChest", (1.3, 0.85, 0.75), (PCX, PCY, 0.38), bevel=0.015, mat=M_WOOD_L)
for k in range(4):
    z = 0.12 + k * 0.17
    rbox("Drawer", (1.22, 0.02, 0.14), (PCX, PCY - 0.43, z), bevel=0.006, mat=M_WOOD_L)
    tube("Handle", [(PCX - 0.15, PCY - 0.46, z), (PCX + 0.15, PCY - 0.46, z)], 0.008, mat=M_BRASS, segs=6)
for k in range(5):
    y = PCY - 0.25 + k * 0.12; L = random.uniform(0.75, 0.95)
    r = random.uniform(0.035, 0.05)
    tube("Roll", [(PCX - L / 2, y, 0.78 + r), (PCX + L / 2, y, 0.78 + r)], r, mat=M_PAPER if k % 2 else M_BLUEPRINT, segs=14)
bin_ = lathe("RollBin", [(0.0, 0.0), (0.16, 0.0), (0.165, 0.55), (0.17, 0.56)], 28, mat=M_DARK); bin_.location = (PCX + 0.9, PCY - 0.05, 0)
for k in range(6):
    a = k * 1.1; r = 0.08
    x0, y0 = PCX + 0.9 + r * math.cos(a), PCY - 0.05 + r * math.sin(a)
    tube("BinRoll", [(x0, y0, 0.05), (x0 + 0.04 * math.cos(a), y0 + 0.04 * math.sin(a), 0.95 + 0.1 * (k % 3))], 0.035, mat=M_PAPER if k % 2 else M_BLUEPRINT, segs=12)

# ---------- shelf with detailed books (back wall, right) ----------
SHX, SHY = 0.9, Y1 - 0.18
BOOK_VARIANTS = [((0.15, 0.28, 0.52), (0.1, 0.18, 0.35), (0.9, 0.84, 0.66)), ((0.58, 0.14, 0.1), (0.36, 0.08, 0.06), (0.92, 0.85, 0.62)),
                 ((0.18, 0.4, 0.28), (0.1, 0.25, 0.17), (0.9, 0.82, 0.6)), ((0.85, 0.72, 0.42), (0.55, 0.42, 0.2), (0.3, 0.18, 0.1)),
                 ((0.28, 0.27, 0.32), (0.15, 0.15, 0.18), (0.85, 0.75, 0.5)), ((0.45, 0.25, 0.14), (0.28, 0.14, 0.08), (0.9, 0.8, 0.55))]
B_MESHES = book_meshes(BOOK_VARIANTS)
M_COVER, nt, out = new_mat("BookCover"); _ca = nt.nodes.new("ShaderNodeVertexColor"); _ca.layer_name = "Col"; cel(nt, out, _ca.outputs["Color"], rim_amt=0.3)
M_PAGES, nt, out = new_mat("BookPages")
_tc = nt.nodes.new("ShaderNodeTexCoord"); _wv = nt.nodes.new("ShaderNodeTexWave"); _wv.wave_type = "BANDS"; _wv.bands_direction = "X"; _wv.inputs["Scale"].default_value = 120
nt.links.new(_tc.outputs["Object"], _wv.inputs["Vector"])
_pr = ramp(nt, [(0.0, (0.86, 0.82, 0.72)), (0.5, (0.97, 0.94, 0.85))]); nt.links.new(_wv.outputs["Fac"], _pr.inputs["Fac"]); cel(nt, out, _pr.outputs["Color"], rim_amt=0.1)
for me_ in B_MESHES: me_.materials.append(M_COVER); me_.materials.append(M_PAGES)
for k, z in enumerate((1.35, 1.75, 2.15)):
    rbox("Shelf", (1.5, 0.3, 0.03), (SHX, SHY, z), bevel=0.006, mat=M_WOOD)
    fill_shelf(B_MESHES, None, SHX - 0.72, SHX + 0.72, SHY - 0.1, z + 0.015, seed=10 + k)
for zb in (1.35, 1.75, 2.15):
    for sx_ in (-0.74, 0.74):
        rbox("Bracket", (0.02, 0.26, 0.12), (SHX + sx_, SHY, zb - 0.07), bevel=0.004, mat=M_DARK)
# a few books lying on the plan chest too
for k in range(3):
    ob_ = bpy.data.objects.new("ChestBook", B_MESHES[k]); sc.collection.objects.link(ob_)
    ob_.rotation_euler = (0, math.radians(90), 0.15 * k); ob_.location = (-1.0, Y1 - 0.5, 0.775 + 0.04 * k + 0.018)

# ---------- wall clock (right wall), canal map, split AC ----------
def wall_group(name, loc):
    """Empty facing -Y (into the room) from the back wall; children are built facing +Z."""
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e)
    e.location = loc; e.rotation_euler = (math.radians(90), 0, 0); return e
CK = wall_group("Clock", (-0.15, Y1 - 0.02, 2.3))
def kid(o): o.parent = CK; return o
kid(lathe("ClockRim", [(0.0, 0.0), (0.24, 0.0), (0.26, 0.02), (0.255, 0.05), (0.235, 0.06), (0.226, 0.045), (0.226, 0.03)], 48, mat=M_FRAME))
kid(lathe("ClockFace", [(0.0, 0.035), (0.225, 0.035)], 48, mat=M_FINJAN))
for h in range(12):
    a = 2 * math.pi * h / 12; L = 0.035 if h % 3 == 0 else 0.018
    kid(tube("Tick", [(0.2 * math.sin(a), 0.2 * math.cos(a), 0.038), ((0.2 - L) * math.sin(a), (0.2 - L) * math.cos(a), 0.038)], 0.005 if h % 3 == 0 else 0.0025, mat=M_DARK, segs=4))
def hand(name, length, width, angle_deg, z):
    hd = bpy.data.objects.new(name, None); sc.collection.objects.link(hd); hd.parent = CK; hd.location = (0, 0, z)
    t = tube(name + "Geo", [(0, -0.02, 0), (0, length, 0)], width, mat=M_DARK, segs=4); t.parent = hd
    hd.rotation_euler = (0, 0, math.radians(-angle_deg)); return hd
HOUR = {"sunset": 6.25, "night": 23.5, "dawn": 5.6}[TOD]
h_hand = hand("HourHand", 0.11, 0.008, (HOUR % 12) * 30, 0.042)
m_hand = hand("MinuteHand", 0.17, 0.005, (HOUR % 1) * 360, 0.046)
kid(tube("ClockPin", [(0, 0, 0.035), (0, 0, 0.05)], 0.008, mat=M_BRASS, segs=8))
MP = wall_group("CanalMapFrame", (-1.6, Y1 - 0.02, 1.85))
f_ = rbox("MapFrame", (1.0, 0.72, 0.03), (0, 0, 0.015), bevel=0.008, mat=M_FRAME); f_.parent = MP
mp = mesh("Map", [(-0.46, -0.32, 0.032), (0.46, -0.32, 0.032), (0.46, 0.32, 0.032), (-0.46, 0.32, 0.032)], [(0, 1, 2, 3)], M_MAP); mp.parent = MP
uvm = mp.data.uv_layers.new(name="UV")
for li, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uvm.data[li].uv = (u, v)
rbox("SplitAC", (0.95, 0.24, 0.3), (0.95, Y1 - 0.14, 2.75), bevel=0.06, mat=M_AC, segments=4)
rbox("ACVent", (0.85, 0.02, 0.04), (0.95, Y1 - 0.27, 2.64), bevel=0.01, mat=mat_flat("ACVent", (0.8, 0.8, 0.8)))
M_SADU2 = sadu_material(cel, new_mat, ramp, k=2.0)
M_FRINGE = mat_flat("Fringe", (0.9, 0.85, 0.75), 0.2)
sadu_rug("SaduRug", -0.05, 0.2, 4.7, 4.5, M_SADU2, M_FRINGE, coll=NOINK, tassels=120)
# potted plant (right of the door side)
lathe("Pot", [(0.0, 0.0), (0.12, 0.0), (0.16, 0.3), (0.17, 0.32)], 24, mat=M_POT).location = (X1 - 0.35, Y1 - 0.4, 0)
rnd = random.Random(5)
for k in range(14):
    a = rnd.uniform(0, 6.28); l = rnd.uniform(0.35, 0.7); up = rnd.uniform(0.6, 1.1)
    base = (X1 - 0.35, Y1 - 0.4, 0.3)
    pts = [(base[0] + l * t * math.cos(a), base[1] + l * t * math.sin(a), base[2] + l * up * t - 0.25 * l * t * t) for t in (0, 0.33, 0.66, 1)]
    tube("Leaf", pts, 0.03, mat=M_PLANT, segs=4, taper=lambda t: 0.4 + math.sin(math.pi * t))
# waste basket with crumpled sheets (one missed the basket)
WBX, WBY = DX + 0.55, DY - 0.75
lathe("Basket", [(0.0, 0.0), (0.13, 0.0), (0.17, 0.36), (0.175, 0.37)], 28, mat=M_BASKET, cap_top=False).location = (WBX, WBY, 0)
def crumple(name, loc, r, seed):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=loc)
    o = bpy.context.active_object; o.name = name
    rr = random.Random(seed)
    for v in o.data.vertices:
        k = 1 + rr.uniform(-0.28, 0.22); v.co = v.co * k
    o.data.materials.append(M_CRUMPLE); return o
for k in range(4): crumple("Crumple", (WBX + random.uniform(-0.06, 0.06), WBY + random.uniform(-0.06, 0.06), 0.3 + 0.03 * k), 0.06, k)
crumple("CrumpleFloor", (WBX + 0.35, WBY + 0.2, 0.055), 0.055, 9)

# ---------- outside: the Al-Ahsa oasis (sea of palm crowns) + Jabal Al-Qarah + low city ----------
OUTC = bpy.data.collections.new("Outside"); sc.collection.children.link(OUTC)
mesh("OasisGround", [(-6000, -6000, GROUND), (-3, -6000, GROUND), (-3, 6000, GROUND), (-6000, 6000, GROUND)], [(0, 1, 2, 3)], M_OASIS_GROUND, OUTC)
M_PT, M_PL = palm_mat("PalmTrunkOut", leaf=False), palm_mat("PalmLeafOut")
def variants(specs):
    vs = []
    for k, (seed, hgt, lod, dates) in enumerate(specs):
        tm, cm = build_palm(seed=seed, height=hgt, lod=lod, dates=dates, name=f"OPalm{seed}_{lod}")
        tm.materials.append(M_PT); cm.materials.append(M_PL); vs.append((tm, cm))
    return vs
NEAR_V = variants([(3, 8.2, 1.0, True), (7, 8.8, 1.0, True), (11, 7.6, 1.0, True)])     # the same detailed palm as the canal
MID_V = variants([(5, 8.4, 0.45, False), (9, 7.8, 0.45, False)])
FAR_V = variants([(13, 8.0, 0.2, False)])
def place_palm(x, y, vs, rnd):
    tm, cm = rnd.choice(vs)
    root = bpy.data.objects.new("OPalm", None); OUTC.objects.link(root); root.location = (x, y, GROUND)
    root.rotation_euler = (rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03), rnd.uniform(0, 6.28)); s_ = rnd.uniform(0.88, 1.15); root.scale = (s_, s_, s_)
    a = bpy.data.objects.new("T", tm); OUTC.objects.link(a); a.parent = root
    b = bpy.data.objects.new("C", cm); NOINK.objects.link(b); b.parent = root
rnd = random.Random(21)
# farm rows: palms planted on a grid (~8 m), slightly jittered, filling the window's view
for gx in range(1, 90):
    x = -4.0 - gx * 7.5
    vs = NEAR_V if -x < 45 else (MID_V if -x < 220 else FAR_V)
    spread = 18 + (-x) * 0.75
    gy = -spread
    while gy < spread + 8:
        if rnd.random() > 0.06:
            place_palm(x + rnd.uniform(-1.5, 1.5), gy + rnd.uniform(-1.5, 1.5), vs, rnd)
        gy += 7.5 * (1 if -x < 220 else 1.6)
# low city among the farms (lights at night)
for i in range(30):
    x = -rnd.uniform(250, 900); y = rnd.uniform(-500, 600); w = rnd.uniform(10, 26); d = rnd.uniform(10, 26); h = rnd.uniform(6, 16)
    rbox("Block", (w, d, h), (x, y, GROUND + h / 2), bevel=0, mat=M_CITY, coll=OUTC)
    if P["city"] > 0:
        for k in range(rnd.randint(3, 8)):
            rbox("Win", (0.3, 1.4, 1.0), (x + w / 2 + 0.16, y + rnd.uniform(-d / 2.5, d / 2.5), GROUND + rnd.uniform(2, h - 1)), bevel=0, mat=M_CITY_LIGHT, coll=NOINK)
# Jabal Al-Qarah: flat-topped mesas on the horizon, in the window's line of sight
QH = 92.0                                                  # 75 m in reality, lifted a little for the anime framing
M_QARAH = qarah_material(cel, new_mat, ramp, QH)
for i, (x, y, rx, ry, hm) in enumerate([(-1250, 180, 380, 220, 1.0), (-1700, -420, 460, 260, 0.85), (-1500, 760, 300, 190, 0.72)]):
    qarah_mesa(f"Qarah{i}", (x, y, GROUND), rx, ry, QH * hm, M_QARAH, coll=OUTC, seed=i)

# ---------- sky (camera-only), stars at night ----------
world = bpy.data.worlds.new("OfficeSky"); sc.world = world
try: world.use_nodes = True
except Exception: pass
# the sky is a camera-only dome (EEVEE lights the scene from the world shader, so the world = dim ambient only)
SKYM, wn, wout = new_mat("SkyDome")
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=2500, location=(0, 0, 0))
dome = bpy.context.active_object; dome.name = "SkyDome"; dome.data.materials.append(SKYM); into(dome, NOINK)
for attr in ("visible_diffuse", "visible_glossy", "visible_shadow", "visible_transmission", "visible_volume_scatter"):
    try: setattr(dome, attr, False)
    except Exception: pass
SKY_NAMES = {"SkyDome"}
tc = wn.nodes.new("ShaderNodeTexCoord"); dv = wn.nodes.new("ShaderNodeVectorMath"); dv.operation = "NORMALIZE"
wn.links.new(tc.outputs["Object"], dv.inputs[0]); sd = wn.nodes.new("ShaderNodeSeparateXYZ"); wn.links.new(dv.outputs[0], sd.inputs[0])
skr = wn.nodes.new("ShaderNodeValToRGB"); els = skr.color_ramp.elements
els[0].position, els[0].color = P["sky"][0][0], (*P["sky"][0][1], 1); els[1].position, els[1].color = P["sky"][-1][0], (*P["sky"][-1][1], 1)
for p_, c_ in P["sky"][1:-1]:
    e_ = els.new(p_); e_.color = (*c_, 1)
wn.links.new(sd.outputs["Z"], skr.inputs["Fac"])
col_out = skr.outputs["Color"]
CLOUD = {"sunset": ((0.74, 0.46, 0.58), (0.98, 0.7, 0.6), (1.0, 0.88, 0.7)),
         "night": ((0.05, 0.06, 0.14), (0.1, 0.12, 0.24), (0.18, 0.2, 0.36)),
         "dawn": ((0.55, 0.52, 0.72), (0.9, 0.72, 0.78), (1.0, 0.86, 0.8))}[TOD]
_dz = wn.nodes.new("ShaderNodeMath"); _dz.operation = "MAXIMUM"; _dz.inputs[1].default_value = 0.035; wn.links.new(sd.outputs["Z"], _dz.inputs[0])
_cz = wn.nodes.new("ShaderNodeCombineXYZ")
for _k in range(3): wn.links.new(_dz.outputs[0], _cz.inputs[_k])
_pj = wn.nodes.new("ShaderNodeVectorMath"); _pj.operation = "DIVIDE"; wn.links.new(dv.outputs[0], _pj.inputs[0]); wn.links.new(_cz.outputs[0], _pj.inputs[1])
def _cn(vec):
    n_ = wn.nodes.new("ShaderNodeTexNoise"); n_.inputs["Scale"].default_value = 0.45; n_.inputs["Detail"].default_value = 6
    n_.inputs["Roughness"].default_value = 0.58; wn.links.new(vec, n_.inputs["Vector"]); return n_.outputs["Fac"]
_c1 = _cn(_pj.outputs[0])
_sh = wn.nodes.new("ShaderNodeVectorMath"); _sh.operation = "ADD"; wn.links.new(_pj.outputs[0], _sh.inputs[0])
_l = math.hypot(SUN_DIR[0], SUN_DIR[1]) or 1; _sh.inputs[1].default_value = (0.1 * SUN_DIR[0] / _l, 0.1 * SUN_DIR[1] / _l, 0)
_c2 = _cn(_sh.outputs[0])
_df = wn.nodes.new("ShaderNodeMath"); _df.operation = "SUBTRACT"; wn.links.new(_c1, _df.inputs[0]); wn.links.new(_c2, _df.inputs[1])
_lm = wn.nodes.new("ShaderNodeMath"); _lm.operation = "MULTIPLY_ADD"; wn.links.new(_df.outputs[0], _lm.inputs[0]); _lm.inputs[1].default_value = 5; _lm.inputs[2].default_value = 0.5
def _wr(stops, interp="CONSTANT"):
    r_ = wn.nodes.new("ShaderNodeValToRGB"); r_.color_ramp.interpolation = interp; e_ = r_.color_ramp.elements
    e_[0].position, e_[0].color = stops[0][0], (*stops[0][1], 1); e_[1].position, e_[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p_, c_ in stops[1:-1]:
        x_ = e_.new(p_); x_.color = (*c_, 1)
    return r_
_csh = _wr([(0.0, CLOUD[0]), (0.42, CLOUD[1]), (0.6, CLOUD[2])]); wn.links.new(_lm.outputs[0], _csh.inputs["Fac"])
_msk = _wr([(0.0, (0, 0, 0)), (0.55, (0.6, 0.6, 0.6)), (0.575, (1, 1, 1))]); wn.links.new(_c1, _msk.inputs["Fac"])
_hb = _wr([(0.0, (0, 0, 0)), (0.05, (0, 0, 0)), (0.14, (1, 1, 1)), (0.55, (1, 1, 1)), (0.75, (0.3, 0.3, 0.3))], "LINEAR"); wn.links.new(sd.outputs["Z"], _hb.inputs["Fac"])
_mm = wn.nodes.new("ShaderNodeMix"); _mm.data_type = "RGBA"; _mm.blend_type = "MULTIPLY"; _mm.inputs["Factor"].default_value = 1
wn.links.new(_msk.outputs["Color"], _mm.inputs[6]); wn.links.new(_hb.outputs["Color"], _mm.inputs[7])
_ms = wn.nodes.new("ShaderNodeSeparateColor"); wn.links.new(_mm.outputs[2], _ms.inputs[0])
_cm = wn.nodes.new("ShaderNodeMix"); _cm.data_type = "RGBA"
wn.links.new(_ms.outputs[0], _cm.inputs["Factor"]); wn.links.new(col_out, _cm.inputs[6]); wn.links.new(_csh.outputs["Color"], _cm.inputs[7])
col_out = _cm.outputs[2]
if P["stars"] > 0:
    vo = wn.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 260; wn.links.new(dv.outputs[0], vo.inputs["Vector"])
    st = wn.nodes.new("ShaderNodeValToRGB"); st.color_ramp.elements[0].position = 0.0; st.color_ramp.elements[0].color = (3 * P["stars"], 3 * P["stars"], 3.2 * P["stars"], 1)
    st.color_ramp.elements[1].position = 0.04; st.color_ramp.elements[1].color = (0, 0, 0, 1)
    wn.links.new(vo.outputs["Distance"], st.inputs["Fac"])
    hb = wn.nodes.new("ShaderNodeMath"); hb.operation = "GREATER_THAN"; hb.inputs[1].default_value = 0.08; wn.links.new(sd.outputs["Z"], hb.inputs[0])
    sm = wn.nodes.new("ShaderNodeMix"); sm.data_type = "RGBA"; sm.blend_type = "MULTIPLY"; sm.inputs["Factor"].default_value = 1
    wn.links.new(st.outputs["Color"], sm.inputs[6]); wn.links.new(hb.outputs[0], sm.inputs[7])
    ad = wn.nodes.new("ShaderNodeMix"); ad.data_type = "RGBA"; ad.blend_type = "ADD"; ad.inputs["Factor"].default_value = 1
    wn.links.new(col_out, ad.inputs[6]); wn.links.new(sm.outputs[2], ad.inputs[7]); col_out = ad.outputs[2]
if P["sun_el"] > -2:
    dt = wn.nodes.new("ShaderNodeVectorMath"); dt.operation = "DOT_PRODUCT"; wn.links.new(dv.outputs[0], dt.inputs[0]); dt.inputs[1].default_value = SUN_DIR
    hl = wn.nodes.new("ShaderNodeValToRGB"); hel = hl.color_ramp.elements
    hel[0].position = 0.9988; hel[0].color = (0, 0, 0, 1); hel[1].position = 0.99992; hel[1].color = (1.45, 1.25, 0.95, 1)
    x_ = hel.new(0.9998); x_.color = (0.4, 0.24, 0.1, 1)
    wn.links.new(dt.outputs["Value"], hl.inputs["Fac"])
    ad2 = wn.nodes.new("ShaderNodeMix"); ad2.data_type = "RGBA"; ad2.blend_type = "ADD"; ad2.inputs["Factor"].default_value = 1
    wn.links.new(col_out, ad2.inputs[6]); wn.links.new(hl.outputs["Color"], ad2.inputs[7]); col_out = ad2.outputs[2]
sem = wn.nodes.new("ShaderNodeEmission"); wn.links.new(col_out, sem.inputs["Color"]); wn.links.new(sem.outputs[0], wout.inputs["Surface"])
wt = world.node_tree; wt.nodes.clear()
wo = wt.nodes.new("ShaderNodeOutputWorld"); bga = wt.nodes.new("ShaderNodeBackground")
bga.inputs["Color"].default_value = (*P["fill"], 1); bga.inputs["Strength"].default_value = P["amb"]
wt.links.new(bga.outputs[0], wo.inputs["Surface"])

# ---------- lights ----------
if P["sun_e"] > 0:
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
    sun = bpy.context.active_object; sun.name = "Sun"
    sun.data.energy = P["sun_e"]; sun.data.color = P["sun_col"]; sun.data.angle = math.radians(0.5)
    dx, dy, dz = (-SUN_DIR[0], -SUN_DIR[1], -SUN_DIR[2])
    sun.rotation_euler = (math.atan2(math.hypot(dx, dy), -dz), 0, math.atan2(dy, dx) + math.pi / 2)
# sky fill through the window (soft, coloured by the time of day)
bpy.ops.object.light_add(type="AREA", location=(X0 - 0.4, (WY0 + WY1) / 2, 1.9))
fill = bpy.context.active_object; fill.data.shape = "RECTANGLE"; fill.data.size = 2.0; fill.data.size_y = 2.0
fill.data.energy = P["fill_e"]; fill.hide_render = P["fill_e"] <= 0; fill.data.color = P["fill"]; fill.rotation_euler = (0, math.radians(-90), 0)
# dust in the light (window beam / lamp cone)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.2, 1.6))
hz = bpy.context.active_object; hz.name = "Haze"; hz.scale = (5.1, 5.1, 3.1); into(hz, NOINK)
hm, hn, ho = new_mat("Haze"); hv = hn.nodes.new("ShaderNodeVolumePrincipled")
hv.inputs["Color"].default_value = (1.0, 0.85, 0.65, 1); hv.inputs["Density"].default_value = 0.012
try: hv.inputs["Anisotropy"].default_value = 0.6
except Exception: pass
hn.links.new(hv.outputs[0], ho.inputs["Volume"]); hz.data.materials.append(hm)
dmesh = None
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.0035); mo = bpy.context.active_object
mo.data.materials.append(mat_emit("DustMote", (1.0, 0.88, 0.6), 2.5)); MOTE = mo.data; bpy.data.objects.remove(mo)
rnd = random.Random(8)
for i in range(120):
    d = bpy.data.objects.new("Mote", MOTE); NOINK.objects.link(d)
    b = (rnd.uniform(-2.4, 0.2), rnd.uniform(-0.6, 2.0), rnd.uniform(0.6, 2.5)); ph = rnd.uniform(0, 6.28)
    for fr in range(1, FRAMES + 1, 6):
        t = fr / 30
        d.location = (b[0] + 0.06 * math.sin(t * 0.6 + ph), b[1] + 0.05 * math.cos(t * 0.4 + ph), b[2] + 0.04 * math.sin(t * 0.8 + ph * 2) + 0.01 * t)
        d.keyframe_insert("location", frame=fr)

# ---------- camera ----------
bpy.ops.object.camera_add(); cam = bpy.context.active_object; sc.camera = cam; cam.data.clip_end = 3000
if CAM == "top":      # 1B / 2B: looking down at the drawing sheet
    cam.location = on_board(0.05, 0.0, 0.85); cam.rotation_euler = (0, -tilt, math.radians(90)); cam.data.lens = 40
else:                 # 1A / 2A / montage: wide, from the room toward the window (window left of frame)
    cam.location = (2.15, -1.95, 1.45); cam.data.lens = 24
    tgt = (-1.4, 1.0, 1.15)
    dx, dy, dz = tgt[0] - cam.location[0], tgt[1] - cam.location[1], tgt[2] - cam.location[2]
    cam.rotation_euler = (math.atan2(math.hypot(dx, dy), -dz), 0, math.atan2(dy, dx) - math.pi / 2)
    cam.keyframe_insert("location", frame=1)
    cam.location = (2.05, -1.85, 1.46); cam.keyframe_insert("location", frame=FRAMES)

try:
    anime_compositor(sc, cam, NOINK, sun_dir=SUN_DIR if P["sun_e"] > 0 else None, fog_near=40, fog_far=2600, fog_amt=0.55,
                     fog_color=P["fog"], ink_color=P["ink"], bloom=(2.2, 0.3, 0.45), beams=None, frame=STILL or 1, skip_geo=("Haze", "SkyDome"))
except Exception as ex:
    print("COMPOSITOR WARN:", ex)

if STILL:
    sc.frame_set(STILL); sc.render.filepath = os.path.join(OUT, f"office_{TOD}_{CAM}_{STILL:04d}.png")
    bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = os.path.join(OUT, f"office_{TOD}_{CAM}_"); bpy.ops.render.render(animation=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"office_{TOD}.blend"))
print("OFFICE DONE", OUT)
