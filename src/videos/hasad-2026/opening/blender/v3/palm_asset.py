# Detailed date palm (Phoenix dactylifera) asset for the anime canal scene — built once, instanced many times.
# Anatomy (botanical refs): pinnate fronds 3–5 m with ~150 leaflets (~30–45 cm × 2 cm) that are V-folded and stick
# out of the rachis in several planes (spiky silhouette); the lowest leaflets are short sharp spines; 20–30 fronds +
# an erect central spear, upper fronds erect, lower drooping and yellowing; trunk clad in persistent woody leaf bases
# (diamond pattern of cut stubs on farm palms), fibre at the crown; hanging date bunches in season.
# Usage inside Blender:  exec(open(path).read()); trunk_me, crown_me = build_palm(seed, height, lod)
import math, random
import bpy

def _col_attr(me, name, cols):
    """Per-vertex colour attribute (point domain)."""
    attr = me.color_attributes.new(name=name, type="FLOAT_COLOR", domain="POINT")
    for i, c in enumerate(cols): attr.data[i].color = (*c, 1.0)

def _rot(v, ax, ang):
    x, y, z = v; c, s = math.cos(ang), math.sin(ang)
    if ax == "x": return (x, y * c - z * s, y * s + z * c)
    if ax == "y": return (x * c + z * s, y, -x * s + z * c)
    return (x * c - y * s, x * s + y * c, z)

