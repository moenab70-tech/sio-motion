"""Small shared helpers (MPFB service access, presets, rest-pose geometry)."""
import importlib, json, os
import bpy
import numpy as np
from mathutils import Vector

_MPFB = None


def mpfb(service):
    """Return an MPFB service class, e.g. mpfb('HumanService')."""
    global _MPFB
    if _MPFB is None:
        mod = next((m for m in bpy.context.preferences.addons.keys() if m.endswith(".mpfb") or m == "mpfb"), None)
        if not mod:
            raise RuntimeError("MPFB extension is not enabled")
        _MPFB = mod
    return getattr(importlib.import_module(f"{_MPFB}.services.{service.lower()}"), service)


def load_preset(kind, name):
    from . import PRESETS
    path = name if name.endswith(".json") else os.path.join(PRESETS, kind, name + ".json")
    with open(path) as f:
        return json.load(f)


def mpfb_asset(kind, name, ext="mhclo"):
    ud = mpfb("LocationService").get_user_data()
    d = os.path.join(ud, kind, name)
    for f in os.listdir(d):
        if f.endswith("." + ext):
            return os.path.join(d, f)
    raise FileNotFoundError(f"{kind}/{name}/*.{ext}")


def rest_coords(body):
    """Object-space vertex positions of the MPFB basemesh with its shape keys mixed (rest pose)."""
    me = body.data
    n = len(me.vertices)
    base = np.empty(n * 3)
    me.vertices.foreach_get("co", base)
    if me.shape_keys:
        kb = me.shape_keys.key_blocks
        kb[0].data.foreach_get("co", base)
        co = base.copy()
        tmp = np.empty_like(base)
        for k in kb[1:]:
            if k.mute or k.value == 0:
                continue
            k.data.foreach_get("co", tmp)
            co += k.value * (tmp - base)
        base = co
    return base.reshape(-1, 3)


def vgroup_weights(body, name):
    vg = body.vertex_groups.get(name)
    w = np.zeros(len(body.data.vertices))
    if vg is None:
        return w
    gi = vg.index
    for v in body.data.vertices:
        for g in v.groups:
            if g.group == gi:
                w[v.index] = g.weight
    return w


def find_rig(body):
    """The generated Rigify rig (or any armature) driving this body."""
    for m in body.modifiers:
        if m.type == 'ARMATURE' and m.object:
            return m.object
    return body.parent if body.parent and body.parent.type == 'ARMATURE' else None


def ensure_collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    parent = parent or bpy.context.scene.collection
    if c.name not in [x.name for x in parent.children]:
        parent.children.link(c)
    return c


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)
