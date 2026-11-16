"""Irrigated canal-bank vegetation (v6.3): Poly Haven assets scattered with Geometry Nodes + density vertex groups.

Assets: assets/environment/polyhaven_canal_vegetation_v2.blend (downloaded through the Blender MCP Poly Haven
integration, 1k/2k textures packed, CC0). Collections VEG_grass / VEG_groundcover / VEG_shrub / VEG_tree / VEG_rock.

Layout (canal along X at y = -38, concrete lip +-3.5 m, ground z = -9):
  * maintenance strip |dy| < 5.0 m kept clear (realistic irrigation infrastructure: service path beside the lining)
  * irrigated belt 5..~24 m from the canal, densest near the water, falling off with distance, broken into clusters
    by low-frequency noise (no uniform carpet), fading out at the canal ends
  * one scatter mesh (EXT_veg_scatter, 1 m grid, never rendered itself) carries one vertex group per layer
    (dens_grass, dens_ground, dens_shrub, dens_tree, dens_rock); a Geometry Nodes modifier per layer reads its group as
    the Distribute-Points density factor and instances the layer's collection with random pick / yaw / scale
  * ground material: Poly Haven 'sparse_grass' soil blended into the sand with the same belt mask (world-space)
"""
import math, os
import bpy
from mathutils import Vector, noise

LIB_BLEND = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library/assets/environment/polyhaven_canal_vegetation_v2.blend"
GROUND_Z = -9.0
CANAL_Y = -38.0
LAYERS = ("VEG_grass", "VEG_groundcover", "VEG_shrub", "VEG_tree", "VEG_rock")
# layer: (density max per m2, min distance, scale range, max tilt, collection)
SPEC = {
    "grass":  dict(coll="VEG_grass",       dmax=16.0,  dist=0.07, scale=(1.0, 1.9), seed=1),
    "ground": dict(coll="VEG_groundcover", dmax=1.4,   dist=0.25, scale=(1.4, 2.8), seed=2),
    "shrub":  dict(coll="VEG_shrub",       dmax=0.12,  dist=1.8,  scale=(1.0, 1.9), seed=3),
    "tree":   dict(coll="VEG_tree",        dmax=0.006, dist=9.0,  scale=(0.9, 1.5), seed=4),
    "rock":   dict(coll="VEG_rock",        dmax=0.012, dist=3.0,  scale=(0.5, 1.4), seed=5),
}
X_RANGE = (-130.0, 185.0)    # detailed scatter where the canal cameras look (3B, 4A); texture carries the rest
Y_HALF = 26.0


