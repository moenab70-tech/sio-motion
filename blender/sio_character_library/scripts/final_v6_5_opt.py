"""Hasad opening V6.5_OPT = V6.5 with camera-aware vegetation and tree LODs (EEVEE previews only).

* Coverage: every production camera (1A..4A, sampled along their whole animation) + the review cameras -> per terrain
  vertex a soft frustum weight (tested at ground, shrub and canopy height, plus where a tree's S3 sun shadow lands)
  and the distance to the nearest camera position that sees it.
* Vegetation masks = V6.5 masks (path strip narrowed) x coverage x distance band.
* LODs built in-file from the V6.5 Poly Haven meshes (no downloads): leaf-card thinning for trees (kept leaves scaled
  up to keep the canopy silhouette), collapse-decimation for ground cover / shrubs / rocks.
final_v6_5.blend stays untouched.
  Blender -b tests/final_v6_5/final_v6_5.blend -P scripts/final_v6_5_opt.py -- --build
  Blender -b tests/final_v6_5_opt/final_v6_5_opt.blend -P scripts/final_v6_5_opt.py -- --previews 50 [tags,...]
  Blender -b tests/final_v6_5_opt/final_v6_5_opt.blend -P scripts/final_v6_5_opt.py -- --hero <tag>
"""
import os, sys, time, math, random, importlib.util
import bpy, bmesh
import numpy as np
from mathutils import Vector, noise

LIB = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
sys.path.insert(0, LIB)
OUT = os.path.join(LIB, "tests", "final_v6_5_opt")
os.makedirs(OUT, exist_ok=True)
_s = importlib.util.spec_from_file_location("v64", os.path.join(LIB, "scripts", "final_v6_4.py")); V64 = importlib.util.module_from_spec(_s); _s.loader.exec_module(V64)
from sio_env import landscape as LS

CANAL_Y = LS.CANAL_Y
PLAN = [("SHOT_A_establishing", "S1", 1, 90), ("SHOT_D_pencil", "S1", 1, 96), ("SHOT_H_calendar", "S2", 1, 22),
        ("SHOT_E_overhead", "S2", 20, 44), ("SHOT_G2_profile", "S3", 1, 102), ("SHOT_C_eyes", "S3", 1, 84),
        ("SHOT_J_canal", "S3", 1, 90), ("SHOT_K3_canal_axis", "S3", 1, 120)]


# ---------------------------------------------------------------- review cameras
def review_cams():
    from sio_env import shots as SH
    rig = bpy.data.objects["engineer_m01_rig"]; bpy.context.scene.frame_set(51)
    H = rig.matrix_world @ rig.pose.bones["DEF-spine.006"].head
    def cam(name, lens, fs, loc, tgt, focus=True, fdist=None):
        c = SH._cam(name, lens, fs); c.data.clip_end = 150000; c.animation_data_clear()
        SH._track(c, SH._target_empty(name + "_t", tgt), focus=focus); c.location = loc
        if fdist:
            c.data.dof.focus_object = None; c.data.dof.focus_distance = fdist
        return c
    return {
        "wide": cam("PV2_wide", 24, 11, (-112.0, -45.0, -1.0), (140.0, -37.0, -9.6), False, 60.0),
        "close": cam("PV2_close", 35, 5.6, (-4.0, -29.0, -7.9), (8.0, -33.0, -8.9)),
        "section": cam("PV2_section", 24, 8, (6.0, -46.8, -7.3), (6.0, -33.0, -9.7)),
        "ots": cam("PV2_ots", 28, 8, (H.x + 0.42, H.y + 0.62, H.z + 0.22), (-1.0, -38.0, -8.0), False, 3.0),
    }


# ---------------------------------------------------------------- coverage
def _samples(extra):
    from sio_env import story
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]; out = []
    jobs = [(c, s, list(range(f0, f1 + 1, 8)) + [f1]) for c, s, f0, f1 in PLAN] + [(c.name, "S3", [51]) for c in extra]
    for cn, ses, frames in jobs:
        story.apply(ses, rig); c = bpy.data.objects[cn]
        for f in frames:
            sc.frame_set(f); m = c.matrix_world
            th = (c.data.sensor_width / 2) / c.data.lens
            out.append(dict(name=cn, loc=np.array(m.translation), right=np.array(m.col[0].xyz.normalized()),
                            up=np.array(m.col[1].xyz.normalized()), fwd=np.array((-m.col[2].xyz).normalized()),
                            th=th, tv=th * 9 / 16, interior=bool(m.translation.y > -1.4 and m.translation.z > -1.0)))
    return out


