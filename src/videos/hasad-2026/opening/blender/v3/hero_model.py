# v3 · Full 3D toon hero modelled to match HERO_SHEET.png (see v3-hero-study.md). Exec'd after toon_lib.py.
# Frame: hero faces -Y, +X = his left, Z up, feet at z=0. 1.78 m tall, 7.5 heads (head 0.237 m).
#   body      : Skin-modifier skeleton (pelvis→spine→neck, legs, arms) + subdivision → rig can be generated from it
#   head      : shaped ellipsoid (anime skull, tapering jaw, flat face), nose, ears; FACE = painted texture (numpy)
#               with eyes / brows / mouth drawn from parameters → expressions are texture swaps (anime style)
#   beard     : shell lifted from the head where the sheet has beard (cheek line → sideburns), mouth opening, moustache
#   hands     : skin-modifier palm + 5 fingers with 3 joints, relaxed curl
#   thobe     : fitted torso → straight skirt to the ankle with soft vertical folds; sleeves; stand-up band collar,
#               4-button placket, chest pocket (his left) + pen, wide 2-button cuffs, side-pocket slits
#   shemagh   : folded triangle, cloth-simulated over cap/head/shoulders (crown + front peak pinned), border stripes
#   agal      : two black rings + two tassel cords at the back; taqiyah edge; sandals; wristwatch (his left)
import math, random
import bpy, bmesh
import mathutils
import numpy as np

H_TOTAL = 1.78
HC = 1.655                     # head centre (eye line)
HA, HB, HC_ = 0.079, 0.097, 0.118   # head half-width / half-depth / half-height

def _m(name, rgb, rim=0.45, translucent=0.0):
    m, nt, out = new_mat(name); cel_output(nt, out, flat(nt, rgb), rim_amt=rim, translucent=translucent); return m

def _into(ob, coll):
    for c in list(ob.users_collection): c.objects.unlink(ob)
    coll.objects.link(ob); return ob

def _smooth(ob):
    for p in ob.data.polygons: p.use_smooth = True

def _ss(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)

# ------------------------------------------------------------------ face texture (anime features drawn with SDFs)
FACE_W, FACE_H = 0.2, 0.26            # metres covered by the face UV square (u: x, v: z)
def face_texture(name="Face", res=1024, eye_open=1.0, look=(0.0, 0.0), brow_tilt=0.0, brow_raise=0.0, smile=0.25,
                 mouth_open=0.0, closed_smile=False, beard=True):
    u = (np.arange(res) + 0.5) / res
    X, Z = np.meshgrid((u - 0.5) * FACE_W, (u - 0.5) * FACE_H)       # metres; Z up (row 0 = bottom)
    rgba = np.zeros((res, res, 4), np.float32)
    def paint(mask, rgb, a=1.0):
        m = np.clip(mask, 0, 1)[..., None] * a
        rgba[..., :3] = rgba[..., :3] * (1 - m) + np.array(rgb, np.float32) * m
        rgba[..., 3:] = np.maximum(rgba[..., 3:], m)
    aa = 0.0006                                                     # antialias width (m)
    def band(d, w): return np.clip((w - np.abs(d)) / aa + 0.5, 0, 1)
    def inside(d): return np.clip(-d / aa + 0.5, 0, 1)
    INK = (0.12, 0.07, 0.05)
    if beard:
        # short boxed beard: cheek line from the sideburn diagonally to the mouth corner, chin, moustache; mouth left clear
        ax = np.abs(X)
        tt = np.clip((ax - 0.024) / (0.078 - 0.024), 0, 1)
        cheek = -0.055 + 0.065 * tt ** 1.25                                         # upper boundary (Z) of the beard
        bmask = inside(Z - cheek)
        mouth = inside(np.hypot(X / 0.021, (Z + 0.0625) / 0.0075) - 1.0)
        bmask = bmask * (1 - mouth)
        must = inside(np.abs(Z + 0.0525) - 0.0052 * (1 - (X / 0.026) ** 2).clip(0) - 0.0005) * (ax < 0.026)
        paint(np.maximum(bmask, must), (0.07, 0.055, 0.05))
        paint(band(Z - cheek, 0.0007) * (Z > -0.075) * (ax > 0.03), (0.04, 0.03, 0.03), 0.6)   # crisp edge line
    for sx in (-1, 1):
        cx, cz = sx * 0.031, 0.0
        dx = (X - cx) * sx                                          # + toward the outer corner
        ew = 0.0165
        t = np.clip(dx / ew, -1, 1)
        up = 0.0085 * eye_open * (1 - t * t) ** 0.55 + 0.0012 * t * eye_open      # outer corner slightly lifted
        lo = -0.0055 * eye_open * (1 - t * t) ** 0.8
        inx = np.abs(dx) < ew
        if eye_open > 0.08 and not closed_smile:
            white = inx & (Z - cz < up) & (Z - cz > lo)
            paint(white.astype(np.float32), (0.97, 0.95, 0.92))
            ix, iz = cx + sx * look[0] * 0.004, cz - 0.0008 + look[1] * 0.003
            r = np.hypot(X - ix, (Z - iz) * 0.9)
            iris = inside(r - 0.0074) * white
            paint(iris, (0.26, 0.15, 0.08))
            paint(inside(r - 0.0042) * white, (0.08, 0.05, 0.04))                  # pupil
            hl = inside(np.hypot(X - (ix - 0.0028), Z - (iz + 0.003)) - 0.0019) * white
            paint(hl, (1, 1, 1))                                                      # catch-light
            paint(inside(np.hypot(X - (ix + 0.0025), Z - (iz - 0.0032)) - 0.0009) * white, (0.95, 0.9, 0.85))
            # upper lash line: thick, extends into a small flick past the outer corner
            lash = band((Z - cz) - up - 0.0009, 0.0011 + 0.0007 * (t > 0.2)) * (np.abs(dx) < ew * 1.08)
            flick = band((Z - cz) - (0.0012 + (dx - ew) * 0.35), 0.0009) * (dx > ew * 0.85) * (dx < ew * 1.3)
            paint(np.maximum(lash, flick), INK)
            paint(band((Z - cz) - lo + 0.0004, 0.00045) * (t > -0.3) * inx, INK, 0.7)    # lower lid (outer 2/3)
            paint(band((Z - cz) - up - 0.0042, 0.00035) * (np.abs(t) < 0.7), INK, 0.45)  # double-lid crease
        else:   # closed eyes: a gentle arc (content / blink)
            arc = (-0.0028 if closed_smile else 0.0) * (1 - t * t) + 0.0009 * t
            paint(band((Z - cz) - arc, 0.0011) * (np.abs(dx) < ew), INK)
        # brows: thick, tapered, straight-ish masculine brow; tilt (+ = inner end down: frown)
        bx0, bx1 = 0.008, 0.05
        bt = np.clip((dx + (cx * sx - bx0)) / (bx1 - bx0), 0, 1)   # 0 inner → 1 outer
        bx = X * sx
        bt = np.clip((bx - bx0) / (bx1 - bx0), 0, 1)
        bz = 0.0205 + brow_raise * 0.004 + 0.003 * np.sin(bt * math.pi) * 0.7 - brow_tilt * 0.004 * (1 - bt) - 0.002 * bt
        th = 0.0034 * (1 - 0.55 * bt) + 0.0008
        brow = band(Z - bz, th / 2) * ((bx > bx0) & (bx < bx1))
        paint(brow, (0.07, 0.05, 0.045))
    # nose: a short shadow stroke on the side + nostril hint (anime simplification)
    paint(band(np.hypot(X + 0.004, Z + 0.036) - 0.006, 0.0006) * (X < -0.002) * (Z < -0.032), INK, 0.55)
    # mouth: line with smile curve; open → dark shape with teeth line
    mw = 0.0185
    mt = np.clip(X / mw, -1, 1)
    mz = -0.062 + smile * 0.004 * mt * mt - smile * 0.0012
    inm = np.abs(X) < mw
    if mouth_open > 0.05:
        top = mz + 0.0012; bot = mz - mouth_open * 0.009 * (1 - mt * mt)
        paint((inm & (Z < top) & (Z > bot)).astype(np.float32), (0.35, 0.1, 0.08))
        paint(((Z < top) & (Z > top - 0.0018) & (np.abs(X) < mw * 0.7)).astype(np.float32), (0.97, 0.95, 0.9))
    paint(band(Z - mz, 0.0008) * inm, (0.3, 0.12, 0.09))
    paint(band(Z - (-0.0705), 0.0007) * (np.abs(X) < 0.009), (0.55, 0.32, 0.24), 0.5)   # lower-lip hint
    img = bpy.data.images.get(name) or bpy.data.images.new(name, res, res, alpha=True)
    img.pixels.foreach_set(rgba.ravel())
    img.pack()
    return img

