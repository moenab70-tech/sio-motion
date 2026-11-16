# Shared anime/toon material helpers for the v3 Blender scenes. Use: exec(open(path).read())
import bpy

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
               t1=0.03, t2=0.14, rim=(1.0, 0.72, 0.38), rim_amt=0.55, alpha_socket=None, translucent=0.0):
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse"); dif.inputs["Color"].default_value = (1, 1, 1, 1)
    light = dif.outputs[0]
    if translucent > 0:   # light coming through from behind (fabric, leaves)
        tl = nt.nodes.new("ShaderNodeBsdfTranslucent"); tl.inputs["Color"].default_value = (translucent, translucent, translucent, 1)
        add_ = nt.nodes.new("ShaderNodeAddShader"); nt.links.new(dif.outputs[0], add_.inputs[0]); nt.links.new(tl.outputs[0], add_.inputs[1])
        light = add_.outputs[0]
    s2r = nt.nodes.new("ShaderNodeShaderToRGB"); nt.links.new(light, s2r.inputs[0])
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


def palm_material(name="PalmToon", leaf=True):
    m, nt, out = new_mat(name)
    ca = nt.nodes.new("ShaderNodeVertexColor"); ca.layer_name = "Col"
    if leaf:
        cel_output(nt, out, ca.outputs["Color"], shadow=(0.45, 0.45, 0.62), mid=(0.8, 0.72, 0.6), lit=(1.3, 1.14, 0.78),
                   t1=0.025, t2=0.12, rim=(1.0, 0.8, 0.32), rim_amt=0.65)
    else:
        cel_output(nt, out, ca.outputs["Color"], rim_amt=0.7)
    try: m.use_backface_culling = False
    except Exception: pass
    return m

# ---------------------------------------------------------------------------------------------
# Shared compositor: bloom → optional sun beams → ink from depth/normal edges (AOV "ink" mask) →
# aerial-perspective fog (AOV "geo" mask). noink: collection whose objects get no ink lines.
def anime_compositor(sc, cam, noink, sun_dir=None, fog_near=12.0, fog_far=170.0, fog_amt=0.88,
                     fog_color=(1.0, 0.8, 0.64), ink_color=(0.22, 0.11, 0.07), bloom=(1.6, 0.35, 0.55),
                     beams=(1.3, 0.55, 0.4), frame=1, skip_geo=("Haze",)):
    import mathutils
    from bpy_extras.object_utils import world_to_camera_view
    vl = sc.view_layers[0]
    tree = bpy.data.node_groups.new("CompAnime", "CompositorNodeTree"); sc.compositing_node_group = tree
    tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    vl.use_pass_z = True; vl.use_pass_normal = True
    if "ink" not in vl.aovs: a_ = vl.aovs.add(); a_.name = "ink"; a_.type = "VALUE"
    if "geo" not in vl.aovs: a2 = vl.aovs.add(); a2.name = "geo"; a2.type = "VALUE"
    inked = set()
    for ob in sc.objects:
        if ob.type == "MESH" and (noink is None or noink not in ob.users_collection):
            for ms in ob.material_slots:
                if ms.material: inked.add(ms.material)
    for m_ in inked:
        aov = m_.node_tree.nodes.new("ShaderNodeOutputAOV"); aov.aov_name = "ink"; aov.inputs["Value"].default_value = 1.0
    for m_ in bpy.data.materials:
        if m_.node_tree and m_.name not in skip_geo:
            g_ = m_.node_tree.nodes.new("ShaderNodeOutputAOV"); g_.aov_name = "geo"; g_.inputs["Value"].default_value = 1.0
    gout = tree.nodes.new("NodeGroupOutput"); rl = tree.nodes.new("CompositorNodeRLayers")
    def mnode(op, a=None, b=None):
        n = tree.nodes.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: tree.links.new(x, n.inputs[i])
        return n.outputs[0]
    glare = tree.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = "Bloom"; glare.inputs["Threshold"].default_value = bloom[0]
    glare.inputs["Strength"].default_value = bloom[1]; glare.inputs["Size"].default_value = bloom[2]
    tree.links.new(rl.outputs["Image"], glare.inputs["Image"]); img = glare.outputs["Image"]
    if sun_dir is not None and beams:
        sc.frame_set(frame)
        sp = world_to_camera_view(sc, cam, cam.matrix_world.translation + mathutils.Vector(sun_dir) * 1000)
        if -0.2 < sp.x < 1.2 and -0.2 < sp.y < 1.2 and sp.z > 0:
            b = tree.nodes.new("CompositorNodeGlare")
            b.inputs["Type"].default_value = "Sun Beams"; b.inputs["Threshold"].default_value = beams[0]
            b.inputs["Strength"].default_value = beams[1]; b.inputs["Size"].default_value = beams[2]
            b.inputs["Sun Position"].default_value = (sp.x, sp.y)
            tree.links.new(img, b.inputs["Image"]); img = b.outputs["Image"]
    inv = mnode("MULTIPLY", mnode("DIVIDE", 1.0, rl.outputs["Depth"]), 12.0)
    sob_d = tree.nodes.new("CompositorNodeFilter"); sob_d.inputs["Type"].default_value = "Sobel"; tree.links.new(inv, sob_d.inputs["Image"])
    sd = tree.nodes.new("CompositorNodeSeparateColor"); tree.links.new(sob_d.outputs[0], sd.inputs[0])
    e_d = mnode("GREATER_THAN", sd.outputs["Red"], 0.35)
    sob_n = tree.nodes.new("CompositorNodeFilter"); sob_n.inputs["Type"].default_value = "Sobel"; tree.links.new(rl.outputs["Normal"], sob_n.inputs["Image"])
    sn = tree.nodes.new("CompositorNodeSeparateColor"); tree.links.new(sob_n.outputs[0], sn.inputs[0])
    e_n = mnode("GREATER_THAN", mnode("ADD", mnode("ADD", sn.outputs["Red"], sn.outputs["Green"]), sn.outputs["Blue"]), 1.6)
    ink = mnode("MULTIPLY", mnode("MULTIPLY", mnode("MAXIMUM", e_d, e_n), rl.outputs["ink"]), 0.8)
    mix = tree.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    tree.links.new(ink, mix.inputs["Factor"]); tree.links.new(img, mix.inputs[6]); mix.inputs[7].default_value = (*ink_color, 1)
    dmap = tree.nodes.new("ShaderNodeMapRange"); tree.links.new(rl.outputs["Depth"], dmap.inputs["Value"])
    dmap.inputs["From Min"].default_value = fog_near; dmap.inputs["From Max"].default_value = fog_far
    fog = mnode("MULTIPLY", mnode("MULTIPLY", mnode("POWER", dmap.outputs["Result"], 0.75), fog_amt), rl.outputs["geo"])
    fmix = tree.nodes.new("ShaderNodeMix"); fmix.data_type = "RGBA"
    tree.links.new(fog, fmix.inputs["Factor"]); tree.links.new(mix.outputs[2], fmix.inputs[6]); fmix.inputs[7].default_value = (*fog_color, 1)
    tree.links.new(fmix.outputs[2], gout.inputs[0])
    return tree

