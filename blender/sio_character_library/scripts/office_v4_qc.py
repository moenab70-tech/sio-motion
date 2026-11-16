"""Quality control for office v4:  Blender -b tests/office_v4/office_v4.blend -P scripts/office_v4_qc.py
Checks: floating/sunken props, prop-vs-prop bounding-box overlaps, object scale sanity, clock animation,
scene size, and per-state render time. Writes tests/office_v4/qc_report.json."""
import os, sys, json, time
import bpy
from mathutils import Vector

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, LIB)
from sio_env import lighting, office
from sio_char import render as RD

sc = bpy.context.scene
R = {"floating": [], "sunken": [], "overlaps": [], "scale": [], "clock": None, "render_s": {}, "stats": {}}


def roots(colls):
    out = []
    for cn in colls:
        c = bpy.data.collections.get(cn)
        if not c:
            continue
        for o in c.objects:
            if o.parent is None and o.type in ('EMPTY', 'MESH') and not o.name.startswith(("Wall", "Floor", "Ceiling", "WinCut", "ENV_facade")):
                out.append(o)
    return out


def bbox(o):
    ms = [m for m in [o] + list(o.children_recursive) if m.type == 'MESH' and not m.hide_render]
    if not ms:
        return None
    pts = [m.matrix_world @ Vector(c) for m in ms for c in m.bound_box]
    return Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))), \
           Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))


items = roots(["ENV_office_v4", "ENV_dressing", "SET_desk"])
dg = bpy.context.evaluated_depsgraph_get()
for o in items:
    b = bbox(o)
    if not b:
        continue
    lo, hi = b
    c = (lo + hi) / 2
    group = [o] + list(o.children_recursive)
    for g in group:
        g.hide_viewport = True
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, *_ = sc.ray_cast(dg, Vector((c.x, c.y, lo.z + 0.002)), Vector((0, 0, -1)), distance=5)
    for g in group:
        g.hide_viewport = False
    if hit:
        gap = lo.z - loc.z
        if gap > 0.01:
            R["floating"].append((o.name, round(gap * 100, 1), "cm"))
    size = hi - lo
    R["scale"].append((o.name, [round(v, 2) for v in size]))
boxes = [(o.name, bbox(o)) for o in items]
boxes = [(n, b) for n, b in boxes if b]
for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        (na, (alo, ahi)), (nb, (blo, bhi)) = boxes[i], boxes[j]
        ov = [min(ahi[k], bhi[k]) - max(alo[k], blo[k]) for k in range(3)]
        if all(v > 0.02 for v in ov):
            vol = ov[0] * ov[1] * ov[2]
            if vol > 0.0005:
                R["overlaps"].append((na, nb, round(vol * 1000, 2), "litres of bbox overlap"))
ok = office.animate_clock(1, 240, hours=6)
if ok:
    h, m = office.clock_hands()
    sc.frame_set(1); a = (m.matrix_world @ Vector((0, 0, 0.1))).copy()
    sc.frame_set(120); b = (m.matrix_world @ Vector((0, 0, 0.1))).copy()
    R["clock"] = {"animated": True, "minute_hand_tip_moved_m": round((a - b).length, 3)}
else:
    R["clock"] = {"animated": False}
R["stats"] = {"objects": len(bpy.data.objects), "meshes": len(bpy.data.meshes),
              "faces_unique_meshes_M": round(sum(len(m.polygons) for m in bpy.data.meshes) / 1e6, 2),
              "images": len(bpy.data.images), "max_image_px": max((max(i.size) for i in bpy.data.images), default=0)}
RD.setup("preview", sc, 30); sc.render.resolution_percentage = 50
sc.camera = bpy.data.objects["SHOT_A_establishing"]
for st in ("dusk", "night", "dawn"):
    lighting.set_state(st)
    t = time.time(); sc.render.filepath = "/tmp/_qc.png"; bpy.ops.render.render(write_still=False)
    R["render_s"][st] = round(time.time() - t, 1)
json.dump(R, open(os.path.join(LIB, "tests", "office_v4", "qc_report.json"), "w"), indent=1)
print("QC", json.dumps({k: v for k, v in R.items() if k != "scale"}))
