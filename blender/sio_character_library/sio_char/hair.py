"""Procedural groomed hair as native Blender Hair Curves (scriptable, no add-ons).

    hair.apply_preset(ch, "short_side_part")   # presets/hair/<name>.json
    hair.apply_preset(ch, "beard_short")

How it works
  1. Landmarks (eyes, ears, lips, crown) are measured on the MPFB rest mesh, so presets scale to any body.
  2. A region function gives every skin point a 0..1 weight (scalp, beard, ...).
  3. Roots are sampled on the region (area x weight); each strand is grown step by step along a
     flow field (part line, comb back, gravity), kept on/above the surface with a BVH (shrinkwrap
     for short hair, collision only for long hair), then gathered/clumped if the preset asks.
  4. The strands become one Curves object with a per-point radius, parented to the head bone,
     so it follows the Rigify rig without simulation. A dark "scalp cap" under the hair hides skin.
"""
import math, random
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from . import util


# ---------------------------------------------------------------- landmarks
def landmarks(body):
    co = util.rest_coords(body)
    wbody = util.vgroup_weights(body, "body") > 0.5
    me = body.data
    def centroid(vg):
        w = util.vgroup_weights(body, vg) > 0.5
        return co[w].mean(0) if w.any() else None
    slot = {s.material.name.split(".")[-1]: i for i, s in enumerate(body.material_slots) if s.material}
    def mat_verts(key):
        idx = next((i for k, i in slot.items() if key in k), None)
        if idx is None:
            return None
        vs = {v for p in me.polygons if p.material_index == idx for v in p.vertices}
        return co[list(vs)] if vs else None
    head = co[wbody & (co[:, 2] > co[wbody][:, 2].max() - 0.35)]
    eyeL, eyeR = centroid("helper-l-eye"), centroid("helper-r-eye")
    lips, ears = mat_verts("lips"), mat_verts("ears")
    L = dict(
        crown_z=float(head[:, 2].max()),
        eye_z=float((eyeL[2] + eyeR[2]) / 2), eye_y=float((eyeL[1] + eyeR[1]) / 2), eye_x=float(abs(eyeL[0] - eyeR[0]) / 2),
        nose_y=float(head[:, 1].min()),
        lips_top=float(lips[:, 2].max()), lips_bot=float(lips[:, 2].min()), lips_y=float(lips[:, 1].min()),
        lips_x=float(np.abs(lips[:, 0]).max()),
        ear_mid=float(ears[:, 2].mean()), ear_top=float(ears[:, 2].max()), ear_bot=float(ears[:, 2].min()),
        ear_front=float(ears[:, 1].min()), ear_back=float(ears[:, 1].max()), ear_x=float(np.abs(ears[:, 0]).min()),
        back_y=float(head[:, 1].max()),
    )
    L["s"] = (L["crown_z"] - L["lips_bot"]) / 0.205          # scale vs. the reference male head
    return L


# ---------------------------------------------------------------- regions
def _lerp(a, b, t):
    return a + (b - a) * np.clip(t, 0, 1)