# ---------------------------------------------------------------------------------------------
# Geometry helpers
def lathe(name, profile, segs=32, mat=None, coll=None, cap_top=False, cap_bottom=True):
    """Revolve a (radius, z) profile around Z → smooth mesh (dallah, finjan, lamp shade, bin...)."""
    import math
    V, F = [], []
    n = len(profile)
    for k in range(segs):
        a = 2 * math.pi * k / segs
        for r, z in profile: V.append((r * math.cos(a), r * math.sin(a), z))
    for k in range(segs):
        k2 = (k + 1) % segs
        for i in range(n - 1):
            F.append((k * n + i, k2 * n + i, k2 * n + i + 1, k * n + i + 1))
    if cap_bottom and profile[0][0] > 0:
        V.append((0, 0, profile[0][1])); c = len(V) - 1
        for k in range(segs): F.append((c, ((k + 1) % segs) * n, k * n))
    if cap_top and profile[-1][0] > 0:
        V.append((0, 0, profile[-1][1])); c = len(V) - 1
        for k in range(segs): F.append((c, k * n + n - 1, ((k + 1) % segs) * n + n - 1))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    for p in me.polygons: p.use_smooth = True
    if mat: me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(ob)
    return ob

def rbox(name, size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.01, mat=None, coll=None, segments=2):
    """Rounded box (bevel modifier) — avoids hard 'cardboard' boxes."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.active_object; ob.name = name; ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        m = ob.modifiers.new("Bevel", "BEVEL"); m.width = bevel; m.segments = segments; m.limit_method = "ANGLE"
    if mat: ob.data.materials.append(mat)
    for p in ob.data.polygons: p.use_smooth = True
    if coll:
        for c in list(ob.users_collection): c.objects.unlink(ob)
        coll.objects.link(ob)
    return ob

def tube(name, pts, radius, mat=None, coll=None, segs=10, taper=None):
    """Tube along a polyline (spout, lamp arms, cables, handles)."""
    import math
    V, F = [], []
    def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    def nrm(a):
        l = math.sqrt(sum(x * x for x in a)) or 1; return (a[0] / l, a[1] / l, a[2] / l)
    def cr(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    n = len(pts)
    for i, p in enumerate(pts):
        t = nrm(sub(pts[min(i + 1, n - 1)], pts[max(i - 1, 0)]))
        ref = (0, 0, 1) if abs(t[2]) < 0.9 else (1, 0, 0)
        u = nrm(cr(t, ref)); v = cr(t, u)
        r = radius * (taper(i / (n - 1)) if taper else 1)
        for k in range(segs):
            a = 2 * math.pi * k / segs
            V.append(tuple(p[j] + r * (math.cos(a) * u[j] + math.sin(a) * v[j]) for j in range(3)))
    for i in range(n - 1):
        for k in range(segs):
            k2 = (k + 1) % segs
            F.append((i * segs + k, i * segs + k2, (i + 1) * segs + k2, (i + 1) * segs + k))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    for p in me.polygons: p.use_smooth = True
    if mat: me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(ob)
    return ob
