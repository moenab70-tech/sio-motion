# Grease Pencil capability test (Blender 5.x, GP v3): hand-drawn-looking strokes with pressure variation,
# animated by the Build modifier (strokes "draw themselves"), rendered with a transparent background.
#   Blender -b --factory-startup -P gp_draw_test.py -- <out_dir> [frames]
import sys, math, os, random
import bpy

out_dir = sys.argv[sys.argv.index("--") + 1]
frames = int(sys.argv[sys.argv.index("--") + 2]) if len(sys.argv) > sys.argv.index("--") + 2 else 60
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 50
sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"
sc.frame_start, sc.frame_end = 1, frames
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"

coll = bpy.data.grease_pencils if hasattr(bpy.data, "grease_pencils") else bpy.data.grease_pencils_v3
gpd = coll.new("Sketch")
ob = bpy.data.objects.new("Sketch", gpd); sc.collection.objects.link(ob)
print("GP data type:", type(gpd).__name__)

mat = bpy.data.materials.new("Graphite"); bpy.data.materials.create_gpencil_data(mat)
mat.grease_pencil.color = (0.16, 0.14, 0.12, 1.0)
gpd.materials.append(mat)

layer = gpd.layers.new("Lines")
fr = layer.frames.new(1)
dr = fr.drawing

rnd = random.Random(7)
def polyline(pts, step=0.04):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n):
            t = i / n
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-0.004, 0.004), y0 + (y1 - y0) * t + rnd.uniform(-0.004, 0.004)))
    out.append(pts[-1]); return out

# canal cross-section, water level, gate, dimension (X/Z picture plane)
shapes = [
    [(-4.2, 0.6), (-2.4, 0.6), (-1.4, -0.9), (1.4, -0.9), (2.4, 0.6), (4.2, 0.6)],
    [(-1.9, -0.1), (1.9, -0.1)],
    [(-0.25, 1.4), (0.25, 1.4), (0.25, -0.9), (-0.25, -0.9), (-0.25, 1.4)],
    [(-1.4, -1.5), (1.4, -1.5)],
]
strokes = [polyline(s) for s in shapes]
dr.add_strokes([len(s) for s in strokes])
for st, pts in zip(dr.strokes, strokes):
    n = len(pts)
    for i, (x, z) in enumerate(pts):
        p = st.points[i]
        p.position = (x, 0, z)
        # pressure: taper in/out like a real pencil stroke
        p.radius = 0.018 * (0.35 + 0.65 * math.sin(math.pi * min(1, (i + 1) / n)) ** 0.6)
        p.opacity = 0.85
    st.material_index = 0

# Build modifier → strokes draw themselves one after another
mtype = "GREASE_PENCIL_BUILD"
mod = ob.modifiers.new("build", mtype)
for k, v in (("mode", "SEQUENTIAL"), ("transition", "GROW"), ("time_mode", "FRAMES"), ("frame_start", 1), ("length", frames - 10)):
    try: setattr(mod, k, v)
    except Exception as e: print("build prop", k, "→", e)

cam_data = bpy.data.cameras.new("cam"); cam_data.type = "ORTHO"; cam_data.ortho_scale = 10
cam = bpy.data.objects.new("cam", cam_data); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0, -10, 0); cam.rotation_euler = (math.radians(90), 0, 0)

os.makedirs(out_dir, exist_ok=True)
sc.render.filepath = os.path.join(out_dir, "f_")
bpy.ops.render.render(animation=True)
print("GP_OK", frames, "frames")