# ------------------------------------------------------------------ body
def _skin_mesh(name, pts, edges, radii, coll, root=0, subsurf=2, mat=None):
    me = bpy.data.meshes.new(name); me.from_pydata(pts, edges, []); me.update()
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    sk = ob.modifiers.new("Skin", "SKIN"); sk.use_smooth_shade = True
    for i, r in enumerate(radii):
        me.skin_vertices[0].data[i].radius = r
    me.skin_vertices[0].data[root].use_root = True
    if subsurf: ob.modifiers.new("Sub", "SUBSURF").levels = subsurf
    if mat: me.materials.append(mat)
    return ob

def build_body(coll, M_SKIN):
    P = {}
    P["pelvis"] = (0, 0.0, 0.95); P["spine"] = (0, 0.005, 1.12); P["chest"] = (0, 0.0, 1.3); P["neck0"] = (0, 0.012, 1.47)
    P["neck1"] = (0, 0.008, 1.56)
    pts, rad, edges = [], [], []
    def add(name, p, r):
        P[name] = p; pts.append(p); rad.append(r); return len(pts) - 1
    i_p = add("pelvis", P["pelvis"], (0.15, 0.1)); i_s = add("spine", P["spine"], (0.135, 0.095)); i_c = add("chest", P["chest"], (0.16, 0.1))
    i_n0 = add("neck0", P["neck0"], (0.06, 0.055)); i_n1 = add("neck1", P["neck1"], (0.05, 0.05))
    edges += [(i_p, i_s), (i_s, i_c), (i_c, i_n0), (i_n0, i_n1)]
    for sx in (-1, 1):
        a = add(f"clav{sx}", (sx * 0.1, 0.01, 1.44), (0.055, 0.05)); b = add(f"sho{sx}", (sx * 0.19, 0.012, 1.42), (0.052, 0.05))
        c = add(f"elb{sx}", (sx * 0.24, 0.025, 1.13), (0.04, 0.04)); d = add(f"wri{sx}", (sx * 0.262, -0.005, 0.875), (0.03, 0.026))
        edges += [(i_c, a), (a, b), (b, c), (c, d)]
        h = add(f"hip{sx}", (sx * 0.095, 0.0, 0.9), (0.085, 0.085)); k = add(f"kne{sx}", (sx * 0.1, -0.01, 0.5), (0.055, 0.055))
        an = add(f"ank{sx}", (sx * 0.105, 0.02, 0.08), (0.035, 0.035)); to = add(f"toe{sx}", (sx * 0.112, -0.12, 0.03), (0.036, 0.018))
        edges += [(i_p, h), (h, k), (k, an), (an, to)]
    body = _skin_mesh("HeroBody", pts, edges, rad, coll, root=i_p, mat=M_SKIN)
    return body, P

# ------------------------------------------------------------------ head
def build_head(coll, M_FACE, M_SKIN, M_BEARD):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=128, v_segments=96, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        # jaw: narrows toward the chin; chin pushed a little forward; neck side of the skull tucks in
        s = _ss(-0.05, -1.0, z)
        x *= 1 - 0.36 * s
        if y < 0: y *= 1 - 0.1 * s
        else: y *= 1 - 0.32 * _ss(-0.2, -1.0, z)
        # flatter face plane, slight cheekbone width, brow ridge
        if y < -0.45: y = -0.45 + (y + 0.45) * 0.62
        x *= 1 + 0.035 * math.exp(-((z + 0.1) / 0.25) ** 2)
        if y < -0.3: y -= 0.03 * math.exp(-((z - 0.22) / 0.1) ** 2)
        if y < -0.5: y -= 0.17 * math.exp(-(x / 0.13) ** 2) * math.exp(-((z + 0.15) / 0.17) ** 2) * (1 + 0.6 * _ss(0.0, -0.3, z))   # nose
        v.co = mathutils.Vector((x * HA, y * HB, z * HC_ + HC))
    me = bpy.data.meshes.new("HeroHead"); bm.to_mesh(me); bm.free()
    uv = me.uv_layers.new(name="UV")
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (co.x / FACE_W + 0.5, (co.z - HC) / FACE_H + 0.5)
    me.materials.append(M_FACE)
    head = bpy.data.objects.new("HeroHead", me); coll.objects.link(head); _smooth(head)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1, location=(sx * HA * 0.98, 0.006, HC - 0.008))
        e = _into(bpy.context.active_object, coll); e.name = f"HeroEar{sx}"; e.scale = (0.011, 0.02, 0.031); e.rotation_euler = (math.radians(-8), sx * 0.25, 0)
        e.data.materials.append(M_SKIN); _smooth(e)
    # beard shell: faces of the head inside the beard mask, pushed out along the normals, given thickness
    bm = bmesh.new(); bm.from_mesh(me)
    def bound(ax):      # cheek line: high at the sideburns, dipping toward the mouth corners
        return 0.012 - 0.06 * _ss(0.072, 0.022, ax)
    keep = set()
    for f in bm.faces:
        c = f.calc_center_median(); X, Y, Z = c.x, c.y, c.z - HC
        ax = abs(X)
        if Y > 0.07 or Z > 0.03: continue
        in_beard = False
        mouth = (ax < 0.021) and (-0.069 < Z < -0.056) and Y < -0.05
        lip_gap = (ax < 0.012) and (-0.056 < Z < -0.044) and Y < -0.05
        if in_beard and not mouth and not lip_gap: keep.add(f.index)
    for f in [f for f in bm.faces if f.index not in keep]: bm.faces.remove(f)
    for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
    bm.normal_update()
    for v in bm.verts: v.co += v.normal * 0.0045
    bme = bpy.data.meshes.new("HeroBeard"); bm.to_mesh(bme); bm.free()
    beard = bpy.data.objects.new("HeroBeard", bme); coll.objects.link(beard); bme.materials.append(M_BEARD); _smooth(beard)
    so = beard.modifiers.new("Thick", "SOLIDIFY"); so.thickness = 0.004; so.offset = -1
    beard.modifiers.new("Sub", "SUBSURF").levels = 1
    # moustache: thick soft bar over the upper lip, joining the beard at the mouth corners
    pts = [(sx * 0.024, -0.091 + 0.012 * (abs(sx) > 0.9), HC - 0.06) for sx in (-1,)]
    must = None and tube("HeroMoustache", [(-0.024, -0.086, HC - 0.062), (-0.012, -0.097, HC - 0.0505), (0.0, -0.099, HC - 0.0495),
                                   (0.012, -0.097, HC - 0.0505), (0.024, -0.086, HC - 0.062)], 0.0048, mat=M_BEARD, coll=coll, segs=10,
                taper=lambda t: 0.55 + 0.45 * math.sin(math.pi * t))
    return head

