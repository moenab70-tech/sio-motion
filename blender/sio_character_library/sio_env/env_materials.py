"""v6.4 canal PBR materials (Poly Haven textures from assets/environment/polyhaven_canal_vegetation_v2.blend).

None of the canal geometry changes; only materials:
  ground  : sand (existing procedural) + sparse soil + lush leafy grass + moist mud by the water + gravel service path,
            world-space mapping with a second rotated/scaled sample blended by macro noise (anti-tiling), one combined
            height -> Bump (normals), roughness per layer (moist soil darker and smoother)
  trunk   : palm_bark (horizontal fibrous rings), box projection in object space (no UVs on the procedural palm),
            bump from the displacement map, brown/grey variation by noise, the palm's own leaf-base colour kept as AO
  fronds  : vertex colour + per-position hue/value variation, two-sided translucency (Translucent BSDF mix),
            roughness 0.45, slight sheen-free specular
  water   : depth tint (deep centre / shallow edges), animated anisotropic ripples moving downstream (+X),
            IOR 1.333, low roughness, keyed linear W + offset (deterministic, no drivers)
  lining  : concrete_wall_009 in world space + darker/smoother wet band at the waterline
Every material keeps the scene's distance-haze group (sio_haze / Group) before Base Color.
"""
import bpy

LIB_BLEND = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library/assets/environment/polyhaven_canal_vegetation_v2.blend"
PH = ("sparse_grass", "leafy_grass", "palm_bark", "gravel_ground_01", "brown_mud_02", "concrete_wall_009")
CANAL_Y = -38.0
FPS = 30.0


def load():
    need = [m for m in PH if m not in bpy.data.materials]
    if need:
        with bpy.data.libraries.load(LIB_BLEND, link=False) as (src, dst):
            dst.materials = [m for m in src.materials if m in need]
    for m in PH:
        bpy.data.materials[m].use_fake_user = True


def _img(mat, kind):
    for n in bpy.data.materials[mat].node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image and kind in n.image.name.lower():
            return n.image
    raise KeyError(f"{mat}:{kind}")


class NT:
    """Tiny node helper."""
    def __init__(self, mat):
        self.m = mat; self.nt = mat.node_tree; self.N = self.nt.nodes; self.L = self.nt.links
    def n(self, t, **kw):
        node = self.N.new(t)
        for k, v in kw.items():
            if k in node.inputs:
                node.inputs[k].default_value = v
            else:
                setattr(node, k, v)
        return node
    def l(self, a, b):
        self.L.new(a, b)
    def math(self, op, a, b=None, c=None):
        m = self.n("ShaderNodeMath", operation=op)
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                m.inputs[i].default_value = v
            else:
                self.l(v, m.inputs[i])
        return m.outputs[0]
    def mix(self, fac, a, b, dtype='RGBA'):
        m = self.n("ShaderNodeMix", data_type=dtype)
        ia, ib = (6, 7) if dtype == 'RGBA' else (2, 3)
        for sock, v in ((m.inputs[0], fac), (m.inputs[ia], a), (m.inputs[ib], b)):
            if isinstance(v, (int, float)):
                sock.default_value = v
            elif isinstance(v, tuple):
                sock.default_value = v
            else:
                self.l(v, sock)
        return m.outputs[2] if dtype == 'RGBA' else m.outputs[0]
    def maprange(self, v, a, b, c=0.0, d=1.0):
        m = self.n("ShaderNodeMapRange", clamp=True)
        self.l(v, m.inputs["Value"])
        m.inputs["From Min"].default_value = a; m.inputs["From Max"].default_value = b
        m.inputs["To Min"].default_value = c; m.inputs["To Max"].default_value = d
        return m.outputs[0]
    def tex(self, image, vec, noncolor=False, proj='FLAT', blend=0.0):
        t = self.n("ShaderNodeTexImage"); t.image = image; t.projection = proj; t.projection_blend = blend
        if noncolor:
            image.colorspace_settings.name = 'Non-Color'
        self.l(vec, t.inputs[0])
        return t