def region_scalp(P, L, R):
    """Hair-covered scalp. R: preset['region'] numbers in metres on the reference head (scaled by L['s'])."""
    s, S = L["s"], R.get("soft", 0.004) * L["s"]
    x, y, z = abs(P[0]), P[1], P[2]
    hl_front = L["eye_z"] + R.get("front", 0.078) * s - R.get("temple_recess", 0.012) * s * min(1, x / (0.045 * s))
    side = L["ear_top"] + R.get("above_ear", 0.004) * s
    burn = L["ear_mid"] + R.get("sideburn", -0.004) * s
    nape = L["ear_bot"] - R.get("nape", 0.035) * s
    yf = (L["ear_front"] - y) / max(1e-4, L["ear_front"] - L["eye_y"])      # 0 at ear front, 1 at eyes
    yb = (y - L["ear_back"]) / max(1e-4, L["back_y"] - L["ear_back"])       # 0 at ear back, 1 at skull back
    if R.get("back_model") == "nape" and y > L["ear_back"] - 0.004 * s:
        # v3: behind the ears the hairline drops to a real nape line (the neck curves inward under the
        # occiput, so depth behind the ear is not a measure of "how far back" - use a short ramp instead),
        # curving up toward the ears at the sides
        t = float(util.smoothstep(L["ear_back"] - 0.004 * s, L["ear_back"] + 0.022 * s, y))
        sides = float(np.clip(x / max(1e-4, L["ear_x"]), 0, 1)) ** 2
        nape_line = nape + R.get("nape_side_rise", 0.03) * s * sides
        line = float(_lerp(side, nape_line, t))
        w = util.smoothstep(-S, S, z - line)
        if L["ear_back"] + 0.012 * s > y > L["ear_front"] and L["ear_bot"] - 0.003 < z < L["ear_top"] + 0.003 and x > L["ear_x"] - 0.004:
            w *= 0.0
        return float(w)
    if yf > 0.25:
        line = hl_front                                   # forehead hairline
    elif yf > 0.0:
        line = float(_lerp(burn, hl_front, yf / 0.25))    # temple -> sideburn
    elif yb < 0.0:
        line = side                                       # above the ear
    else:
        line = float(_lerp(side, nape, yb * 1.6))         # down the back of the head to the nape
    w = util.smoothstep(-S, S, z - line)
    # keep the ears and the face clear
    if L["ear_back"] > y > L["ear_front"] and L["ear_bot"] - 0.003 < z < L["ear_top"] + 0.003 and x > L["ear_x"] - 0.004:
        w *= 0.0
    return float(w)


def region_beard(P, L, R, lips_kd=None):
    s, S = L["s"], R.get("soft", 0.005) * L["s"]
    y, z, x = P[1], P[2], abs(P[0])
    sb_y, sb_z = L["ear_front"] + 0.001, L["ear_mid"] + R.get("sideburn_top", 0.007) * s
    mc_y, mc_z = L["lips_y"] + 0.019 * s, L["lips_top"] + R.get("cheek_line", 0.002) * s
    top = _lerp(sb_z, mc_z, (sb_y - y) / max(1e-4, sb_y - mc_y))
    chin_z = L["lips_bot"] - R.get("chin_depth", 0.065) * s
    bot = _lerp(chin_z, L["ear_bot"] - 0.03 * s, (y - (L["lips_y"] + 0.04 * s)) / (0.065 * s))
    beard = util.smoothstep(-S, S, top - z) * util.smoothstep(-S, S, z - bot) * util.smoothstep(-S, S, sb_y + 0.003 - y)
    must = (util.smoothstep(-S, S, L["lips_top"] + 0.017 * s - z) * util.smoothstep(-S, S, z - (L["lips_top"] + R.get("mustache_gap", -0.004) * s))
            * util.smoothstep(-S, S, L["lips_x"] + 0.006 * s - x) * util.smoothstep(-S, S, L["lips_y"] + 0.024 * s - y))
    w = max(float(beard), float(must) * R.get("mustache", 1.0))
    if lips_kd is not None:
        d = lips_kd.find(Vector(P))[2]
        c = R.get("lip_clearance", 0.004) * s
        w -= 1 - float(util.smoothstep(c * 0.3, c, d))
    return max(0.0, min(1.0, w))


# ---------------------------------------------------------------- flows (unit tangent wanted at point)
def ponytail_gather(L, F):
    g = F.get("gather", (0.0, 0.0, 0.02))
    return Vector((g[0] * L["s"], L["back_y"] - 0.004 + g[1] * L["s"], L["ear_top"] + g[2] * L["s"]))