# ------------------------------------------------------------------ hands
def build_hand(coll, M_SKIN, wrist, sx):
    """Relaxed hand hanging at the side, palm facing the thigh (+/-X), fingers gently curled."""
    wx, wy, wz = wrist
    inward = -sx                                  # toward the body
    pts, rad, edges = [], [], []
    def add(p, r): pts.append(p); rad.append(r); return len(pts) - 1
    w = add((wx, wy, wz), (0.026, 0.02))
    pc = add((wx + inward * 0.004, wy - 0.002, wz - 0.05), (0.04, 0.014)); edges.append((w, pc))
    fingers = [(-0.024, 0.078), (-0.008, 0.086), (0.008, 0.08), (0.023, 0.064)]   # (y offset across the palm, length)
    for k, (fy, L) in enumerate(fingers):
        kn = add((wx + inward * 0.006, wy + fy, wz - 0.092), (0.0088, 0.0085)); edges.append((pc, kn))
        prev = kn; ang = 0.0
        for j in range(3):
            ang += 0.32 + 0.06 * k
            seg = L / 3
            px, py, pz = pts[prev]
            p = (px + inward * seg * math.sin(ang) * 0.9, py, pz - seg * math.cos(ang))
            q = add(p, (0.0082 - 0.0009 * j, 0.0078 - 0.0009 * j)); edges.append((prev, q)); prev = q
    t0 = add((wx + inward * 0.012, wy - 0.03, wz - 0.035), (0.012, 0.011)); edges.append((w, t0))
    t1 = add((wx + inward * 0.022, wy - 0.045, wz - 0.07), (0.0095, 0.009)); edges.append((t0, t1))
    t2 = add((wx + inward * 0.026, wy - 0.05, wz - 0.098), (0.0085, 0.008)); edges.append((t1, t2))
    return _skin_mesh(f"HeroHand{sx}", pts, edges, rad, coll, root=w, mat=M_SKIN)

# ------------------------------------------------------------------ thobe
THOBE_PROF = None   # [(z, cy, rx, ry)] measured from the body; None → fixed profile below

def thobe_profile_from_body(body, margin=0.03):
    dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); m_ = ev.to_mesh()
    co = np.array([body.matrix_world @ v.co for v in m_.vertices]); ev.to_mesh_clear()
    prof = []
    for z in np.linspace(0.06, 1.5, 49):
        sl = co[np.abs(co[:, 2] - z) < 0.012]
        if len(sl) < 6: continue
        ax = np.sort(np.abs(sl[:, 0]))
        gaps = np.where(np.diff(ax) > 0.02)[0]
        tmax = ax[gaps[0]] if len(gaps) else ax[-1]                   # body edge before the first gap (arms/hands excluded)
        core = sl[np.abs(sl[:, 0]) <= tmax + 1e-6]
        y0, y1 = core[:, 1].min(), core[:, 1].max()
        prof.append([float(z), float((y0 + y1) / 2), float(tmax + margin), float((y1 - y0) / 2 + margin)])
    prof = np.array(prof)
    # the skirt hangs straight from the hips: never narrower than the hips, a gentle flare to the hem
    hip = prof[np.argmin(np.abs(prof[:, 0] - 0.92))]
    for r in prof:
        if r[0] < 0.92:
            t = (0.92 - r[0]) / 0.86
            r[2] = max(r[2], hip[2] * (1 + 0.1 * t)); r[3] = max(r[3], hip[3] * (1 + 0.08 * t)); r[1] = hip[1] * (1 - t) + r[1] * t * 0.0 + hip[1] * t
    zsh = 1.37
    neck = prof[-1]
    shrow = prof[np.argmin(np.abs(prof[:, 0] - zsh))].copy()
    for r in prof:
        if r[0] > zsh:
            t = (r[0] - zsh) / (neck[0] - zsh)
            r[2] = shrow[2] + (0.075 - shrow[2]) * t ** 0.8
            r[3] = shrow[3] + (0.072 - shrow[3]) * t ** 0.8
    # smooth
    for k in (1, 2, 3):
        prof[1:-1, k] = (prof[:-2, k] + 2 * prof[1:-1, k] + prof[2:, k]) / 4
    return [tuple(r) for r in prof]

def _ring_cy(z):
    if THOBE_PROF is None: return 0.0
    zs = [r[0] for r in THOBE_PROF]; return float(np.interp(z, zs, [r[1] for r in THOBE_PROF]))

def _ring_radii(z):
    if THOBE_PROF is not None:
        zs = [r[0] for r in THOBE_PROF]
        return float(np.interp(z, zs, [r[2] for r in THOBE_PROF])), float(np.interp(z, zs, [r[3] for r in THOBE_PROF]))
    # (z, rx, ry) profile of the garment (slim Saudi fit), front/back nearly straight below the waist
    prof = [(0.06, 0.255, 0.195), (0.3, 0.24, 0.18), (0.6, 0.225, 0.165), (0.9, 0.205, 0.145), (1.05, 0.185, 0.13),
            (1.2, 0.188, 0.13), (1.32, 0.192, 0.128), (1.36, 0.19, 0.125), (1.4, 0.17, 0.118), (1.44, 0.13, 0.105), (1.47, 0.095, 0.085), (1.49, 0.075, 0.072)]
    for (z0, a0, b0), (z1, a1, b1) in zip(prof, prof[1:]):
        if z <= z1:
            t = (z - z0) / (z1 - z0); t = max(0, min(1, t)); return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t
    return prof[-1][1], prof[-1][2]

