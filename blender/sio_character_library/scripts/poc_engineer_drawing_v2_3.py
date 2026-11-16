"""V2.3: V2.2 + full back-of-head hair (nape hairline + rigid skull skin), corrected forward seated lean,
realistic procedural skin. Previous versions untouched.   Headless: Blender -b -P scripts/poc_engineer_drawing_v2_3.py -- --render
"""
import os, sys, importlib.util
from mathutils import Vector

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else \
    "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
_spec = importlib.util.spec_from_file_location("poc_v2_2", os.path.join(LIB, "scripts", "poc_engineer_drawing_v2_2.py"))
V22 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V22)
V2 = V22.V2
V2.OUT = os.path.join(LIB, "tests", "poc_engineer_drawing_v2_3"); os.makedirs(V2.OUT, exist_ok=True)
V2.RENDER = globals().get("RENDER", "--render" in sys.argv)


def _eye_mid(rig):
    from sio_char import rig as R
    return (R.bone_head(rig, "DEF-eye.L") + R.bone_head(rig, "DEF-eye.R")) / 2


def cam_rear(rig, pencil, eyes):
    h = _eye_mid(rig); return (h + Vector((0.05, 0.62, 0.10)), h + Vector((0, 0.08, 0.02)), 85)


def cam_rear_side(rig, pencil, eyes):
    h = _eye_mid(rig); return (h + Vector((-0.52, 0.30, 0.06)), h + Vector((0, 0.06, 0.02)), 85)


def cam_rear_three_quarter(rig, pencil, eyes):
    return ((-1.25, 1.45, 1.45), (0.0, -0.1, 0.85), 40)


V2.CONFIG.update(
    tag="v2_3",
    preset="engineer_m01_v2_3",
    sit=dict(seat_y=0.07, spine_lean=(16, 7), pelvis_tilt=2, forward=True),
    look=dict(strength=0.25, max_deg=14, neck_share=0.4),
    reach=0.07,
    extra_cams={**V2.CONFIG["extra_cams"], "CAM_rear": cam_rear, "CAM_rear_side": cam_rear_side,
                "CAM_rear_threequarter": cam_rear_three_quarter},
    still_cams=["CAM_front", "CAM_side", "CAM_threequarter", "CAM_rear_threequarter", "CAM_face", "CAM_grip",
                "CAM_rear", "CAM_rear_side"],
)

if __name__ == "__main__" or "__file__" not in dir():
    V2.main()
