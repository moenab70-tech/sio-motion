"""V2.2: V2.1 + hand/pencil/desk collision corrections (geometry/animation only; materials identical to V2.1).
  - left hand: flat resting pose, lifted until no vertex is below the desk top
  - writing hand: pencil tip-out increased automatically until the curled fingers clear the desk
Same cameras/lights/timing. V1/V2/V2.1 untouched.   Headless: Blender -b -P scripts/poc_engineer_drawing_v2_2.py -- --render
"""
import os, sys, importlib.util
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in dir() else \
    "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/blender/sio_character_library"
_spec = importlib.util.spec_from_file_location("poc_v2_1", os.path.join(LIB, "scripts", "poc_engineer_drawing_v2_1.py"))
V21 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V21)     # sets the v2.1 CONFIG on its V2 module
V2 = V21.V2
V2.OUT = os.path.join(LIB, "tests", "poc_engineer_drawing_v2_2"); os.makedirs(V2.OUT, exist_ok=True)
V2.RENDER = globals().get("RENDER", "--render" in sys.argv)
V2.CONFIG.update(tag="v2_2", resolve_contacts=True, left_hand_pose="rest_flat")
if __name__ == "__main__" or "__file__" not in dir():
    V2.main()
