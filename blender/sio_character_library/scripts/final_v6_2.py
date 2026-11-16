"""Hasad opening v6.2 - cinematography + render-quality pass on top of final_v6_1.blend (which stays untouched).
  * 2B: rear-right SHOT_G replaced by SHOT_G2_profile (side profile toward the window, 38 mm f/4)
  * 4A: high rise SHOT_K replaced by SHOT_K3_canal_axis (level one-point push along the canal, 35 mm f/8)
  * 1B: SHOT_D_pencil f/2.8 (~1 mm DoF) -> f/11, focus keyed per frame 12 mm in front of the pencil tip
  * shadows: sun use_shadow_jitter (stair-stepped soft-shadow edges), shadow rays 3 / steps 12
  Blender -b tests/final_v6/final_v6_1.blend -P scripts/final_v6_2.py -- --build
  Blender -b tests/final_v6_2/final_v6_2.blend -P scripts/final_v6_2.py -- --render [SLOT ...]
  Blender -b tests/final_v6_2/final_v6_2.blend -P scripts/final_v6_2.py -- --preview     (low-res movement preview)
"""
import os, sys, subprocess
import bpy
LIB = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
sys.path.insert(0, LIB)
OUT = os.path.join(LIB, "tests", "final_v6_2"); os.makedirs(OUT, exist_ok=True)
REPO = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics"
FRAMES_DIR = os.path.join(REPO, "public/media/opening/blender_v6_2")
V6_FRAMES = os.path.join(REPO, "public/media/opening/blender_v6")
FF = os.path.join(REPO, "node_modules/@remotion/compositor-darwin-arm64")
PLAN = {
    "1A": [("SHOT_A_establishing", "S1", 1, 90)],
    "1B": [("SHOT_D_pencil", "S1", 1, 96)],
    "2A": [("SHOT_H_calendar", "S2", 1, 22), ("SHOT_E_overhead", "S2", 20, 44)],
    "2B": [("SHOT_G2_profile", "S3", 1, 102)],
    "3A": [("SHOT_C_eyes", "S3", 1, 84)],
    "3B": [("SHOT_J_canal", "S3", 1, 90)],
    "4A": [("SHOT_K3_canal_axis", "S3", 1, 120)],
}
RERENDER = ["1A", "1B", "2A", "2B", "3B", "4A"]   # 3A (eye close-up, no hard sun shadows, unchanged camera) reuses v6 frames


def quality(sc):
    sun = bpy.data.objects["L_sun"].data
    sun.use_shadow_jitter = True; sun.shadow_jitter_overblur = 0.0
    sc.eevee.shadow_ray_count = 3; sc.eevee.shadow_step_count = 12


def build():
    from sio_env import shots as SH
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    sc.frame_set(1); H = rig.matrix_world @ rig.pose.bones["DEF-spine.006"].head
    def cam(name, lens, fstop, path, target, n):
        c = SH._cam(name, lens, fstop); c.data.clip_end = 150000
        SH._track(c, SH._target_empty(name + "_target", target)); SH._move(c, path, 1, n); return c
    cam("SHOT_G2_profile", 38, 4.0, [(H.x + 1.90, H.y + 0.40, H.z - 0.01), (H.x + 1.68, H.y + 0.30, H.z - 0.04)],
        (H.x - 0.22, H.y - 0.55, H.z - 0.13), 102)
    cam("SHOT_K3_canal_axis", 35, 8.0, [(-72.0, -38.0, -7.45), (-52.0, -38.0, -6.55)], (160.0, -38.0, -7.9), 120)
    # 1B focus: keyed per frame, 12 mm in front of the tip (fingertip and tip both inside the f/11 zone)
    c = bpy.data.objects["SHOT_D_pencil"]; tip = bpy.data.objects["SHOT_D_tip_target"]
    c.data.dof.focus_object = None; c.data.dof.aperture_fstop = 11.0
    for f in range(1, 97):
        sc.frame_set(f)
        c.data.dof.focus_distance = (tip.matrix_world.translation - c.matrix_world.translation).length - 0.012
        c.data.dof.keyframe_insert("focus_distance", frame=f)
    quality(sc)
    sc.frame_set(1); sc.camera = bpy.data.objects["SHOT_A_establishing"]
    path = os.path.join(OUT, "final_v6_2.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, relative_remap=False); print("FINAL_V6_2 saved", path)


def render(slots, pct=100, samples=64):
    from sio_env import story
    from sio_char import render as RD
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    RD.setup("cinematic", sc, 30); quality(sc)
    sc.render.resolution_percentage = pct; sc.eevee.taa_render_samples = samples; sc.render.film_transparent = False
    im = sc.render.image_settings; im.media_type = 'IMAGE'; im.file_format = 'PNG'; im.color_mode = 'RGB'; im.compression = 30
    for slot in slots:
        d = os.path.join(FRAMES_DIR, slot); os.makedirs(d, exist_ok=True)
        idx = 1
        for cam, ses, f0, n in PLAN[slot]:
            story.apply(ses, rig); sc.camera = bpy.data.objects[cam]
            for f in range(f0, f0 + n):
                p = os.path.join(d, f"f_{idx:04d}.png")
                if not os.path.exists(p):
                    sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
                idx += 1
        print("SLOT_DONE", slot, idx - 1, "frames")


def preview():
    """Movement preview of the three changed shots (640x360, 12 samples, every frame) -> one mp4."""
    from sio_env import story
    from sio_char import render as RD
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    RD.setup("cinematic", sc, 30); quality(sc); sc.render.resolution_percentage = 34; sc.eevee.taa_render_samples = 12
    im = sc.render.image_settings; im.media_type = 'IMAGE'; im.file_format = 'JPEG'; im.quality = 90
    D = os.path.join(OUT, "preview_frames"); os.makedirs(D, exist_ok=True); i = 0
    for slot in ("1B", "2B", "4A"):
        for cam, ses, f0, n in PLAN[slot]:
            story.apply(ses, rig); sc.camera = bpy.data.objects[cam]
            for f in range(f0, f0 + n):
                i += 1; sc.frame_set(f); sc.render.filepath = os.path.join(D, f"p_{i:04d}.jpg"); bpy.ops.render.render(write_still=True)
    out = os.path.join(OUT, "v6_2_camera_preview_1B_2B_4A.mp4")
    subprocess.run([os.path.join(FF, "ffmpeg"), "-y", "-loglevel", "error", "-framerate", "30", "-i", os.path.join(D, "p_%04d.jpg"),
                    "-vf", "scale=640:360", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out], env=dict(os.environ, DYLD_LIBRARY_PATH=FF), check=True)
    print("PREVIEW", out)


if __name__ == "__main__" or "__file__" not in dir():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--build" in a: build()
    if "--preview" in a: preview()
    if "--render" in a:
        pct = int(a[a.index("--pct") + 1]) if "--pct" in a else 100
        render([x for x in a if x in PLAN] or RERENDER, pct)
