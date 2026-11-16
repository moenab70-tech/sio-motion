"""Headless Poly Haven test: Blender -b tests/polyhaven/polyhaven_test.blend -P scripts/test_polyhaven.py"""
import os, sys, json, bpy
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, LIB)
from sio_char import polyhaven as PH
r = {"background": bpy.app.background}
bpy.ops.mesh.primitive_cube_add(size=0.6, location=(1.1, 0.2, 0.3)); cube = bpy.context.active_object; cube.name = "PH_test_denim"
m = PH.material("denim_fabric_05", res="1k"); cube.data.materials.append(m)
r["denim_maps"] = sorted(n.image.name for n in m.node_tree.nodes if n.type == 'TEX_IMAGE')
r["links_ok"] = all(next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs[k].is_linked for k in ("Base Color", "Roughness", "Normal"))
r["missing_images"] = [i.name for i in bpy.data.images if i.filepath and not os.path.exists(bpy.path.abspath(i.filepath)) and not i.packed_file]
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = 960, 640
sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = os.path.join(LIB, "tests", "polyhaven", "polyhaven_test.png")
bpy.ops.render.render(write_still=True)
r["render"] = sc.render.filepath
print("PH_REPORT", json.dumps(r))
