"""3D view through the office window (Al-Ahsa oasis, third floor): farmland ground ~9 m below the window,
an irrigation canal, rows of date palms (the detailed procedural palm from the canal scene, instanced),
low buildings and distant flat-topped mesas, all fading into a shared distance haze whose colour follows
the time of day (lighting.set_state updates it). Real geometry -> correct parallax for moving cameras.
"""
import math, random, os
import bpy, bmesh
from mathutils import Vector, Matrix

PALM_PY = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/src/videos/hasad-2026/opening/blender/v3/palm_asset.py"
GROUND_Z = -9.0
HAZE = "SIO_haze"


def _coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(c)
    return c


def haze_group():
    """Node group: mixes a surface colour toward the haze colour with camera distance (aerial perspective)."""
    g = bpy.data.node_groups.get(HAZE)
    if g:
        return g
    g = bpy.data.node_groups.new(HAZE, 'ShaderNodeTree')
    g.interface.new_socket("Color", in_out='INPUT', socket_type='NodeSocketColor')
    g.interface.new_socket("Color", in_out='OUTPUT', socket_type='NodeSocketColor')
    gi = g.nodes.new("NodeGroupInput"); go = g.nodes.new("NodeGroupOutput")
    cam = g.nodes.new("ShaderNodeCameraData")
    mr = g.nodes.new("ShaderNodeMapRange"); mr.name = "range"
    mr.inputs["From Min"].default_value = 15.0; mr.inputs["From Max"].default_value = 650.0
    mr.inputs["To Max"].default_value = 0.85
    pw = g.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 0.7
    col = g.nodes.new("ShaderNodeRGB"); col.name = "haze_color"; col.outputs[0].default_value = (0.95, 0.72, 0.55, 1)
    mix = g.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'
    g.links.new(cam.outputs["View Distance"], mr.inputs["Value"]); g.links.new(mr.outputs[0], pw.inputs[0])
    g.links.new(pw.outputs[0], mix.inputs["Factor"]); g.links.new(gi.outputs[0], mix.inputs[6])
    g.links.new(col.outputs[0], mix.inputs[7]); g.links.new(mix.outputs[2], go.inputs[0])
    return g


