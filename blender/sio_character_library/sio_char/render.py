"""Render presets tuned for an M2 Pro / 16 GB.

    render.setup("preview")      # Eevee, 50 %, 16 samples  (look checks, animation previews)
    render.setup("cinematic")    # Eevee raytraced, 100 %, 64 samples, AgX
    render.setup("cycles")       # Cycles Metal GPU, 128 samples + denoise (stills only)
    render.setup("toon")         # Eevee, Standard view transform for cel materials
"""
import bpy

PRESETS = {
    "preview":   dict(engine="BLENDER_EEVEE", pct=50, samples=16, view="AgX", rt=False),
    "cinematic": dict(engine="BLENDER_EEVEE", pct=100, samples=64, view="AgX", rt=True),
    "cycles":    dict(engine="CYCLES", pct=100, samples=128, view="AgX", rt=False),
    "toon":      dict(engine="BLENDER_EEVEE", pct=100, samples=32, view="Standard", rt=False),
}


def setup(name="preview", scene=None, fps=30):
    sc = scene or bpy.context.scene
    P = PRESETS[name]
    sc.render.engine = P["engine"]
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = P["pct"]
    sc.render.fps = fps
    sc.view_settings.view_transform = P["view"]
    if P["engine"] == "BLENDER_EEVEE":
        e = sc.eevee
        for k, v in (("taa_render_samples", P["samples"]), ("use_raytracing", P["rt"]), ("use_shadows", True),
                     ("shadow_resolution_scale", 1.0)):
            try:
                setattr(e, k, v)
            except Exception:
                pass
    else:
        c = sc.cycles
        c.samples = P["samples"]; c.use_denoising = True
        try:
            c.device = 'GPU'
            prefs = bpy.context.preferences.addons["cycles"].preferences
            prefs.compute_device_type = 'METAL'
            prefs.get_devices()
            for d in prefs.devices:
                d.use = True
        except Exception:
            pass
    sc.render.hair_type = 'STRIP'
    return sc


def still(path, camera=None, scene=None):
    sc = scene or bpy.context.scene
    if camera:
        sc.camera = bpy.data.objects[camera] if isinstance(camera, str) else camera
    im = sc.render.image_settings
    if hasattr(im, "media_type"):
        im.media_type = 'IMAGE'
    im.file_format = 'PNG'
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


def animation_preview(path_mp4, frame_start, frame_end, scene=None):
    sc = scene or bpy.context.scene
    sc.frame_start, sc.frame_end = frame_start, frame_end
    im = sc.render.image_settings
    if hasattr(im, "media_type"):          # Blender 5.x: video is a separate media type
        im.media_type = 'VIDEO'
    im.file_format = 'FFMPEG'
    sc.render.ffmpeg.format = 'MPEG4'
    sc.render.ffmpeg.codec = 'H264'
    sc.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    sc.render.filepath = path_mp4
    bpy.ops.render.render(animation=True)
    return path_mp4