def build_thobe(coll, M_THOBE, M_BTN, M_INKLINE, M_PEN):
    segs, rows = 72, 70
    z0, z1 = 0.06, (THOBE_PROF[-1][0] if THOBE_PROF else 1.49)
    V, F = [], []
    rnd = random.Random(3)
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    for j in range(rows + 1):
        z = z0 + (z1 - z0) * (j / rows) ** 0.95
        rx, ry = _ring_radii(z)
        fold = 0.012 * _ss(1.0, 0.1, z)                        # soft vertical folds grow toward the hem
        for i in range(segs):
            a = 2 * math.pi * i / segs
            f = 1 + fold * (math.sin(a * 7 + ph[0]) * 0.6 + math.sin(a * 13 + ph[1]) * 0.4) * (0.4 + 0.6 * abs(math.cos(a)))
            V.append((rx * f * math.sin(a), _ring_cy(z) - ry * f * math.cos(a), z))     # a=0 → front (-Y)
    for j in range(rows):
        for i in range(segs):
            i2 = (i + 1) % segs; F.append((j * segs + i, j * segs + i2, (j + 1) * segs + i2, (j + 1) * segs + i))
    V.append((0, 0, z0)); c = len(V) - 1
    me = bpy.data.meshes.new("Thobe"); me.from_pydata(V, [], F); me.update(); me.materials.append(M_THOBE)
    th = bpy.data.objects.new("Thobe", me); coll.objects.link(th); _smooth(th)
    th.modifiers.new("Sub", "SUBSURF").levels = 1
    # sleeves (shoulder → wrist), slightly bent, a few soft folds at the elbow, wide cuffs with 2 buttons
    for sx in (-1, 1):
        sh = (sx * 0.12, 0.012, 1.39); el = (sx * 0.243, 0.025, 1.13); cu = (sx * 0.262, 0.0, 0.93)
        path = [sh, (sx * 0.19, 0.012, 1.37), ((sx * 0.19 + el[0]) / 2 + sx * 0.012, 0.018, 1.28), el, ((el[0] + cu[0]) / 2 + sx * 0.004, 0.015, 1.03), cu]
        tube(f"Sleeve{sx}", path, 0.064, mat=M_THOBE, coll=coll, segs=24, taper=lambda t: 1.0 - 0.22 * t - 0.04 * math.sin(t * 9) ** 2)
        cuff = tube(f"Cuff{sx}", [(cu[0], cu[1], cu[2] + 0.005), (cu[0] + sx * 0.002, cu[1] - 0.004, cu[2] - 0.065)], 0.047, mat=M_THOBE, coll=coll, segs=24)
        tube(f"CuffSeam{sx}", [(cu[0] + 0.047 * math.sin(a), cu[1] - 0.047 * math.cos(a), cu[2] + 0.004) for a in [k * math.pi / 12 for k in range(25)]], 0.0012, mat=M_INKLINE, coll=coll, segs=4)
        for k in range(2):
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.0055, depth=0.003, location=(cu[0] + sx * 0.046, cu[1] + 0.01, cu[2] - 0.022 - 0.022 * k), rotation=(0, math.radians(90), 0))
            _into(bpy.context.active_object, coll).data.materials.append(M_BTN)
    # stand-up band collar with a front opening line and 2 buttons; placket with 4 buttons
    col = lathe("Collar", [(0.07, 1.485), (0.068, 1.5), (0.066, 1.535), (0.064, 1.54)], 40, mat=M_THOBE, coll=coll, cap_bottom=False)
    col.scale = (1.0, 0.93, 1.0)
    tube("CollarLine", [(0, -0.062, 1.488), (0, -0.0605, 1.538)], 0.0011, mat=M_INKLINE, coll=coll, segs=4)
    for z in (1.505, 1.527):
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.0045, depth=0.003, location=(0, -0.0635, z), rotation=(math.radians(90), 0, 0))
        _into(bpy.context.active_object, coll).data.materials.append(M_BTN)
    def front_y(z): return _ring_cy(z) - _ring_radii(z)[1] - 0.0015
    pl = [(0.0, front_y(z), z) for z in (1.48, 1.4, 1.32, 1.24)]
    for sx in (-1, 1):
        tube(f"PlacketEdge{sx}", [(sx * 0.011, front_y(z) - 0.0005, z) for z in (1.47, 1.36, 1.235)], 0.001, mat=M_INKLINE, coll=coll, segs=4)
    tube("PlacketEnd", [(-0.011, front_y(1.235), 1.235), (0, front_y(1.225) - 0.0005, 1.222), (0.011, front_y(1.235), 1.235)], 0.001, mat=M_INKLINE, coll=coll, segs=4)
    for z in (1.445, 1.395, 1.345, 1.295):
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.0048, depth=0.003, location=(0, front_y(z) - 0.001, z), rotation=(math.radians(90), 0, 0))
        _into(bpy.context.active_object, coll).data.materials.append(M_BTN)
    # chest pocket on his LEFT (+X) with a pen clipped in it
    px, pz = 0.088, 1.31
    pocket = [(px - 0.05, front_y(pz + 0.055) - 0.002, pz + 0.055), (px + 0.05, front_y(pz + 0.055) - 0.002, pz + 0.055),
              (px + 0.05, front_y(pz - 0.06) - 0.002, pz - 0.06), (px - 0.05, front_y(pz - 0.06) - 0.002, pz - 0.06), (px - 0.05, front_y(pz + 0.055) - 0.002, pz + 0.055)]
    tube("PocketEdge", pocket, 0.0011, mat=M_INKLINE, coll=coll, segs=4)
    tube("PocketTop", [pocket[0], pocket[1]], 0.0018, mat=M_THOBE, coll=coll, segs=6)
    tube("Pen", [(px - 0.03, front_y(pz) - 0.004, pz + 0.035), (px - 0.03, front_y(pz) - 0.004, pz + 0.09)], 0.0045, mat=M_PEN, coll=coll, segs=8)
    tube("PenClip", [(px - 0.03, front_y(pz) - 0.0095, pz + 0.04), (px - 0.03, front_y(pz) - 0.0095, pz + 0.085)], 0.0012, mat=M_BTN, coll=coll, segs=4)
    # side-pocket slits on both hips
    for sx in (-1, 1):
        rx, ry = _ring_radii(0.92)
        tube(f"SideSlit{sx}", [(sx * (rx + 0.002), -0.01, 0.98), (sx * (rx + 0.003), -0.02, 0.84)], 0.0012, mat=M_INKLINE, coll=coll, segs=4)
    return th

