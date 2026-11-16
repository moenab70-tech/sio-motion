"""Render a 3 s MP4 preview of the currently opened .blend:  Blender -b file.blend -P scripts/render_preview.py -- out.mp4 [percent]"""
import sys, os, bpy
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
from sio_char import render as RD
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = argv[0] if argv else os.path.splitext(bpy.data.filepath)[0] + "_preview.mp4"
sc = bpy.context.scene
RD.setup("preview", sc, 30)
sc.render.resolution_percentage = int(argv[1]) if len(argv) > 1 else 50
sc.camera = bpy.data.objects.get("CAM_anim") or sc.camera
RD.animation_preview(out, sc.frame_start, sc.frame_end, sc)
print("WROTE", out)