def _smooth(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def masks(x, y):
    """Per-layer density 0..1 at a world XY point."""
    d = abs(y - CANAL_Y)
    side = 1 if y > CANAL_Y else -1
    clear = _smooth(4.6, 5.6, d)                                    # service strip
    belt = clear * (1.0 - _smooth(14.0, Y_HALF, d))                 # irrigated belt
    ends = 1.0 - _smooth(150.0, 205.0, abs(x - 25.0))
    n_big = noise.noise(Vector((x * 0.035, y * 0.035 + side * 7.3, 1.7)))          # -1..1, clusters ~30 m
    n_mid = noise.noise(Vector((x * 0.11, y * 0.11, 4.2)))
    cluster = _smooth(-0.35, 0.45, n_big * 0.75 + n_mid * 0.35)
    near = 1.0 - _smooth(5.0, 13.0, d)                              # water-fed edge strip
    grass = belt * ends * (0.35 + 0.65 * max(cluster, near * 0.8))
    ground = belt * ends * (0.25 + 0.75 * cluster)
    shrub = belt * ends * _smooth(0.15, 0.7, n_big * 0.8 + n_mid * 0.5) * (1.0 - 0.6 * near)
    tree = clear * ends * _smooth(8.0, 11.0, d) * (1.0 - _smooth(18.0, Y_HALF, d)) * _smooth(0.05, 0.55, n_big)
    edge = _smooth(14.0, 20.0, d) * (1.0 - _smooth(22.0, Y_HALF + 4, d))            # belt-to-desert transition
    rock = ends * (edge * 0.9 + 0.25 * clear * near) * _smooth(-0.2, 0.5, -n_big + 0.4 * n_mid)
    return dict(grass=grass, ground=ground, shrub=shrub, tree=tree, rock=rock)


def append_library():
    have = [c for c in LAYERS if bpy.data.collections.get(c)]
    if len(have) < len(LAYERS):
        with bpy.data.libraries.load(LIB_BLEND, link=False) as (src, dst):
            dst.collections = [c for c in src.collections if c in LAYERS]
            dst.materials = [m for m in src.materials if m in ("sparse_grass", "leafy_grass")]
    holder = bpy.data.collections.get("ENV_veg_library") or bpy.data.collections.new("ENV_veg_library")
    if holder.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(holder)
    for c in LAYERS:
        col = bpy.data.collections[c]
        if col.name not in holder.children:
            holder.children.link(col)
    # grass layer: only the full tufts (bermuda medium/seedling + grass_medium_02); the 5-10 cm bits read as noise
    gc = bpy.data.collections["VEG_grass"]
    for o in list(gc.objects):
        if "_small_" in o.name or "_flattened_" in o.name:
            gc.objects.unlink(o)
    for lc in bpy.context.view_layer.layer_collection.children:
        if lc.collection == holder:
            lc.exclude = True            # source objects never render; GN instances still do
    return holder


def scatter_mesh(step=1.0):
    name = "EXT_veg_scatter"
    if bpy.data.objects.get(name):
        bpy.data.objects.remove(bpy.data.objects[name])
    xs = [X_RANGE[0] + i * step for i in range(int((X_RANGE[1] - X_RANGE[0]) / step) + 1)]
    ys = [CANAL_Y - Y_HALF - 4 + j * step for j in range(int((2 * Y_HALF + 8) / step) + 1)]
    verts = [(x, y, GROUND_Z + 0.01) for y in ys for x in xs]
    nx = len(xs)
    faces = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(len(ys) - 1) for i in range(nx - 1)]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new(name, me)
    coll = bpy.data.collections.get("ENV_exterior") or bpy.context.scene.collection
    coll.objects.link(o)
    groups = {k: o.vertex_groups.new(name=f"dens_{k}") for k in SPEC}
    for k in SPEC:
        g = groups[k]
        for v in me.vertices:
            w = masks(v.co.x, v.co.y)[k]
            if w > 0.002:
                g.add([v.index], w, 'REPLACE')
    return o


def _gn_layer(key, spec):
    name = f"SIO_veg_{key}"
    ng = bpy.data.node_groups.get(name)
    if ng:
        bpy.data.node_groups.remove(ng)
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    att = N.new("GeometryNodeInputNamedAttribute"); att.data_type = 'FLOAT'; att.inputs["Name"].default_value = f"dens_{key}"
    dist = N.new("GeometryNodeDistributePointsOnFaces"); dist.distribute_method = 'POISSON'
    dist.inputs["Distance Min"].default_value = spec["dist"]; dist.inputs["Density Max"].default_value = spec["dmax"]
    dist.inputs["Seed"].default_value = spec["seed"]
    L.new(gi.outputs[0], dist.inputs["Mesh"]); L.new(att.outputs["Attribute"], dist.inputs["Density Factor"])
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = bpy.data.collections[spec["coll"]]
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    ci.transform_space = 'ORIGINAL'
    iop = N.new("GeometryNodeInstanceOnPoints"); iop.inputs["Pick Instance"].default_value = True
    ridx = N.new("FunctionNodeRandomValue"); ridx.data_type = 'INT'
    ridx.inputs["Min"].default_value = 0; ridx.inputs["Max"].default_value = 999; ridx.inputs["Seed"].default_value = spec["seed"] + 10
    ryaw = N.new("FunctionNodeRandomValue"); ryaw.data_type = 'FLOAT'
    ryaw.inputs["Min"].default_value = 0.0; ryaw.inputs["Max"].default_value = 2 * math.pi; ryaw.inputs["Seed"].default_value = spec["seed"] + 20
    rtilt = N.new("FunctionNodeRandomValue"); rtilt.data_type = 'FLOAT'
    rtilt.inputs["Min"].default_value = -0.06; rtilt.inputs["Max"].default_value = 0.06; rtilt.inputs["Seed"].default_value = spec["seed"] + 30
    comb = N.new("ShaderNodeCombineXYZ")
    L.new(rtilt.outputs[0], comb.inputs["X"]); L.new(ryaw.outputs[0], comb.inputs["Z"])
    # size varies per point and is biased by local density (lusher plants where the mask is strong)
    rsc = N.new("FunctionNodeRandomValue"); rsc.data_type = 'FLOAT'
    rsc.inputs["Min"].default_value = spec["scale"][0]; rsc.inputs["Max"].default_value = spec["scale"][1]; rsc.inputs["Seed"].default_value = spec["seed"] + 40
    att2 = N.new("GeometryNodeInputNamedAttribute"); att2.data_type = 'FLOAT'; att2.inputs["Name"].default_value = f"dens_{key}"
    mapr = N.new("ShaderNodeMapRange"); mapr.inputs["To Min"].default_value = 0.7; mapr.inputs["To Max"].default_value = 1.15
    L.new(att2.outputs["Attribute"], mapr.inputs["Value"])
    mul = N.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
    L.new(rsc.outputs[0], mul.inputs[0]); L.new(mapr.outputs[0], mul.inputs[1])
    L.new(dist.outputs["Points"], iop.inputs["Points"]); L.new(ci.outputs[0], iop.inputs["Instance"])
    L.new(ridx.outputs[0], iop.inputs["Instance Index"]); L.new(comb.outputs[0], iop.inputs["Rotation"])
    L.new(mul.outputs[0], iop.inputs["Scale"])
    L.new(iop.outputs[0], go.inputs[0])
    return ng


