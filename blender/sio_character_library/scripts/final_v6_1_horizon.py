"""v6.1 fix: the desert ground (1.8 km plane) ended inside the 4A aerial view (hard edge against the sky).
Enlarges EXT_ground's own mesh x60 around its origin (object-space noise -> same texture density, no seam),
raises camera clip, saves final_v6_1.blend (final_v6.blend untouched). --test <dir> renders 4A probe frames."""
import bpy, sys, os
sys.path.insert(0, "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library")
g = bpy.data.objects["EXT_ground"]
g.data = g.data.copy(); g.data.name = "EXT_ground_v6_1"
for v in g.data.vertices:
    v.co.x *= 60.0; v.co.y *= 60.0
g.data.update()
g.visible_shadow = False   # a 100 km receiver self-shadows in EEVEE; the ground never needs to cast
print('GROUND polys', len(g.data.polygons))
for o in bpy.data.objects:
    if o.type == 'CAMERA': o.data.clip_end = max(o.data.clip_end, 150000.0)
OUT = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library/tests/final_v6/final_v6_1.blend"
bpy.ops.wm.save_as_mainfile(filepath=OUT, relative_remap=False); print("SAVED", OUT)
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if "--test" in a:
    from sio_env import story; from sio_char import render as RD
    sc = bpy.context.scene; d = a[a.index("--test") + 1]
    RD.setup("cinematic", sc, 30); sc.render.resolution_percentage = 33; sc.eevee.taa_render_samples = 16
    story.apply("S3", bpy.data.objects["engineer_m01_rig"])
    sc.render.image_settings.media_type = 'IMAGE'; sc.render.image_settings.file_format = 'JPEG'
    for cam, f in (("SHOT_K_rise", 90), ("SHOT_K_rise", 120), ("SHOT_J_canal", 45), ("SHOT_A_establishing", 45)):
        sc.camera = bpy.data.objects[cam]; sc.frame_set(f)
        sc.render.filepath = os.path.join(d, f"probe_{cam}_{f}.jpg"); bpy.ops.render.render(write_still=True)
