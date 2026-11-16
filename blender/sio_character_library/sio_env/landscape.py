"""v6.5 landscape: terrain relief, recessed trapezoidal canal, layered Poly Haven vegetation, palms to the background.

Coordinates (unchanged canal alignment): canal axis along X at y = -38, original ground z = -9, building facade y = -1.33.

Canal channel (visual reference, not an engineering spec): coping 0.4 m each side (|dy| 3.1..3.5, z = -8.96),
side slopes 1:1.5 down to a 2.6 m wide bed at z = -10.2 (depth ~1.24 m), water surface z = -9.35 (0.35 m freeboard).
Runs x = -400..1200 so it continues into the haze in every +X looking shot.

Terrain: one height function h(x, y) used for the meshes, palm placement and vegetation:
  * edge pinned to the coping (z = -9.0 at |dy| = 3.5), service path almost flat to 5.5 m
  * embankment berm ~0.5 m centred 7 m from the axis on both banks
  * undulation (fBm) growing with distance: ~0.15 m near the canal, ~2.5 m at 80 m, rolling hills 6-20 m in the far field
  * fades to flat at the building (y > -8)
EXT_terrain_near (1.5 m grid, carries the density vertex groups) + EXT_terrain_far (12 m grid, sunk under the near
patch). Old flat EXT_ground stays far below as a fallback (z -9.8). Both terrains use the EXT_ground material.
"""
import math, random
import bpy
from mathutils import Vector, noise

CANAL_Y = -38.0
Z0 = -9.0
COPING_Z = -8.96
BED_Z = -10.2
WATER_Z = -9.35
HALF_TOP, HALF_BED, HALF_OUT = 3.1, 1.3, 3.5
X_CANAL = (-400.0, 1200.0)
NEAR = dict(x=(-260.0, 700.0), y=(-150.0, -1.4), step=1.5)
FAR = dict(x=(-2200.0, 4200.0), y=(-3200.0, 400.0), step=12.0)
CAM_PATHS = [((-38.0, -33.5), (-14.0, -34.5))]          # 3B bank dolly: keep tall plants off the lens
LIB_V3 = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library/assets/environment/polyhaven_canal_vegetation_v3.blend"


def _sm(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def _fbm(x, y, scale, octaves=4, seed=0.0):
    v, a, f, norm = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        v += a * noise.noise(Vector((x * scale * f, y * scale * f, seed + 3.1 * f)))
        norm += a; a *= 0.5; f *= 2.03
    return v / norm


def height(x, y):
    """Terrain height (world z) at (x, y), outside the channel."""
    dy = abs(y - CANAL_Y)
    if dy < HALF_OUT:
        return Z0
    near_b = _sm(HALF_OUT, 5.5, dy)
    berm = 0.5 * math.exp(-((dy - 7.0) / 2.0) ** 2) * near_b
    amp = 0.15 + 2.4 * _sm(8.0, 80.0, dy)
    und = _fbm(x, y, 0.018, 4, 1.3) * amp * near_b
    hills = (6.0 + 14.0 * _sm(400.0, 1400.0, dy)) * _sm(140.0, 420.0, dy) * max(0.0, _fbm(x, y, 0.0022, 3, 7.7) + 0.35)
    build = _sm(-8.0, -20.0, y) if y > CANAL_Y else 1.0          # flat in front of the building
    return Z0 + (berm + und) * build + hills


def _grid(name, xr, yr, step, skip_channel=True, sink_near=False):
    xs = [xr[0] + i * step for i in range(int((xr[1] - xr[0]) / step) + 1)]
    ys = [yr[0] + j * step for j in range(int((yr[1] - yr[0]) / step) + 1)]
    if skip_channel:
        # exact edge rows at the coping line on both sides
        ys = sorted(set([y for y in ys if abs(y - CANAL_Y) >= HALF_OUT] + [CANAL_Y - HALF_OUT, CANAL_Y + HALF_OUT]))
    verts, idx = [], {}
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            z = height(x, y)
            if sink_near and NEAR["x"][0] + 6 < x < NEAR["x"][1] - 6 and NEAR["y"][0] + 6 < y < NEAR["y"][1] - 6:
                z -= 3.0
            idx[(i, j)] = len(verts); verts.append((x, y, z))
    faces = []
    for j in range(len(ys) - 1):
        if skip_channel and ys[j] < CANAL_Y < ys[j + 1]:
            continue                                            # the gap is the canal
        for i in range(len(xs) - 1):
            faces.append((idx[(i, j)], idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)]))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o)
    o = bpy.data.objects.new(name, me)
    (bpy.data.collections.get("ENV_exterior") or bpy.context.scene.collection).objects.link(o)
    o.data.materials.append(bpy.data.objects["EXT_ground"].active_material)
    return o