def _mat(name, base_socket_fn, rough=0.9, emission_from_haze=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Roughness"].default_value = rough
    hz = nt.nodes.new("ShaderNodeGroup"); hz.node_tree = haze_group()
    base_socket_fn(nt, hz.inputs[0])
    nt.links.new(hz.outputs[0], b.inputs["Base Color"])
    return m


def _flat(rgb):
    def f(nt, sock):
        sock.default_value = (*rgb, 1)
    return f


def _noise2(c1, c2, scale):
    def f(nt, sock):
        tc = nt.nodes.new("ShaderNodeTexCoord"); n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = 6
        r = nt.nodes.new("ShaderNodeValToRGB")
        r.color_ramp.elements[0].color = (*c1, 1); r.color_ramp.elements[1].color = (*c2, 1)
        nt.links.new(tc.outputs["Object"], n.inputs["Vector"]); nt.links.new(n.outputs["Fac"], r.inputs[0])
        nt.links.new(r.outputs[0], sock)
    return f


def _vcol():
    def f(nt, sock):
        a = nt.nodes.new("ShaderNodeVertexColor"); a.layer_name = "Col"; nt.links.new(a.outputs["Color"], sock)
    return f


def build(seed=11, palm_count=140, lod=0.55):
    rng = random.Random(seed)
    coll = _coll("ENV_exterior")
    # ground: farmland (greens) with sandy patches, 1.2 km square
    bpy.ops.mesh.primitive_plane_add(size=1800, location=(0, -820, GROUND_Z))
    g = bpy.context.active_object; g.name = "EXT_ground"
    g.data.materials.append(_mat("EXT_ground", _noise2((0.16, 0.24, 0.09), (0.55, 0.45, 0.30), 0.02), 0.95))
    # canal: straight irrigation channel across the view (water + concrete lips)
    for name, w, z, mat in (("EXT_canal_lip", 7.0, GROUND_Z + 0.02, _mat("EXT_concrete", _flat((0.62, 0.58, 0.52)), 0.8)),
                            ("EXT_canal_water", 5.0, GROUND_Z + 0.04, None)):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -38, z))
        o = bpy.context.active_object; o.name = name; o.scale = (420, w, 1)
        if mat is None:
            mat = bpy.data.materials.new("EXT_water"); mat.use_nodes = True
            b = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            b.inputs["Base Color"].default_value = (0.05, 0.12, 0.13, 1); b.inputs["Roughness"].default_value = 0.05
            b.inputs["Metallic"].default_value = 0.0
        o.data.materials.append(mat)
    # distant mesas (Jabal Al-Qarah-like): displaced flat-topped cylinders
    mesa_mat = _mat("EXT_mesa", _noise2((0.55, 0.38, 0.28), (0.78, 0.66, 0.52), 0.05), 0.95)
    for i in range(5):
        r = rng.uniform(45, 90); h = rng.uniform(28, 48)
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=h, location=(rng.uniform(-420, 420), rng.uniform(-720, -600), GROUND_Z + h / 2))
        o = bpy.context.active_object; o.name = f"EXT_mesa_{i}"
        bm = bmesh.new(); bm.from_mesh(o.data)
        for v in bm.verts:
            if v.co.z > 0:
                v.co.x *= 0.82; v.co.y *= 0.82
            k = 1 + 0.12 * math.sin(math.atan2(v.co.y, v.co.x) * 5 + i)
            v.co.x *= k; v.co.y *= k
        bm.to_mesh(o.data); bm.free()
        o.data.materials.append(mesa_mat)
    # low buildings on the far side of the canal
    bmat = _mat("EXT_building", _noise2((0.78, 0.72, 0.62), (0.88, 0.84, 0.76), 0.3), 0.85)
    for i in range(14):
        sx, sy, sz = rng.uniform(6, 16), rng.uniform(6, 12), rng.uniform(4, 9)
        bpy.ops.mesh.primitive_cube_add(location=(rng.uniform(-140, 140), rng.uniform(-150, -70), GROUND_Z + sz / 2))
        o = bpy.context.active_object; o.name = f"EXT_building_{i}"; o.scale = (sx / 2, sy / 2, sz / 2)
        o.data.materials.append(bmat)
    for o in [x for x in bpy.data.objects if x.name.startswith("EXT_")]:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    # palms: 4 variants built once (procedural date palm), then instanced
    ns = {}
    exec(open(PALM_PY).read(), ns)
    trunk_mat = _mat("EXT_palm_trunk", _vcol(), 0.9)
    crown_mat = _mat("EXT_palm_crown", _vcol(), 0.7)
    variants = []
    for v in range(4):
        tm, cm = ns["build_palm"](seed=100 + v, height=rng.uniform(7, 11), lod=lod, dates=False, name=f"EXT_palm_v{v}")
        tm.materials.append(trunk_mat); cm.materials.append(crown_mat)
        variants.append((tm, cm))
    proto = _coll("ENV_exterior_palm_variants")
    for o in [x for x in bpy.data.objects if x.data in [m for pair in variants for m in pair]]:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        proto.objects.link(o)
    placed = 0
    for i in range(palm_count):
        if i < 50:   # two rows along the canal banks
            x = -150 + (i % 25) * 12 + rng.uniform(-2, 2); y = -32 if i < 25 else -44
            y += rng.uniform(-1.5, 1.5)
        else:        # grove beyond
            x = rng.uniform(-220, 220); y = rng.uniform(-260, -55)
            if -50 < y < -26:
                continue
        tm, cm = variants[rng.randrange(4)]
        s = rng.uniform(0.85, 1.15); rz = rng.uniform(0, 2 * math.pi)
        for mesh in (tm, cm):
            o = bpy.data.objects.new(f"EXT_palm_{i}", mesh); coll.objects.link(o)
            o.location = (x, y, GROUND_Z); o.rotation_euler.z = rz; o.scale = (s,) * 3
        placed += 1
    proto.hide_render = True; proto.hide_viewport = True
    return coll, placed


def set_haze(rgb, near=15.0, far=650.0, amount=0.85):
    g = haze_group()
    g.nodes["haze_color"].outputs[0].default_value = (*rgb, 1)
    r = g.nodes["range"]; r.inputs["From Min"].default_value = near; r.inputs["From Max"].default_value = far
    r.inputs["To Max"].default_value = amount


