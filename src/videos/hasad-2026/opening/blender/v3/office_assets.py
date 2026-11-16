# Detailed reusable assets for the office (see v3-office-study.md, round 2). Exec'd after toon_lib.py.
#   sim_curtain()  – linen curtain draped by a real cloth simulation (pinch-pleat header + tie-back pins), then frozen
#   book_meshes()  – one hardcover book built from its real parts (case, overhang, rounded spine, raised bands, label,
#                    gilt lines, head/tail bands, page block), a few colour variants for instancing
#   sadu_material()/sadu_rug() – Al Sadu bands: comb stripes, drus al-khail (horse-teeth) triangles, al-'uwairjan dots, fringes
#   qarah_mesa()   – Jabal Al-Qarah mesa: reddish base + talus, fluted grey-beige sandstone with red marl bands,
#                    overhanging limestone cap, dark cave mouths
import math, random
import bpy

# ------------------------------------------------------------------ curtain (cloth simulation)
def sim_curtain(name, x_plane, y_wall, y_open, z_top, z_bottom, tie_z, mat, coll=None, frames=70, seed=1):
    """y_wall: edge against the wall (where it is tied back); y_open: edge toward the window centre."""
    rnd = random.Random(seed)
    flat_w = abs(y_open - y_wall) * 2.3            # real fabric width (gathered ~2.3×)
    nx, nz = 46, 56
    sgn = 1 if y_open > y_wall else -1
    V, F, pin = [], [], []
    for j in range(nz + 1):
        t = j / nz                                   # 0 = top, 1 = bottom
        z = z_top - (z_top - z_bottom) * t
        for i in range(nx + 1):
            u = i / nx
            # header: pinch pleats every 4 columns (zig-zag in x) across the rod width
            head_y = y_wall + sgn * abs(y_open - y_wall) * u
            head_x = x_plane + (0.07 if (i // 2) % 2 else 0.0)
            # tie-back: the whole width gathered into a 0.12 m bunch near the wall
            tie_y = y_wall + sgn * 0.12 * u
            if z >= tie_z:
                k = (z_top - z) / (z_top - tie_z); k = k * k
                y = head_y * (1 - k) + tie_y * k
            else:
                k = (tie_z - z) / (tie_z - z_bottom)
                y = tie_y * (1 - k) + (y_wall + sgn * abs(y_open - y_wall) * 0.9 * u) * k
            x = head_x if j == 0 else x_plane + 0.05 * math.sin(u * math.pi * 11) + rnd.uniform(-0.004, 0.004)
            V.append((x, y, z))
            pin.append(1.0 if j == 0 else (1.0 if abs(z - tie_z) < (z_top - z_bottom) / nz * 0.6 else 0.0))
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    ob = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(ob)
    vg = ob.vertex_groups.new(name="pin")
    for idx, w in enumerate(pin):
        if w > 0: vg.add([idx], w, "REPLACE")
    cl = ob.modifiers.new("Cloth", "CLOTH")
    s = cl.settings
    s.quality = 7; s.mass = 0.35; s.air_damping = 2.0
    s.tension_stiffness = 18; s.compression_stiffness = 18; s.shear_stiffness = 6; s.bending_stiffness = 0.6
    s.vertex_group_mass = "pin"; s.pin_stiffness = 1.0
    cl.point_cache.frame_start = 1; cl.point_cache.frame_end = frames
    sc_ = bpy.context.scene
    old = (sc_.frame_start, sc_.frame_end)
    sc_.frame_start, sc_.frame_end = 1, max(frames, old[1])
    for f in range(1, frames + 1): sc_.frame_set(f)
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier="Cloth")
    sc_.frame_start, sc_.frame_end = old; sc_.frame_set(1)
    so = ob.modifiers.new("Thick", "SOLIDIFY"); so.thickness = 0.004
    for p in ob.data.polygons: p.use_smooth = True
    ob.data.materials.append(mat)
    return ob

# ------------------------------------------------------------------ book
def book_meshes(variants, h=0.24, d=0.17, t=0.036):
    """variants: list of (cover_rgb, band_rgb, label_rgb). Returns meshes with 'Col' attribute; slot 0 = cover, 1 = pages.
    Local frame: spine faces -Y, fore-edge +Y, height +Z, thickness X. Origin at bottom-centre of the spine."""
    out = []
    for vi, (cov, band, lab) in enumerate(variants):
        V, F, C, M = [], [], [], []
        def box(x0, x1, y0, y1, z0, z1, col, mi=0):
            b = len(V)
            V.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
            C.extend([col] * 8)
            for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
                F.append(tuple(b + k for k in f)); M.append(mi)
        def spine_arc(r, z0, z1, col, segs=12, y_off=0.0):
            b = len(V)
            for k in range(segs + 1):
                a = math.pi * k / segs             # half-circle bulging toward -Y
                x, y = r * math.cos(a), -r * math.sin(a) + y_off
                V.extend([(x, y, z0), (x, y, z1)]); C.extend([col, col])
            for k in range(segs):
                i0 = b + 2 * k; F.append((i0, i0 + 2, i0 + 3, i0 + 1)); M.append(0)
        bt, ov = 0.0028, 0.003                     # board thickness, overhang
        hx = t / 2
        box(-hx, -hx + bt, 0.0, d, 0.0, h, cov)                   # boards
        box(hx - bt, hx, 0.0, d, 0.0, h, cov)
        box(-hx + bt, hx - bt, 0.004, d - ov, ov, h - ov, (0.96, 0.93, 0.84), 1)   # page block (inset = overhang)
        spine_arc(hx, 0.0, h, cov)                                 # rounded spine
        for zc in (0.22 * h, 0.78 * h):                            # raised bands
            spine_arc(hx + 0.0016, zc - 0.004, zc + 0.004, band)
        spine_arc(hx + 0.0008, 0.36 * h, 0.64 * h, lab, segs=8)   # title label
        for zc in (0.35 * h, 0.65 * h):                            # gilt lines
            spine_arc(hx + 0.0012, zc - 0.0012, zc + 0.0012, (0.95, 0.75, 0.3), segs=8)
        for zc in (ov, h - ov - 0.003):                            # head / tail bands
            box(-hx + bt, hx - bt, 0.0, 0.006, zc, zc + 0.003, band)
        me = bpy.data.meshes.new(f"Book{vi}"); me.from_pydata(V, [], F); me.update()
        for p, mi in zip(me.polygons, M): p.material_index = mi
        attr = me.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
        for i, c in enumerate(C): attr.data[i].color = (*c, 1)
        out.append(me)
    return out

def fill_shelf(meshes, mats, x0, x1, y, z, coll=None, seed=0, leaning=True):
    """Spines facing the room (-Y). Mixed heights/thickness, a gap, a leaning book, sometimes a flat stack."""
    rnd = random.Random(seed)
    x = x0
    placed = []
    while x < x1 - 0.05:
        if rnd.random() < 0.03 and x < x1 - 0.3:            # a horizontal stack of 2–4 books
            zz = z
            for k in range(rnd.randint(2, 4)):
                me = rnd.choice(meshes); ob = bpy.data.objects.new("BookFlat", me); (coll or bpy.context.scene.collection).objects.link(ob)
                s = rnd.uniform(0.85, 1.05); th = rnd.uniform(0.8, 1.3)
                ob.scale = (th, s, s); ob.rotation_euler = (0, math.radians(90), rnd.uniform(-0.08, 0.08))
                ob.location = (x + 0.12, y, zz + 0.036 * th / 2 + 0.002); zz += 0.036 * th
            x += 0.27; continue
        me = rnd.choice(meshes)
        s = rnd.uniform(0.9, 1.12); th = rnd.uniform(0.8, 1.4)
        ob = bpy.data.objects.new("Book", me); (coll or bpy.context.scene.collection).objects.link(ob)
        w = 0.036 * th
        ob.scale = (th, rnd.uniform(0.9, 1.08), s); ob.location = (x + w / 2, y, z)
        ob.rotation_euler = (0, 0, rnd.uniform(-0.03, 0.03))
        x += w + rnd.uniform(0.0, 0.003)
        if rnd.random() < 0.05: x += rnd.uniform(0.04, 0.1)
        placed.append(ob)
    if leaning and placed:                                    # last book leans on its neighbour
        ob = placed[-1]; ob.rotation_euler = (0, math.radians(-14), 0); ob.location.x += 0.02
    return placed

# ------------------------------------------------------------------ Sadu rug
def sadu_material(cel_fn, new_mat, ramp, k=1.0):
    m, nt, out = new_mat("SaduRug")
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["UV"], sp.inputs[0])
    def M(op, a, b=None, c=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate((a, b, c)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: nt.links.new(x, n.inputs[i])
        return n.outputs[0]
    u, v = sp.outputs["X"], sp.outputs["Y"]
    d = M("PINGPONG", v, 0.5)                                    # 0 at long edges → 0.5 centre
    def between(x, a, b): return M("MULTIPLY", M("GREATER_THAN", x, a), M("LESS_THAN", x, b))
    BLACK, WHITE, RED, BROWN, BEIGE = (0.05, 0.04, 0.04), (0.9, 0.86, 0.78), (0.55, 0.08, 0.06), (0.32, 0.18, 0.1), (0.8, 0.68, 0.5)
    base = ramp(nt, [(0.0, BLACK), (0.035, BLACK), (0.1, RED), (0.21, BLACK), (0.235, BROWN), (0.3, RED)])
    nt.links.new(d, base.inputs["Fac"])
    col = base.outputs["Color"]
    def over(col_in, mask, rgb):
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
        nt.links.new(mask, mx.inputs["Factor"]); nt.links.new(col_in, mx.inputs[6]); mx.inputs[7].default_value = (*rgb, 1)
        return mx.outputs[2]
    # comb stripes (0.035–0.1): fine alternating stripes along the length
    comb = M("MULTIPLY", between(d, 0.035, 0.1), M("GREATER_THAN", M("PINGPONG", M("MULTIPLY", u, 140 * k), 1.0), 0.5))
    col = over(col, comb, WHITE)
    # drus al-khail — horse teeth (0.1–0.21): a row of white triangles rising from the band's inner edge
    tooth = M("MULTIPLY", M("PINGPONG", M("MULTIPLY", u, 36 * k), 0.5), 2.0)           # 0..1 saw-tooth
    rel = M("DIVIDE", M("SUBTRACT", d, 0.1), 0.11)
    teeth = M("MULTIPLY", between(d, 0.1, 0.21), M("LESS_THAN", rel, tooth))
    col = over(col, teeth, WHITE)
    # al-'uwairjan dots (0.235–0.3): beige dots on brown
    du = M("LESS_THAN", M("PINGPONG", M("MULTIPLY", u, 90 * k), 0.5), 0.14)
    dv = M("LESS_THAN", M("PINGPONG", M("MULTIPLY", M("SUBTRACT", d, 0.2675), 55), 0.5), 0.16)
    dots = M("MULTIPLY", between(d, 0.235, 0.3), M("MULTIPLY", du, dv))
    col = over(col, dots, BEIGE)
    # centre field: red with thin beige/black stripes and a central black-white diamond chain
    fs = M("MULTIPLY", between(d, 0.3, 0.5), M("LESS_THAN", M("PINGPONG", M("MULTIPLY", d, 22), 0.5), 0.06))
    col = over(col, fs, BEIGE)
    dia = M("LESS_THAN", M("ADD", M("PINGPONG", M("MULTIPLY", u, 18 * k), 0.5), M("MULTIPLY", M("SUBTRACT", 0.5, d), 3.0)), 0.36)
    col = over(col, M("MULTIPLY", between(d, 0.4, 0.5), dia), BLACK)
    dia2 = M("LESS_THAN", M("ADD", M("PINGPONG", M("MULTIPLY", u, 18 * k), 0.5), M("MULTIPLY", M("SUBTRACT", 0.5, d), 3.0)), 0.2)
    col = over(col, M("MULTIPLY", between(d, 0.42, 0.5), dia2), WHITE)
    cel_fn(nt, out, col, rim_amt=0)
    return m

def sadu_rug(name, cx, cy, L, W, mat, fringe_mat, coll=None, tassels=44):
    """Rug lying along X (length L) × Y (width W), with tassels on the short ends and 1 cm thickness."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(cx - L / 2, cy - W / 2, 0.012), (cx + L / 2, cy - W / 2, 0.012), (cx + L / 2, cy + W / 2, 0.012), (cx - L / 2, cy + W / 2, 0.012)], [], [(0, 1, 2, 3)])
    me.update(); uv = me.uv_layers.new(name="UV")
    for li, (a, b) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[li].uv = (a, b)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(ob)
    so = ob.modifiers.new("Thick", "SOLIDIFY"); so.thickness = 0.01; so.offset = -1
    rnd = random.Random(4)
    for sx in (-1, 1):
        for k in range(tassels):
            y = cy - W / 2 + W * (k + 0.5) / tassels
            x0 = cx + sx * L / 2; ln = rnd.uniform(0.06, 0.085)
            pts = [(x0, y, 0.008), (x0 + sx * ln * 0.5, y + rnd.uniform(-0.005, 0.005), 0.004), (x0 + sx * ln, y + rnd.uniform(-0.01, 0.01), 0.002)]
            tube("Tassel", pts, 0.0035, mat=fringe_mat, coll=coll, segs=5)
    return ob

# ------------------------------------------------------------------ Jabal Al-Qarah
def qarah_material(cel_fn, new_mat, ramp, top_z):
    m, nt, out = new_mat("QarahRock")
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    zn = nt.nodes.new("ShaderNodeMath"); zn.operation = "DIVIDE"; zn.inputs[1].default_value = top_z
    # wobble the strata a little so the bands aren't ruler-straight
    wob = nt.nodes.new("ShaderNodeTexNoise"); wob.inputs["Scale"].default_value = 0.004; nt.links.new(tc.outputs["Object"], wob.inputs["Vector"])
    wz = nt.nodes.new("ShaderNodeMath"); wz.operation = "MULTIPLY_ADD"; nt.links.new(wob.outputs["Fac"], wz.inputs[0]); wz.inputs[1].default_value = 4.0
    nt.links.new(sp.outputs["Z"], wz.inputs[2]); nt.links.new(wz.outputs[0], zn.inputs[0])
    strata = ramp(nt, [(0.0, (0.6, 0.33, 0.22)), (0.1, (0.7, 0.42, 0.28)), (0.16, (0.78, 0.69, 0.56)), (0.3, (0.66, 0.36, 0.26)),
                       (0.32, (0.8, 0.71, 0.58)), (0.48, (0.74, 0.64, 0.52)), (0.55, (0.64, 0.34, 0.25)), (0.57, (0.8, 0.72, 0.6)),
                       (0.74, (0.72, 0.4, 0.28)), (0.76, (0.79, 0.7, 0.57)), (0.94, (0.93, 0.87, 0.74))])
    nt.links.new(zn.outputs[0], strata.inputs["Fac"])
    # vertical erosion flutes: noise stretched along Z → darker streaks
    mp = nt.nodes.new("ShaderNodeMapping"); nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); mp.inputs["Scale"].default_value = (0.25, 0.25, 0.012)
    fl = nt.nodes.new("ShaderNodeTexNoise"); fl.inputs["Scale"].default_value = 1.0; fl.inputs["Detail"].default_value = 3
    nt.links.new(mp.outputs["Vector"], fl.inputs["Vector"])
    flr = ramp(nt, [(0.0, (0.86, 0.83, 0.85)), (0.42, (1, 1, 1))]); nt.links.new(fl.outputs["Fac"], flr.inputs["Fac"])
    mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1
    nt.links.new(strata.outputs["Color"], mul.inputs[6]); nt.links.new(flr.outputs["Color"], mul.inputs[7])
    # cave mouths in the lower third
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 0.05; nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    cave = nt.nodes.new("ShaderNodeMath"); cave.operation = "LESS_THAN"; cave.inputs[1].default_value = 0.12; nt.links.new(vo.outputs["Distance"], cave.inputs[0])
    low = nt.nodes.new("ShaderNodeMath"); low.operation = "LESS_THAN"; low.inputs[1].default_value = 0.3; nt.links.new(zn.outputs[0], low.inputs[0])
    hi = nt.nodes.new("ShaderNodeMath"); hi.operation = "GREATER_THAN"; hi.inputs[1].default_value = 0.12; nt.links.new(zn.outputs[0], hi.inputs[0])
    cm = nt.nodes.new("ShaderNodeMath"); cm.operation = "MULTIPLY"; nt.links.new(cave.outputs[0], cm.inputs[0]); nt.links.new(low.outputs[0], cm.inputs[1])
    cm2 = nt.nodes.new("ShaderNodeMath"); cm2.operation = "MULTIPLY"; nt.links.new(cm.outputs[0], cm2.inputs[0]); nt.links.new(hi.outputs[0], cm2.inputs[1])
    cmix = nt.nodes.new("ShaderNodeMix"); cmix.data_type = "RGBA"
    nt.links.new(cm2.outputs[0], cmix.inputs["Factor"]); nt.links.new(mul.outputs[2], cmix.inputs[6]); cmix.inputs[7].default_value = (0.18, 0.1, 0.08, 1)
    cel_fn(nt, out, cmix.outputs[2], rim_amt=0.4)
    return m

def qarah_mesa(name, center, rx, ry, height, mat, coll=None, seed=0):
    """Irregular flat-topped mesa: talus apron → near-vertical fluted cliff → overhanging limestone cap → flat top."""
    rnd = random.Random(seed)
    segs = 160
    phases = [rnd.uniform(0, 6.28) for _ in range(4)]
    def rad(a):
        return 1 + 0.12 * math.sin(3 * a + phases[0]) + 0.07 * math.sin(7 * a + phases[1]) + 0.035 * math.sin(17 * a + phases[2]) + 0.02 * math.sin(41 * a + phases[3])
    levels = [(-0.0, 1.32), (0.08, 1.12), (0.14, 1.03), (0.9, 1.0), (0.955, 0.985), (0.965, 1.025), (1.0, 1.02)]
    V, F = [], []
    for k in range(segs):
        a = 2 * math.pi * k / segs; r0 = rad(a)
        flute = 1 + 0.004 * math.sin(a * 97 + phases[1]) + 0.003 * math.sin(a * 233 + phases[2]) * math.sin(a * 11)
        for (zt, rs) in levels:
            f = flute if 0.14 <= zt <= 0.9 else 1.0
            V.append((rx * r0 * rs * f * math.cos(a), ry * r0 * rs * f * math.sin(a), height * zt))
    nl = len(levels)
    for k in range(segs):
        k2 = (k + 1) % segs
        for i in range(nl - 1):
            F.append((k * nl + i, k2 * nl + i, k2 * nl + i + 1, k * nl + i + 1))
    V.append((0, 0, height)); c = len(V) - 1
    for k in range(segs): F.append((c, k * nl + nl - 1, ((k + 1) % segs) * nl + nl - 1))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update(); me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = center
    return ob

# ------------------------------------------------------------------ pinch-pleat drapery (procedural, fabric-conserving folds)
def drape(name, x_back, y_wall, y_open, z_top, z_bot, mat, coll=None, tie_z=None, tie_w=0.22, fullness=2.5,
          pleat=0.127, base_col=(0.3, 0.5, 0.5), band_col=None, seed=1, rings_mat=None, rod_x=None):
    """Curtain hanging in the plane x≈x_back (folds bulge toward +x / the room), spanning y_wall → y_open.
    Fold depth follows how much the fabric is gathered locally (2.5× fullness → deep tubes; tie-back → hourglass)."""
    rnd = random.Random(seed)
    width = abs(y_open - y_wall); sgn = 1 if y_open > y_wall else -1
    folds = max(3, round(width / pleat))
    nx, nz = folds * 10, 96
    def wfac(z):
        if tie_z is None:
            return 1.0
        def sm(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
        r_tie = tie_w / width
        if z >= tie_z:
            return 1.0 + (r_tie - 1.0) * sm((z_top - z) / (z_top - tie_z)) ** 1.4
        return r_tie + (0.62 - r_tie) * sm((tie_z - z) / (tie_z - z_bot)) ** 0.8
    phases = [rnd.uniform(0, 6.28) for _ in range(3)]
    V, F, C = [], [], []
    band = band_col or tuple(c * 0.78 for c in base_col)
    for j in range(nz + 1):
        t = j / nz; z = z_top - (z_top - z_bot) * t
        w = wfac(z)
        lam = pleat * w
        gather = fullness / max(w, 0.08)
        A = min(0.14, lam / (2 * math.pi) * math.sqrt(max(gather * gather - 1, 0.0)) * 0.55)
        if z > z_top - 0.09: A *= 0.55                     # stitched pleat heads are tighter
        for i in range(nx + 1):
            u = i / nx
            ph = 2 * math.pi * folds * u + 0.35 * math.sin(z * 2.1 + phases[0]) + 0.2 * math.sin(u * 5 + phases[1])
            s = math.sin(ph); s = math.copysign(abs(s) ** 0.75, s)   # rounder tubes, sharper valleys
            x = x_back + A * (1 + s)
            if j == nz: x += 0.01                           # hem rolls slightly forward
            y = y_wall + sgn * width * w * u
            V.append((x, y, z))
            C.append(band if (z < z_bot + 0.1 or z > z_top - 0.1) else base_col)
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    for p in me.polygons: p.use_smooth = True
    attr = me.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
    for i, c in enumerate(C): attr.data[i].color = (*c, 1)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(ob)
    so = ob.modifiers.new("Thick", "SOLIDIFY"); so.thickness = 0.005
    if rings_mat is not None and rod_x is not None:          # a ring on the rod at every pleat
        for k in range(folds + 1):
            y = y_wall + sgn * width * k / folds
            bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.0045, location=(rod_x, y, z_top + 0.03), rotation=(0, math.radians(90), 0))
            r_ = bpy.context.active_object; r_.data.materials.append(rings_mat)
            for c_ in list(r_.users_collection): c_.objects.unlink(r_)
            (coll or bpy.context.scene.collection).objects.link(r_)
    return ob
