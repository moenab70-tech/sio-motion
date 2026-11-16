# Renders the 3D hero like HERO_SHEET.png: front · three-quarter · side · back (orthographic, beige backdrop, cel + ink),
# plus a face close-up. The model turns in front of a fixed camera so the lighting matches between views.
# Run: Blender -b --factory-startup -P hero_turnaround.py -- <out_dir> [percent=100]
import sys, os, math
import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/hero_turn/"
PCT = int(argv[1]) if len(argv) > 1 else 100
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
sc.render.image_settings.file_format = "PNG"
try: sc.eevee.taa_render_samples = 32
except Exception: pass
exec(open(os.path.join(HERE, "toon_lib.py")).read())
exec(open(os.path.join(HERE, "hero_model.py")).read())

NOINK = bpy.data.collections.new("NoInk"); sc.collection.children.link(NOINK)
root, coll = build_full_hero_v2()

# world: dim warm ambient only; the beige backdrop is a camera-only cylinder
w = bpy.data.worlds.new("W"); sc.world = w
bg = w.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (1.0, 0.92, 0.82, 1); bg.inputs["Strength"].default_value = 0.06
M_BD, nt, out = new_mat("Backdrop")
e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.86, 0.82, 0.74, 1); nt.links.new(e.outputs[0], out.inputs["Surface"])
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=20, depth=30, location=(0, 0, 1))
bd = bpy.context.active_object; bd.data.materials.append(M_BD)
for c in list(bd.users_collection): c.objects.unlink(bd)
NOINK.objects.link(bd)
for attr in ("visible_diffuse", "visible_glossy", "visible_shadow"):
    try: setattr(bd, attr, False)
    except Exception: pass
# a soft contact shadow disc under the feet
M_SH, nt, out = new_mat("Contact")
e2 = nt.nodes.new("ShaderNodeEmission"); e2.inputs["Color"].default_value = (0.72, 0.66, 0.58, 1); nt.links.new(e2.outputs[0], out.inputs["Surface"])
bpy.ops.mesh.primitive_circle_add(vertices=48, radius=0.32, fill_type="NGON", location=(0, -0.02, 0.001))
cd = bpy.context.active_object; cd.scale = (1.0, 0.45, 1); cd.data.materials.append(M_SH)
for c in list(cd.users_collection): c.objects.unlink(cd)
NOINK.objects.link(cd)

# key light: front-left, high (classic character-sheet light); a cool rim from behind
bpy.ops.object.light_add(type="SUN"); key = bpy.context.active_object
key.data.energy = 2.6; key.data.color = (1.0, 0.95, 0.88); key.rotation_euler = (math.radians(52), 0, math.radians(-32))
bpy.ops.object.light_add(type="SUN"); rim = bpy.context.active_object
rim.data.energy = 0.8; rim.data.color = (0.85, 0.9, 1.0); rim.rotation_euler = (math.radians(70), 0, math.radians(160))

bpy.ops.object.camera_add(location=(0, -8, 0.93), rotation=(math.radians(90), 0, 0))
cam = bpy.context.active_object; sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = 2.02
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 620, 1080, PCT

try:
    anime_compositor(sc, cam, NOINK, sun_dir=None, fog_amt=0.0, ink_color=(0.1, 0.07, 0.06), bloom=(3.0, 0.1, 0.3), beams=None,
                     skip_geo=("Backdrop", "Contact"))
except Exception as ex:
    print("COMPOSITOR WARN:", ex)

views = [("front", 0), ("threequarter", -45), ("side", -90), ("back", 180)]
paths = []
for name, deg in views:
    root.rotation_euler = (0, 0, math.radians(deg))
    sc.render.filepath = os.path.join(OUT, f"view_{name}.png"); bpy.ops.render.render(write_still=True)
    paths.append(sc.render.filepath)
# compose the four views side by side
imgs = []
for p in paths:
    im = bpy.data.images.load(p); a = np.array(im.pixels[:], np.float32).reshape(im.size[1], im.size[0], 4); imgs.append(a)
sheet = np.concatenate(imgs, axis=1)
out_img = bpy.data.images.new("Turnaround", sheet.shape[1], sheet.shape[0], alpha=True)
out_img.pixels.foreach_set(sheet.ravel()); out_img.filepath_raw = os.path.join(OUT, "HERO_3D_TURNAROUND.png"); out_img.file_format = "PNG"; out_img.save()

# face close-up (perspective, three-quarter)
root.rotation_euler = (0, 0, math.radians(-28))
cam.data.type = "PERSP"; cam.data.lens = 85
cam.location = (0, -1.25, 1.66); cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.resolution_x, sc.render.resolution_y = 1000, 1000
sc.render.filepath = os.path.join(OUT, "HERO_3D_FACE.png"); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hero_model.blend"))
print("TURNAROUND DONE", OUT)
