"""Office v4 = the approved v3 Poly Haven office (walls, arched window, parquet, shelves, lamp, tea set ...) placed
around the approved engineer set-up, plus extra dressing (plants, books, rolled plans, paper stacks, a framed map).

The v3 office was laid out with the desk under the window along X; the character pipeline uses the desk at
(0,-0.62) facing -Y. One rigid transform maps the old office onto the character's desk (rotate +90 deg, move),
so nothing is rebuilt and the original .blend is untouched (objects are appended).
"""
import math, os, random
import bpy
from mathutils import Matrix, Vector

OFFICE_BLEND = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/src/videos/hasad-2026/opening/blender/v3/office_polyhaven.blend"
MODELS = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/src/videos/hasad-2026/opening/blender/v3/polyhaven_cache/models"
T_OFFICE = Matrix.Translation((0.6, 1.37, 0.0)) @ Matrix.Rotation(math.radians(90), 4, 'Z')
# props already supplied by the character set (desk/chair) or that would sit under the drawing hand
SKIP = {"PH_metal_office_desk", "PH_dining_chair_02", "PH_office_notepads"}
ROOM = dict(xmin=-2.4, xmax=3.6, ymin=-1.13, ymax=3.87, h=3.0)      # interior after the transform


def _coll(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    p = parent or bpy.context.scene.collection
    if c.name not in [x.name for x in p.children]:
        p.children.link(c)
    return c


def _root(o):
    while o.parent:
        o = o.parent
    return o


def append_office(collection_name="ENV_office_v4"):
    """Append Office_Shell + Office_Props from the v3 office and move them onto the character's desk."""
    coll = _coll(collection_name)
    with bpy.data.libraries.load(OFFICE_BLEND, link=False) as (a, b):
        b.collections = ["Office_Shell", "Office_Props"]
    keep = []
    for c in b.collections:
        for o in list(c.objects):
            if _root(o).name.split(".")[0] in SKIP or o.name.split(".")[0] in SKIP:   # appended names may get .001
                continue
            keep.append(o)
    for c in b.collections:
        bpy.data.collections.remove(c)
    for o in keep:
        coll.objects.link(o)
    for o in [o for o in bpy.data.objects if o.users == 0]:
        bpy.data.objects.remove(o)
    for o in keep:
        if o.parent is None and o.name in bpy.data.objects:
            o.matrix_basis = T_OFFICE @ o.matrix_basis     # matrix_world is stale right after append
    cut = bpy.data.objects.get("WinCut")            # window boolean cutter: keep (moved with the wall), never rendered
    if cut:
        cut.hide_render = True; cut.display_type = 'WIRE'; cut.hide_set(True)
    return coll


def import_gltf(asset_id, coll, name=None):
    path = os.path.join(MODELS, asset_id, f"{asset_id}.gltf")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{asset_id} not in the Poly Haven cache (run fetch_model.py {asset_id} 1k)")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(name or f"PH_{asset_id}", None); coll.objects.link(root)
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
        if o.parent is None:
            o.parent = root
    return root


def instance_of(root, name, loc, rot_z=0.0, scale=1.0, coll=None):
    """Lightweight copy: new empty + linked-data children (meshes/materials shared)."""
    coll = coll or root.users_collection[0]
    e = bpy.data.objects.new(name, None); coll.objects.link(e)
    for ch in root.children:
        c = ch.copy(); coll.objects.link(c); c.parent = e
    e.location = loc; e.rotation_euler = (0, 0, rot_z); e.scale = (scale,) * 3
    return e


def _mat(name, rgb, rough=0.6):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    return m


def rolled_plan(name, loc, length=0.62, radius=0.022, rot=(0, 0, 0), coll=None, tint=(0.86, 0.88, 0.9)):
    """Rolled engineering drawing: a thin open cylinder with a visible spiral end and a rubber band."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=length, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    o.data.materials.append(_mat("SIO_plan_paper", tint, 0.8))
    sol = o.modifiers.new("Wall", 'SOLIDIFY'); sol.thickness = -0.003
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=radius + 0.0008, minor_radius=0.0012, location=loc, rotation=rot)
    band = bpy.context.active_object; band.name = name + "_band"
    band.data.materials.append(_mat("SIO_rubber_band", (0.55, 0.12, 0.08), 0.5)); band.parent = o
    band.matrix_parent_inverse = o.matrix_world.inverted()
    for x in (o, band):
        if coll:
            for c in list(x.users_collection):
                c.objects.unlink(x)
            coll.objects.link(x)
    return o


def paper_stack(name, loc, n=24, size=(0.297, 0.21), rot_z=0.0, coll=None, seed=1):
    """Stack of A4 sheets as one mesh, slightly misaligned sheets for a used look."""
    import bmesh
    rng = random.Random(seed)
    bm = bmesh.new()
    for i in range(n):
        dx, dy, a = rng.uniform(-0.004, 0.004), rng.uniform(-0.004, 0.004), rng.uniform(-0.03, 0.03)
        z = i * 0.00011
        w, h = size[0] / 2, size[1] / 2
        pts = [(-w, -h), (w, -h), (w, h), (-w, h)]
        vs = [bm.verts.new((x * math.cos(a) - y * math.sin(a) + dx, x * math.sin(a) + y * math.cos(a) + dy, z)) for x, y in pts]
        bm.faces.new(vs)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(o)
    o.location = loc; o.rotation_euler.z = rot_z
    me.materials.append(_mat("SIO_stack_paper", (0.9, 0.89, 0.85), 0.85))
    sol = o.modifiers.new("Thick", 'SOLIDIFY'); sol.thickness = 0.00009
    return o


def dress(coll_name="ENV_dressing", desk_top=0.7875):
    """Extra set dressing on top of the v3 office (positions in the v4 room, metres)."""
    coll = _coll(coll_name)
    out = {}
    # plants: a tall one in the window corner, the cached medium one by the bookshelf, a succulent on the desk
    p1 = import_gltf("potted_plant_01", coll); p1.location = (2.05, -0.72, 0.0); p1.rotation_euler.z = 0.6; out["plant_tall"] = p1
    p4 = import_gltf("potted_plant_04", coll); p4.location = (-0.22, -0.64, desk_top); p4.rotation_euler.z = 1.1; out["plant_desk"] = p4
    p2 = import_gltf("potted_plant_02", coll); p2.location = (-1.9, 3.3, 0.0); p2.scale = (0.8,) * 3; out["plant_corner"] = p2
    # books: a second encyclopedia set lying on the desk corner as references
    # references on top of the bookshelf (the desk back edge is already full: binder, pen cup, lamp)
    bk = import_gltf("book_encyclopedia_set_01", coll); bk.rotation_euler = (0, 0, math.pi); out["books_desk"] = bk
    shelf = bpy.data.objects.get("PH_wooden_bookshelf_worn")
    if shelf:
        pts = [m.matrix_world @ Vector(c) for m in shelf.children_recursive if m.type == 'MESH' for c in m.bound_box]
        bk.location = (sum(p.x for p in pts) / len(pts) + 0.25, sum(p.y for p in pts) / len(pts), 2.2)
    # framed project map on the right wall
    fr = import_gltf("hanging_picture_frame_02", coll); fr.location = (3.58, 0.9, 1.65); fr.rotation_euler.z = math.radians(-90); out["map_frame"] = fr
    # rolled plans: three in a waste-paper bin style stand near the desk, two on the desk
    for i, (dx, dy, tilt) in enumerate(((-1.36, -0.36, 0.12), (-1.31, -0.31, -0.1), (-1.39, -0.28, 0.05))):
        rolled_plan(f"SIO_plan_roll_{i}", (dx, dy, 0.34), 0.66, 0.024, rot=(tilt, 0.08 * i, 0), coll=coll)
    # two rolls lying along the free front-right corner of the desk (cylinder axis along Y)
    rolled_plan("SIO_plan_roll_desk_0", (0.80, -0.38, desk_top + 0.0225), 0.42, 0.022, rot=(math.radians(90), 0, 0.05), coll=coll)
    rolled_plan("SIO_plan_roll_desk_1", (0.85, -0.40, desk_top + 0.0205 + 0.0), 0.40, 0.020, rot=(math.radians(90), 0, -0.06), coll=coll)
    # small succulent on the drawer cabinet (dropped onto whatever surface is there)
    p5 = instance_of(p4, "PH_potted_plant_04_cabinet", (0, 0, 0), rot_z=2.2, scale=0.9, coll=coll)
    place_on_surface(p5, -1.25, 3.62)
    out["plant_cabinet"] = p5
    # paper stacks / drafts
    out["stack_a"] = paper_stack("SIO_paper_stack_a", (0.42, -0.42, desk_top + 0.0005), 30, rot_z=0.12, coll=coll, seed=4)
    out["stack_b"] = paper_stack("SIO_paper_stack_b", (-0.80, -0.50, desk_top + 0.0005), 12, rot_z=-0.2, coll=coll, seed=7)
    for key in ("plant_tall", "plant_desk", "plant_corner", "books_desk"):
        o = out[key]
        place_on_surface(o, o.location.x, o.location.y)
    shelf_books = bpy.data.objects.get("PH_book_encyclopedia_set_01")        # v3 set on the cabinet floated 12 cm
    if shelf_books:
        place_on_surface(shelf_books, shelf_books.location.x, shelf_books.location.y)
    return out


def clock_hands():
    """(hour, minute) hand objects of the Poly Haven wall clock (names differ between files)."""
    h = next((o for o in bpy.data.objects if "hour" in o.name.lower() and o.type == 'MESH'), None)
    m = next((o for o in bpy.data.objects if "minute" in o.name.lower() and o.type == 'MESH'), None)
    return h, m


def animate_clock(f0, f1, hours=6.0):
    """Turn the hands by `hours` between f0 and f1 about the dial centre (pivot fixed first if needed)."""
    h, m = clock_hands()
    body = next((o for o in bpy.data.objects if o.type == 'MESH' and o.name.split(".")[0] == "wall_clock"), None)
    if not (h and m and body):
        return False
    lo = Vector([min(c[i] for c in body.bound_box) for i in range(3)]); hi = Vector([max(c[i] for c in body.bound_box) for i in range(3)])
    size = hi - lo
    axis = min(range(3), key=lambda k: size[k])                 # dial normal = thinnest local axis
    centre_world = body.matrix_world @ ((lo + hi) / 2)
    for o, turns in ((h, hours / 12.0), (m, hours)):
        local_c = o.matrix_world.inverted() @ centre_world
        local_c[axis] = 0.0
        if local_c.length > 0.002:                              # move the pivot onto the dial centre
            o.data.transform(Matrix.Translation(-local_c))
            o.matrix_world = o.matrix_world @ Matrix.Translation(local_c)
        o.rotation_mode = 'XYZ'
        base = o.rotation_euler[axis]
        o.keyframe_insert("rotation_euler", index=axis, frame=f0)
        o.rotation_euler[axis] = base - turns * 2 * math.pi
        o.keyframe_insert("rotation_euler", index=axis, frame=f1)
        o.rotation_euler[axis] = base
        if o.animation_data and o.animation_data.action:
            from sio_char.anim import _set_interp
            _set_interp(o.animation_data.action, None, 'LINEAR')
    return True


def place_on_surface(obj, x, y, z_from=2.9, ignore=()):
    """Drop obj so its lowest point rests on whatever is below (x, y). Returns the surface z (or None)."""
    sc = bpy.context.scene
    hidden = [obj] + list(obj.children_recursive) + [bpy.data.objects[n] for n in ignore if n in bpy.data.objects]
    for o in hidden:
        o.hide_viewport = True
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, *_ = sc.ray_cast(dg, Vector((x, y, z_from)), Vector((0, 0, -1)))
    for o in hidden:
        o.hide_viewport = False
    if not hit:
        return None
    bpy.context.view_layer.update()
    pts = [m.matrix_world @ Vector(c) for m in [obj] + list(obj.children_recursive) if m.type == 'MESH' for c in m.bound_box]
    zmin = min(p.z for p in pts) if pts else obj.location.z
    obj.location = (x, y, obj.location.z + (loc.z - zmin))
    return loc.z


def facade(width=30.0, below=9.4, above=6.0, y_out=-1.33, thickness=0.06):
    """Exterior wall of the building around the office window (only the face the cameras can see from
    outside); the window opening is cut with the office's own WinCut boolean so it matches exactly."""
    o = bpy.data.objects.get("ENV_facade")
    if o:
        return o
    bpy.ops.mesh.primitive_cube_add(location=(0.6, y_out - thickness / 2, (above - below) / 2))
    o = bpy.context.active_object; o.name = "ENV_facade"
    o.scale = (width / 2, thickness / 2, (above + below) / 2)
    bpy.ops.object.transform_apply(scale=True)
    m = bpy.data.materials.get("Plaster_Cream")
    if m:
        o.data.materials.append(m)
    cut = bpy.data.objects.get("WinCut")
    if cut:
        b = o.modifiers.new("Window", 'BOOLEAN'); b.object = cut; b.operation = 'DIFFERENCE'; b.solver = 'EXACT'
    for c in list(o.users_collection):
        c.objects.unlink(o)
    _coll("ENV_office_v4").objects.link(o)
    # a slim concrete sill band under the window line, repeating on each floor, gives scale from outside
    for i, z in enumerate((0.72, -2.28, -5.28, -8.28)):
        bpy.ops.mesh.primitive_cube_add(location=(0.6, y_out - thickness - 0.04, z))
        s = bpy.context.active_object; s.name = f"ENV_facade_band_{i}"; s.scale = (width / 2, 0.05, 0.06)
        s.data.materials.append(_mat("SIO_concrete_band", (0.7, 0.67, 0.62), 0.8))
        for c in list(s.users_collection):
            c.objects.unlink(s)
        _coll("ENV_office_v4").objects.link(s)
    return o
