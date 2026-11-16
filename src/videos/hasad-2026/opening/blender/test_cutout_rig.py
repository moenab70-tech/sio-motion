# Blender headless capability test: cutout image → subdivided plane → 2-bone armature (real mesh deformation)
# + background layer + camera push (parallax) → transparent PNG sequence for Remotion.
# Run: Blender -b -P test_cutout_rig.py -- <cutout.png> <background.png|-> <out_dir> [frames]
import sys, math, os
import bpy

args = sys.argv[sys.argv.index("--") + 1:]
cutout, background, out_dir = args[0], args[1], args[2]
frames = int(args[3]) if len(args) > 3 else 36

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "BLENDER_EEVEE_NEXT"
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1920, 1080, 50
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.frame_start, scene.frame_end = 1, frames
scene.render.fps = 30
scene.view_settings.view_transform = "Standard"  # keep illustration colours unchanged

def image_plane(path, name, height, z):
    img = bpy.data.images.load(path)
    w, h = img.size
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=24, size=1)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (height * w / h, height, 1)
    ob.location = (0, 0, z)
    bpy.ops.object.transform_apply(scale=True)
    mat = bpy.data.materials.new(name + "-mat")
    mat.use_nodes = True
    # Blender ≥ 4.2 (EEVEE Next): surface_render_method; older: blend_method
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    else:
        mat.blend_method = "BLEND"
    nt = mat.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
    emit = nt.nodes.new("ShaderNodeEmission")
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
    nt.links.new(transp.outputs[0], mix.inputs[1])
    nt.links.new(emit.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(mat)
    ob.rotation_euler = (math.radians(90), 0, 0)  # stand up, facing the camera (−Y)
    return ob, height * w / h

if background != "-":
    bg, _ = image_plane(background, "background", 6.0, 0)
    bg.location.y = 4  # far layer

fig, width = image_plane(cutout, "figure", 3.0, 0)
fig.location.z = 1.5

# armature: lower bone (fixed) + upper bone (sways) — the upper half bends, the base stays planted
bpy.ops.object.armature_add(location=(0, -0.01, 0))
arm = bpy.context.active_object
bpy.ops.object.mode_set(mode="EDIT")
b0 = arm.data.edit_bones[0]; b0.name = "lower"; b0.head = (0, 0, 0); b0.tail = (0, 0, 1.4)
b1 = arm.data.edit_bones.new("upper"); b1.head = (0, 0, 1.4); b1.tail = (0, 0, 3.0); b1.parent = b0
bpy.ops.object.mode_set(mode="OBJECT")

# weights by height (smooth blend around the waist) → genuine deformation, not a rigid rotation
low, up = fig.vertex_groups.new(name="lower"), fig.vertex_groups.new(name="upper")
mw = fig.matrix_world
for v in fig.data.vertices:
    z = (mw @ v.co).z
    t = min(1, max(0, (z - 1.1) / 0.6))
    low.add([v.index], 1 - t, "REPLACE"); up.add([v.index], t, "REPLACE")
mod = fig.modifiers.new("rig", "ARMATURE"); mod.object = arm

pb = arm.pose.bones["upper"]
pb.rotation_mode = "XYZ"
for f in range(1, frames + 1):
    # bone Y = its length axis (twist); local Z = bend within the picture plane
    pb.rotation_euler = (0, 0, math.radians(9 * math.sin(f / frames * 2 * math.pi)))
    pb.keyframe_insert("rotation_euler", frame=f)

# camera: slow push-in → parallax between the figure and the far background
cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 50
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam); scene.camera = cam
cam.rotation_euler = (math.radians(90), 0, 0)
for f, y in ((1, -12.0), (frames, -10.5)):
    cam.location = (0.4, y, 1.6); cam.keyframe_insert("location", frame=f)

os.makedirs(out_dir, exist_ok=True)
scene.render.filepath = os.path.join(out_dir, "f_")
bpy.ops.render.render(animation=True)
print("RENDER_OK", frames, "frames →", out_dir)
