"""Procedural crumpled-paper + draft-sheet clutter with deterministic presets.

Poly Haven has paper stacks/notepads but no crumpled paper, so balls are generated: an A4-sized sheet volume is
approximated by a subdivided icosphere pushed by two noise octaves + random flat facets (creases), scaled to
4.5-7 cm. Eight variants are built once and instanced (shared meshes). Placement is seeded and rests on the
desk / floor (bottom of each ball sits on the surface).

Presets (cumulative): clean -> early -> attempts -> late_night -> dawn
    clutter.build()                       # once
    clutter.show("attempts")              # static state
    clutter.key_states([(1,"clean"), (40,"early"), ...])   # discrete changes (constant interpolation)
"""
import math, random
import bpy, bmesh
from mathutils import Vector, noise

PRESET_COUNTS = {           # (desk balls, floor balls, extra draft sheets)
    "clean":      (0, 0, 0),
    "early":      (2, 1, 1),
    "attempts":   (5, 4, 3),
    "late_night": (8, 9, 5),
    "dawn":       (9, 12, 6),
}
ORDER = ["clean", "early", "attempts", "late_night", "dawn"]


def _coll():
    c = bpy.data.collections.get("ENV_clutter") or bpy.data.collections.new("ENV_clutter")
    if c.name not in [x.name for x in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(c)
    return c


def _paper_mat():
    m = bpy.data.materials.get("SIO_crumpled_paper")
    if m:
        return m
    m = bpy.data.materials.new("SIO_crumpled_paper"); m.use_nodes = True
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (0.9, 0.89, 0.85, 1); b.inputs["Roughness"].default_value = 0.85
    for k in ("Subsurface Weight",):
        if k in b.inputs:
            b.inputs[k].default_value = 0.15
    return m


def crumpled_mesh(seed, radius=0.03):
    rng = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=radius)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    planes = [Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))).normalized() for _ in range(9)]
    for v in bm.verts:
        p = v.co.normalized()
        d = 0.28 * noise.noise(p * 2.2 + off) + 0.12 * noise.noise(p * 6.0 + off * 2)
        # creases: snap toward a few random planes -> flat facets with sharp folds
        for pl in planes:
            s = p.dot(pl)
            if s > 0.82:
                d -= (s - 0.82) * 0.9
        v.co = p * radius * (1.0 + d)
    sx, sy, sz = rng.uniform(0.9, 1.25), rng.uniform(0.85, 1.15), rng.uniform(0.7, 0.95)
    for v in bm.verts:
        v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
    me = bpy.data.meshes.new(f"SIO_crumple_{seed}"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = False
    me.materials.append(_paper_mat())
    return me


def build(desk_top=0.7875, desk_area=((0.25, 0.85), (-0.95, -0.25)), floor_area=((0.6, 1.6), (-0.9, 0.4)),
          basket=(1.35, -0.48), seed=42, sketch_ink=None):
    """Create every clutter object once (hidden); presets only toggle visibility."""
    rng = random.Random(seed)
    coll = _coll()
    variants = [crumpled_mesh(seed * 10 + i, radius=rng.uniform(0.024, 0.034)) for i in range(8)]
    items = {"desk": [], "floor": [], "sheets": []}
    maxd, maxf, maxs = PRESET_COUNTS["dawn"]
    def drop(mesh, x, y, z_surface, name):
        o = bpy.data.objects.new(name, mesh); coll.objects.link(o)
        o.rotation_euler = (rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28))
        bpy.context.view_layer.update()
        zmin = min((o.matrix_world @ Vector(c)).z - o.location.z for c in o.bound_box)
        o.location = (x, y, z_surface - zmin - 0.002)          # rest on the surface (2 mm settle)
        return o
    for i in range(maxd):
        x = rng.uniform(*desk_area[0]); y = rng.uniform(*desk_area[1])
        items["desk"].append(drop(variants[rng.randrange(8)], x, y, desk_top, f"SIO_crumple_desk_{i:02d}"))
    for i in range(maxf):
        if i < 5:   # around the basket first (missed throws)
            a = rng.uniform(0, 6.28); r = rng.uniform(0.2, 0.45)
            x, y = basket[0] + r * math.cos(a), basket[1] + r * math.sin(a)
        else:
            x = rng.uniform(*floor_area[0]); y = rng.uniform(*floor_area[1])
        items["floor"].append(drop(variants[rng.randrange(8)], x, y, 0.0, f"SIO_crumple_floor_{i:02d}"))
    from sio_env.office import paper_stack
    for i in range(maxs):   # loose draft sheets fanning out on the desk
        o = paper_stack(f"SIO_draft_{i:02d}", (rng.uniform(0.15, 0.7), rng.uniform(-0.9, -0.4), desk_top + 0.0012 + i * 0.0003),
                        n=1, rot_z=rng.uniform(-0.6, 0.6), coll=coll, seed=100 + i)
        items["sheets"].append(o)
    bpy.context.scene["sio_clutter"] = {k: [o.name for o in v] for k, v in items.items()}
    show("clean")
    return items


def _items():
    d = bpy.context.scene.get("sio_clutter", {})
    return {k: [bpy.data.objects[n] for n in v if n in bpy.data.objects] for k, v in d.items()}


def show(preset, frame=None):
    nd, nf, ns = PRESET_COUNTS[preset]
    it = _items()
    for key, n in (("desk", nd), ("floor", nf), ("sheets", ns)):
        for i, o in enumerate(it.get(key, [])):
            hide = i >= n
            o.hide_render = hide; o.hide_viewport = hide
            if frame is not None:
                o.keyframe_insert("hide_render", frame=frame); o.keyframe_insert("hide_viewport", frame=frame)


def key_states(schedule):
    """schedule: [(frame, preset), ...] - discrete changes (place them on cuts / time-lapse beats)."""
    for f, p in schedule:
        show(p, frame=f)
    for o in [o for v in _items().values() for o in v]:
        ad = o.animation_data
        if ad and ad.action:
            from sio_char.anim import _fcurves
            for fc in _fcurves(ad.action):
                for k in fc.keyframe_points:
                    k.interpolation = 'CONSTANT'