def flow(kind, P, N, L, F, rng, free=False):
    up, back, down = Vector((0, 0, 1)), Vector((0, 1, 0)), Vector((0, 0, -1))
    x = P.x
    if kind == "side_part":
        part = F.get("part_x", -0.035) * L["s"]
        away = Vector((1 if x > part else -1, 0, 0))
        top = float(util.smoothstep(L["ear_top"] + 0.03 * L["s"], L["crown_z"] - 0.025 * L["s"], P.z))
        front = float(util.smoothstep(L["ear_back"], L["eye_y"], P.y))          # 1 at the forehead, 0 behind the ears
        rear = float(util.smoothstep(L["ear_back"], L["back_y"], P.y))          # crown/back of the head
        top *= 1.0 - 0.75 * rear                                                # the back of the crown falls down
        d_top = back * F.get("back", 0.75) + away * F.get("sweep", 0.55) * front + up * F.get("lift", 0.15) * front
        d_side = down * 0.75 + back * 0.55
        d = d_top * top + d_side * (1 - top)
    elif kind == "side_part_v2":
        # groomed side part: a clean parting line on the top-front, the large side swept across and back,
        # the small side combed down toward the ear, tapered sides combed down/back, nape straight down
        s_ = L["s"]
        part = F.get("part_x", 0.03) * s_
        big = -1.0 if part > 0 else 1.0                      # the large side lies away from the parting
        side_sign = 1.0 if x > part else -1.0
        top = float(util.smoothstep(L["ear_top"] + 0.035 * s_, L["crown_z"] - 0.03 * s_, P.z))
        front = float(util.smoothstep(L["ear_back"] + 0.01 * s_, L["eye_y"], P.y))
        rear = float(util.smoothstep(L["ear_back"], L["back_y"], P.y))
        if side_sign == big:                                 # large side: across + back
            d_top = back * F.get("back", 0.7) + Vector((big, 0, 0)) * F.get("sweep", 0.75) * (0.35 + 0.65 * front)
        else:                                                # small side: toward the ear, then down
            d_top = Vector((side_sign, 0, 0)) * 0.9 + back * 0.35 + down * 0.25
        d_top = d_top * (1 - rear) + (down * 0.8 + back * 0.5) * rear
        d_side = down * 0.8 + back * 0.6
        d = d_top * top + d_side * (1 - top)
    elif kind == "beard":
        if N.z < -0.55:                           # under the jaw: forward and down
            d = Vector((0, -0.7, -1))
        elif P.z > L["lips_top"] - 0.004 and P.y < L["lips_y"] + 0.03:   # mustache
            d = Vector((0.55 if x > 0 else -0.55, 0, -1))
        else:
            d = down
    elif kind == "long_center_part":
        away = Vector((1 if x > 0 else -1, 0, 0))
        top = float(util.smoothstep(L["ear_top"], L["crown_z"], P.z))
        front = float(util.smoothstep(L["ear_front"], L["eye_y"], P.y))   # hairline: sweep back/out, never over the face
        d = down * (1.0 - 0.85 * front) + away * (F.get("sweep", 0.6) * top + 0.9 * front) + back * (0.25 + 0.9 * front)
    elif kind == "ponytail":
        g = ponytail_gather(L, F)
        d = (g - P)
        if d.length < F.get("gather_radius", 0.014) * L["s"] or free:
            d = down + back * F.get("tail_back", 0.35)
            free = True
    else:
        d = down
    d = d.normalized()
    j = F.get("jitter", 0.12)
    if free:                                   # hanging hair: no surface projection
        d += Vector((rng.uniform(-j, j), rng.uniform(-j, j), rng.uniform(-j, j))) * 0.5
        return d.normalized()
    t = d - N * d.dot(N)
    # where the wanted direction is nearly normal to the skin (head sides), its projection collapses and
    # would point anywhere -> fade toward "down along the skin" instead (removes flyaways and wings)
    dt = down - N * down.dot(N)
    if dt.length > 1e-4:
        t = t + dt.normalized() * max(0.0, 0.55 - t.length) * 2.0
    if t.length < 1e-4:
        t = d
    t.normalize()
    t += Vector((rng.uniform(-j, j), rng.uniform(-j, j), rng.uniform(-j, j)))
    return (t - N * t.dot(N)).normalized()


# ---------------------------------------------------------------- strands
def _rest_bvh(body, co, mask_z):
    me = body.data
    tris, keep = [], []
    for p in me.polygons:
        vs = list(p.vertices)
        if co[vs][:, 2].max() < mask_z:
            continue
        for i in range(1, len(vs) - 1):
            tris.append((vs[0], vs[i], vs[i + 1]))
    return BVHTree.FromPolygons([Vector(c) for c in co], tris, all_triangles=True), tris