def _sm(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def coverage(P, samples, heights, sun=None, sun_h=0.0):
    """Soft frustum weight (1 inside the frame + 12 % margin, 0 at 40 % outside) and nearest seeing-camera distance."""
    W = np.zeros(len(P)); D = np.full(len(P), 1e9)
    tests = [P + np.array([0.0, 0.0, h]) for h in heights]
    if sun is not None and sun_h > 0:                       # where the canopy shadow lands
        off = -np.array([sun[0], sun[1], 0.0]) * 0.0 + np.array([sun[0], sun[1], 0.0]) * (sun_h / max(0.08, -sun[2]))
        tests.append(P + off)
    for s in samples:
        for Q in tests:
            v = Q - s["loc"]; depth = v @ s["fwd"]
            ok = depth > 0.3; dd = np.where(ok, depth, 1.0)
            out = np.maximum(np.abs(v @ s["right"]) / (dd * s["th"]), np.abs(v @ s["up"]) / (dd * s["tv"]))
            w = np.where(ok, 1.0 - _sm(1.12, 1.40, out), 0.0)
            if s["interior"]:                                # office cameras: only through the window wall (y=-1.23)
                cy = s["loc"][1]; den = Q[:, 1] - cy; den = np.where(np.abs(den) < 1e-6, -1e-6, den)
                t = (WIN_Y - cy) / den; X = s["loc"][0] + t * (Q[:, 0] - s["loc"][0]); Z = s["loc"][2] + t * (Q[:, 2] - s["loc"][2])
                w = w * ((t > 0) & (t < 1) & (X > WIN_X[0]) & (X < WIN_X[1]) & (Z > WIN_Z[0]) & (Z < WIN_Z[1]))
            W = np.maximum(W, w)
            dist = np.linalg.norm(P - s["loc"], axis=1)
            D = np.where(w > 0.01, np.minimum(D, dist), D)
    return W, D


WIN_Y, WIN_X, WIN_Z = -1.23, (-2.4, 3.6), (0.75, 3.0)        # Wall_Left (facade window wall), generous


def band(d, lo, hi, soft=0.18):
    a = np.ones_like(d) if lo <= 0 else _sm(lo * (1 - soft), lo * (1 + soft), d)
    b = np.ones_like(d) if hi is None else 1.0 - _sm(hi * (1 - soft), hi * (1 + soft), d)
    return a * b


# ---------------------------------------------------------------- base masks (V6.5 + narrower service strip)
CLEAR_PATHS = [((-38.0, -33.5), (-14.0, -34.5)), ((-4.0, -29.0), (-4.0, -29.0)), ((6.0, -46.8), (6.0, -46.8))]


def _cam_clear(x, y, r=2.6):
    best = 1e9
    for (ax, ay), (bx, by) in CLEAR_PATHS:
        vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
        t = 0.0 if L2 < 1e-9 else max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / L2))
        best = min(best, math.hypot(x - (ax + t * vx), y - (ay + t * vy)))
    return LS._sm(r * 0.5, r, best)