def _haze_socket(nt_obj, bsdf):
    hz = next((n for n in nt_obj.N if n.type == 'GROUP' and n.node_tree and "haze" in n.node_tree.name.lower()), None)
    return hz.inputs[0] if hz else bsdf.inputs["Base Color"]


def _anti_tile(h, pos, mat, kind, size, noncolor=False):
    """Two samples (size, size*1.37 rotated 37 deg) blended by macro noise -> breaks visible repetition."""
    img = _img(mat, kind)
    m1 = h.n("ShaderNodeMapping"); m1.inputs["Scale"].default_value = (1 / size, 1 / size, 1)
    m2 = h.n("ShaderNodeMapping"); m2.inputs["Scale"].default_value = (1 / (size * 1.37),) * 2 + (1,)
    m2.inputs["Rotation"].default_value[2] = 0.646; m2.inputs["Location"].default_value = (0.31, 0.77, 0)
    h.l(pos, m1.inputs[0]); h.l(pos, m2.inputs[0])
    a = h.tex(img, m1.outputs[0], noncolor); b = h.tex(img, m2.outputs[0], noncolor)
    return a.outputs[0], b.outputs[0]


def ground(obj_name="EXT_ground", lush=False):
    """Rebuild the ground colour/roughness/normal network (keeps the existing sand ramp + haze group)."""
    m = bpy.data.objects[obj_name].active_material
    h = NT(m)
    bsdf = next(n for n in h.N if n.type == 'BSDF_PRINCIPLED')
    target = _haze_socket(h, bsdf)
    ramp = next(n for n in h.N if n.type == 'VALTORGB')
    # drop the v6.3 belt network (keep sand ramp, its noise, haze group, BSDF, output)
    keep = {bsdf, ramp, target.node, next(n for n in h.N if n.type == 'OUTPUT_MATERIAL')}
    keep |= {l.from_node for l in h.nt.links if l.to_node == ramp}
    keep |= {l.from_node for l in h.nt.links if l.to_node in keep and l.from_node.type == 'TEX_COORD'}
    for n in list(h.N):
        if n not in keep:
            h.N.remove(n)
    geo = h.n("ShaderNodeNewGeometry"); pos = geo.outputs["Position"]
    sep = h.n("ShaderNodeSeparateXYZ"); h.l(pos, sep.inputs[0])
    d = h.math('ABSOLUTE', h.math('SUBTRACT', sep.outputs["Y"], CANAL_Y))           # distance to canal axis
    macro = h.n("ShaderNodeTexNoise", **{"Scale": 0.035, "Detail": 4.0}); h.l(pos, macro.inputs["Vector"])
    micro = h.n("ShaderNodeTexNoise", **{"Scale": 0.45, "Detail": 3.0}); h.l(pos, micro.inputs["Vector"])
    mix_t = h.maprange(h.n("ShaderNodeTexNoise", **{"Scale": 0.08, "Detail": 2.0}).outputs["Fac"], 0.35, 0.65)
    h.l(pos, mix_t.node.inputs[0].links[0].from_node.inputs["Vector"]) if False else None
    nz8 = mix_t.node.inputs["Value"].links[0].from_node; h.l(pos, nz8.inputs["Vector"])
    # layer masks
    wob = h.math('MULTIPLY_ADD', macro.outputs["Fac"], 14.0, 13.0)                  # belt edge ~20..27 m
    belt = h.maprange(h.math('SUBTRACT', d, wob), -6.0, 0.0, 1.0, 0.0)
    ex = h.math('ABSOLUTE', h.math('SUBTRACT', sep.outputs["X"], 25.0))
    ends = h.maprange(ex, 170.0, 230.0, 1.0, 0.0)
    belt = h.math('MULTIPLY', belt, ends)
    if lush:   # v6.5: irrigated landscape everywhere; macro noise leaves patches of sparser soil, no desert sand
        belt = h.maprange(macro.outputs["Fac"], 0.25, 0.55, 0.55, 1.0)
    path = h.math('MULTIPLY', h.maprange(d, 3.5, 3.9), h.maprange(d, 4.6, 5.6, 1.0, 0.0))        # gravel service strip
    moist = h.math('MULTIPLY', h.maprange(d, 5.2, 5.6), h.maprange(d, 6.2, 7.4, 1.0, 0.0))        # damp soil past the path
    moist = h.math('MULTIPLY', moist, h.maprange(micro.outputs["Fac"], 0.3, 0.6, 0.4, 0.75))
    core = h.math('MULTIPLY', h.maprange(belt, 0.45, 0.9), h.maprange(d, 5.6, 7.5))
    soil = h.math('MULTIPLY', belt, h.maprange(d, 5.6, 6.2))
    # textures (anti-tiled, world XY)
    sparse_c = h.mix(mix_t, *_anti_tile(h, pos, "sparse_grass", "diff", 2.0))
    leafy_c = h.mix(mix_t, *_anti_tile(h, pos, "leafy_grass", "diff", 2.0))
    gravel_c = h.mix(mix_t, *_anti_tile(h, pos, "gravel_ground_01", "diff", 3.0))
    mud_c = h.mix(mix_t, *_anti_tile(h, pos, "brown_mud_02", "diff", 1.3))
    lhsv = h.n("ShaderNodeHueSaturation", **{"Hue": 0.575, "Saturation": 1.45, "Value": 1.1}); h.l(leafy_c, lhsv.inputs["Color"])
    shsv = h.n("ShaderNodeHueSaturation", **{"Saturation": 1.25, "Value": 1.05}); h.l(sparse_c, shsv.inputs["Color"])
    sand = ramp.outputs["Color"]
    # subtle macro colour variation on the sand (sun-bleached vs darker patches)
    sand = h.mix(h.maprange(macro.outputs["Fac"], 0.3, 0.7, 0.0, 0.25), sand, (0.55, 0.45, 0.33, 1.0))
    c = h.mix(soil, sand, shsv.outputs[0])
    c = h.mix(core, c, lhsv.outputs[0])
    mudd = h.n("ShaderNodeHueSaturation", **{"Value": 0.85}); h.l(mud_c, mudd.inputs["Color"])
    c = h.mix(moist, c, mudd.outputs[0])
    c = h.mix(path, c, gravel_c)
    h.l(c, target)
    # roughness
    rough_l = h.mix(mix_t, *_anti_tile(h, pos, "leafy_grass", "rough", 2.0, True))
    rough_g = h.mix(mix_t, *_anti_tile(h, pos, "gravel_ground_01", "rough", 3.0, True))
    r = h.mix(core, 0.95, rough_l, 'FLOAT')
    r = h.mix(moist, r, 0.55, 'FLOAT')
    r = h.mix(path, r, rough_g, 'FLOAT')
    h.l(r, bsdf.inputs["Roughness"])
    # normals: one combined height -> bump
    hs = h.mix(mix_t, *_anti_tile(h, pos, "sparse_grass", "displacement", 2.0, True))
    hg = h.mix(mix_t, *_anti_tile(h, pos, "gravel_ground_01", "displacement", 3.0, True))
    hm = h.mix(mix_t, *_anti_tile(h, pos, "brown_mud_02", "displacement", 1.3, True))
    ht = h.mix(belt, 0.5, hs, 'FLOAT'); ht = h.mix(moist, ht, hm, 'FLOAT'); ht = h.mix(path, ht, hg, 'FLOAT')
    sand_h = h.n("ShaderNodeTexNoise", **{"Scale": 3.0, "Detail": 6.0}); h.l(pos, sand_h.inputs["Vector"])
    ht = h.mix(h.math('MAXIMUM', h.math('MAXIMUM', belt, path), moist), sand_h.outputs["Fac"], ht, 'FLOAT')
    bump = h.n("ShaderNodeBump", **{"Strength": 0.55, "Distance": 0.04}); h.l(ht, bump.inputs["Height"])
    h.l(bump.outputs["Normal"], bsdf.inputs["Normal"])
    m.name = m.name  # no-op, keeps name
    return m


