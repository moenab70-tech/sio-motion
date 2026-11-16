# Close-up check of the palm asset with toon shading, backlit by a low sun.
import sys, os, math, bpy
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
exec(open(os.path.join(HERE, "toon_lib.py")).read())
exec(open(os.path.join(HERE, "palm_asset.py")).read())
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1350, 60
w = bpy.data.worlds.new("w"); sc.world = w; bg = w.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.98, 0.7, 0.45, 1)
sc.render.film_transparent = False; bg.inputs["Strength"].default_value = 0.05
tm, cm = build_palm(seed=3, height=7.5, lod=1.0)
mt, ml = palm_material("Trunk", leaf=False), palm_material("Leaf")
tm.materials.append(mt); cm.materials.append(ml)
for me in (tm, cm):
    ob = bpy.data.objects.new(me.name, me); sc.collection.objects.link(ob)
print("verts", len(tm.vertices) + len(cm.vertices))
bpy.ops.object.light_add(type="SUN"); s = bpy.context.active_object; s.data.energy = 3; s.rotation_euler = (math.radians(80), 0, math.radians(170))
bpy.ops.object.camera_add(location=(0, -13, 5.2)); cam = bpy.context.active_object; sc.camera = cam
cam.rotation_euler = (math.radians(84), 0, 0); cam.data.lens = 38
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
