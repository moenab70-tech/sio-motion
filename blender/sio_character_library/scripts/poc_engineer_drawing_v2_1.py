"""V2.1 (final polish, Ready for User Approval): the v2 build with only these changes
  - pencil 19 cm x 8.4 mm in a tripod grip resting on the thumb-index web (no shaft through the palm)
  - one blink (at the pencil lift between strokes) instead of two
  - material polish from preset engineer_m01_v2_1 (skin less glossy + more SSS, cotton sheen, softer hair highlights)
  - extra cameras: three-quarter and pencil-grip close-up
Same cameras/lights/timing as v2 for a fair comparison. v1/v2 outputs are untouched.

Headless:  Blender -b -P scripts/poc_engineer_drawing_v2_1.py -- --render
"""
import os, sys, importlib.util
from mathutils import Vector

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else \
    "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
_spec = importlib.util.spec_from_file_location("poc_v2", os.path.join(LIB, "scripts", "poc_engineer_drawing_v2.py"))
V2 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V2)

V2.OUT = os.path.join(LIB, "tests", "poc_engineer_drawing_v2_1")
os.makedirs(V2.OUT, exist_ok=True)
V2.RENDER = globals().get("RENDER", "--render" in sys.argv)


def cam_threequarter(rig, pencil, eyes):
    return ((1.10, -1.30, 1.42), (0.0, -0.15, 1.02), 40)


def cam_grip(rig, pencil, eyes):
    from sio_char import rig as R
    tgt = pencil.matrix_world.translation.lerp(R.bone_head(rig, "DEF-f_index.01.R"), 0.5)
    return (tgt + Vector((0.20, -0.24, 0.14)), tgt, 70)


V2.CONFIG.update(
    tag="v2_1",
    preset="engineer_m01_v2_1",
    pencil=dict(length=0.19, radius=0.0042),
    grip=dict(mode="web", tip_out=0.026, web_lift=0.014, pinch_mix=0.5),
    blinks=[64],
    extra_cams={"CAM_threequarter": cam_threequarter, "CAM_grip": cam_grip},
    still_cams=["CAM_front", "CAM_side", "CAM_threequarter", "CAM_face", "CAM_grip", "CAM_seated"],
)

if __name__ == "__main__" or "__file__" not in dir():
    V2.main()
