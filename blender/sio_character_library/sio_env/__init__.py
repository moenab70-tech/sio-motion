"""SIO environment library: the engineering office (v4) around the approved engineer.

    from sio_env import office, exterior, lighting, clutter, shots
Everything is Python-driven (MCP live session or `Blender -b`). Assets come from the shared Poly Haven cache
(`sio_char.polyhaven.CACHE`); nothing here downloads unless a cached file is missing.
"""
from . import office, exterior, lighting, clutter, shots  # noqa: F401