def generate(ch, preset_name):
    H = util.load_preset("hair", preset_name)
    body, rng = ch.body, random.Random(H.get("seed", 1))
    L = landmarks(body)
    co = util.rest_coords(body)
    in_body = util.vgroup_weights(body, "body") > 0.5
    bvh, tris = _rest_bvh(body, co, L["lips_bot"] - H.get("collision_depth", 0.12) * L["s"])
    lips_kd = None
    if H["region"]["type"] == "beard":
        from mathutils import kdtree
        lv = [v for p in body.data.polygons if "lips" in body.material_slots[p.material_index].material.name for v in p.vertices]
        lips_kd = kdtree.KDTree(len(lv))
        for i, v in enumerate(lv):
            lips_kd.insert(Vector(co[v]), i)
        lips_kd.balance()
    reg = (lambda p: region_beard(p, L, H["region"], lips_kd)) if H["region"]["type"] == "beard" else (lambda p: region_scalp(p, L, H["region"]))

    # candidate triangles (body skin only) with area and region weight at the centroid
    T = np.array([t for t in tris if in_body[list(t)].all()])
    A, B, C = co[T[:, 0]], co[T[:, 1]], co[T[:, 2]]
    area = 0.5 * np.linalg.norm(np.cross(B - A, C - A), axis=1)
    cen = (A + B + C) / 3
    w = np.array([reg(c) for c in cen])
    pick = w > 0.02
    T, A, B, C, area, w = T[pick], A[pick], B[pick], C[pick], area[pick], w[pick]
    nr = np.random.default_rng(H.get("seed", 1))
    stratified = H.get("sampling") == "stratified"
    symmetric = H.get("symmetric", False)
    if symmetric:                                    # grow one half, mirror the other (exact symmetry)
        half = ((A + B + C) / 3)[:, 0] >= -0.0005
        T, A, B, C, area, w = T[half], A[half], B[half], C[half], area[half], w[half]
    if stratified:
        # even coverage: expected count per triangle, low-discrepancy points inside it (no clumps or gaps)
        expect = H["density_per_cm2"] * 1e4 * area * w
        cnt = np.floor(expect + nr.random(len(expect))).astype(int)
        idx = np.repeat(np.arange(len(T)), cnt)
        j = np.concatenate([np.arange(c) for c in cnt]) if cnt.sum() else np.zeros(0)
        g = 1.32471795724474602596
        r1 = (0.5 + j / g + nr.random(len(idx)) * 0.15) % 1.0
        r2 = (0.5 + j / (g * g) + nr.random(len(idx)) * 0.15) % 1.0
        n_strands = len(idx)
    else:
        total = float((area * w).sum())
        n_strands = int(H["density_per_cm2"] * total * 1e4)
        prob = area * w / (area * w).sum()
        idx = nr.choice(len(T), size=n_strands, p=prob)
        r1, r2 = nr.random(n_strands), nr.random(n_strands)
    sq = np.sqrt(r1)
    roots = A[idx] * (1 - sq)[:, None] + B[idx] * (sq * (1 - r2))[:, None] + C[idx] * (sq * r2)[:, None]
    clear = H["region"].get("lip_clearance")

    K = H.get("points", 8)
    G = H["growth"]
    Fl = H.get("flow", {})
    strands, radii = [], []
    for i in range(n_strands):
        p = Vector(roots[i])
        loc, n, _, _ = bvh.find_nearest(p)
        wr = reg(p)
        if not stratified and wr < rng.random() * 0.6:
            continue
        if wr <= 0.0:
            continue
        Lh = rng.uniform(*G["length"]) * L["s"] * (0.35 + 0.65 * wr if G.get("length_by_weight", True) else 1)
        zone = _length_zone(H, L, p)
        Lh *= zone
        vol = G.get("volume", 0.004) * (zone if G.get("volume_by_zone", True) else 1.0)
        if G.get("side_volume_cut"):            # keep the silhouette narrow over the parietal ridge
            vol *= 1.0 - G["side_volume_cut"] * float(util.smoothstep(0.035 * L["s"], 0.065 * L["s"], abs(p.x)))
        pts = [p.copy()]
        step = Lh / (K - 1)
        free = False
        kind = Fl.get("kind", "down")
        gather = ponytail_gather(L, Fl) if kind == "ponytail" else None
        rel = G.get("release_below")
        a = rng.uniform(0, 2 * math.pi)
        spread_dir = Vector((math.cos(a), math.sin(a) * 0.6, 0)) * math.sqrt(rng.random())
        for k in range(1, K):
            s = k / (K - 1)
            if gather is not None and (p - gather).length < Fl.get("gather_radius", 0.014) * L["s"]:
                free = True
            d = flow(kind, p, n, L, Fl, rng, free=free)
            if free and gather is not None:            # spread the tail into a round bundle
                d = (d + spread_dir * Fl.get("tail_spread", 0.22)).normalized()
            if G.get("gravity", 0) > 0 and free:
                d = (d + Vector((0, 0, -G["gravity"]))).normalized()
            q = p + d * step
            loc, n2, _, dist = bvh.find_nearest(q)
            if loc is not None:
                h = (G.get("root_lift", 0.0004) + vol * min(1.0, s * G.get("volume_ramp", 1.0)) ** G.get("volume_shape", 0.7)
                     * (1.0 - G.get("tip_settle", 0.0) * s ** 4)) * L["s"]      # tips lie back down on the layer below
                above = (q - loc).dot(n2)
                if rel is not None and not free and q.z < L["ear_bot"] + rel * L["s"]:
                    free = True                               # long hair leaves the head below the ears
                if (G.get("hug", True) and not free) or above < h:
                    q = loc + n2 * h                          # shrinkwrap (short hair) / collision push-out (long hair)
                n = n2
            p = q
            pts.append(p.copy())
        if clear and lips_kd is not None:
            pts = _trim_near(pts, lips_kd, clear * L["s"])
            if pts is None:
                continue
        strands.append(pts)
        r0 = H["radius"] * rng.uniform(0.8, 1.2)
        rad = [r0 * (1 - (k / (K - 1)) * (1 - H.get("tip_ratio", 0.25))) for k in range(K)]
        radii.append(rad)
        if symmetric and abs(pts[0].x) > 0.0008:
            strands.append([Vector((-v.x, v.y, v.z)) for v in pts]); radii.append(rad)
    if H.get("clump"):
        _clump(strands, H["clump"], rng)
    for _ in range(H.get("smooth_iters", 0)):          # remove kinks along each strand (root fixed)
        for s_ in strands:
            for k in range(1, len(s_) - 1):
                s_[k] = s_[k].lerp((s_[k - 1] + s_[k + 1]) * 0.5, 0.5)
    if H.get("final_collide", True):
        # clump/smooth can pull points into the skin: push every point back above the surface
        floor = G.get("root_lift", 0.0004) * L["s"]
        for s_ in strands:
            for k in range(1, len(s_)):
                loc, nrm, _, _ = bvh.find_nearest(s_[k])
                if loc is None:
                    continue
                above = (s_[k] - loc).dot(nrm)
                if above < floor:
                    s_[k] = s_[k] + nrm * (floor - above)
    return _make_curves(ch, H, strands, radii, preset_name), H, L