def channel():
    """Trapezoidal concrete channel + coping, water lowered into it."""
    prof = [(-HALF_OUT, COPING_Z), (-HALF_TOP, COPING_Z), (-HALF_BED, BED_Z), (HALF_BED, BED_Z), (HALF_TOP, COPING_Z), (HALF_OUT, COPING_Z)]
    xs = [X_CANAL[0] + i * 10.0 for i in range(int((X_CANAL[1] - X_CANAL[0]) / 10.0) + 1)]
    verts, faces = [], []
    for x in xs:
        for dy, z in prof:
            verts.append((x, CANAL_Y + dy, z))
    n = len(prof)
    for i in range(len(xs) - 1):
        for k in range(n - 1):
            a = i * n + k
            faces.append((a, a + n, a + n + 1, a + 1))
    me = bpy.data.meshes.new("EXT_canal_channel"); me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.get("EXT_canal_channel")
    if o:
        bpy.data.objects.remove(o)
    o = bpy.data.objects.new("EXT_canal_channel", me)
    (bpy.data.collections.get("ENV_exterior") or bpy.context.scene.collection).objects.link(o)
    o.data.materials.append(bpy.data.materials["EXT_concrete"])
    # normals up/inward (towards the water)
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if sum(f.normal.z for f in bm.faces) < 0:
        for f in bm.faces:
            f.normal_flip()
    bm.to_mesh(me); bm.free()
    # old flat lining off, water into the channel
    lip = bpy.data.objects.get("EXT_canal_lip")
    if lip:
        lip.hide_render = True; lip.hide_viewport = True
    w = bpy.data.objects["EXT_canal_water"]
    L0 = w.dimensions.x / w.scale.x; W0 = w.dimensions.y / w.scale.y
    half_w = HALF_BED + (WATER_Z - BED_Z) / (COPING_Z - BED_Z) * (HALF_TOP - HALF_BED)
    w.scale.x = (X_CANAL[1] - X_CANAL[0]) / L0; w.scale.y = 2 * half_w / W0
    w.location = ((X_CANAL[0] + X_CANAL[1]) / 2, CANAL_Y, WATER_Z)
    m = w.active_material; b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Transmission Weight"].default_value = 0.4                     # see a little of the bed near the edges
    try:
        m.use_raytrace_refraction = True
    except Exception:
        pass
    return o, round(2 * half_w, 2)


def terrain():
    near = _grid("EXT_terrain_near", NEAR["x"], NEAR["y"], NEAR["step"])
    far = _grid("EXT_terrain_far", FAR["x"], FAR["y"], FAR["step"], skip_channel=False, sink_near=True)
    g = bpy.data.objects["EXT_ground"]; g.location.z = -9.8                   # old flat plane: deep fallback only
    return near, far


def _cam_clear(x, y, r=2.6):
    best = 1e9
    for (ax, ay), (bx, by) in CAM_PATHS:
        vx, vy = bx - ax, by - ay; t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy)))
        best = min(best, math.hypot(x - (ax + t * vx), y - (ay + t * vy)))
    return _sm(r * 0.5, r, best)