def near_masks(x, y):
    sm = LS._sm; dy = abs(y - CANAL_Y)
    clear = sm(4.3, 4.9, dy)                                    # coping + ~0.8 m gravel strip stay clear (was 5.4..6.2)
    n1 = noise.noise(Vector((x * 0.03, y * 0.03, 2.2))); n2 = noise.noise(Vector((x * 0.09, y * 0.09, 5.1)))
    cl = sm(-0.3, 0.4, 0.75 * n1 + 0.35 * n2)
    grass = clear * (1.0 - 0.6 * sm(24.0, 55.0, dy)) * (0.5 + 0.5 * max(cl, 1.0 - sm(6.0, 14.0, dy)))
    ground = clear * (0.35 + 0.65 * cl)
    shrub = clear * _cam_clear(x, y) * (0.25 + 0.75 * sm(0.1, 0.6, n1 + 0.5 * n2)) * (0.6 + 0.4 * (1 - sm(14.0, 40.0, dy)))
    tree = sm(8.5, 11.0, dy) * (1 - sm(55.0, 80.0, dy)) * _cam_clear(x, y, 4.0) * sm(-0.25, 0.35, n1 + 0.3 * n2) * (1 - sm(-14.0, -6.0, y))
    corridor = 1.0 - (1.0 - sm(10.0, 16.0, abs(x - 1.0))) * (1.0 if y > CANAL_Y else 0.0)   # office window -> canal sightline
    tree *= corridor
    treebg = sm(26.0, 38.0, dy) * sm(-0.3, 0.3, n1 + 0.5 * n2) * (1 - sm(-24.0, -12.0, y))
    edge = math.exp(-((dy - 9.0) / 2.2) ** 2) + 0.6 * math.exp(-((dy - 5.6) / 0.5) ** 2)   # berm toe + path edge
    rock = clear * _cam_clear(x, y, 1.6) * (0.65 * edge + 0.3 * sm(0.3, 0.7, -n1 + 0.5 * n2))
    shrub *= 0.35 + 0.65 * corridor
    return dict(grass=grass, ground=ground, shrub=shrub, treemid=tree, treebg=treebg, rock=rock)


def far_masks(x, y):
    sm = LS._sm
    n1 = noise.noise(Vector((x * 0.008, y * 0.008, 9.4))); n2 = noise.noise(Vector((x * 0.03, y * 0.03, 1.9)))
    groves = sm(-0.45, 0.2, n1 + 0.4 * n2)
    N = LS.NEAR
    off_near = 0.0 if (N["x"][0] < x < N["x"][1] and N["y"][0] < y < N["y"][1]) else 1.0
    bld = (1 - sm(-14.0, -4.0, y)) if y > CANAL_Y else 1.0
    return dict(treefar=groves * off_near * bld, shrubfar=groves * off_near * 0.6)


def _masks(o, fn):
    co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", co); P = co.reshape(-1, 3)
    mw = np.array(o.matrix_world); P = P @ mw[:3, :3].T + mw[:3, 3]
    keys = list(fn(0.0, -60.0)); M = {k: np.empty(len(P)) for k in keys}
    for i, (x, y, _) in enumerate(P):
        m = fn(float(x), float(y))
        for k in keys:
            M[k][i] = m[k]
    return P, M


def _write_groups(o, weights):
    for g in list(o.vertex_groups):
        if g.name.startswith("dens_"):
            o.vertex_groups.remove(g)
    for k, w in weights.items():
        g = o.vertex_groups.new(name=f"dens_{k}")
        wq = np.round(w, 2)
        for val in np.unique(wq):
            if val < 0.005:
                continue
            g.add(np.nonzero(wq == val)[0].tolist(), float(val), 'REPLACE')


# ---------------------------------------------------------------- LODs (in-file, from the V6.5 Poly Haven meshes)
def _lod_holder(name):
    holder = bpy.data.collections["ENV_veg_library_v3"]
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in holder.children:
        holder.children.link(c)
    return c