def _trim_near(pts, kd, clearance):
    """Cut a strand where it comes within `clearance` of the lips and resample it to the same point count.
    Returns None if even the root is too close."""
    K = len(pts)
    cut = None
    for k, p in enumerate(pts):
        if kd.find(p)[2] < clearance:
            cut = k
            break
    if cut is None:
        return pts
    if cut <= 1:
        return None
    keep = pts[:cut]
    seg = [0.0]
    for a, b in zip(keep[:-1], keep[1:]):
        seg.append(seg[-1] + (b - a).length)
    total = seg[-1] * 0.9
    out = []
    for i in range(K):
        d = total * i / (K - 1)
        j = max(x for x in range(len(seg)) if seg[x] <= d) if d < seg[-1] else len(seg) - 2
        j = min(j, len(keep) - 2)
        t = (d - seg[j]) / max(1e-9, seg[j + 1] - seg[j])
        out.append(keep[j].lerp(keep[j + 1], min(1.0, t)))
    return out


def _length_zone(H, L, p):
    z = H.get("length_zones")
    if not z:
        return 1.0
    top = float(util.smoothstep(L["ear_top"], L["crown_z"] - 0.02 * L["s"], p.z))
    if "rear_taper" in z:                    # barber taper: shorter toward the crown/back as well as the sides
        rear = float(util.smoothstep(L["ear_front"], L["back_y"], p.y))
        top *= 1.0 - z["rear_taper"] * rear
    f = z.get("sides", 1.0) * (1 - top) + z.get("top", 1.0) * top
    if "nape_fade" in z and p.y > L["ear_back"] - 0.01:
        # fade: length grows from ~20 % at the nape line to full over nape_fade metres (no hard shelf)
        nape_z = L["ear_bot"] - H["region"].get("nape", 0.035) * L["s"]
        f *= 0.2 + 0.8 * float(util.smoothstep(nape_z, nape_z + z["nape_fade"] * L["s"], p.z))
    return f