# ------------------------------------------------------------------ shemagh (cloth sim), agal, cap
def _shemagh_material():
    m, nt, out = new_mat("Shemagh")
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["UV"], sp.inputs[0])
    RED, WHITE = (0.74, 0.06, 0.08), (0.97, 0.95, 0.92)
    def M(op, a, b=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: nt.links.new(x, n.inputs[i])
        return n.outputs[0]
    # small houndstooth-like check: two offset square grids, "teeth" from a diagonal
    k = 95.0
    gu, gv = M("MULTIPLY", sp.outputs["X"], k), M("MULTIPLY", sp.outputs["Y"], k)
    fu, fv = M("FRACT", gu), M("FRACT", gv)
    cu = M("GREATER_THAN", fu, 0.5); cv = M("GREATER_THAN", fv, 0.5)
    checker = M("ABSOLUTE", M("SUBTRACT", cu, cv))
    tooth = M("LESS_THAN", M("FRACT", M("ADD", gu, gv)), 0.25)
    pat = M("MINIMUM", M("ADD", checker, M("MULTIPLY", tooth, 0.6)), 1.0)
    # border along the two square edges (u≈0, v≈0): white band with two red stripes
    d = M("MINIMUM", M("MINIMUM", sp.outputs["X"], sp.outputs["Y"]), M("MINIMUM", M("SUBTRACT", 1.0, sp.outputs["X"]), M("SUBTRACT", 1.0, sp.outputs["Y"])))
    br = ramp(nt, [(0.0, WHITE), (0.012, RED), (0.02, WHITE), (0.028, RED), (0.036, WHITE), (0.05, (0, 0, 0))])
    nt.links.new(d, br.inputs["Fac"])
    inner = M("GREATER_THAN", d, 0.05)
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; nt.links.new(pat, mx.inputs["Factor"])
    mx.inputs[6].default_value = (*WHITE, 1); mx.inputs[7].default_value = (*RED, 1)
    mx2 = nt.nodes.new("ShaderNodeMix"); mx2.data_type = "RGBA"; nt.links.new(inner, mx2.inputs["Factor"])
    nt.links.new(br.outputs["Color"], mx2.inputs[6]); nt.links.new(mx.outputs[2], mx2.inputs[7])
    cel_output(nt, out, mx2.outputs[2], rim_amt=0.5, translucent=0.15)
    try: m.use_backface_culling = False
    except Exception: pass
    return m

CAP_C, CAP_R = (0.0, -0.004, HC + 0.035), (0.086, 0.103, 0.098)
def build_headwear(coll, M_WHITE, M_BLACK, colliders, frames=110):
    # taqiyah (also the collider the shemagh rests on)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=24, radius=1, location=CAP_C)
    cap = _into(bpy.context.active_object, coll); cap.name = "Taqiyah"; cap.scale = CAP_R; cap.data.materials.append(M_WHITE); _smooth(cap)
    bm = bmesh.new(); bm.from_mesh(cap.data)
    cut_local = (HC + 0.024 - CAP_C[2]) / CAP_R[2]            # keep only above the brow line (front a bit higher)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < cut_local + 0.12 * max(0.0, -v.co.y)], context="VERTS")
    bm.to_mesh(cap.data); bm.free()
    so_ = cap.modifiers.new("Thick", "SOLIDIFY"); so_.thickness = 0.003
    # shemagh = square folded on its diagonal: right-angle corner A hangs down the back; fold edge across the forehead
    N = 64; SIDE = 1.15
    half = SIDE / math.sqrt(2)                        # diamond half-diagonal
    V, F, UV, idx = [], [], [], {}
    FRONT = -0.098                                    # the folded front edge sits here (forehead)
    for i_ in range(N + 1):
        for j_ in range(N + 1):
            s_, t_ = i_ / N, j_ / N                    # square coords → rotate 45°
            px = (s_ - t_) * half; py = (s_ + t_ - 1) * half + FRONT      # diamond centred on the fold line → folded triangle
            pass                                      # cut later with a clean bisect
            r = (px / (CAP_R[0] + 0.004)) ** 2 + ((py - CAP_C[1]) / (CAP_R[1] + 0.004)) ** 2
            x, y = px, py
            if r < 1: z = CAP_C[2] + (CAP_R[2] + 0.006) * math.sqrt(1 - r)
            else:   # start as a wide umbrella OUTSIDE the body; gravity drapes it onto the shoulders
                d_m = (math.sqrt(r) - 1) * 0.095
                dx_, dy_ = px, (py - CAP_C[1]); L_ = math.hypot(dx_, dy_) or 1
                R_ = 0.11 + 0.6 * d_m
                x = dx_ / L_ * R_; y = CAP_C[1] + dy_ / L_ * R_ * 1.1
                z = CAP_C[2] + 0.004 - 0.8 * d_m
            if py < FRONT + 0.012 and abs(px) < 0.07:  # Saudi front peak
                z += 0.026 * (1 - abs(px) / 0.07); y -= 0.01 * (1 - abs(px) / 0.07)
            idx[(i_, j_)] = len(V); V.append((x, y, z)); UV.append((s_, t_))
    for i_ in range(N):
        for j_ in range(N):
            q = [(i_, j_), (i_ + 1, j_), (i_ + 1, j_ + 1), (i_, j_ + 1)]
            if all(k in idx for k in q): F.append(tuple(idx[k] for k in q))
    me = bpy.data.meshes.new("Shemagh"); me.from_pydata(V, [], F); me.update()
    _uvtmp = me.uv_layers.new(name="UV")
    for poly in me.polygons:
        for li in poly.loop_indices: _uvtmp.data[li].uv = UV[me.loops[li].vertex_index]
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, FRONT, 0), plane_no=(0, 1, 0), clear_inner=True)
    bm.to_mesh(me); bm.free(); me.update()
    V = [tuple(v.co) for v in me.vertices]
    sh = bpy.data.objects.new("Shemagh", me); coll.objects.link(sh)
    vg = sh.vertex_groups.new(name="pin")
    for k_, (x, y, z) in enumerate(V):
        r = (x / CAP_R[0]) ** 2 + ((y - CAP_C[1]) / CAP_R[1]) ** 2
        peak = (abs(x) < 0.06) and (y < -0.08) and z > HC + 0.03
        brow_edge = (abs(x) < 0.095) and (y < FRONT + 0.02)
        if r < 0.62 or peak or brow_edge: vg.add([k_], 1.0, "REPLACE")
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=1, location=(0, -0.04, HC - 0.05))
    guard = _into(bpy.context.active_object, coll); guard.name = "FaceGuard"; guard.scale = (0.095, 0.08, 0.1); guard.hide_render = True
    colliders = colliders + [(guard, 0.006)]
    for ob, th_ in colliders + [(cap, 0.004)]:
        c_ = ob.modifiers.new("Collision", "COLLISION"); c_.settings.thickness_outer = th_
        try: c_.settings.cloth_friction = 10
        except Exception: pass
    cl = sh.modifiers.new("Cloth", "CLOTH"); s = cl.settings
    s.quality = 10; s.mass = 0.16; s.air_damping = 1.2; s.bending_stiffness = 0.3
    s.tension_stiffness = 14; s.compression_stiffness = 14; s.shear_stiffness = 5
    s.vertex_group_mass = "pin"; s.pin_stiffness = 1.0
    cs = cl.collision_settings; cs.use_self_collision = True; cs.self_distance_min = 0.003; cs.distance_min = 0.004
    cl.point_cache.frame_start = 1; cl.point_cache.frame_end = frames
    sh.data.materials.append(_shemagh_material())
    sc_ = bpy.context.scene; old = (sc_.frame_start, sc_.frame_end)
    sc_.frame_start, sc_.frame_end = 1, max(frames, old[1])
    for f in range(1, frames + 1): sc_.frame_set(f)
    with bpy.context.temp_override(object=sh, active_object=sh, selected_objects=[sh]):
        bpy.ops.object.modifier_apply(modifier="Cloth")
    sc_.frame_start, sc_.frame_end = old; sc_.frame_set(1)
    so = sh.modifiers.new("Thick", "SOLIDIFY"); so.thickness = 0.003; _smooth(sh)
    # agal: two thick black rings sitting on the crown (slightly lower at the back) + two tassel cords
    tilt = math.radians(-9)
    for k_, (dz, scl) in enumerate(((0.062, 1.0), (0.08, 0.975))):
        ring = []
        for q in range(49):
            a = 2 * math.pi * q / 48
            x = CAP_R[0] * 1.07 * scl * math.sin(a); y = CAP_C[1] - CAP_R[1] * 1.05 * scl * math.cos(a)
            z = HC + dz + (y - CAP_C[1]) * math.sin(-tilt) * 0.9           # lower at the back
            ring.append((x, y, z))
        tube(f"Agal{k_}", ring, 0.0095, mat=M_BLACK, coll=coll, segs=10)
    for sx in (-1, 1):
        p0 = (sx * 0.03, CAP_R[1] + 0.02, HC + 0.055)
        cord = tube(f"AgalCord{sx}", [p0, (sx * 0.05, 0.13, HC - 0.03), (sx * 0.075, 0.12, HC - 0.15), (sx * 0.09, 0.11, HC - 0.25)], 0.0045, mat=M_BLACK, coll=coll, segs=6)
        tip = (sx * 0.09, 0.11, HC - 0.25)
        lathe(f"Tassel{sx}", [(0.0, 0.0), (0.008, -0.004), (0.014, -0.03), (0.016, -0.055), (0.0, -0.056)], 12, mat=M_BLACK, coll=coll).location = tip
    return sh, cap