def thin_tree(src, name, keep, cap, twig_keep, seed, branch_target=None, wood_islands=None):
    """Leaf-card thinning: drop (1-keep) of the leaf islands, scale survivors so the canopy keeps its silhouette."""
    me = src.data.copy(); me.name = name
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    mats = [(m.name.lower() if m else "") for m in me.materials]
    rng = random.Random(seed); s = min(cap, 1.0 / math.sqrt(keep))
    seen = set(); kill = []; woods = []
    for f in bm.faces:
        if f.index in seen:
            continue
        comp = []; stack = [f]; seen.add(f.index)
        while stack:
            g = stack.pop(); comp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index); stack.append(h)
        leaf = "lea" in mats[f.material_index] if f.material_index < len(mats) else False
        if leaf:
            if rng.random() > keep:
                kill.extend(comp)
            else:
                vs = {v for g in comp for v in g.verts}; c = sum((v.co for v in vs), Vector()) / len(vs)
                for v in vs:
                    v.co = c + (v.co - c) * s
        elif len(comp) < 24 and rng.random() > twig_keep:
            kill.extend(comp)
        else:
            woods.append(comp)
    if wood_islands and len(woods) > wood_islands:            # far LODs: only the main limbs survive
        woods.sort(key=len, reverse=True)
        for comp in woods[wood_islands:]:
            kill.extend(comp)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bm.to_mesh(me); bm.free()
    if branch_target:                                        # collapse-decimate the wood only, leaves stay cards
        leaf = {i for i, m in enumerate(mats) if "lea" in m}
        meb = me.copy(); meb.name = name + "_wood"
        for mesh, drop_leaf in ((meb, True), (me, False)):
            b2 = bmesh.new(); b2.from_mesh(mesh)
            bmesh.ops.delete(b2, geom=[f for f in b2.faces if (f.material_index in leaf) == drop_leaf], context='FACES')
            b2.to_mesh(mesh); b2.free()
        wood = decimate(bpy.data.objects.new("_wood_src", meb), "_wood_dec", branch_target)
        b3 = bmesh.new(); b3.from_mesh(me); b3.from_mesh(wood.data); b3.to_mesh(me); b3.free()
        bpy.data.objects.remove(wood); bpy.data.objects.remove(bpy.data.objects["_wood_src"])
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o)
    return bpy.data.objects.new(name, me)


def decimate(src, name, target):
    n = len(src.data.polygons)
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o)
    if n <= target:
        return bpy.data.objects.new(name, src.data)            # already light: share the mesh
    tmp = bpy.data.objects.new("_tmp_dec", src.data); bpy.context.scene.collection.objects.link(tmp)
    md = tmp.modifiers.new("dec", 'DECIMATE'); md.ratio = target / n
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg)); me.name = name
    bpy.data.objects.remove(tmp)
    return bpy.data.objects.new(name, me)


def build_lods():
    info = {}
    mid = ["island_tree_01", "island_tree_02", "island_tree_03", "tree_small_02"]
    bg = mid + ["jacaranda_tree"]
    c = _lod_holder("LOD_tree_mid_L1")
    for s in mid:
        o = bpy.data.objects[f"{s}_far"]
        if o.name not in c.objects:
            c.objects.link(o)
    for cname, names, keep, cap, twig, wood, isl in (("LOD_tree_mid_L2", mid, 0.14, 2.4, 0.25, 8000, 400), ("LOD_tree_bg_L2", bg, 0.12, 2.6, 0.2, 6000, 300),
                                                     ("LOD_tree_bg_L3", mid, 0.025, 4.6, 0.0, 1200, 40)):
        c = _lod_holder(cname)
        for i, s in enumerate(names):
            o = thin_tree(bpy.data.objects[f"{s}_far"], f"{s}_{cname[-2:]}{'m' if 'mid' in cname else 'b'}", keep, cap, twig, 7 + i, wood, isl)
            c.objects.link(o); print("OPT_LOD", o.name, len(o.data.polygons))
    for cname, src, target in (("LOD_groundcover_L1", "VEG_groundcover", 1400), ("LOD_shrub_L1", "VEG_shrub", 5000),
                               ("LOD_rock_L1", "VEG_rock", 3000)):
        c = _lod_holder(cname)
        for o in bpy.data.collections[src].objects:
            c.objects.link(decimate(o, o.name.split(".")[0] + "_L1", target))
    for c in bpy.data.collections:
        if c.name.startswith("LOD_") or c.name.startswith("VEG_"):
            info[c.name] = sum(len(o.data.polygons) for o in c.objects)
    return info