def gn_scatter(obj):
    for m in list(obj.modifiers):
        obj.modifiers.remove(m)
    # all layers in one evaluation: Join of every layer group
    top = bpy.data.node_groups.get("SIO_veg_scatter")
    if top:
        bpy.data.node_groups.remove(top)
    top = bpy.data.node_groups.new("SIO_veg_scatter", 'GeometryNodeTree')
    top.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    top.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi = top.nodes.new("NodeGroupInput"); go = top.nodes.new("NodeGroupOutput")
    join = top.nodes.new("GeometryNodeJoinGeometry")
    for k, spec in SPEC.items():
        g = top.nodes.new("GeometryNodeGroup"); g.node_tree = _gn_layer(k, spec)
        top.links.new(gi.outputs[0], g.inputs[0]); top.links.new(g.outputs[0], join.inputs[0])
    top.links.new(join.outputs[0], go.inputs[0])
    md = obj.modifiers.new("SIO_veg_scatter", 'NODES'); md.node_group = top
    return md


def ground_blend():
    """Blend Poly Haven sparse_grass soil into EXT_ground with the belt mask (world XY, before the haze group)."""
    g = bpy.data.objects["EXT_ground"]; m = g.active_material
    nt = m.node_tree
    if nt.nodes.get("sio_belt_mix"):
        return
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    haze = next((n for n in nt.nodes if n.type == 'GROUP'), None)
    target = haze.inputs[0] if haze else bsdf.inputs["Base Color"]
    sand_src = target.links[0].from_socket
    def tex(kind, mat="sparse_grass"):
        src = bpy.data.materials[mat].node_tree
        n = next((x for x in src.nodes if x.type == 'TEX_IMAGE' and kind in x.image.name.lower()), None)
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = n.image; t.interpolation = 'Linear'
        return t
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sep.inputs[0])
    # UV = world XY / 2 m (texture is 2 x 2 m), slight rotation to hide the grid
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.5, 0.5, 1); mp.inputs["Rotation"].default_value[2] = 0.31
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])
    diff = tex("diff"); rough = tex("rough")
    for t in (diff, rough):
        nt.links.new(mp.outputs[0], t.inputs[0])
    rough.image.colorspace_settings.name = 'Non-Color'
    # belt mask in the shader (same shape as masks(): distance to the canal + low-frequency noise)
    dy = nt.nodes.new("ShaderNodeMath"); dy.operation = 'SUBTRACT'; dy.inputs[1].default_value = CANAL_Y
    nt.links.new(sep.outputs["Y"], dy.inputs[0])
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = 'ABSOLUTE'; nt.links.new(dy.outputs[0], ab.inputs[0])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.035; nz.inputs["Detail"].default_value = 4
    nt.links.new(geo.outputs["Position"], nz.inputs["Vector"])
    nzm = nt.nodes.new("ShaderNodeMath"); nzm.operation = 'MULTIPLY_ADD'
    nzm.inputs[1].default_value = 14.0; nzm.inputs[2].default_value = 13.0     # belt edge 20..27 m, wobbling
    nt.links.new(nz.outputs["Fac"], nzm.inputs[0])
    edge = nt.nodes.new("ShaderNodeMapRange"); edge.clamp = True
    edge.inputs["To Min"].default_value = 1.0; edge.inputs["To Max"].default_value = 0.0
    nt.links.new(ab.outputs[0], edge.inputs["Value"])
    lo = nt.nodes.new("ShaderNodeMath"); lo.operation = 'SUBTRACT'; lo.inputs[1].default_value = 6.0
    nt.links.new(nzm.outputs[0], lo.inputs[0]); nt.links.new(lo.outputs[0], edge.inputs["From Min"]); nt.links.new(nzm.outputs[0], edge.inputs["From Max"])
    path = nt.nodes.new("ShaderNodeMapRange"); path.clamp = True               # service strip next to the lining: soil, not grass
    path.inputs["From Min"].default_value = 4.0; path.inputs["From Max"].default_value = 6.0
    nt.links.new(ab.outputs[0], path.inputs["Value"])
    ex = nt.nodes.new("ShaderNodeMath"); ex.operation = 'ABSOLUTE'
    exs = nt.nodes.new("ShaderNodeMath"); exs.operation = 'SUBTRACT'; exs.inputs[1].default_value = 25.0
    nt.links.new(sep.outputs["X"], exs.inputs[0]); nt.links.new(exs.outputs[0], ex.inputs[0])
    ends = nt.nodes.new("ShaderNodeMapRange"); ends.clamp = True
    ends.inputs["From Min"].default_value = 170.0; ends.inputs["From Max"].default_value = 230.0
    ends.inputs["To Min"].default_value = 1.0; ends.inputs["To Max"].default_value = 0.0
    nt.links.new(ex.outputs[0], ends.inputs["Value"])
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = 'MULTIPLY'
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = 'MULTIPLY'; m2.name = "sio_belt_mask"
    nt.links.new(edge.outputs[0], m1.inputs[0]); nt.links.new(ends.outputs[0], m1.inputs[1])
    pathmix = nt.nodes.new("ShaderNodeMath"); pathmix.operation = 'MULTIPLY_ADD'
    pathmix.inputs[1].default_value = 0.7; pathmix.inputs[2].default_value = 0.3        # strip keeps 30 % (soil tone)
    nt.links.new(path.outputs[0], pathmix.inputs[0])
    nt.links.new(m1.outputs[0], m2.inputs[0]); nt.links.new(pathmix.outputs[0], m2.inputs[1])
    # irrigated soil is slightly greener/darker than the texture average under this sun
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = 1.3; hsv.inputs["Value"].default_value = 1.08
    nt.links.new(diff.outputs["Color"], hsv.inputs["Color"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.name = "sio_belt_mix"
    nt.links.new(m2.outputs[0], mix.inputs["Factor"]); nt.links.new(sand_src, mix.inputs[6]); nt.links.new(hsv.outputs[0], mix.inputs[7])
    # lush core: leafy_grass where the mask is strong (watered strip), sparse soil in the transition
    leafy = tex("diff", "leafy_grass"); nt.links.new(mp.outputs[0], leafy.inputs[0])
    core = nt.nodes.new("ShaderNodeMapRange"); core.clamp = True
    core.inputs["From Min"].default_value = 0.45; core.inputs["From Max"].default_value = 0.9
    nt.links.new(m2.outputs[0], core.inputs["Value"])
    lhsv = nt.nodes.new("ShaderNodeHueSaturation"); lhsv.inputs["Hue"].default_value = 0.575
    lhsv.inputs["Saturation"].default_value = 1.45; lhsv.inputs["Value"].default_value = 1.1
    nt.links.new(leafy.outputs["Color"], lhsv.inputs["Color"])
    mix2 = nt.nodes.new("ShaderNodeMix"); mix2.data_type = 'RGBA'; mix2.name = "sio_belt_core"
    nt.links.new(core.outputs[0], mix2.inputs["Factor"]); nt.links.new(mix.outputs[2], mix2.inputs[6]); nt.links.new(lhsv.outputs[0], mix2.inputs[7])
    nt.links.new(mix2.outputs[2], target)
    rmix = nt.nodes.new("ShaderNodeMix"); rmix.data_type = 'FLOAT'
    rmix.inputs[2].default_value = bsdf.inputs["Roughness"].default_value
    nt.links.new(m2.outputs[0], rmix.inputs["Factor"]); nt.links.new(rough.outputs["Color"], rmix.inputs[3])
    nt.links.new(rmix.outputs[0], bsdf.inputs["Roughness"])


def thin_palms(keep_row=0.68, keep_grove=0.35, seed=7):
    """Fewer, less regular palms: irregular gaps in the canal rows, most of the far grove removed."""
    import random
    rng = random.Random(seed)
    ids = sorted({int(o.name.split("_")[2].split(".")[0]) for o in bpy.data.objects if o.name.startswith("EXT_palm_") and o.name.split("_")[2].split(".")[0].isdigit()})
    gone = set()
    for i in ids:
        if rng.random() > (keep_row if i < 50 else keep_grove):
            gone.add(i)
    n = 0
    for o in [o for o in bpy.data.objects if o.name.startswith("EXT_palm_")]:
        p = o.name.split("_")[2].split(".")[0]
        if p.isdigit() and int(p) in gone:
            bpy.data.objects.remove(o); n += 1
    return len(ids), len(ids) - len(gone)


def remove_dark_shrubs():
    """Dried wild_rooibos instances render as near-black blobs in shade -> all removed. Searsia is removed inside the
    irrigated belt (replaced by the new green layers) and kept in the distant dry field. Identified by material."""
    n = 0
    for o in [o for o in bpy.data.objects if o.name.startswith("EXT_ph_") and o.data]:
        mats = {m.name for m in o.data.materials if m}
        dry = any(m.startswith("wild_rooibos") for m in mats)
        searsia = any(m.startswith("searsia") for m in mats)
        if dry or (searsia and abs(o.location.y - CANAL_Y) < Y_HALF + 4):
            bpy.data.objects.remove(o); n += 1
    return n


def green_boost(m, hue=0.54, sat=1.5, val=1.45):
    """Healthy irrigated foliage: lift saturation/value of the leaf base colour before the distance haze
    (warm low sun + haze otherwise push the Poly Haven greens toward khaki)."""
    nt = m.node_tree
    if nt.nodes.get("sio_green"):
        return
    hz = nt.nodes.get("sio_haze")
    b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    sock = hz.inputs[0] if hz else (b.inputs["Base Color"] if b else None)
    if sock is None or not sock.links:
        return
    src = sock.links[0].from_socket
    h = nt.nodes.new("ShaderNodeHueSaturation"); h.name = "sio_green"
    h.inputs["Hue"].default_value = hue; h.inputs["Saturation"].default_value = sat; h.inputs["Value"].default_value = val
    nt.links.new(src, h.inputs["Color"]); nt.links.new(h.outputs[0], sock)


def haze_new_materials():
    from sio_env.exterior import _haze_existing
    mats = set()
    for c in LAYERS:
        for o in bpy.data.collections[c].objects:
            mats |= {s.material for s in o.material_slots if s.material}
    for m in mats:
        _haze_existing(m)
        if not any(k in m.name for k in ("boulder", "stone", "trunk", "branches")):
            green_boost(m)
    return len(mats)


def build():
    append_library()
    removed = remove_dark_shrubs()
    palms = thin_palms()
    o = scatter_mesh()
    gn_scatter(o)
    ground_blend()
    nm = haze_new_materials()
    return dict(removed_dark_shrubs=removed, palms_before_after=palms, hazed_materials=nm, scatter=o.name)