def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def _norm(a):
    l = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def _lerp3(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

GREEN = (0.24, 0.42, 0.2)      # glaucous grey-green
GREEN_YOUNG = (0.42, 0.58, 0.18)
YELLOW = (0.62, 0.55, 0.22)
DRY = (0.50, 0.36, 0.18)

def _frond(V, F, C, rnd, base, yaw, pitch, length, color, lod):
    """One pinnate frond. base: attach point; yaw: around trunk; pitch: + up / - down at the base."""
    n_seg = 16
    # rachis centre line in the frond's local plane (x forward, z up): starts at `pitch`, gravity bends it down
    pts, ang = [], pitch
    p = (0.0, 0.0, 0.0)
    droop = (0.7 + 0.4 * rnd.random()) * (0.85 + 0.3 * max(0.0, -pitch))   # stiffness variation; lower fronds sag more
    for i in range(n_seg + 1):
        pts.append(p)
        step = length / n_seg
        p = (p[0] + step * math.cos(ang), 0.0, p[2] + step * math.sin(ang))
        ang -= droop * (0.9 / n_seg) * (0.6 + i / n_seg)   # more bend toward the tip
    twist = rnd.uniform(-0.25, 0.25)              # the whole frond rolls a little
    def to_world(v):
        v = _rot(v, "x", twist)
        v = _rot(v, "z", yaw)
        return _add(v, base)
    # rachis as a thin 3-sided tapered tube
    ring = []
    for i, c in enumerate(pts):
        t = i / n_seg; r = 0.045 * (1 - t) + 0.006
        nxt = pts[min(i + 1, n_seg)]; prv = pts[max(i - 1, 0)]
        tan = _norm((nxt[0] - prv[0], 0, nxt[2] - prv[2]))
        side = (0, 1, 0); up = _cross(side, tan)
        idx = []
        for k in range(3):
            a = 2 * math.pi * k / 3
            off = _add(_mul(side, r * math.cos(a)), _mul(up, r * math.sin(a)))
            V.append(to_world(_add(c, off))); C.append(_lerp3(color, (0.55, 0.5, 0.3), 0.4)); idx.append(len(V) - 1)
        ring.append(idx)
    for i in range(n_seg):
        for k in range(3):
            a, b = ring[i][k], ring[i][(k + 1) % 3]; c, d = ring[i + 1][(k + 1) % 3], ring[i + 1][k]
            F.append((a, b, c, d))
    # leaflets: ~75 per side (lod scales), V-folded (two planes), forward-angled, spines at the base
    per_side = int(75 * lod)
    for side_sign in (-1, 1):
        for j in range(per_side):
            t = 0.08 + 0.9 * (j + rnd.uniform(-0.3, 0.3)) / per_side
            seg = min(int(t * n_seg), n_seg - 1); ft = t * n_seg - seg
            c = _lerp3(pts[seg], pts[seg + 1], ft)
            tan = _norm(_add(pts[seg + 1], _mul(pts[seg], -1)))
            spine = t < 0.2
            # length profile: spines short; leaflets longest in the middle, short at the tip
            L = 0.16 + 0.1 * t / 0.2 if spine else 0.62 * math.sin(math.pi * (0.15 + 0.8 * (t - 0.2) / 0.8)) ** 0.7 + 0.08
            L *= rnd.uniform(0.85, 1.12) * length / 3.6
            W = 0.012 if spine else 0.024
            # direction: sideways, swept toward the tip, lifted out of the frond plane (V-shape, several planes)
            elev = rnd.choice([0.35, 0.65, 0.95]) * (0.5 if spine else 1.0) + rnd.uniform(-0.1, 0.1)
            sweep = 0.75 if spine else 0.55 + rnd.uniform(-0.1, 0.1)
            sidev = (0, side_sign, 0)
            up = _norm(_cross(tan, sidev)) if side_sign > 0 else _norm(_cross(sidev, tan))
            d = _norm(_add(_add(_mul(sidev, math.cos(sweep)), _mul(tan, math.sin(sweep))), _mul(up, math.sin(elev))))
            wv = _norm(_cross(d, up))        # leaflet width direction
            # 3-point blade, slight droop along its length, V-fold: centre ridge raised
            base_i = len(V)
            prof = [(0.0, 1.0), (0.55, 0.85), (1.0, 0.0)]
            for (s, wk) in prof:
                pos = _add(c, _mul(d, L * s)); pos = (pos[0], pos[1], pos[2] - 0.08 * L * s * s)
                half = W * wk
                V.append(to_world(_add(pos, _mul(wv, -half)))); V.append(to_world(_add(pos, _mul(up, half * 0.7)))); V.append(to_world(_add(pos, _mul(wv, half))))
                tip_col = _lerp3(color, (0.72, 0.66, 0.3), 0.35 * s) if not spine else _lerp3(color, (0.6, 0.55, 0.3), 0.5)
                C.extend([tip_col] * 3)
            for r_ in range(2):
                a0 = base_i + 3 * r_; a1 = a0 + 3
                F.append((a0, a0 + 1, a1 + 1, a1)); F.append((a0 + 1, a0 + 2, a1 + 2, a1 + 1))

def _dates(V, F, C, rnd, base, yaw):
    """A hanging date bunch: a stalk arching out and down, with strands of amber dates."""
    stalk = []
    for i in range(7):
        t = i / 6
        stalk.append(_add(base, _rot((0.55 * t, 0, -0.15 * t - 0.75 * t * t), "z", yaw)))
    for i in range(6):
        a, b = stalk[i], stalk[i + 1]; k = len(V)
        V.extend([_add(a, (0, 0, 0.02)), _add(a, (0.02, 0, -0.02)), _add(b, (0.02, 0, -0.02)), _add(b, (0, 0, 0.02))])
        C.extend([(0.72, 0.45, 0.12)] * 4); F.append((k, k + 1, k + 2, k + 3))
    tip = stalk[-1]
    for s in range(18):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(0.02, 0.16)
        start = _add(tip, (r * math.cos(a), r * math.sin(a), 0.05))
        for q in range(rnd.randint(4, 8)):
            pz = start[2] - 0.06 * q - rnd.uniform(0, 0.03)
            ctr = (start[0] + rnd.uniform(-0.03, 0.03), start[1] + rnd.uniform(-0.03, 0.03), pz)
            col = rnd.choice([(0.9, 0.52, 0.1), (0.95, 0.68, 0.16), (0.78, 0.3, 0.1)])
            k = len(V); rx, rz = 0.017, 0.026
            V.extend([_add(ctr, (0, 0, rz)), _add(ctr, (rx, 0, 0)), _add(ctr, (0, rx, 0)), _add(ctr, (-rx, 0, 0)), _add(ctr, (0, -rx, 0)), _add(ctr, (0, 0, -rz))])
            C.extend([col] * 6)
            for e in range(4):
                F.append((k, k + 1 + e, k + 1 + (e + 1) % 4)); F.append((k + 5, k + 1 + (e + 1) % 4, k + 1 + e))

def build_palm(seed=1, height=8.0, lod=1.0, dates=True, name="Palm"):
    rnd = random.Random(seed)
    # ---- trunk: persistent leaf-base stubs → diamond relief; slight S-curve; wider foot ----
    tv, tf, tc = [], [], []
    sides, row_h = 24, 0.06
    rows = int(height / row_h)
    curve = (rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25))
    for r in range(rows + 1):
        z = r * row_h; t = z / height
        rad = 0.24 + 0.1 * (1 - t) ** 3 + 0.03 * t
        cx, cy = curve[0] * math.sin(math.pi * t), curve[1] * t * t
        for k in range(sides):
            th = 2 * math.pi * k / sides
            u, v = th * 6 / (2 * math.pi), z / 0.2       # 6 stubs around, one row each 20 cm (offset rows)
            fu, fv = (u + v) % 1.0, (u - v) % 1.0
            stub = (abs(fu - 0.5) * 2) * (abs(fv - 0.5) * 2)     # 0 at crevices → 1 at stub centres
            rr = rad + 0.045 * stub * (0.4 + 0.6 * t) * (0 if t < 0.04 else 1)
            tv.append((cx + rr * math.cos(th), cy + rr * math.sin(th), z))
            shade = 0.45 + 0.55 * stub
            tc.append(_lerp3((0.2, 0.12, 0.07), (0.5, 0.36, 0.22), shade))
    for r in range(rows):
        for k in range(sides):
            a = r * sides + k; b = r * sides + (k + 1) % sides
            tf.append((a, b, b + sides, a + sides))
    trunk_me = bpy.data.meshes.new(f"{name}_trunk"); trunk_me.from_pydata(tv, [], tf); trunk_me.update()
    _col_attr(trunk_me, "Col", tc)
    for p in trunk_me.polygons: p.use_smooth = True
    top = (curve[0] * math.sin(math.pi), curve[1], height)
    # ---- crown ----
    V, F, C = [], [], []
    # fibrous boot at the crown
    for k in range(10):
        a = 2 * math.pi * k / 10 + rnd.uniform(-0.2, 0.2)
        b0 = _add(top, (0.2 * math.cos(a), 0.2 * math.sin(a), -0.5))
        b1 = _add(top, (0.34 * math.cos(a), 0.34 * math.sin(a), 0.15))
        w = (0.12 * -math.sin(a), 0.12 * math.cos(a), 0)
        i = len(V); V.extend([_add(b0, w), _add(b0, _mul(w, -1)), _add(b1, _mul(w, -1)), _add(b1, w)])
        C.extend([(0.42, 0.3, 0.17)] * 4); F.append((i, i + 1, i + 2, i + 3))
    # fronds: spear + phyllotaxis spiral, pitch from erect (top) to drooping (bottom)
    n = rnd.randint(24, 30)
    golden = math.radians(137.5)
    for i in range(n):
        t = i / (n - 1)
        yaw = i * golden + rnd.uniform(-0.15, 0.15)
        pitch = math.radians(66 - 92 * t ** 1.25 + rnd.uniform(-7, 7))   # farm palms: the lowest fronds are pruned
        length = rnd.uniform(3.4, 4.4) * (0.75 + 0.25 * min(1, t * 3))
        z = -0.55 * t
        base = _add(top, (0.22 * math.cos(yaw), 0.22 * math.sin(yaw), z))
        col = GREEN if t < 0.7 else _lerp3(GREEN, YELLOW, (t - 0.7) / 0.3)
        if t > 0.93 and rnd.random() < 0.6: col = DRY
        col = _lerp3(col, GREEN_YOUNG, max(0, 0.25 - t))
        _frond(V, F, C, rnd, base, yaw, pitch, length, col, lod)
    for i in range(3):   # central spear: young, erect, lighter
        yaw = rnd.uniform(0, 2 * math.pi)
        _frond(V, F, C, rnd, _add(top, (0, 0, 0.1)), yaw, math.radians(rnd.uniform(78, 86)), rnd.uniform(2.0, 2.8), GREEN_YOUNG, lod * 0.8)
    if dates:
        for i in range(rnd.randint(3, 5)):
            yaw = rnd.uniform(0, 2 * math.pi)
            _dates(V, F, C, rnd, _add(top, (0.25 * math.cos(yaw), 0.25 * math.sin(yaw), -0.45)), yaw)
    crown_me = bpy.data.meshes.new(f"{name}_crown"); crown_me.from_pydata(V, [], F); crown_me.update()
    _col_attr(crown_me, "Col", C)
    return trunk_me, crown_me