# ---------------------------------------------------------------- layer specs (key -> collection, density, distance band)
def specs():
    near = {
        # key           collection            dmax   dist  scale        seed  band(lo, hi)  fade beyond (start, end)
        "grassL0":    ("VEG_grass",           9.0,  0.08, (1.0, 2.0), 11, (0, None), (32.0, 85.0)),
        "groundL0":   ("VEG_groundcover",     2.2,  0.20, (1.3, 2.8), 12, (0, 12.0), None),
        "groundL1":   ("LOD_groundcover_L1",  2.2,  0.20, (1.3, 2.8), 32, (12.0, None), (110.0, 190.0)),
        "shrubL0":    ("VEG_shrub",           0.18, 1.3,  (1.0, 2.1), 13, (0, 28.0), None),
        "shrubL1":    ("LOD_shrub_L1",        0.18, 1.3,  (1.0, 2.1), 33, (28.0, None), (320.0, 480.0)),
        "treemidL0":  ("VEG_tree_mid",        0.04, 5.0,  (1.7, 2.7), 14, (0, 32.0), None),
        "treemidL1":  ("LOD_tree_mid_L1",     0.04, 5.0,  (1.7, 2.7), 34, (32.0, 110.0), None),
        "treemidL2":  ("LOD_tree_mid_L2",     0.04, 5.0,  (1.7, 2.7), 54, (110.0, None), None),
        "treebgL1":   ("VEG_tree_far",        0.010, 8.5, (0.75, 1.2), 16, (0, 140.0), None),
        "treebgL2":   ("LOD_tree_bg_L2",      0.010, 8.5, (0.75, 1.2), 36, (140.0, 380.0), None),
        "treebgL3":   ("LOD_tree_bg_L3",      0.010, 8.5, (1.8, 3.0), 56, (380.0, None), None),
        "rockL0":     ("VEG_rock",            0.035, 1.5, (0.5, 1.5), 15, (0, 22.0), None),
        "rockL1":     ("LOD_rock_L1",         0.035, 1.5, (0.5, 1.5), 35, (22.0, None), (110.0, 170.0)),
    }
    far = {
        "treefarL2":  ("LOD_tree_bg_L2",      0.009, 10.0, (0.8, 1.4), 21, (0, 420.0), None),
        "treefarL3":  ("LOD_tree_bg_L3",      0.009, 10.0, (1.8, 3.0), 41, (420.0, None), (1800.0, 3000.0)),
        "shrubfarL1": ("LOD_shrub_L1",        0.02,  4.0, (1.6, 3.0), 22, (0, None), (500.0, 800.0)),
    }
    return near, far


TALL = ("tree",)


def layer_weights(P, base, specs_, samples, sun):
    cov_low, d_low = coverage(P, samples, (0.3, 1.2))
    cov_tall, d_tall = coverage(P, samples, (0.0, 6.0, 14.0), sun=sun, sun_h=9.0)
    out = {}; stats = {}
    for key, (coll, dmax, dist, scale, seed, (lo, hi), fade) in specs_.items():
        b = key.rstrip("0123456789")[:-1]
        tall = b.startswith("tree")
        cov, d = (cov_tall, d_tall) if tall else (cov_low, d_low)
        w = base[b] * cov * band(d, lo, hi)
        if fade:
            w = w * (1.0 - _sm(fade[0], fade[1], d))
        out[key] = np.clip(w, 0.0, 1.0)
        stats[key] = round(float((out[key] > 0.005).mean()), 3)
    return out, stats, dict(cov_low=float((cov_low > 0.01).mean()), cov_tall=float((cov_tall > 0.01).mean()))


def scatter(o, specs_, top):
    sp = {k: dict(coll=v[0], dmax=v[1], dist=v[2], scale=v[3], seed=v[4]) for k, v in specs_.items()}
    return LS.scatter(o, sp, top)


def tune_path_material():
    """Narrow the gravel service strip in EXT_ground (3.5..4.8 m from the axis) so the banks read green, not sandy."""
    m = bpy.data.objects["EXT_terrain_near"].active_material
    remap = {(4.6, 5.6): (3.9, 4.4), (5.2, 5.6): (4.1, 4.5), (6.2, 7.4): (5.0, 5.8), (5.6, 7.5): (4.3, 5.4), (5.6, 6.2): (4.3, 4.7)}
    done = []
    for n in m.node_tree.nodes:
        if n.type == 'MAP_RANGE' and not n.inputs[1].is_linked and not n.inputs[2].is_linked:
            k = (round(n.inputs[1].default_value, 2), round(n.inputs[2].default_value, 2))
            if k in remap:
                n.inputs[1].default_value, n.inputs[2].default_value = remap[k]; done.append(k)
            elif k == (0.25, 0.55) and round(n.inputs[3].default_value, 2) == 0.55:      # lush belt: fewer bare-soil patches
                n.inputs[3].default_value = 0.82; done.append(("belt_min", 0.82))
    return done