# ------------------------------------------------------------------ feet, sandals, watch
def build_sandals(coll, M_SOLE, M_STRAP):
    for sx in (-1, 1):
        cx = sx * 0.108
        rbox(f"Sole{sx}", (0.1, 0.27, 0.022), (cx, -0.045, 0.011), bevel=0.012, mat=M_SOLE, coll=coll, segments=3)
        strap = [(cx + 0.055 * math.cos(a), -0.075, 0.022 + 0.05 * math.sin(a)) for a in [k * math.pi / 14 for k in range(15)]]
        tube(f"Strap{sx}", strap, 0.016, mat=M_STRAP, coll=coll, segs=8)

def build_watch(coll, M_STRAP, M_SILVER, wrist):
    wx, wy, wz = wrist
    tube("WatchBand", [(wx + 0.03 * math.cos(a), wy + 0.027 * math.sin(a), wz - 0.008) for a in [k * math.pi / 10 for k in range(21)]], 0.0055, mat=M_STRAP, coll=coll, segs=6)
    face = lathe("WatchFace", [(0.0, 0.0), (0.013, 0.0), (0.014, 0.004), (0.0, 0.005)], 20, mat=M_SILVER, coll=coll)
    face.location = (wx + 0.03, wy, wz - 0.008); face.rotation_euler = (0, math.radians(90), 0)

# ------------------------------------------------------------------ assemble
def build_full_hero(coll=None, face_kw=None, frames=190):
    sc = bpy.context.scene
    if coll is None:
        coll = bpy.data.collections.new("Hero"); sc.collection.children.link(coll)
    M_SKIN = _m("HeroSkin", (0.8, 0.57, 0.42), rim=0.5)
    M_BEARD = _m("HeroBeardMat", (0.06, 0.05, 0.05), rim=0.25)
    M_THOBE = _m("HeroThobe", (0.96, 0.955, 0.94), rim=0.55, translucent=0.1)
    M_WHITE = _m("HeroCap", (0.97, 0.97, 0.95))
    M_BLACK = _m("HeroAgal", (0.035, 0.035, 0.04), rim=0.5)
    M_BTN = _m("HeroButton", (0.86, 0.86, 0.84), rim=0.6)
    M_INK = _m("HeroSeam", (0.62, 0.62, 0.66), rim=0.0)
    M_PEN = _m("HeroPen", (0.08, 0.08, 0.1), rim=0.6)
    M_SOLE = _m("HeroSole", (0.06, 0.06, 0.06), rim=0.3)
    M_STRAP = _m("HeroStrap", (0.1, 0.09, 0.09), rim=0.4)
    M_WSTRAP = _m("HeroWatchStrap", (0.32, 0.18, 0.1), rim=0.3)
    # face material: painted feature texture over the skin, then cel-shaded
    img = face_texture(**(face_kw or {}))
    M_FACE, nt, out = new_mat("HeroFace")
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img; tx.interpolation = "Cubic"; tx.extension = "CLIP"
    uvn = nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map = "UV"; nt.links.new(uvn.outputs[0], tx.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs[6].default_value = (0.8, 0.57, 0.42, 1)
    nt.links.new(tx.outputs["Alpha"], mx.inputs["Factor"]); nt.links.new(tx.outputs["Color"], mx.inputs[7])
    cel_output(nt, out, mx.outputs[2], rim_amt=0.5)
    body, P = build_body(coll, M_SKIN)
    body.hide_render = True; body.hide_viewport = False
    _skin_mesh("HeroNeck", [(0, 0.012, 1.46), (0, 0.006, 1.6)], [(0, 1)], [(0.052, 0.05), (0.048, 0.046)], coll, mat=M_SKIN)
    for sx in (-1, 1):
        _skin_mesh(f"HeroFoot{sx}", [(sx * 0.105, 0.02, 0.1), (sx * 0.105, 0.015, 0.05), (sx * 0.11, -0.06, 0.035), (sx * 0.112, -0.135, 0.032)],
                   [(0, 1), (1, 2), (2, 3)], [(0.032, 0.032), (0.034, 0.028), (0.04, 0.016), (0.036, 0.012)], coll, mat=M_SKIN)
    head = build_head(coll, M_FACE, M_SKIN, M_BEARD)
    hands = [build_hand(coll, M_SKIN, (sx * 0.264, -0.004, 0.865), sx) for sx in (-1, 1)]
    thobe = build_thobe(coll, M_THOBE, M_BTN, M_INK, M_PEN)
    build_sandals(coll, M_SOLE, M_STRAP)
    build_watch(coll, M_WSTRAP, M_BTN, (0.264, -0.004, 0.875))
    beard = bpy.data.objects.get("HeroBeard")
    colliders = [(head, 0.004), (thobe, 0.006), (beard, 0.003)] + [(bpy.data.objects[f"Sleeve{sx}"], 0.006) for sx in (-1, 1)]
    for e in ("HeroEar-1", "HeroEar1"):
        if bpy.data.objects.get(e): colliders.append((bpy.data.objects[e], 0.003))
    shem, cap = build_headwear(coll, M_WHITE, M_BLACK, colliders, frames=frames)
    g_ = bpy.data.objects.get("FaceGuard")
    if g_: colliders.append((g_, 0))
    # tidy: drop the collision modifiers now that the cloth is frozen
    for ob, _ in colliders + [(cap, 0)]:
        for md in list(ob.modifiers):
            if md.type == "COLLISION": ob.modifiers.remove(md)
    bpy.context.view_layer.update()
    root = bpy.data.objects.new("HeroRoot", None); coll.objects.link(root)
    for ob in list(coll.objects):
        if ob is not root and ob.parent is None:
            mw = ob.matrix_world.copy(); ob.parent = root; ob.matrix_world = mw
    return root, coll

# =====================================================================================================
# v2 body: Blender Studio "Human Base Meshes" (CC0) realistic male → 1.78 m, our anime head on top,
# a simple armature with automatic weights, arms lowered to the sides (character-sheet pose).
HBM_PATH = "/Users/mohammadalqurain/Downloads/human-base-meshes-bundle-v1.4.1 2/human_base_meshes_bundle.blend"
HBM_SCALE = 1.78 / 1.6844

def load_base_body(coll, M_SKIN, path=HBM_PATH, name="GEO-body_male_realistic", cut_z=1.565):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [name]
    o = dst.objects[0]; coll.objects.link(o)
    o.parent = None
    for md in o.modifiers:
        if md.type == "MULTIRES":
            md.levels = 1; md.render_levels = 1; md.sculpt_levels = 1
    bpy.context.view_layer.objects.active = o
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]):
        for md in list(o.modifiers):
            if md.type == "MULTIRES":
                bpy.ops.object.multires_base_apply(modifier=md.name) if False else bpy.ops.object.modifier_apply(modifier=md.name)
    me = o.data
    mw = o.matrix_world.copy()
    me.transform(mw); o.matrix_world = mathutils.Matrix.Identity(4)
    co = np.array([v.co[:] for v in me.vertices])
    cx = (co[:, 0].min() + co[:, 0].max()) / 2; cy = co[:, 1].mean()
    me.transform(mathutils.Matrix.Scale(HBM_SCALE, 4) @ mathutils.Matrix.Translation((-cx, -cy, 0)))
    co2 = np.array([v.co[:] for v in me.vertices])
    nk = co2[(co2[:, 2] > 1.5) & (co2[:, 2] < 1.55)]
    me.transform(mathutils.Matrix.Translation((0, -float(nk[:, 1].mean()), 0)))
    # remove the realistic head: our anime head sits on the neck
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > cut_z], context="VERTS")
    bm.to_mesh(me); bm.free(); me.update()
    me.materials.clear(); me.materials.append(M_SKIN)
    for p in me.polygons: p.use_smooth = True
    o.name = "HeroBody"
    return o