def near_masks(x, y):
    dy = abs(y - CANAL_Y)
    clear = _sm(5.4, 6.2, dy)                                   # coping + service path stay clear
    n1 = noise.noise(Vector((x * 0.03, y * 0.03, 2.2))); n2 = noise.noise(Vector((x * 0.09, y * 0.09, 5.1)))
    cl = _sm(-0.3, 0.4, 0.75 * n1 + 0.35 * n2)                 # cluster field
    vis_x = 1.0 - _sm(110.0, 330.0, x) * 0.75                  # detail where the cameras look, sparser far down +X
    near_cam = 1.0 - _sm(30.0, 70.0, dy) * 0.6
    gx = (1.0 - _sm(150.0, 260.0, x)) * (1.0 - _sm(-130.0, -100.0, -x))
    grass = clear * gx * (1.0 - 0.85 * _sm(24.0, 55.0, dy)) * (0.45 + 0.55 * max(cl, 1.0 - _sm(6.0, 14.0, dy)))
    ground = clear * vis_x * (0.3 + 0.7 * cl)
    shrub = clear * _cam_clear(x, y) * (0.25 + 0.75 * _sm(0.1, 0.6, n1 + 0.5 * n2)) * (0.6 + 0.4 * (1 - _sm(14.0, 40.0, dy)))
    tree = _sm(8.5, 11.0, dy) * (1 - _sm(45.0, 70.0, dy)) * _cam_clear(x, y, 4.0) * _sm(-0.2, 0.4, n1 + 0.3 * n2) * (1 - _sm(-14.0, -6.0, y))
    treebg = _sm(28.0, 40.0, dy) * _sm(-0.3, 0.3, n1 + 0.5 * n2) * (1 - _sm(-24.0, -12.0, y))                       # layered groves behind
    edge = math.exp(-((dy - 9.5) / 2.0) ** 2)                   # rocks on the berm's outer toe + scattered clusters
    rock = clear * _cam_clear(x, y, 1.6) * (0.7 * edge + 0.3 * _sm(0.3, 0.7, -n1 + 0.5 * n2))
    return dict(grass=grass, ground=ground, shrub=shrub, treemid=tree, treebg=treebg, rock=rock)


def far_masks(x, y):
    dy = abs(y - CANAL_Y)
    n1 = noise.noise(Vector((x * 0.008, y * 0.008, 9.4))); n2 = noise.noise(Vector((x * 0.03, y * 0.03, 1.9)))
    groves = _sm(-0.35, 0.25, n1 + 0.4 * n2)
    keep_off_near = 1.0 - (1.0 if (NEAR["x"][0] < x < NEAR["x"][1] and NEAR["y"][0] < y < NEAR["y"][1]) else 0.0)
    near_far_band = 1.0 if (NEAR["x"][0] - 40 < x < NEAR["x"][1] + 400 and -260 < y < 40) else 0.0
    trees_on_near_edge = 0.0
    return dict(treefar=groves * keep_off_near * (1 - _sm(-14.0, -4.0, y) if y > CANAL_Y else 1.0) * (0.35 + 0.65 * near_far_band),
                shrubfar=groves * keep_off_near * 0.6 * near_far_band)


def weight_groups(o, fn):
    keys = list(fn(0.0, -60.0).keys())
    groups = {k: (o.vertex_groups.get(f"dens_{k}") or o.vertex_groups.new(name=f"dens_{k}")) for k in keys}
    by = {k: {} for k in keys}
    for v in o.data.vertices:
        m = fn(v.co.x, v.co.y)
        for k in keys:
            w = m[k]
            if w > 0.003:
                by[k].setdefault(round(w, 2), []).append(v.index)
    for k in keys:
        for w, ids in by[k].items():
            groups[k].add(ids, w, 'REPLACE')
    return keys


