# Grease Pencil line-art renderer (Blender 5.x, GP v3) → transparent PNG sequence in PIXEL space of a target image.
# Each entry draws itself (Build modifier) between its own `from` and `to` frames, with a hand-drawn look:
# resampled points, small wobble, tapered pressure, optional overshoot. Opacity can be keyframed (eraser / fade).
#   Blender -b --factory-startup -P gp_lines.py -- <spec.json>
# spec: { "w":1920, "h":1088, "frames":96, "out":"/abs/dir/",
#         "lines":[ { "pts":[[x,y],...], "from":6, "to":30, "color":[r,g,b], "alpha":0.9, "px":3.2,
#                     "jitter":1.0, "overshoot":0, "fade":[[f,opacity],...] } ] }
import sys, json, math, os, random
import bpy

spec = json.load(open(sys.argv[sys.argv.index("--") + 1]))
W, H, F = spec["w"], spec["h"], spec["frames"]
U = 100.0  # pixels per Blender unit
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"
sc.frame_start, sc.frame_end = 1, F
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"

cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"; cd.ortho_scale = W / U; cd.sensor_fit = "HORIZONTAL"
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0, -10, 0); cam.rotation_euler = (math.radians(90), 0, 0)

gpd = bpy.data.grease_pencils.new("Lines")
ob = bpy.data.objects.new("Lines", gpd); sc.collection.objects.link(ob)
mats = {}
def material(color, alpha):
    key = (tuple(round(c, 3) for c in color), round(alpha, 3))
    if key in mats: return mats[key]
    m = bpy.data.materials.new(f"m{len(mats)}"); bpy.data.materials.create_gpencil_data(m)
    m.grease_pencil.color = (*color, alpha)
    gpd.materials.append(m); mats[key] = len(gpd.materials) - 1
    return mats[key]

rnd = random.Random(spec.get("seed", 11))
def resample(pts, step=5.0, jitter=1.0, overshoot=0.0):
    pts = [tuple(p) for p in pts]
    if overshoot and len(pts) >= 2:  # pencil carries a little past the start/end like a real stroke
        (x0, y0), (x1, y1) = pts[0], pts[1]; d = math.hypot(x1 - x0, y1 - y0) or 1
        pts.insert(0, (x0 - (x1 - x0) / d * overshoot, y0 - (y1 - y0) / d * overshoot))
        (x0, y0), (x1, y1) = pts[-2], pts[-1]; d = math.hypot(x1 - x0, y1 - y0) or 1
        pts.append((x1 + (x1 - x0) / d * overshoot, y1 + (y1 - y0) / d * overshoot))
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n):
            t = i / n
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-jitter, jitter), y0 + (y1 - y0) * t + rnd.uniform(-jitter, jitter)))
    out.append(pts[-1])
    return out

for idx, L in enumerate(spec["lines"]):
    name = f"s{idx:03d}"
    layer = gpd.layers.new(name)
    dr = layer.frames.new(1).drawing
    pts = resample(L["pts"], jitter=L.get("jitter", 1.0), overshoot=L.get("overshoot", 0.0))
    dr.add_strokes([len(pts)])
    st = dr.strokes[0]
    n = len(pts); base = L.get("px", 3.0) / 2 / U
    for i, (x, y) in enumerate(pts):
        p = st.points[i]
        p.position = ((x - W / 2) / U, 0, (H / 2 - y) / U)
        t = (i + 1) / n
        p.radius = base * (0.45 + 0.55 * math.sin(math.pi * min(1.0, t)) ** 0.5) * (0.9 + 0.2 * rnd.random())
        p.opacity = 1.0
    st.material_index = material(L.get("color", [0.18, 0.16, 0.14]), L.get("alpha", 0.9))
    mod = ob.modifiers.new(f"b{idx}", "GREASE_PENCIL_BUILD")
    mod.tree_node_filter = name
    mod.mode = "SEQUENTIAL"; mod.transition = "GROW"
    mod.time_mode = "FRAMES"
    mod.start_delay = max(0, L["from"] - 1)
    mod.length = max(1, L["to"] - L["from"])
    for f, op in L.get("fade", []):
        layer.opacity = op
        gpd.keyframe_insert(data_path=f'layers["{name}"].opacity', frame=f)

os.makedirs(spec["out"], exist_ok=True)
sc.render.filepath = os.path.join(spec["out"], "f_")
bpy.ops.render.render(animation=True)
print("GP_LINES_OK", len(spec["lines"]), "lines,", F, "frames")
