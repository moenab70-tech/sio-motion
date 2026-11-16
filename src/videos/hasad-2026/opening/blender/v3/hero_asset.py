# v3 · Prototype 3D toon hero (see v3-hero-study.md / HERO_SHEET.png). Exec'd after toon_lib.py inside a scene script.
# 1.78 m, 7.5 heads. Saudi thobe (stand-up band collar + 2 buttons, cuffs with cufflinks, chest pocket + pen),
# head with short black beard, red/white shemagh draped by a REAL cloth simulation over the head and shoulders
# (crown pinned under the agal), black double agal with two tassel cords at the back, wristwatch.
# build_hero(loc, yaw, frames, wind) → root empty; head/chest are keyed for a slow head turn + breathing.
import math, random
import bpy
import mathutils

def _cel_mat(name, rgb, rim=0.5, translucent=0.0):
    m, nt, out = new_mat(name); cel_output(nt, out, flat(nt, rgb), rim_amt=rim, translucent=translucent); return m

def _shemagh_mat():
    m, nt, out = new_mat("Shemagh")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 120
    ck.inputs["Color1"].default_value = (0.72, 0.05, 0.07, 1); ck.inputs["Color2"].default_value = (0.97, 0.95, 0.92, 1)
    nt.links.new(tc.outputs["UV"], ck.inputs["Vector"])
    # houndstooth-like breakup + a red border band near the edges
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["UV"], sp.inputs[0])
    def edge(sock):
        a = nt.nodes.new("ShaderNodeMath"); a.operation = "PINGPONG"; a.inputs[1].default_value = 0.5; nt.links.new(sock, a.inputs[0]); return a.outputs[0]
    mn = nt.nodes.new("ShaderNodeMath"); mn.operation = "MINIMUM"; nt.links.new(edge(sp.outputs["X"]), mn.inputs[0]); nt.links.new(edge(sp.outputs["Y"]), mn.inputs[1])
    br = ramp(nt, [(0.0, (0.97, 0.95, 0.92)), (0.012, (0.72, 0.05, 0.07)), (0.03, (0.97, 0.95, 0.92)), (0.04, (0, 0, 0))])
    nt.links.new(mn.outputs[0], br.inputs["Fac"])
    inside = nt.nodes.new("ShaderNodeMath"); inside.operation = "GREATER_THAN"; inside.inputs[1].default_value = 0.04; nt.links.new(mn.outputs[0], inside.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    nt.links.new(inside.outputs[0], mx.inputs["Factor"]); nt.links.new(br.outputs["Color"], mx.inputs[6]); nt.links.new(ck.outputs["Color"], mx.inputs[7])
    cel_output(nt, out, mx.outputs[2], rim_amt=0.55, translucent=0.2)
    try: m.use_backface_culling = False
    except Exception: pass
    return m

def _link(ob, coll, parent=None):
    for c in list(ob.users_collection): c.objects.unlink(ob)
    coll.objects.link(ob)
    if parent is not None:
        mw = ob.matrix_world.copy(); ob.parent = parent; ob.matrix_world = mw
    return ob

def build_hero(loc=(0, 0, 0), yaw=0.0, frames=120, wind=(1.0, 0.0, 0.0), wind_strength=180.0, coll=None, noink=None, seed=1):
    sc = bpy.context.scene
    if coll is None:
        coll = bpy.data.collections.new("HeroColl"); sc.collection.children.link(coll)
    M_THOBE = _cel_mat("Thobe", (0.95, 0.94, 0.92), rim=0.6, translucent=0.15)
    M_SKIN = _cel_mat("Skin", (0.78, 0.55, 0.4), rim=0.5)
    M_BEARD = _cel_mat("Beard", (0.06, 0.05, 0.05), rim=0.3)
    M_BLACK = _cel_mat("Agal", (0.04, 0.04, 0.045), rim=0.5)
    M_SILVER = _cel_mat("Silver", (0.8, 0.82, 0.86), rim=0.7)
    M_LEATHER = _cel_mat("WatchLeather", (0.32, 0.18, 0.1), rim=0.3)
    M_SHEM = _shemagh_mat()
    H = 1.78; HEAD = H / 7.5

    root = bpy.data.objects.new("Hero", None); coll.objects.link(root)
    # ---- thobe body: revolved profile, elliptical section (deeper than wide is wrong → scale Y 0.72)
    prof = [(0.0, 0.03), (0.29, 0.03), (0.3, 0.06), (0.27, 0.45), (0.22, 0.85), (0.18, 0.98), (0.17, 1.08), (0.19, 1.2),
            (0.2, 1.32), (0.19, 1.4), (0.13, 1.46), (0.06, 1.5), (0.055, 1.53)]
    body = lathe("ThobeBody", prof, 40, mat=M_THOBE, coll=coll, cap_bottom=True)
    body.scale = (1.0, 0.72, 1.0)
    # gentle hem sway (wave modifier) — the thobe moves in the breeze without a full simulation
    wv = body.modifiers.new("Breeze", "WAVE"); wv.use_x = True; wv.use_y = False; wv.height = 0.012; wv.width = 0.6; wv.speed = 0.05
    wv.falloff_radius = 0.0; wv.start_position_object = None
    try: wv.use_normal = False
    except Exception: pass
    # stand-up band collar + two buttons + placket + chest pocket with a pen
    collar = lathe("Collar", [(0.064, 1.5), (0.066, 1.545), (0.062, 1.55)], 32, mat=M_THOBE, coll=coll, cap_bottom=False)
    collar.scale = (1.0, 0.95, 1.0)
    for z in (1.515, 1.537):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.006, location=(0, -0.063, z)); _link(bpy.context.active_object, coll).data.materials.append(M_SILVER)
    tube("Placket", [(0, -0.143, 1.25), (0, -0.14, 1.48)], 0.004, mat=M_THOBE, coll=coll, segs=4)
    rbox("Pocket", (0.11, 0.004, 0.12), (-0.09, -0.142, 1.3), bevel=0.003, mat=M_THOBE, coll=coll)
    tube("Pen", [(-0.065, -0.146, 1.3), (-0.065, -0.147, 1.38)], 0.005, mat=M_BLACK, coll=coll, segs=6)
    # ---- arms: sleeves hang slightly forward, cuffs with cufflinks, hands
    arms = []
    for sx in (-1, 1):
        sh = (sx * 0.2, 0.0, 1.38); el = (sx * 0.25, -0.03, 1.08); wr = (sx * 0.24, -0.06, 0.82)
        sl = tube(f"Sleeve{sx}", [sh, ((sh[0] + el[0]) / 2, -0.01, 1.24), el, ((el[0] + wr[0]) / 2, -0.045, 0.95), wr], 0.055, mat=M_THOBE, coll=coll, segs=16,
                  taper=lambda t: 1.0 - 0.28 * t)
        cuff = tube(f"Cuff{sx}", [(wr[0], wr[1] + 0.005, wr[2] + 0.04), (wr[0], wr[1], wr[2] - 0.005)], 0.043, mat=M_THOBE, coll=coll, segs=16)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.007, location=(wr[0] + sx * 0.04, wr[1], wr[2] + 0.02))
        _link(bpy.context.active_object, coll).data.materials.append(M_SILVER)
        # hand: palm + four fingers + thumb, relaxed curl
        hand = bpy.data.objects.new(f"Hand{sx}", None); coll.objects.link(hand); hand.location = (wr[0], wr[1] + 0.01, wr[2] - 0.02)
        p = rbox(f"Palm{sx}", (0.035, 0.08, 0.09), (wr[0], wr[1] + 0.01, wr[2] - 0.07), bevel=0.015, mat=M_SKIN, coll=coll, segments=3)
        for k in range(4):
            y0 = wr[1] - 0.025 + k * 0.018
            tube(f"Finger{sx}{k}", [(wr[0], y0, wr[2] - 0.11), (wr[0] - sx * 0.006, y0, wr[2] - 0.15), (wr[0] - sx * 0.018, y0 + 0.004, wr[2] - 0.175)], 0.0085, mat=M_SKIN, coll=coll, segs=6)
        tube(f"Thumb{sx}", [(wr[0] - sx * 0.015, wr[1] - 0.035, wr[2] - 0.06), (wr[0] - sx * 0.02, wr[1] - 0.05, wr[2] - 0.1)], 0.01, mat=M_SKIN, coll=coll, segs=6)
        if sx < 0:   # wristwatch on the left wrist
            tube("WatchStrap", [(wr[0] + 0.03 * math.cos(a), wr[1] + 0.03 * math.sin(a), wr[2] - 0.012) for a in [i * math.pi / 8 for i in range(17)]], 0.006, mat=M_LEATHER, coll=coll, segs=4)
        arms.append(sl)
    # ---- neck + head (skull, jaw, ears, short black beard, nose)
    neck = tube("Neck", [(0, 0.0, 1.5), (0, 0.005, 1.6)], 0.052, mat=M_SKIN, coll=coll, segs=16)
    head = bpy.data.objects.new("HeadPivot", None); coll.objects.link(head); head.location = (0, 0.0, 1.6)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=1, location=(0, -0.005, 1.665))
    skull = bpy.context.active_object; skull.name = "Skull"; skull.scale = (0.078, 0.095, 0.112); skull.data.materials.append(M_SKIN)
    for p in skull.data.polygons: p.use_smooth = True
    _link(skull, coll)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=14, radius=1, location=(0, -0.035, 1.6))
    beard = bpy.context.active_object; beard.name = "Beard"; beard.scale = (0.072, 0.07, 0.06); beard.data.materials.append(M_BEARD)
    for p in beard.data.polygons: p.use_smooth = True
    _link(beard, coll)
    rbox("Moustache", (0.05, 0.012, 0.008), (0, -0.097, 1.632), bevel=0.004, mat=M_BEARD, coll=coll)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1, location=(0, -0.1, 1.665))
    nose = bpy.context.active_object; nose.scale = (0.012, 0.018, 0.022); nose.data.materials.append(M_SKIN); _link(nose, coll)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1, location=(sx * 0.078, 0.0, 1.665))
        ear = bpy.context.active_object; ear.scale = (0.01, 0.018, 0.028); ear.data.materials.append(M_SKIN); _link(ear, coll)
        # simple anime eyes + brows (only seen in three-quarter / profile)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1, location=(sx * 0.032, -0.086, 1.69))
        eye = bpy.context.active_object; eye.scale = (0.011, 0.004, 0.008); eye.data.materials.append(M_BEARD); _link(eye, coll)
        rbox(f"Brow{sx}", (0.03, 0.006, 0.006), (sx * 0.032, -0.086, 1.707), rot=(0, sx * 0.15, 0), bevel=0.002, mat=M_BEARD, coll=coll)
    # ---- white taqiyah cap under the shemagh (collider for the cloth too)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=(0, -0.005, 1.7))
    cap = bpy.context.active_object; cap.name = "Taqiyah"; cap.scale = (0.083, 0.1, 0.085); cap.data.materials.append(M_THOBE); _link(cap, coll)
    # ---- shemagh: folded triangle draped by cloth simulation over head + shoulders
    N = 46; S = 1.15
    V, F, pin = [], [], []
    for j in range(N + 1):
        for i in range(N + 1):
            u, v = i / N, j / N
            V.append(((u - 0.5) * S, (v - 0.5) * S, 0.0))
    for j in range(N):
        for i in range(N):
            a = j * (N + 1) + i; F.append((a, a + 1, a + N + 2, a + N + 1))
    me = bpy.data.meshes.new("Shemagh"); me.from_pydata(V, [], F); me.update()
    uvl = me.uv_layers.new(name="UV")
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index; uvl.data[li].uv = ((vi % (N + 1)) / N, (vi // (N + 1)) / N)
    shem = bpy.data.objects.new("Shemagh", me); coll.objects.link(shem)
    # rotate 45° so it is a diamond: one corner at the front peak, one at the back
    shem.rotation_euler = (0, 0, math.radians(45)); shem.location = (0, -0.005, 1.79)
    bpy.context.view_layer.update()
    vg = shem.vertex_groups.new(name="crown")
    mw = shem.matrix_world
    for k, vv in enumerate(me.vertices):
        w = mw @ vv.co
        d = math.hypot(w.x / 0.085, (w.y + 0.005) / 0.1)
        if d < 1.0: vg.add([k], 1.0, "REPLACE")
    for ob, thick in ((skull, 0.006), (cap, 0.006), (body, 0.01), (beard, 0.004)):
        c_ = ob.modifiers.new("Collision", "COLLISION"); c_.settings.thickness_outer = thick
        try: c_.settings.cloth_friction = 8
        except Exception: pass
    for a in arms:
        c_ = a.modifiers.new("Collision", "COLLISION"); c_.settings.thickness_outer = 0.008
    cl = shem.modifiers.new("Cloth", "CLOTH"); s = cl.settings
    s.quality = 8; s.mass = 0.15; s.air_damping = 1.2; s.bending_stiffness = 0.08
    s.tension_stiffness = 12; s.compression_stiffness = 12; s.shear_stiffness = 4
    s.vertex_group_mass = "crown"; s.pin_stiffness = 1.0
    cs = cl.collision_settings; cs.use_self_collision = True; cs.self_distance_min = 0.004; cs.distance_min = 0.005
    cl.point_cache.frame_start = 1; cl.point_cache.frame_end = frames
    shem.data.materials.append(M_SHEM)
    if noink is not None: _link(shem, noink)
    # wind (gusting) for the shemagh tails
    bpy.ops.object.effector_add(type="WIND", location=(loc[0] - 3 * wind[0], loc[1] - 3 * wind[1], 1.7))
    wf = bpy.context.active_object; wf.name = "Wind"
    _link(wf, sc.collection)
    wf.rotation_euler = mathutils.Vector(wind).to_track_quat("Z", "Y").to_euler()
    wf.field.strength = wind_strength; wf.field.noise = 2.0; wf.field.flow = 0.5
    for f, k in ((1, 0.4), (frames // 3, 1.0), (frames // 2, 0.6), (frames, 1.0)):
        wf.field.strength = wind_strength * k; wf.field.keyframe_insert("strength", frame=f)
    # ---- agal: two black rings on the crown + two tassel cords down the back
    for z, r in ((1.775, 0.088), (1.79, 0.086)):
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.075, major_segments=40, minor_segments=8, location=(0, -0.005, z))
        t = bpy.context.active_object; t.scale = (r, r * 1.15, r); t.data.materials.append(M_BLACK); _link(t, coll)
    for sx in (-0.025, 0.025):
        tube(f"AgalCord{sx}", [(sx, 0.095, 1.77), (sx * 1.3, 0.11, 1.65), (sx * 1.5, 0.12, 1.52)], 0.005, mat=M_BLACK, coll=coll, segs=6)
        bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.016, radius2=0.004, depth=0.05, location=(sx * 1.5, 0.12, 1.5))
        _link(bpy.context.active_object, coll).data.materials.append(M_BLACK)

    # ---- parent everything (except the cloth + wind, which live in world space) under the root, then place it
    bpy.context.view_layer.update()
    def zc(ob):
        if ob.type != "MESH": return ob.matrix_world.translation.z
        pts = [ob.matrix_world @ mathutils.Vector(c) for c in ob.bound_box]
        return sum(p_.z for p_ in pts) / 8
    head.parent = root
    for ob in list(coll.objects):
        if ob in (root, shem, head) or ob.parent is not None: continue
        mw_ = ob.matrix_world.copy()
        ob.parent = head if zc(ob) > 1.565 else root            # head parts turn with the head pivot
        ob.matrix_world = mw_
    mw_ = shem.matrix_world.copy(); shem.parent = head; shem.matrix_world = mw_   # crown pins follow the head
    root.location = loc; root.rotation_euler = (0, 0, yaw)
    # ---- performance (stop-motion rhythm: a pose every 2 frames ≈ 12 fps, held)
    def key_head(f, pitch, yaw_):
        head.rotation_euler = (math.radians(pitch), 0, math.radians(yaw_)); head.keyframe_insert("rotation_euler", frame=f)
    def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
    for f in range(1, frames + 1, 2):
        t = f / frames
        # looks down at the water, then lifts his gaze along the canal toward the sun
        lift = smooth((t - 0.25) / 0.4)
        key_head(f, -14 * (1 - lift) + 3 * lift, -10 * (1 - lift) + 4 * lift)
        # one deep breath: chest rises, shoulders lift a touch
        b = math.sin(math.pi * smooth((t - 0.45) / 0.45))
        body.scale = (1.0 + 0.015 * b, 0.72 + 0.02 * b, 1.0); body.keyframe_insert("scale", frame=f)
        head.location = (0, 0, 1.6 + 0.008 * b); head.keyframe_insert("location", frame=f)
    for ob in (head, body):
        if ob.animation_data and ob.animation_data.action:
            for fc in fcurves_of(ob.animation_data.action):
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
    return root, shem