SPEC_NEAR = {
    "grass":   dict(coll="VEG_grass",       dmax=6.0,   dist=0.10, scale=(1.1, 2.1), seed=11),
    "ground":  dict(coll="VEG_groundcover", dmax=1.6,   dist=0.22, scale=(1.3, 2.8), seed=12),
    "shrub":   dict(coll="VEG_shrub",       dmax=0.16,  dist=1.4,  scale=(1.0, 2.1), seed=13),
    "treemid": dict(coll="VEG_tree_mid",    dmax=0.03,  dist=5.5,  scale=(1.7, 2.7), seed=14),
    "treebg":  dict(coll="VEG_tree_far",    dmax=0.008, dist=9.0,  scale=(0.75, 1.2), seed=16),
    "rock":    dict(coll="VEG_rock",        dmax=0.03,  dist=1.6,  scale=(0.5, 1.5), seed=15),
}
SPEC_FAR = {
    "treefar":  dict(coll="VEG_tree_far", dmax=0.008,  dist=10.0, scale=(0.8, 1.4), seed=21),
    "shrubfar": dict(coll="VEG_shrub",    dmax=0.02,   dist=4.0,  scale=(1.6, 3.0),  seed=22),
}


def load_library():
    need = ["VEG_grass", "VEG_groundcover", "VEG_shrub", "VEG_tree_mid", "VEG_tree_far", "VEG_rock", "OFFICE_planters"]
    # v6.3 brought older VEG_* (v2) collections in: rename them out of the way so the v3 ones load with clean names
    for c in need:
        old = bpy.data.collections.get(c)
        if old:
            old.name = c + "_v2"
    with bpy.data.libraries.load(LIB_V3, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c in need]
    for c in need:                                          # free the superseded v2 copies (memory on 16 GB)
        old = bpy.data.collections.get(c + "_v2")
        if old:
            for o in list(old.objects):
                if not any(u.name in need for u in o.users_collection):
                    bpy.data.objects.remove(o)
            bpy.data.collections.remove(old)
    holder = bpy.data.collections.get("ENV_veg_library_v3") or bpy.data.collections.new("ENV_veg_library_v3")
    if holder.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(holder)
    for c in need:
        col = bpy.data.collections[c]
        if col.name not in holder.children and c != "OFFICE_planters":
            holder.children.link(col)
    for lc in bpy.context.view_layer.layer_collection.children:
        if lc.collection == holder:
            lc.exclude = True
    return holder


def scatter(o, spec, top_name):
    from sio_env import vegetation as VG
    for m in list(o.modifiers):
        o.modifiers.remove(m)
    top = bpy.data.node_groups.get(top_name)
    if top:
        bpy.data.node_groups.remove(top)
    top = bpy.data.node_groups.new(top_name, 'GeometryNodeTree')
    top.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    top.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi = top.nodes.new("NodeGroupInput"); go = top.nodes.new("NodeGroupOutput"); join = top.nodes.new("GeometryNodeJoinGeometry")
    top.links.new(gi.outputs[0], join.inputs[0])                         # keep the terrain itself
    for k, sp in spec.items():
        g = top.nodes.new("GeometryNodeGroup"); g.node_tree = VG._gn_layer(k, sp)
        top.links.new(gi.outputs[0], g.inputs[0]); top.links.new(g.outputs[0], join.inputs[0])
    top.links.new(join.outputs[0], go.inputs[0])
    md = o.modifiers.new(top_name, 'NODES'); md.node_group = top
    return top


def clear_old():
    """Remove the v6.3/6.4 flat-ground vegetation (re-scattered on the terrain) - the old objects only, no data loss in
    earlier .blend versions."""
    n = 0
    for o in list(bpy.data.objects):
        if o.name == "EXT_veg_scatter" or (o.name.startswith("EXT_ph_") and o.data):
            bpy.data.objects.remove(o); n += 1
    return n


