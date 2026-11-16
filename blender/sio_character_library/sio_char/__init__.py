"""SIO character library for Blender 5.3 (MPFB + Rigify + native Hair Curves).

Use inside Blender (MCP or headless):

    import sys; sys.path.insert(0, "<repo>/blender/sio_character_library")
    import sio_char
    ch = sio_char.character.build("engineer_m01")      # body, skin, eyes, clothes, Rigify rig
    sio_char.hair.apply_preset(ch, "short_side_part")  # head hair  (Hair Curves)
    sio_char.hair.apply_preset(ch, "beard_short")      # beard      (Hair Curves)

See README.md for the full workflow.
"""
import os

LIB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = os.path.join(LIB_ROOT, "presets")

from . import util, character, materials, hair, rig, anim, render, extensions  # noqa: E402,F401