def _clump(strands, C, rng):
    """Pull strands toward a few random neighbours' paths (cheap clumping)."""
    n = len(strands)
    if n < 10:
        return
    roots = np.array([s[0] for s in strands])
    from mathutils import kdtree
    kd = kdtree.KDTree(n)
    for i, r in enumerate(roots):
        kd.insert(Vector(r), i)
    kd.balance()
    guides = rng.sample(range(n), max(1, int(n * C.get("guides", 0.04))))
    gk = kdtree.KDTree(len(guides))
    for j, g in enumerate(guides):
        gk.insert(Vector(roots[g]), j)
    gk.balance()
    f = C.get("factor", 0.5)
    for i, s in enumerate(strands):
        g = strands[guides[gk.find(Vector(roots[i]))[1]]]
        K = len(s)
        for k in range(1, K):
            t = (k / (K - 1)) ** C.get("shape", 1.5) * f
            s[k] = s[k].lerp(g[k] + (s[0] - g[0]) * (1 - t), t)


def _make_curves(ch, H, strands, radii, preset_name):
    name = f"{ch.name}_hair_{preset_name}"
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old)
    cu = bpy.data.hair_curves.new(name)
    K = len(strands[0])
    cu.add_curves([K] * len(strands))
    pos = np.array([[c.x, c.y, c.z] for s in strands for c in s], dtype=np.float32)
    cu.attributes["position"].data.foreach_set("vector", pos.ravel())
    rad = cu.attributes.get("radius") or cu.attributes.new("radius", 'FLOAT', 'POINT')
    rad.data.foreach_set("value", np.array(radii, dtype=np.float32).ravel())
    ob = bpy.data.objects.new(name, cu)
    for c in ch.body.users_collection:
        c.objects.link(ob)
    ob["sio_owner"] = ch.name
    ob["sio_part"] = "hair_" + preset_name
    from . import materials
    cu.materials.append(materials.hair_material(ch, H))
    # follow the rig: either rigidly with the head bone (v1/v2) or riding on the deforming skin (v3, "attach":"surface")
    if H.get("attach") == "surface":
        _attach_to_surface(ch, ob)
    else:
        _parent_to_head(ch, ob, H)
    if H.get("scalp_cap"):
        _scalp_cap(ch, H, preset_name)
    return ob


def _bone_for_region(ch, H):
    want = H.get("bone")
    rig = ch.rig
    if want and want in rig.data.bones:
        return want
    for b in ("DEF-spine.006", "DEF-head", "head", "ORG-spine.006"):
        if b in rig.data.bones:
            return b
    return rig.data.bones[0].name


def _parent_to_head(ch, ob, H):
    rig = ch.rig
    bone = _bone_for_region(ch, H)
    saved = rig.data.pose_position
    rig.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    mw_body = ch.body.matrix_world.copy()           # rest coords are body-object space
    ob.parent = rig
    ob.parent_type = 'BONE'
    ob.parent_bone = bone
    bpy.context.view_layer.update()
    pb = rig.pose.bones[bone]
    bone_world = rig.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))
    ob.matrix_parent_inverse = bone_world.inverted() @ mw_body
    ob.matrix_basis = Matrix.Identity(4)
    rig.data.pose_position = saved
    bpy.context.view_layer.update()