def build_rig(coll, body):
    k = HBM_SCALE
    def P(x, y, z): return mathutils.Vector((x * k, y * k, z * k))
    arm = bpy.data.armatures.new("HeroRig"); rig = bpy.data.objects.new("HeroRig", arm); coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    with bpy.context.temp_override(active_object=rig, object=rig, selected_objects=[rig]):
        bpy.ops.object.mode_set(mode="EDIT")
        eb = arm.edit_bones
        def bone(n, h, t, parent=None, connect=False):
            b = eb.new(n); b.head = h; b.tail = t
            if parent: b.parent = eb[parent]; b.use_connect = connect
            return b
        bone("hips", P(0, 0.02, 0.93), P(0, 0.02, 1.05))
        bone("spine", P(0, 0.02, 1.05), P(0, 0.02, 1.2), "hips", True)
        bone("chest", P(0, 0.02, 1.2), P(0, 0.02, 1.4), "spine", True)
        bone("neck", P(0, 0.0, 1.4), P(0, -0.005, 1.5), "chest", True)
        bone("head", P(0, -0.005, 1.5), P(0, -0.005, 1.68), "neck", True)
        S = mathutils.Vector((0.165, 0.03, 1.405)); T = mathutils.Vector((0.44, -0.075, 0.763))
        for sx, sfx in ((1, ".L"), (-1, ".R")):
            def m(v): return P(sx * v.x, v.y, v.z)
            sh = S; el = S + (T - S) * 0.40 + mathutils.Vector((0.0, 0.03, 0.0)); wr = S + (T - S) * 0.76; tip = T
            bone("shoulder" + sfx, P(sx * 0.03, 0.02, 1.38), m(sh), "chest")
            bone("upper_arm" + sfx, m(sh), m(el), "shoulder" + sfx, True)
            bone("forearm" + sfx, m(el), m(wr), "upper_arm" + sfx, True)
            bone("hand" + sfx, m(wr), m(tip), "forearm" + sfx, True)
            bone("thigh" + sfx, P(sx * 0.095, 0.03, 0.93), P(sx * 0.105, 0.0, 0.5), "hips")
            bone("shin" + sfx, P(sx * 0.105, 0.0, 0.5), P(sx * 0.12, 0.07, 0.09), "thigh" + sfx, True)
            bone("foot" + sfx, P(sx * 0.12, 0.07, 0.09), P(sx * 0.13, -0.07, 0.02), "shin" + sfx, True)
        bpy.ops.object.mode_set(mode="OBJECT")
    # automatic (heat) weights
    for o_ in bpy.context.view_layer.objects: o_.select_set(False)
    body.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    return rig

def pose_sheet(rig):
    """Arms relaxed at the sides (as in HERO_SHEET), elbows slightly bent, feet a little closer."""
    pb = rig.pose.bones
    for sfx, sx in ((".L", 1), (".R", -1)):
        pb["upper_arm" + sfx].rotation_mode = "XYZ"; pb["forearm" + sfx].rotation_mode = "XYZ"; pb["hand" + sfx].rotation_mode = "XYZ"
        pb["thigh" + sfx].rotation_mode = "XYZ"
    bpy.context.view_layer.update()
    # rotate the upper arm in world space toward the body (about the forward axis)
    for sfx, sx in ((".L", 1), (".R", -1)):
        b = pb["upper_arm" + sfx]
        ang = math.radians(17) * sx
        R = mathutils.Matrix.Rotation(ang, 4, "Y")
        head = rig.matrix_world @ b.head
        mw = rig.matrix_world @ b.matrix
        new = mathutils.Matrix.Translation(head) @ R @ mathutils.Matrix.Translation(-head) @ mw
        b.matrix = rig.matrix_world.inverted() @ new
        bpy.context.view_layer.update()
        fb = pb["forearm" + sfx]
        R2 = mathutils.Matrix.Rotation(math.radians(6) * sx, 4, "Y")
        h2 = rig.matrix_world @ fb.head; mw2 = rig.matrix_world @ fb.matrix
        fb.matrix = rig.matrix_world.inverted() @ (mathutils.Matrix.Translation(h2) @ R2 @ mathutils.Matrix.Translation(-h2) @ mw2)
        bpy.context.view_layer.update()
        th = pb["thigh" + sfx]
        R3 = mathutils.Matrix.Rotation(math.radians(3.5) * sx, 4, "Y")
        h3 = rig.matrix_world @ th.head; mw3 = rig.matrix_world @ th.matrix
        th.matrix = rig.matrix_world.inverted() @ (mathutils.Matrix.Translation(h3) @ R3 @ mathutils.Matrix.Translation(-h3) @ mw3)
        bpy.context.view_layer.update()

def joint(rig, bone, end="head"):
    b = rig.pose.bones[bone]; return rig.matrix_world @ (b.head if end == "head" else b.tail)

def build_thobe_v2(coll, rig, M_THOBE, M_BTN, M_INKLINE, M_PEN):
    th = build_thobe(coll, M_THOBE, M_BTN, M_INKLINE, M_PEN)
    # re-route the sleeves along the posed arms
    for sx, sfx in ((-1, ".R"), (1, ".L")):
        for nm in (f"Sleeve{sx}", f"Cuff{sx}", f"CuffSeam{sx}"):
            o_ = bpy.data.objects.get(nm)
            if o_: bpy.data.objects.remove(o_)
        sh = joint(rig, "upper_arm" + sfx); el = joint(rig, "forearm" + sfx); wr = joint(rig, "hand" + sfx)
        inner = mathutils.Vector((sx * 0.12, 0.012, sh.z - 0.02))
        path = [inner, sh + mathutils.Vector((0, 0, 0.01)), sh.lerp(el, 0.5) + mathutils.Vector((sx * 0.008, 0, 0)), el, el.lerp(wr, 0.55), wr + (el - wr).normalized() * 0.09]
        tube(f"Sleeve{sx}", [tuple(p) for p in path], 0.064, mat=M_THOBE, coll=coll, segs=24, taper=lambda t: 1.0 - 0.24 * t - 0.04 * math.sin(t * 9) ** 2)
        cdir = (wr - el).normalized()
        c0 = wr - cdir * 0.085; c1 = wr - cdir * 0.012
        tube(f"Cuff{sx}", [tuple(c0), tuple(c1)], 0.046, mat=M_THOBE, coll=coll, segs=24)
        side = mathutils.Vector((sx, 0, 0))
        for kk in range(2):
            p = c0.lerp(c1, 0.3 + 0.35 * kk) + side * 0.045
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.0055, depth=0.003, location=p, rotation=(0, math.radians(90), 0))
            _into(bpy.context.active_object, coll).data.materials.append(M_BTN)
    # buttons that build_thobe placed on the old cuffs: remove the ones far from the new cuffs
    return th

