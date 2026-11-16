# SIO puppet-warp shot builder (Blender 5.x, headless). Reusable for any illustrated cut-out shot.
#   Blender -b --factory-startup -P puppet.py -- <shot.json>
# shot.json:
# { "frames": 75, "fps": 30, "res": [1920,1080], "percent": 100, "out": "abs/dir/",
#   "camera": { "lens": 50, "keys": [ {"f":1,"x":0,"z":0,"dist":10}, ... ],
#               "dof": { "fstop": 2.0, "keys": [ {"f":1,"focus":10}, ... ] } },
#   "layers": [ { "name":"bg", "image":"abs.png", "depth": 3, "overscan": 1.12, "x":0, "z":0,
#                 "handles": [ { "u":0.62, "v":0.30, "r":0.07,                 # centre + radius (fractions of image width)
#                                "keys":[{"f":1,"dx":0,"dy":0,"rot":0,"s":1}], # px of the source image, y down; rot in degrees
#                                "wave": {"dx":0,"dy":2,"rot":0,"s":0,"hz":0.3,"phase":0} } ] } ] }
# Each layer = subdivided image plane; handles deform it with smooth Gaussian weights (no seams, no gaps),
# baked as one shape key per frame. Camera moves in 3D → real parallax between depths + optional rack focus.
import sys, json, math, os
import bpy

spec = json.load(open(sys.argv[sys.argv.index("--") + 1]))
F, fps = spec["frames"], spec.get("fps", 30)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y = spec.get("res", [1920, 1080])
sc.render.resolution_percentage = spec.get("percent", 100)
sc.render.film_transparent = True
sc.render.fps = fps
sc.frame_start, sc.frame_end = 1, F
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
# 1:1 pixel renders: a small reconstruction filter keeps the painting as sharp as the source
sc.render.filter_size = spec.get("filter_size", 1.5)

def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def key_at(keys, f, field, default):
    if not keys: return default
    ks = sorted(keys, key=lambda k: k["f"])
    if f <= ks[0]["f"]: return ks[0].get(field, default)
    for a, b in zip(ks, ks[1:]):
        if a["f"] <= f <= b["f"]:
            t = smooth((f - a["f"]) / max(1, b["f"] - a["f"]))
            return a.get(field, default) + (b.get(field, default) - a.get(field, default)) * t
    return ks[-1].get(field, default)

# camera
cam_spec = spec["camera"]
cd = bpy.data.cameras.new("cam"); cd.lens = cam_spec.get("lens", 50); cd.sensor_fit = "HORIZONTAL"; cd.sensor_width = 36
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.rotation_euler = (math.radians(90), 0, 0)  # looks along +Y
k0 = cam_spec["keys"][0]
base_dist = k0.get("dist", 10)
for k in cam_spec["keys"]:
    cam.location = (k.get("x", 0), -k.get("dist", base_dist), k.get("z", 0)); cam.keyframe_insert("location", frame=k["f"])
    if "lens" in k: cd.lens = k["lens"]; cd.keyframe_insert("lens", frame=k["f"])
if "dof" in cam_spec:
    cd.dof.use_dof = True; cd.dof.aperture_fstop = cam_spec["dof"].get("fstop", 2.8)
    for k in cam_spec["dof"]["keys"]:
        cd.dof.focus_distance = k["focus"]; cd.dof.keyframe_insert("focus_distance", frame=k["f"])
aspect = sc.render.resolution_y / sc.render.resolution_x