VEG_TEX = ("tree", "shrub", "grass", "weed", "celandine", "didelta", "boulder", "rock_07", "stone_01", "jacaranda", "island",
           "leafy_grass", "sparse_grass", "gravel_ground", "brown_mud", "concrete_wall_009", "palm_bark", "pachira", "anthurium",
           "planter_pot")


def textures_8bit():
    """16-bit Poly Haven PNGs load as float buffers (2K = 64 MB + mips each). Re-pack the vegetation/ground maps as 8-bit:
    data maps (rough/normal/alpha/mask/disp) keep their raw values, colour maps are re-encoded linear -> sRGB.
    Character, office and HDRI images are not touched."""
    done, saved = 0, 0
    for im in list(bpy.data.images):
        n = im.name.lower()
        if not (im.is_float and im.packed_file and im.users and any(k in n for k in VEG_TEX)) or im.size[0] == 0:
            continue
        w, h = im.size; px = np.empty(w * h * 4, dtype=np.float32); im.pixels.foreach_get(px)
        cs = im.colorspace_settings.name
        if cs not in ("Non-Color", "Raw", "Linear"):                       # colour map: float buffer is scene-linear
            rgb = px.reshape(-1, 4)[:, :3]
            rgb[:] = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.power(np.clip(rgb, 0, None), 1 / 2.4) - 0.055)
        new = bpy.data.images.new(im.name + "_8b", w, h, alpha=True, float_buffer=False)
        new.colorspace_settings.name = cs
        new.alpha_mode = im.alpha_mode
        new.pixels.foreach_set(np.clip(px, 0.0, 1.0)); new.pack()
        im.user_remap(new); saved += w * h * 12; done += 1
        bpy.data.images.remove(im)
    return done, round(saved / 1e9, 2)


def count_instances():
    from collections import Counter
    src = {}
    for c in bpy.data.collections:
        if c.name.startswith(("VEG_", "LOD_")):
            for o in c.objects:
                src[o.name] = c.name
    dg = bpy.context.evaluated_depsgraph_get(); cnt = Counter(); polys = Counter()
    for inst in dg.object_instances:
        if inst.is_instance and inst.parent and inst.parent.name.startswith("EXT_terrain"):
            on = inst.object.original.name; k = src.get(on, on); cnt[k] += 1
            polys[k] += len(inst.object.original.data.polygons) if inst.object.type == 'MESH' else 0
    return cnt, polys


