"""Resolve a .blend's relative texture paths against ITS ORIGINAL folder and store them absolute.
   Blender -b <copied.blend> -P scripts/fix_blend_paths.py -- <original_folder>"""
import sys, os, bpy
orig = sys.argv[sys.argv.index("--") + 1]
fixed = missing = 0
for img in bpy.data.images:
    fp = img.filepath
    if fp.startswith("//"):
        cand = os.path.normpath(os.path.join(orig, fp[2:]))
        if os.path.exists(cand):
            img.filepath = cand; fixed += 1
        else:
            missing += 1
bpy.ops.wm.save_mainfile()
print("FIXED", fixed, "MISSING", missing)
