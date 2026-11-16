"""Hasad opening v6.4 = v6.3 + canal PBR materials (sio_env.env_materials) + deterministic wind/water motion
(sio_env.wind). final_v6_3.blend stays untouched. Preview-only until approved.
  Blender -b tests/final_v6_3/final_v6_3.blend -P scripts/final_v6_4.py -- --build
  Blender -b tests/final_v6_4/final_v6_4.blend -P scripts/final_v6_4.py -- --stills  [tag]
  Blender -b tests/final_v6_4/final_v6_4.blend -P scripts/final_v6_4.py -- --anim wind|water
  Blender -b <blend> -P scripts/final_v6_4.py -- --compare <engine> <case> <out.png>   (one frame, for timing/memory)
"""
import os, sys, time, subprocess, importlib.util
import bpy
LIB = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
sys.path.insert(0, LIB)
OUT = os.path.join(LIB, "tests", "final_v6_4"); os.makedirs(os.path.join(OUT, "previews"), exist_ok=True)
REPO = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics"
FF = os.path.join(REPO, "node_modules/@remotion/compositor-darwin-arm64")
_s = importlib.util.spec_from_file_location("v62", os.path.join(LIB, "scripts", "final_v6_2.py")); V62 = importlib.util.module_from_spec(_s); _s.loader.exec_module(V62)
CASES = {  # comparison frames
    "face_office": ("S3", "SHOT_C_eyes", 40),
    "canal_landscape": ("S3", "SHOT_J_canal", 45),
    "water_vegetation": ("S3", "SHOT_K3_canal_axis", 60),
    "shadows_desk": ("S2", "SHOT_E_overhead", 40),
}


def build():
    from sio_env import env_materials, wind
    print("MATS", env_materials.apply_all())
    print("WIND", wind.build())
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, 300
    path = os.path.join(OUT, "final_v6_4.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, relative_remap=False); print("FINAL_V6_4 saved", path)


def _eevee(sc, pct=100, samples=64):
    from sio_char import render as RD
    RD.setup("cinematic", sc, 30); V62.quality(sc); sc.render.resolution_percentage = pct; sc.eevee.taa_render_samples = samples


def _cycles(sc, pct=100, samples=256):
    from sio_char import render as RD
    RD.setup("cycles", sc, 30); c = sc.cycles
    sc.render.resolution_percentage = pct
    c.device = 'GPU'; c.samples = samples; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.02
    c.use_denoising = True; c.denoiser = 'OPENIMAGEDENOISE'
    try:
        c.denoising_use_gpu = True
    except Exception:
        pass
    c.use_light_tree = True; c.max_bounces = 8; c.diffuse_bounces = 3; c.glossy_bounces = 3; c.transmission_bounces = 6
    c.transparent_max_bounces = 16; c.volume_bounces = 0; c.sample_clamp_indirect = 10.0
    c.volume_step_rate = 4.0
    print("CYCLES_DEVICES", [(d.name, d.type, d.use) for d in bpy.context.preferences.addons["cycles"].preferences.devices])


def stills(tag):
    from sio_env import story
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]; _eevee(sc)
    im = sc.render.image_settings; im.media_type = 'IMAGE'; im.file_format = 'PNG'; im.color_mode = 'RGB'
    for name, (ses, cam, f) in (("canal_bank", ("S3", "SHOT_J_canal", 45)), ("canal_axis", ("S3", "SHOT_K3_canal_axis", 60))):
        story.apply(ses, rig); sc.camera = bpy.data.objects[cam]; sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, "previews", f"{tag}_{name}.png"); bpy.ops.render.render(write_still=True); print("STILL", tag, name)


def anim(kind):
    """Short low-cost motion previews: wind (bank shot, 3 s) / water (close preview camera on the canal, 3 s)."""
    from sio_env import story, shots as SH
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]; _eevee(sc, 40, 16)
    story.apply("S3", rig)
    if kind == "wind":
        cam = bpy.data.objects["SHOT_J_canal"]; f0, n = 1, 90
    else:   # preview-only camera, not part of the edit
        cam = SH._cam("PREVIEW_water", 50, 8); cam.data.clip_end = 150000
        SH._track(cam, SH._target_empty("PREVIEW_water_t", (-20.0, -38.0, -9.0)))
        cam.animation_data_clear(); cam.location = (-31.0, -34.2, -7.6); f0, n = 1, 90
    sc.camera = cam
    im = sc.render.image_settings; im.media_type = 'IMAGE'; im.file_format = 'JPEG'; im.quality = 90
    D = os.path.join(OUT, f"anim_{kind}"); os.makedirs(D, exist_ok=True)
    for i, f in enumerate(range(f0, f0 + n)):
        sc.frame_set(f); sc.render.filepath = os.path.join(D, f"a_{i + 1:04d}.jpg"); bpy.ops.render.render(write_still=True)
    out = os.path.join(OUT, f"v6_4_{kind}_preview.mp4")
    subprocess.run([os.path.join(FF, "ffmpeg"), "-y", "-loglevel", "error", "-framerate", "30", "-i", os.path.join(D, "a_%04d.jpg"),
                    "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out], env=dict(os.environ, DYLD_LIBRARY_PATH=FF), check=True)
    print("ANIM", out)


def compare(engine, case, out):
    from sio_env import story
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    (_cycles if engine == "cycles" else _eevee)(sc)
    ses, cam, f = CASES[case]; story.apply(ses, rig); sc.camera = bpy.data.objects[cam]; sc.frame_set(f)
    im = sc.render.image_settings; im.media_type = 'IMAGE'; im.file_format = 'PNG'; im.color_mode = 'RGB'
    sc.render.filepath = out; t = time.time(); bpy.ops.render.render(write_still=True)
    print("COMPARE", engine, case, "seconds", round(time.time() - t, 1))


if __name__ == "__main__" or "__file__" not in dir():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--build" in a: build()
    if "--stills" in a: stills(a[a.index("--stills") + 1])
    if "--anim" in a: anim(a[a.index("--anim") + 1])
    if "--compare" in a:
        i = a.index("--compare"); compare(a[i + 1], a[i + 2], a[i + 3])