def make_layer(L):
    img = bpy.data.images.load(L["image"]); iw, ih = img.size
    depth = L.get("depth", 0.0)
    dist = base_dist + depth
    vis_w = dist * 36.0 / cd.lens                      # frame width visible at this depth
    W = vis_w * L.get("overscan", 1.1) * L.get("scale", 1.0)
    H = W * ih / iw
    nx = L.get("grid", 96); ny = max(8, round(nx * ih / iw))
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=nx, y_subdivisions=ny, size=1)
    ob = bpy.context.active_object; ob.name = L["name"]
    me = ob.data
    for v in me.vertices:  # grid spans −0.5..0.5 → set exact plane size, keep it in the X/Z picture plane
        u, vv = v.co.x + 0.5, v.co.y + 0.5
        v.co = (L.get("x", 0) + (u - 0.5) * W, 0, L.get("z", 0) + (vv - 0.5) * H)
    ob.location = (0, depth, 0)
    # material: emission + alpha (colours exactly as painted)
    mat = bpy.data.materials.new(L["name"] + "-m"); mat.use_nodes = True
    if hasattr(mat, "surface_render_method"): mat.surface_render_method = "BLENDED"
    nt = mat.node_tree; nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img; tex.extension = "EXTEND"; tex.interpolation = L.get("interp", spec.get("interp", "Cubic"))
    em = nt.nodes.new("ShaderNodeEmission"); tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader"); out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], em.inputs["Color"]); nt.links.new(tex.outputs["Alpha"], mx.inputs["Fac"])
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs["Surface"])
    me.materials.append(mat)
    # UVs follow the original (undeformed) grid → the painting moves WITH the mesh
    uv = me.uv_layers.active.data
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv[li].uv = ((co.x - L.get("x", 0)) / W + 0.5, (co.z - L.get("z", 0)) / H + 0.5)
    handles = L.get("handles", [])
    if not handles: return
    base = [(v.co.x, v.co.z) for v in me.vertices]
    px = W / iw  # world units per source pixel
    hs = []
    for h in handles:
        cx = L.get("x", 0) + (h["u"] - 0.5) * W
        cz = L.get("z", 0) + (0.5 - h["v"] * iw / ih) * H if h.get("v_in_width") else L.get("z", 0) + (0.5 - h["v"]) * H
        r = h["r"] * W
        w = [math.exp(-2.0 * ((x - cx) ** 2 + (z - cz) ** 2) / (r * r)) for (x, z) in base]
        hs.append((h, cx, cz, w))
    # normalise overlapping weights so the total never exceeds 1
    for i in range(len(base)):
        s = sum(hh[3][i] for hh in hs)
        if s > 1:
            for hh in hs: hh[3][i] /= s
    ob.shape_key_add(name="Basis")
    for f in range(1, F + 1):
        t = (f - 1) / fps
        kb = ob.shape_key_add(name=f"f{f:04d}", from_mix=False)
        params = []
        for (h, cx, cz, w) in hs:
            dx = key_at(h.get("keys"), f, "dx", 0.0); dy = key_at(h.get("keys"), f, "dy", 0.0)
            rot = key_at(h.get("keys"), f, "rot", 0.0); s = key_at(h.get("keys"), f, "s", 1.0)
            wv = h.get("wave")
            if wv:
                ph = 2 * math.pi * wv.get("hz", 0.3) * t + wv.get("phase", 0.0)
                dx += wv.get("dx", 0) * math.sin(ph); dy += wv.get("dy", 0) * math.sin(ph)
                rot += wv.get("rot", 0) * math.sin(ph); s += wv.get("s", 0) * math.sin(ph)
            a = math.radians(-rot)  # positive rot = clockwise on screen
            params.append((cx, cz, w, dx * px, -dy * px, math.cos(a), math.sin(a), s))
        for i, (x, z) in enumerate(base):
            ox = oz = 0.0
            for (cx, cz, w, tx, tz, ca, sa, s) in params:
                wi = w[i]
                if wi < 1e-4: continue
                rx, rz = (x - cx) * s, (z - cz) * s
                nx_, nz_ = cx + rx * ca - rz * sa + tx, cz + rx * sa + rz * ca + tz
                ox += wi * (nx_ - x); oz += wi * (nz_ - z)
            kb.data[i].co = (x + ox, 0, z + oz)
        for ff, val in ((f - 1, 0.0), (f, 1.0), (f + 1, 0.0)):
            if 1 <= ff <= F:
                kb.value = val; kb.keyframe_insert("value", frame=ff)
    if ob.data.shape_keys.animation_data and ob.data.shape_keys.animation_data.action:
        act = ob.data.shape_keys.animation_data.action
        for fc in getattr(act, "fcurves", []):
            for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"

for L in spec["layers"]:
    make_layer(L)

os.makedirs(spec["out"], exist_ok=True)
sc.render.filepath = os.path.join(spec["out"], "f_")
bpy.ops.render.render(animation=True)
print("PUPPET_OK", F, "frames →", spec["out"])