def build_full_hero_v2(coll=None, face_kw=None, frames=190):
    sc = bpy.context.scene
    if coll is None:
        coll = bpy.data.collections.new("Hero"); sc.collection.children.link(coll)
    M_SKIN = _m("HeroSkin", (0.8, 0.57, 0.42), rim=0.5)
    M_THOBE = _m("HeroThobe", (0.96, 0.955, 0.94), rim=0.55, translucent=0.1)
    M_WHITE = _m("HeroCap", (0.97, 0.97, 0.95)); M_BLACK = _m("HeroAgal", (0.035, 0.035, 0.04), rim=0.5)
    M_BTN = _m("HeroButton", (0.86, 0.86, 0.84), rim=0.6); M_INK = _m("HeroSeam", (0.62, 0.62, 0.66), rim=0.0)
    M_PEN = _m("HeroPen", (0.08, 0.08, 0.1), rim=0.6); M_SOLE = _m("HeroSole", (0.06, 0.06, 0.06), rim=0.3)
    M_STRAP = _m("HeroStrap", (0.1, 0.09, 0.09), rim=0.4); M_WSTRAP = _m("HeroWatchStrap", (0.32, 0.18, 0.1), rim=0.3)
    M_BEARD = _m("HeroBeardMat", (0.06, 0.05, 0.05), rim=0.25)
    img = face_texture(**(face_kw or {}))
    M_FACE, nt, out = new_mat("HeroFace")
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img; tx.interpolation = "Cubic"; tx.extension = "CLIP"
    uvn = nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map = "UV"; nt.links.new(uvn.outputs[0], tx.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs[6].default_value = (0.8, 0.57, 0.42, 1)
    nt.links.new(tx.outputs["Alpha"], mx.inputs["Factor"]); nt.links.new(tx.outputs["Color"], mx.inputs[7])
    cel_output(nt, out, mx.outputs[2], rim_amt=0.5)
    body = load_base_body(coll, M_SKIN)
    global THOBE_PROF
    THOBE_PROF = None                                   # the fixed garment profile reads cleaner than slices
    rig = build_rig(coll, body)
    vis = body.copy(); vis.name = "HeroSkinVisible"; coll.objects.link(vis)
    vg = vis.vertex_groups.new(name="visible")
    S = mathutils.Vector((0.165, 0.03, 1.405)) * HBM_SCALE; T = mathutils.Vector((0.44, -0.075, 0.763)) * HBM_SCALE
    keep = []
    for v in body.data.vertices:
        c = v.co
        arm_t = ((mathutils.Vector((abs(c.x), c.y, c.z)) - S).dot(T - S)) / (T - S).length_squared
        if c.z > 1.47 or c.z < 0.12 or (abs(c.x) > 0.2 and arm_t > 0.7): keep.append(v.index)
    vg.add(keep, 1.0, "REPLACE")
    mk = vis.modifiers.new("ShowOnly", "MASK"); mk.vertex_group = "visible"
    body.hide_render = True
    pose_sheet(rig)
    head = build_head(coll, M_FACE, M_SKIN, M_BEARD)
    thobe = build_thobe(coll, M_THOBE, M_BTN, M_INK, M_PEN)
    # thobe sleeves/cuffs along the posed arms (replace the generic ones)
    for nm in [o.name for o in coll.objects if o.name.startswith(("Sleeve", "Cuff"))]:
        bpy.data.objects.remove(bpy.data.objects[nm])
    for o in [o for o in coll.objects if o.name.startswith("Cylinder") and o.location.z < 1.0]:
        bpy.data.objects.remove(o)                       # old cuff buttons
    dg = bpy.context.evaluated_depsgraph_get(); evb = body.evaluated_get(dg); emb = evb.to_mesh()
    PB = np.array([body.matrix_world @ v.co for v in emb.vertices]); evb.to_mesh_clear()
    def arm_centre(a, b, t, sx):
        p = a.lerp(b, t); d = (b - a).normalized()
        rel = PB - np.array(p); along = rel @ np.array(d)
        sel = PB[(np.abs(along) < 0.015) & (PB[:, 0] * sx > abs(p.x) - 0.09) & (np.linalg.norm(rel, axis=1) < 0.12)]
        return mathutils.Vector(sel.mean(axis=0)) if len(sel) > 5 else p
    for sx, sfx in ((-1, ".R"), (1, ".L")):
        sh0 = joint(rig, "upper_arm" + sfx); el0 = joint(rig, "forearm" + sfx); wr0 = joint(rig, "hand" + sfx)
        sh = arm_centre(sh0, el0, 0.15, sx); el = arm_centre(sh0, el0, 1.0, sx); wr = arm_centre(el0, wr0, 0.97, sx)
        inner = mathutils.Vector((sx * 0.11, sh.y, sh.z - 0.02))
        mid1 = arm_centre(sh0, el0, 0.55, sx); mid2 = arm_centre(el0, wr0, 0.5, sx)
        path = [inner, sh + mathutils.Vector((0, 0, 0.012)), mid1, el, mid2, wr + (el - wr).normalized() * 0.085]
        tube(f"Sleeve{sx}", [tuple(p) for p in path], 0.068, mat=M_THOBE, coll=coll, segs=24, taper=lambda t: 1.0 - 0.25 * t - 0.035 * math.sin(t * 9) ** 2)
        cdir = (wr - el).normalized(); c0 = wr - cdir * 0.085; c1 = wr - cdir * 0.008
        tube(f"Cuff{sx}", [tuple(c0), tuple(c1)], 0.045, mat=M_THOBE, coll=coll, segs=24)
        for kk in range(2):
            p = c0.lerp(c1, 0.3 + 0.35 * kk) + mathutils.Vector((sx * 0.044, 0.0, 0.0))
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.0055, depth=0.003, location=p, rotation=(0, math.radians(90), 0))
            _into(bpy.context.active_object, coll).data.materials.append(M_BTN)
        if sx > 0: build_watch(coll, M_WSTRAP, M_BTN, tuple(c1 + cdir * 0.03))
    # sandals under the real feet
    dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); evm = ev.to_mesh()
    co = np.array([body.matrix_world @ v.co for v in evm.vertices]); ev.to_mesh_clear()
    for sx in (-1, 1):
        f = co[(co[:, 2] < 0.04) & (co[:, 0] * sx > 0.02)]
        cx_, cy_ = f[:, 0].mean(), f[:, 1].mean(); ln = f[:, 1].max() - f[:, 1].min()
        rbox(f"Sole{sx}", (0.105, ln + 0.03, 0.02), (cx_, cy_, 0.006), bevel=0.012, mat=M_SOLE, coll=coll, segments=3)
        strap = [(cx_ + 0.058 * math.cos(a), cy_ - ln * 0.18, 0.016 + 0.052 * math.sin(a)) for a in [kk * math.pi / 14 for kk in range(15)]]
        tube(f"Strap{sx}", strap, 0.017, mat=M_STRAP, coll=coll, segs=8)
    beard = bpy.data.objects.get("HeroBeard")
    colliders = [(head, 0.004), (thobe, 0.006), (body, 0.006)] + [(bpy.data.objects[f"Sleeve{sx}"], 0.006) for sx in (-1, 1)]
    if beard: colliders.append((beard, 0.003))
    shem, cap = build_headwear(coll, M_WHITE, M_BLACK, colliders, frames=frames)
    g_ = bpy.data.objects.get("FaceGuard")
    if g_: colliders.append((g_, 0))
    for ob, _ in colliders + [(cap, 0)]:
        for md in list(ob.modifiers):
            if md.type == "COLLISION": ob.modifiers.remove(md)
    bpy.context.view_layer.update()
    root = bpy.data.objects.new("HeroRoot", None); coll.objects.link(root)
    for ob in list(coll.objects):
        if ob is not root and ob.parent is None:
            mw = ob.matrix_world.copy(); ob.parent = root; ob.matrix_world = mw
    return root, coll