def palm_trunk(mat_name="EXT_palm_trunk"):
    m = bpy.data.materials[mat_name]; h = NT(m)
    bsdf = next(n for n in h.N if n.type == 'BSDF_PRINCIPLED'); target = _haze_socket(h, bsdf)
    vcol = next(n for n in h.N if n.type == 'VERTEX_COLOR')
    tc = h.n("ShaderNodeTexCoord")
    mp = h.n("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / 0.62, 1 / 0.62, 1 / 0.62)   # ~ real ring spacing
    h.l(tc.outputs["Object"], mp.inputs[0])
    diff = h.tex(_img("palm_bark", "diff"), mp.outputs[0], proj='BOX', blend=0.35)
    rough = h.tex(_img("palm_bark", "rough"), mp.outputs[0], True, 'BOX', 0.35)
    disp = h.tex(_img("palm_bark", "displacement"), mp.outputs[0], True, 'BOX', 0.35)
    var = h.n("ShaderNodeTexNoise", **{"Scale": 1.4, "Detail": 3.0}); h.l(tc.outputs["Object"], var.inputs["Vector"])
    grey = h.mix(h.maprange(var.outputs["Fac"], 0.35, 0.7, 0.0, 0.35), diff.outputs["Color"], (0.38, 0.33, 0.28, 1.0))
    # sun-bleached brown/grey: lift the dark scan, keep the leaf-base relief colour from the procedural palm as AO
    lift = h.n("ShaderNodeHueSaturation", **{"Saturation": 1.0, "Value": 1.55}); h.l(grey, lift.inputs["Color"])
    ao = h.n("ShaderNodeMix", data_type='RGBA', blend_type='MULTIPLY'); ao.inputs[0].default_value = 0.45
    h.l(lift.outputs[0], ao.inputs[6]); vb = h.n("ShaderNodeHueSaturation", **{"Saturation": 0.4, "Value": 1.8}); h.l(vcol.outputs["Color"], vb.inputs["Color"])
    h.l(vb.outputs[0], ao.inputs[7])
    for l in list(target.links):
        h.nt.links.remove(l)
    h.l(ao.outputs[2], target)
    h.l(rough.outputs["Color"], bsdf.inputs["Roughness"])
    bump = h.n("ShaderNodeBump", **{"Strength": 0.8, "Distance": 0.03}); h.l(disp.outputs["Color"], bump.inputs["Height"])
    h.l(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def palm_fronds(mat_name="EXT_palm_crown"):
    m = bpy.data.materials[mat_name]; h = NT(m)
    bsdf = next(n for n in h.N if n.type == 'BSDF_PRINCIPLED'); target = _haze_socket(h, bsdf)
    out = next(n for n in h.N if n.type == 'OUTPUT_MATERIAL')
    vcol = next(n for n in h.N if n.type == 'VERTEX_COLOR')
    tc = h.n("ShaderNodeTexCoord")
    nz = h.n("ShaderNodeTexNoise", **{"Scale": 0.9, "Detail": 2.0}); h.l(tc.outputs["Object"], nz.inputs["Vector"])
    hv = h.n("ShaderNodeHueSaturation"); h.l(vcol.outputs["Color"], hv.inputs["Color"])
    h.l(h.maprange(nz.outputs["Fac"], 0.3, 0.7, 0.485, 0.52), hv.inputs["Hue"])
    h.l(h.maprange(nz.outputs["Fac"], 0.3, 0.7, 0.85, 1.12), hv.inputs["Value"])
    hv.inputs["Saturation"].default_value = 1.1
    for l in list(target.links):
        h.nt.links.remove(l)
    h.l(hv.outputs[0], target)
    bsdf.inputs["Roughness"].default_value = 0.45
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.35
    # thin leaves: light passes through -> mix a Translucent BSDF fed by the (hazed) colour
    tr = h.n("ShaderNodeBsdfTranslucent"); h.l(target.node.outputs[0] if target.node.type == 'GROUP' else hv.outputs[0], tr.inputs["Color"])
    ms = h.n("ShaderNodeMixShader"); ms.inputs[0].default_value = 0.28
    for l in list(out.inputs["Surface"].links):
        h.nt.links.remove(l)
    h.l(bsdf.outputs[0], ms.inputs[1]); h.l(tr.outputs[0], ms.inputs[2]); h.l(ms.outputs[0], out.inputs["Surface"])
    m.use_backface_culling = False
    return m


def water(mat_name="EXT_water", frames=(1, 300)):
    m = bpy.data.materials[mat_name]; h = NT(m)
    bsdf = next(n for n in h.N if n.type == 'BSDF_PRINCIPLED')
    geo = h.n("ShaderNodeNewGeometry"); pos = geo.outputs["Position"]
    sep = h.n("ShaderNodeSeparateXYZ"); h.l(pos, sep.inputs[0])
    d = h.math('ABSOLUTE', h.math('SUBTRACT', sep.outputs["Y"], CANAL_Y))
    depth = h.maprange(d, 0.4, 2.45, 1.0, 0.0)                      # 1 = deep centre, 0 = at the lining
    deep = (0.012, 0.045, 0.05, 1.0); shallow = (0.07, 0.11, 0.085, 1.0)
    col = h.mix(h.math('POWER', depth, 0.6), shallow, deep)
    h.l(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.035; bsdf.inputs["IOR"].default_value = 1.333
    # flow: coordinates stretched along X and shifted downstream over time (keyed, linear, extrapolated)
    flow = h.n("ShaderNodeMapping", name="sio_flow"); flow.inputs["Scale"].default_value = (0.35, 1.6, 1.0)
    h.l(pos, flow.inputs[0])
    n1 = h.n("ShaderNodeTexNoise", noise_dimensions='4D', name="sio_ripple"); n1.inputs["Scale"].default_value = 2.2
    n1.inputs["Detail"].default_value = 3.0; n1.inputs["Roughness"].default_value = 0.55
    h.l(flow.outputs[0], n1.inputs["Vector"])
    n2 = h.n("ShaderNodeTexNoise", noise_dimensions='4D', name="sio_ripple_fine"); n2.inputs["Scale"].default_value = 9.0
    n2.inputs["Detail"].default_value = 2.0; h.l(flow.outputs[0], n2.inputs["Vector"])
    ht = h.math('MULTIPLY_ADD', n2.outputs["Fac"], 0.35, n1.outputs["Fac"])
    bump = h.n("ShaderNodeBump", **{"Strength": 0.32, "Distance": 0.02}); h.l(ht, bump.inputs["Height"])
    h.l(bump.outputs["Normal"], bsdf.inputs["Normal"])
    # flow lines: long streaks (stretched along X) modulate roughness -> moving sheen bands read as current
    streak = h.n("ShaderNodeMapping"); streak.inputs["Scale"].default_value = (0.08, 1.4, 1.0); h.l(flow.outputs[0], streak.inputs[0])
    sn = h.n("ShaderNodeTexNoise", noise_dimensions='4D', name="sio_streak"); sn.inputs["Scale"].default_value = 3.0
    sn.inputs["Detail"].default_value = 2.0; h.l(streak.outputs[0], sn.inputs["Vector"])
    h.l(h.maprange(sn.outputs["Fac"], 0.35, 0.7, 0.02, 0.11), bsdf.inputs["Roughness"])
    # keyed animation: downstream drift 0.45 m/s, ripple evolution
    f0, f1 = frames; secs = (f1 - f0) / FPS
    for f, x, w in ((f0, 0.0, 0.0), (f1, -0.45 * secs * 0.35, 0.35 * secs)):
        flow.inputs["Location"].default_value[0] = x; flow.inputs["Location"].keyframe_insert("default_value", index=0, frame=f)
        n1.inputs["W"].default_value = w; n1.inputs["W"].keyframe_insert("default_value", frame=f)
        n2.inputs["W"].default_value = w * 1.7; n2.inputs["W"].keyframe_insert("default_value", frame=f)
        sn.inputs["W"].default_value = w * 0.5; sn.inputs["W"].keyframe_insert("default_value", frame=f)
    _linear(m.node_tree)
    return m


def _linear(idblock):
    ad = idblock.animation_data
    if not ad or not ad.action:
        return
    from sio_char.anim import _fcurves
    for fc in _fcurves(ad.action):
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'
        fc.extrapolation = 'LINEAR'


def lining(mat_name="EXT_concrete"):
    m = bpy.data.materials[mat_name]; h = NT(m)
    bsdf = next(n for n in h.N if n.type == 'BSDF_PRINCIPLED'); target = _haze_socket(h, bsdf)
    geo = h.n("ShaderNodeNewGeometry"); pos = geo.outputs["Position"]
    sep = h.n("ShaderNodeSeparateXYZ"); h.l(pos, sep.inputs[0])
    d = h.math('ABSOLUTE', h.math('SUBTRACT', sep.outputs["Y"], CANAL_Y))
    c = h.mix(0.5, *_anti_tile(h, pos, "concrete_wall_009", "diff", 1.805))
    r = h.mix(0.5, *_anti_tile(h, pos, "concrete_wall_009", "rough", 1.805, True), dtype='FLOAT')
    hd = h.mix(0.5, *_anti_tile(h, pos, "concrete_wall_009", "displacement", 1.805, True), dtype='FLOAT')
    nz = h.n("ShaderNodeTexNoise", **{"Scale": 1.2, "Detail": 3.0}); h.l(pos, nz.inputs["Vector"])
    wet = h.maprange(h.math('ADD', d, h.math('MULTIPLY', nz.outputs["Fac"], 0.12)), 2.55, 2.85, 1.0, 0.0)   # waterline band
    lift = h.n("ShaderNodeHueSaturation", **{"Value": 1.25, "Saturation": 0.8}); h.l(c, lift.inputs["Color"])
    wetc = h.n("ShaderNodeHueSaturation", **{"Value": 0.55, "Saturation": 1.15}); h.l(lift.outputs[0], wetc.inputs["Color"])
    col = h.mix(wet, lift.outputs[0], wetc.outputs[0])
    for l in list(target.links):
        h.nt.links.remove(l)
    h.l(col, target)
    h.l(h.mix(wet, r, 0.25, 'FLOAT'), bsdf.inputs["Roughness"])
    bump = h.n("ShaderNodeBump", **{"Strength": 0.35, "Distance": 0.01}); h.l(hd, bump.inputs["Height"])
    h.l(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def planar_probe():
    """EEVEE: planar light probe over the canal water -> real reflections of the palm crowns (screen-space tracing
    cannot see objects above the frame). Cycles ignores it."""
    o = bpy.data.objects.get("EXT_canal_planar")
    if o is None:
        lp = bpy.data.lightprobes.new("EXT_canal_planar", 'PLANE')
        o = bpy.data.objects.new("EXT_canal_planar", lp)
        (bpy.data.collections.get("ENV_exterior") or bpy.context.scene.collection).objects.link(o)
    w = bpy.data.objects["EXT_canal_water"]
    o.location = (w.location.x, -38.0, w.matrix_world.translation.z + 0.001)
    o.scale = (210.0, 2.5, 1.0)
    o.data.influence_distance = 0.4
    return o


def apply_all():
    load()          # planar_probe() tested in v6.4: in EEVEE 5.3 it blacked out the canal reflections -> not used
    return dict(ground=ground().name, trunk=palm_trunk().name, fronds=palm_fronds().name, water=water().name, lining=lining().name)