def palms_to_background(seed=5):
    """No palm model exists on Poly Haven -> keep the procedural palms, but only far from the canal and the cameras."""
    rng = random.Random(seed)
    crowns = {}
    for o in bpy.data.objects:
        if o.name.startswith("EXT_palm_") and not o.name.startswith("EXT_palm_v") and o.data:
            crowns.setdefault(o.name.split(".")[0], []).append(o)
    spots = []
    groves = [(260, -110, 60), (420, -95, 70), (600, -130, 80), (330, 10, 50), (-40, -175, 60), (120, -190, 70), (520, 30, 60)]
    for key, objs in crowns.items():
        gx, gy, r = groves[rng.randrange(len(groves))]
        for _ in range(30):
            x, y = gx + rng.uniform(-r, r), gy + rng.uniform(-r * 0.5, r * 0.5)
            if abs(y - CANAL_Y) > 45 and y < -12 or y > 0:
                break
        z = height(x, y) - 0.25
        for o in objs:
            o.location = (x, y, z)
        spots.append((round(x), round(y)))
    return len(crowns)


def office_planters():
    """Window greenery: a pachira floor planter left of the desk + two anthurium pots on the sill corners."""
    lib = bpy.data.collections["OFFICE_planters"]
    coll = bpy.data.collections.get("ENV_office_planters") or bpy.data.collections.new("ENV_office_planters")
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    for o in list(coll.objects):
        bpy.data.objects.remove(o)
    def inst(src_name, loc, s=1.0, rz=0.0):
        src = bpy.data.objects[src_name]
        o = bpy.data.objects.new(f"OFFICE_{src_name}", src.data)   # shares mesh + materials
        coll.objects.link(o); o.location = loc; o.scale = (s, s, s); o.rotation_euler.z = rz
        return o
    pot_big = inst("planter_pot_clay", (-1.42, -0.78, 0.0), 2.4, 0.4)              # 0.53 m tall pot
    tree = inst("pachira_aquatica_01_d", (-1.42, -0.78, 0.46), 0.95, 1.1)          # ~1.55 m money tree
    s1 = inst("planter_pot_clay", (-0.72, -1.23, 0.8), 0.75, 0.0)                  # sill corners (window x -0.9..0.9)
    a1 = inst("anthurium_botany_05_e", (-0.72, -1.23, 0.95), 0.9, 0.6)
    s2 = inst("planter_pot_clay", (0.74, -1.23, 0.8), 0.75, 1.2)
    a2 = inst("anthurium_botany_06_f", (0.74, -1.23, 0.95), 0.9, 2.3)
    return [o.name for o in coll.objects]


def hide_boxes():
    n = 0
    for o in bpy.data.objects:
        if o.name.startswith("EXT_building_"):
            o.hide_render = True; o.hide_viewport = True; n += 1
    return n


def build():
    from sio_env import env_materials, wind
    out = {}
    bpy.context.scene["sio_haze_override"] = (0.80, 0.83, 0.86, 1500.0, 0.72)   # atmospheric (cool) instead of desert dust
    out["hidden_boxes"] = hide_boxes()
    env_materials.ground(lush=True)                          # green farmland everywhere, no desert sand
    out["library"] = load_library().name
    out["removed_old_scatter_objects"] = clear_old()
    ch, ww = channel(); out["channel"] = ch.name; out["water_width_m"] = ww
    near, far = terrain(); out["terrain"] = (len(near.data.vertices), len(far.data.vertices))
    out["near_groups"] = weight_groups(near, near_masks)
    out["far_groups"] = weight_groups(far, far_masks)
    scatter(near, SPEC_NEAR, "SIO_land_near"); scatter(far, SPEC_FAR, "SIO_land_far")
    out["palms_moved"] = palms_to_background()
    out["planters"] = office_planters()
    out["wind"] = wind.scatter_wind(bpy.data.objects["SIO_wind"], tops=("SIO_land_near", "SIO_land_far"))
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    return out