def _surface_ng():
    g = bpy.data.node_groups.get("SIO_deform_curves_on_surface")
    if g:
        return g
    g = bpy.data.node_groups.new("SIO_deform_curves_on_surface", 'GeometryNodeTree')
    g.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    g.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi = g.nodes.new("NodeGroupInput"); go = g.nodes.new("NodeGroupOutput")
    d = g.nodes.new("GeometryNodeDeformCurvesOnSurface")
    g.links.new(gi.outputs[0], d.inputs[0]); g.links.new(d.outputs[0], go.inputs[0])
    return g


def _rest(ch, on=True):
    ch.rig.data.pose_position = 'REST' if on else 'POSE'
    bpy.context.view_layer.update()


def _attach_to_surface(ch, ob):
    """Hair Curves deform with the skin (Blender's native hair attachment): roots get surface UVs in the rest
    pose, the body keeps a rest_position attribute, and a Deform Curves on Surface node moves every strand
    with the posed, smoothed skin - no rigid bone parenting, so nothing sinks where neck and head weights blend."""
    body = ch.body
    body.add_rest_position_attribute = True
    _rest(ch, True)
    ob.parent = body; ob.parent_type = 'OBJECT'
    ob.matrix_parent_inverse.identity(); ob.matrix_basis.identity()
    cu = ob.data
    cu.surface = body
    cu.surface_uv_map = body.data.uv_layers.active.name
    bpy.context.view_layer.update()
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST')
    m = ob.modifiers.get("SIO_surface") or ob.modifiers.new("SIO_surface", 'NODES')
    m.node_group = _surface_ng()
    _rest(ch, False)


def _bind_mesh_to_surface(ch, ob):
    """Scalp cap follows the deforming skin through a Surface Deform modifier bound in the rest pose."""
    body = ch.body
    _rest(ch, True)
    ob.parent = body; ob.parent_type = 'OBJECT'
    ob.matrix_parent_inverse.identity(); ob.matrix_basis.identity()
    m = ob.modifiers.get("SIO_surface") or ob.modifiers.new("SIO_surface", 'SURFACE_DEFORM')
    m.target = body
    bpy.context.view_layer.update()
    with bpy.context.temp_override(object=ob, active_object=ob):
        bpy.ops.object.surfacedeform_bind(modifier=m.name)
    _rest(ch, False)


def _scalp_cap(ch, H, preset_name):
    """Thin hair-coloured shell on the region (weight -> alpha) so skin never shows through strands."""
    body = ch.body
    L = landmarks(body)
    co = util.rest_coords(body)
    in_body = util.vgroup_weights(body, "body") > 0.5
    reg = lambda p: region_scalp(p, L, H["region"]) if H["region"]["type"] != "beard" else region_beard(p, L, H["region"])
    name = f"{ch.name}_cap_{preset_name}"
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old)
    bm = bmesh.new()
    lay = bm.verts.layers.float.new("hair_w")
    vmap = {}
    for p in body.data.polygons:
        vs = list(p.vertices)
        if not in_body[vs].all() or co[vs][:, 2].max() < L["lips_bot"] - 0.12 * L["s"]:
            continue
        ws = [reg(Vector(co[v])) for v in vs]
        if max(ws) < 0.01:
            continue
        for v, wv in zip(vs, ws):
            if v not in vmap:
                vmap[v] = bm.verts.new(co[v]); vmap[v][lay] = wv
        try:
            bm.faces.new([vmap[v] for v in vs])
        except ValueError:
            pass
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    for bv in bm.verts:
        bv.co += bv.normal * H["scalp_cap"].get("offset", 0.0004) * L["s"]
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    for c in body.users_collection:
        c.objects.link(ob)
    ob["sio_owner"] = ch.name
    from . import materials
    me.materials.append(materials.cap_material(ch, H))
    if H.get("attach") == "surface":
        _bind_mesh_to_surface(ch, ob)
    else:
        _parent_to_head(ch, ob, H)
    return ob


def apply_preset(ch, preset_name):
    ob, H, L = generate(ch, preset_name)
    if H.get("hide_proxy_hair", True) and ch.preset.get("hide_mpfb_hair_proxy"):
        for o in bpy.data.objects:
            if o.get("sio_owner") == ch.name and o.type == 'MESH' and any(h in o.name for h in ("short0", "long0", "bob0", "ponytail0", "afro0", "braid0")):
                o.hide_render = True; o.hide_set(True)
    return ob
