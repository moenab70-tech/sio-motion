"""Office v5 = office v4 environment + engineer V2.3 + multi-session story (workdays, not a sleepless night)
+ collaborators. v4 files are untouched.

  Blender -b -P scripts/office_v5.py -- --previews     (build + session stills)
  Blender -b tests/office_v5/office_v5.blend -P scripts/office_v5.py -- --story    (time-progression preview video)
"""
import os, sys, importlib.util, subprocess
import bpy
from mathutils import Vector

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else \
    "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
if LIB not in sys.path:
    sys.path.insert(0, LIB)
OUT = os.path.join(LIB, "tests", "office_v5"); os.makedirs(os.path.join(OUT, "previews"), exist_ok=True)
FF = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/node_modules/@remotion/compositor-darwin-arm64"


def build():
    _spec = importlib.util.spec_from_file_location("poc_v2_3", os.path.join(LIB, "scripts", "poc_engineer_drawing_v2_3.py"))
    V23 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V23)
    V2 = V23.V2
    V2.OUT = OUT; V2.RENDER = False
    V2.CONFIG.update(tag="office_v5_character")
    ch = V2.main()
    for m in [m for m in list(sys.modules) if m.startswith("sio_env")]:
        del sys.modules[m]
    from sio_env import office, exterior, lighting, clutter, shots, story
    from sio_char import render as RD
    for n in ("SET_floor", "SET_wall", "KEY_window", "FILL", "RIM", "DESK_lamp"):
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o)
    for o in [o for o in bpy.data.objects if o.type == 'CAMERA' and o.name.startswith("CAM_")]:
        bpy.data.objects.remove(o)
    desk_top = 0.7875
    office.append_office(); office.dress(desk_top=desk_top); office.facade()
    exterior.build(); exterior.poly_haven_vegetation()
    clutter.build(desk_top=desk_top, desk_area=((0.25, 0.66), (-0.62, -0.2)))
    story.setup(ch)
    paper = bpy.data.objects["SIO_paper"].matrix_world.translation
    story.collaborators(paper=(paper.x, paper.y, paper.z))
    pencil = bpy.data.objects["SIO_pencil"]
    shots.all_shots(ch.rig, pencil)
    # extra story cameras: calendar insert + collaboration wide
    cal = bpy.data.objects["STORY_calendar"].matrix_world.translation
    c = shots._cam("SHOT_H_calendar", 70, 2.8); shots._track(c, shots._target_empty("SHOT_H_target", cal))
    shots._move(c, [cal + Vector((1.1, -0.15, -0.05)), cal + Vector((1.0, -0.12, -0.04))], 1, 60)
    c = shots._cam("SHOT_I_collab", 28, 4); shots._track(c, shots._target_empty("SHOT_I_target", (0.0, -0.15, 1.1)))
    shots._move(c, [(2.35, -0.70, 1.55), (2.15, -0.62, 1.52)], 1, 150)        # window corner, inside the room
    story.apply("S1", ch.rig)
    sc = bpy.context.scene; sc.camera = bpy.data.objects["SHOT_A_establishing"]
    RD.setup("preview", sc, 30); sc.frame_start, sc.frame_end = 1, 150
    path = os.path.join(OUT, "office_v5.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.file.make_paths_absolute(); bpy.ops.wm.save_as_mainfile(filepath=path, relative_remap=False)
    print("OFFICE_V5 saved", path)


def previews():
    from sio_env import story
    from sio_char import render as RD
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    RD.setup("preview", sc, 30); sc.render.resolution_percentage = 50
    plan = [("01_S1_afternoon_wide", "S1", "SHOT_A_establishing", 60), ("02_calendar_day13", "S2", "SHOT_H_calendar", 30),
            ("03_S2_morning_overhead", "S2", "SHOT_E_overhead", 40), ("04_S3_late_afternoon_threeq", "S3", "SHOT_G_dawn_reveal", 100),
            ("05_S3_eyes", "S3", "SHOT_C_eyes", 40), ("06_S3_pencil", "S3", "SHOT_D_pencil", 40),
            ("07_collaboration", "COLLAB", "SHOT_I_collab", 60)]
    for name, ses, cam, f in plan:
        story.apply(ses, rig); sc.frame_set(f)
        RD.still(os.path.join(OUT, "previews", name + ".png"), cam, sc); print("PREVIEW", name)


def story_video():
    """~12 s time-progression preview (480x270, 15 fps): S1 -> calendar -> S2 -> S3 -> collaboration."""
    from sio_env import story
    from sio_char import render as RD
    sc = bpy.context.scene; rig = bpy.data.objects["engineer_m01_rig"]
    RD.setup("preview", sc, 15); sc.render.resolution_percentage = 25; sc.frame_step = 2
    try:
        sc.eevee.taa_render_samples = 12
    except Exception:
        pass
    D = os.path.join(OUT, "story_clips"); os.makedirs(D, exist_ok=True)
    plan = [("1_S1_afternoon_wide", "S1", "SHOT_A_establishing", 1, 60, None),
            ("2_S1_pencil", "S1", "SHOT_D_pencil", 1, 45, None),
            ("3_calendar_12", "S1", "SHOT_H_calendar", 1, 15, None),
            ("4_calendar_13", "S2", "SHOT_H_calendar", 16, 30, None),
            ("5_S2_morning_overhead", "S2", "SHOT_E_overhead", 1, 45, None),
            ("6_calendar_14", "S3", "SHOT_H_calendar", 31, 45, None),
            ("7_S3_late_afternoon", "S3", "SHOT_G_dawn_reveal", 60, 120, None),
            ("8_collaboration", "COLLAB", "SHOT_I_collab", 1, 75, None)]
    clips = []
    for name, ses, cam, f0, f1, _ in plan:
        story.apply(ses, rig)
        p = os.path.join(D, name + ".mp4"); sc.camera = bpy.data.objects[cam]
        RD.animation_preview(p, f0, f1, sc); clips.append(p)
    lst = os.path.join(D, "clips.txt"); open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
    final = os.path.join(OUT, "office_v5_story_preview.mp4")
    subprocess.run([os.path.join(FF, "ffmpeg"), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "15", final], env=dict(os.environ, DYLD_LIBRARY_PATH=FF), check=True)
    print("STORY_PREVIEW", final)


if __name__ == "__main__" or "__file__" not in dir():
    if "--story" in sys.argv:
        story_video()
    else:
        build()
        if "--previews" in sys.argv:
            previews()