def build():
    from sio_env import wind
    t0 = time.time(); sc = bpy.context.scene
    sc["sio_haze_override"] = (0.80, 0.83, 0.86, 1700.0, 0.62)          # same blue-gray haze, a little lighter
    mesas = [o.name for o in bpy.data.objects if o.name.startswith("EXT_mesa")]
    for n in mesas:                                                       # sandstone desert mesas -> off (no desert)
        bpy.data.objects[n].hide_render = True; bpy.data.objects[n].hide_viewport = True
    print("OPT hidden mesas", mesas)
    print("OPT path material", tune_path_material())
    print("OPT textures_8bit (count, GB float buffers freed)", textures_8bit(), round(time.time() - t0))
    lods = build_lods(); print("OPT lods", lods, round(time.time() - t0));
    cams = review_cams()
    from sio_env import story
    story.apply("S3", bpy.data.objects["engineer_m01_rig"])
    sun = np.array(bpy.data.objects["L_sun"].matrix_world.to_3x3() @ Vector((0, 0, -1)))
    samples = _samples(list(cams.values())); print("OPT camera samples", len(samples))
    near_s, far_s = specs()
    near = bpy.data.objects["EXT_terrain_near"]; far = bpy.data.objects["EXT_terrain_far"]
    P, base = _masks(near, near_masks); w, st, cv = layer_weights(P, base, near_s, samples, sun); _write_groups(near, w)
    print("OPT near coverage", cv, "layer area", st)
    P, base = _masks(far, far_masks); w, st, cv = layer_weights(P, base, far_s, samples, sun); _write_groups(far, w)
    print("OPT far coverage", cv, "layer area", st)
    for k in [g.name for g in bpy.data.node_groups if g.name.startswith("SIO_veg_") or g.name.startswith("SIO_land_")]:
        bpy.data.node_groups.remove(bpy.data.node_groups[k])
    scatter(near, near_s, "SIO_land_near"); scatter(far, far_s, "SIO_land_far")
    print("OPT wind", wind.scatter_wind(bpy.data.objects["SIO_wind"], tops=("SIO_land_near", "SIO_land_far")))
    sc.frame_set(60)
    cnt, polys = count_instances()
    for k in sorted(cnt):
        print(f"OPT_INST {k:22s} n {cnt[k]:>8,d} polys {polys[k]:>14,d}")
    print("OPT_INST TOTAL", sum(cnt.values()), f"{sum(polys.values()):,d}")
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    path = os.path.join(OUT, "final_v6_5_opt.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, relative_remap=False); print("FINAL_V6_5_OPT saved", path, round(time.time() - t0), "s")


# ---------------------------------------------------------------- previews
PREVIEWS = [
    ("01_3B_canal_bank_f45", "Shot 3B - canal bank & vegetation", "S3", "SHOT_J_canal", 45),
    ("02_4A_canal_axis_f001", "Shot 4A - canal push-in (start)", "S3", "SHOT_K3_canal_axis", 1),
    ("03_4A_canal_axis_f060", "Shot 4A - canal push-in (middle)", "S3", "SHOT_K3_canal_axis", 60),
    ("04_4A_canal_axis_f120", "Shot 4A - canal push-in (final)", "S3", "SHOT_K3_canal_axis", 120),
    ("05_wide_landscape", "Review - wide canal landscape", "S3", "PV2_wide", 51),
    ("06_closeup_vegetation_rocks", "Review - vegetation, rocks, ground", "S3", "PV2_close", 51),
    ("07_canal_cross_section", "Review - canal cross-section (1.24 m deep)", "S3", "PV2_section", 51),
    ("08_ots_engineer_achievement", "Review - over-the-shoulder, engineer & canal", "S3", "PV2_ots", 51),
]


def _label(sc, text):
    r = sc.render; r.use_stamp = True
    for a in dir(r):
        if a.startswith("use_stamp_") and a != "use_stamp_note":
            try: setattr(r, a, False)
            except Exception: pass
    r.use_stamp_note = True; r.stamp_note_text = text; r.stamp_font_size = 14 if r.resolution_percentage <= 50 else 26
    r.stamp_background = (0, 0, 0, 0.6)


def previews(pct=50, only=None, samples=32, outdir="previews", fmt="JPEG"):
    from sio_env import story
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    V64._eevee(sc, pct, samples)
    sc.render.use_motion_blur = False
    im = sc.render.image_settings; im.media_type = 'IMAGE'; im.file_format = fmt
    if fmt == "JPEG": im.quality = 93
    else: im.color_mode = 'RGB'
    print("RENDER_SETTINGS", sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, pct, "%",
          "view", sc.view_settings.view_transform, "taa", sc.eevee.taa_render_samples, "mblur", sc.render.use_motion_blur,
          "jitter", bpy.data.objects["L_sun"].data.use_shadow_jitter)
    for tag, label, ses, cam, f in PREVIEWS:
        if only and tag not in only:
            continue
        story.apply(ses, rig); sc.camera = bpy.data.objects[cam]; sc.frame_set(f)
        _label(sc, f"{label}  |  frame {f}  |  EEVEE {int(1920 * pct / 100)}x{int(1080 * pct / 100)} AgX  |  V6.5_OPT")
        sc.render.filepath = os.path.join(OUT, outdir, tag + (".jpg" if fmt == "JPEG" else ".png")); t = time.time()
        bpy.ops.render.render(write_still=True)
        print("PREV", tag, round(time.time() - t, 1), flush=True)


if __name__ == "__main__" or "__file__" not in dir():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--build" in a: build()
    if "--previews" in a:
        i = a.index("--previews"); pct = int(a[i + 1]) if len(a) > i + 1 and a[i + 1].isdigit() else 50
        only = a[i + 2].split(",") if len(a) > i + 2 else None
        previews(pct, only)
    if "--hero" in a:
        i = a.index("--hero"); previews(100, [a[i + 1]], samples=64, outdir="hero", fmt="PNG")
