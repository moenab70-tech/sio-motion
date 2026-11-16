"""Read-only analysis of final_v6_5.blend: polygons per library object, instances per layer (by source collection),
camera samples for 3B / 4A. Prints only, saves nothing.
  Blender -b tests/final_v6_5/final_v6_5.blend -P scripts/final_v6_5_opt_analyze.py
"""
import bpy
from collections import Counter, defaultdict

sc = bpy.context.scene
print("=== LIBRARY ===")
src_coll = {}
for c in ("VEG_grass", "VEG_groundcover", "VEG_shrub", "VEG_tree_mid", "VEG_tree_far", "VEG_rock"):
    col = bpy.data.collections[c]
    tot = 0
    for o in col.objects:
        n = len(o.data.polygons) if o.type == 'MESH' else 0
        tot += n; src_coll[o.name] = c
        print(f"  {c:16s} {o.name:40s} polys {n:>9,d} dims {tuple(round(d,1) for d in o.dimensions)}")
    print(f"  {c} objects {len(col.objects)} polys {tot:,d}")

sc.frame_set(60)
dg = bpy.context.evaluated_depsgraph_get()
cnt = Counter(); tris = Counter()
for inst in dg.object_instances:
    if inst.is_instance and inst.parent and inst.parent.name.startswith("EXT_terrain"):
        on = inst.object.original.name
        key = (inst.parent.name, src_coll.get(on, on))
        cnt[key] += 1
        tris[key] += len(inst.object.original.data.polygons) if inst.object.type == 'MESH' else 0
print("=== INSTANCES (frame 60) ===")
for k in sorted(cnt):
    print(f"  {k[0]:18s} {k[1]:18s} n {cnt[k]:>8,d}  polys {tris[k]:>14,d}")
print("  TOTAL n", sum(cnt.values()), "polys", f"{sum(tris.values()):,d}")

print("=== CAMERAS ===")
for cn in ("SHOT_J_canal", "SHOT_K3_canal_axis"):
    c = bpy.data.objects[cn]
    for f in (1, 30, 60, 90, 120):
        sc.frame_set(f)
        m = c.matrix_world
        print(f"  {cn} f{f} loc {tuple(round(v,2) for v in m.translation)} fwd {tuple(round(v,2) for v in (-m.col[2].xyz))} lens {c.data.lens} sensor {c.data.sensor_width} fit {c.data.sensor_fit}")
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.data.type == 'SUN':
        print("  SUN", o.name, tuple(round(v, 3) for v in (o.matrix_world.to_3x3() @ __import__('mathutils').Vector((0, 0, -1)))), "hide_render", o.hide_render)
for o in bpy.data.objects:
    if o.name.startswith("SIO_sketch") or o.name.startswith("SIO_ink"):
        print("  STORY", o.name, o.type, tuple(round(v, 1) for v in o.matrix_world.translation), tuple(round(v, 1) for v in o.dimensions), "hide_render", o.hide_render)
print("ANALYZE_DONE")