# ------------------------------------------------------------------ Poly Haven vegetation (CC0, cached at 1k)
PH_MODELS = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/src/videos/hasad-2026/opening/blender/v3/polyhaven_cache/models"
PH_VEG = {  # asset id: (decimate ratio for distant use, variant name filter)
    "island_tree_01": (0.08, None),
    "island_tree_02": (0.10, None),
    "searsia_lucida": (0.35, ("_a_", "_b_", "_c_", "_d_", "_e_")),
    "wild_rooibos_bush": (1.0, ("_a", "_b", "_c")),
}


def _ph_variants(asset_id, ratio, keep, proto_coll):
    """Import a cached Poly Haven model, split it into variant meshes with the origin at the base centre,
    decimate once for distance, park them (hidden) as instancing prototypes."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(PH_MODELS, asset_id, f"{asset_id}.gltf"))
    new = [o for o in bpy.data.objects if o not in before]
    out = []
    for o in new:
        if o.type != 'MESH' or (keep and not any(k in o.name for k in keep)):
            continue
        bpy.context.view_layer.update()
        mw = o.matrix_world.copy()
        o.parent = None; o.matrix_world = mw
        me = o.data
        me.transform(mw); o.matrix_world = Matrix.Identity(4)
        xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
        c = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
        me.transform(Matrix.Translation(-c))
        if ratio < 1.0:
            d = o.modifiers.new("dec", 'DECIMATE'); d.ratio = ratio
            bpy.context.view_layer.objects.active = o
            with bpy.context.temp_override(object=o, active_object=o):
                bpy.ops.object.modifier_apply(modifier="dec")
        for cc in list(o.users_collection):
            cc.objects.unlink(o)
        proto_coll.objects.link(o)
        out.append(o.data)
    for o in new:
        if o.name in bpy.data.objects and o.type != 'MESH':
            bpy.data.objects.remove(o)
        elif o.name in bpy.data.objects and o.data not in out:
            bpy.data.objects.remove(o)
    return out


def poly_haven_vegetation(seed=23, trees=70, shrubs=280):
    """Scatter Poly Haven trees/shrubs (instanced, shared meshes) between the palms of the oasis."""
    rng = random.Random(seed)
    coll = _coll("ENV_exterior_polyhaven")
    proto = _coll("ENV_exterior_ph_prototypes")
    V = {a: _ph_variants(a, r, k, proto) for a, (r, k) in PH_VEG.items()}
    proto.hide_render = True; proto.hide_viewport = True
    tree_meshes = V["island_tree_01"] + V["island_tree_02"]
    shrub_meshes = V["searsia_lucida"] + V["wild_rooibos_bush"]
    placed = {"trees": 0, "shrubs": 0}
    def put(mesh, x, y, s):
        o = bpy.data.objects.new(f"EXT_ph_{mesh.name}", mesh); coll.objects.link(o)
        o.location = (x, y, GROUND_Z); o.rotation_euler.z = rng.uniform(0, 2 * math.pi); o.scale = (s,) * 3
    for i in range(trees):
        if i < 18:   # shade trees along the far canal bank
            x, y = rng.uniform(-120, 120), rng.uniform(-58, -48)
        else:
            x, y = rng.uniform(-200, 200), rng.uniform(-240, -60)
        put(tree_meshes[rng.randrange(len(tree_meshes))], x, y, rng.uniform(1.5, 2.4)); placed["trees"] += 1
    for i in range(shrubs):
        if i < 120:  # clumps on both canal banks
            x = rng.uniform(-160, 160); y = rng.choice((-30.5, -45.5)) + rng.uniform(-2.5, 2.5)
        else:
            x, y = rng.uniform(-200, 200), rng.uniform(-200, -24)
            if -48 < y < -28:
                continue
        put(shrub_meshes[rng.randrange(len(shrub_meshes))], x, y, rng.uniform(1.4, 2.6)); placed["shrubs"] += 1
    # Poly Haven materials: keep detail but feed them through the distance haze like the rest of the exterior
    for m in {mm for me in tree_meshes + shrub_meshes for mm in me.materials if mm}:
        _haze_existing(m)
    return placed


def _haze_existing(m):
    if not m or not m.use_nodes or m.node_tree.nodes.get("sio_haze"):
        return
    nt = m.node_tree
    b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not b or not b.inputs["Base Color"].links:
        return
    src = b.inputs["Base Color"].links[0].from_socket
    hz = nt.nodes.new("ShaderNodeGroup"); hz.node_tree = haze_group(); hz.name = "sio_haze"
    nt.links.new(src, hz.inputs[0]); nt.links.new(hz.outputs[0], b.inputs["Base Color"])
