"""Camera-motion preview of the shot library (low-res, every 2nd frame, 15 fps):
   Blender -b tests/office_v4/office_v4.blend -P scripts/office_v4_camera_preview.py
Each shot renders as its own clip in tests/office_v4/camera_preview/, then the clips are concatenated with
Remotion's bundled ffmpeg into office_v4_camera_preview.mp4."""
import os, sys, subprocess
import bpy

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, LIB)
from sio_env import lighting, clutter, office
from sio_char import render as RD

OUT = os.path.join(LIB, "tests", "office_v4", "camera_preview"); os.makedirs(OUT, exist_ok=True)
FF = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/node_modules/@remotion/compositor-darwin-arm64"
sc = bpy.context.scene
RD.setup("preview", sc, 15)
sc.render.resolution_percentage = 25   # 480x270 (H.264 needs even sizes)
try:
    sc.eevee.taa_render_samples = 12
except Exception:
    pass
sc.frame_step = 2

PLAN = [  # (clip, camera, state, clutter, f0, f1)
    ("A_establishing_dusk", "SHOT_A_establishing", "dusk", "early", 1, 120),
    ("B_exterior_in_dusk", "SHOT_B_exterior_in", "dusk", "early", 1, 150),
    ("D_pencil_night", "SHOT_D_pencil", "night", "attempts", 1, 90),
    ("C_eyes_night", "SHOT_C_eyes", "night", "late_night", 1, 90),
    ("E_overhead_night", "SHOT_E_overhead", "night", "late_night", 1, 90),
    ("F_timelapse", "SHOT_F_timelapse", None, None, 1, 240),
    ("G_dawn_reveal", "SHOT_G_dawn_reveal", "dawn", "dawn", 1, 150),
]
clips = []
for name, cam, state, cl, f0, f1 in PLAN:
    if state is None:
        # time passing: light dusk -> night -> dawn, clutter grows in discrete beats, clock runs
        lighting.key_state("dusk", 1); lighting.key_state("night", 100); lighting.key_state("night", 160); lighting.key_state("dawn", 240)
        clutter.key_states([(1, "early"), (60, "attempts"), (130, "late_night"), (200, "dawn")])
        office.animate_clock(1, 240, hours=8)
    else:
        lighting.set_state(state); clutter.show(cl)
    path = os.path.join(OUT, name + ".mp4")
    sc.camera = bpy.data.objects[cam]
    RD.animation_preview(path, f0, f1, sc)
    clips.append(path)
    if state is None:   # remove the time-lapse keys so later clips use static states
        for idb in [o.data for o in bpy.data.objects if o.type == 'LIGHT'] + [sc.world, sc] + \
                   [bpy.data.objects[n] for n in sc.get("sio_clutter", {}).get("desk", []) + sc.get("sio_clutter", {}).get("floor", []) + sc.get("sio_clutter", {}).get("sheets", [])]:
            if getattr(idb, "animation_data", None):
                idb.animation_data_clear()
        if sc.world.node_tree.animation_data:
            sc.world.node_tree.animation_data_clear()
lst = os.path.join(OUT, "clips.txt")
open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
final = os.path.join(LIB, "tests", "office_v4", "office_v4_camera_preview.mp4")
env = dict(os.environ, DYLD_LIBRARY_PATH=FF)
subprocess.run([os.path.join(FF, "ffmpeg"), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "15", final], env=env, check=True)
print("CAMERA_PREVIEW", final)
