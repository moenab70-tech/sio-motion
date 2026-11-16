"""Reusable, deterministic wind for the canal environment (v6.4). Headless-safe: Geometry Nodes Scene Time +
procedural noise; controller values reach the modifiers through plain (non-Python) SUM drivers.

Controller: empty "SIO_wind" (arrow). Its Z rotation = wind direction. Custom properties:
  strength (m of tip travel for a palm frond at stiffness 1), gust_freq (Hz of the base sway),
  gust_scale (spatial size of travelling gusts, m), gust_speed (m/s gusts travel downwind),
  stiff_palm, stiff_tree, stiff_grass, stiff_shrub (higher = stiffer = less motion)

Deformers
  * palm crowns  : GN modifier SIO_wind_deform, weight = (radial distance from the trunk axis / 4 m)^1.6 -> tips move,
                   the crown base and trunk stay; small droop with the sway; per-palm phase from its location
  * island trees : same modifier in height mode, weight = ((z - 1.6 m) / height)^2 -> trunks stable
  * scatter      : grass / ground cover / shrubs / small trees are instances -> tilt about their base inside the
                   scatter tree (Rotate Instances, local), angle = strength * travelling gust noise / stiffness
"""
import math
import bpy

PROPS = dict(strength=0.32, gust_freq=0.35, gust_scale=38.0, gust_speed=4.5,
             stiff_palm=1.0, stiff_tree=3.5, stiff_grass=1.0, stiff_shrub=2.4)


def controller(direction_deg=200.0):
    o = bpy.data.objects.get("SIO_wind") or bpy.data.objects.new("SIO_wind", None)
    if o.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(o)
    o.empty_display_type = 'SINGLE_ARROW'; o.empty_display_size = 3.0
    o.location = (0.0, -38.0, -6.0); o.rotation_euler = (0.0, math.radians(90), math.radians(direction_deg))   # arrow (+Z) -> +X, then yaw
    for k, v in PROPS.items():
        if k not in o:
            o[k] = v
    return o


def _drive(md, sock_name, ctrl, prop, ng):
    ident = next(i.identifier for i in ng.interface.items_tree if getattr(i, "in_out", None) == 'INPUT' and i.name == sock_name)
    sock = getattr(md.properties.inputs, ident)          # Blender 5.3: modifier inputs live under .properties.inputs
    sock.value = float(ctrl[prop])
    fc = md.id_data.driver_add(sock.path_from_id() + ".value")
    drv = fc.driver; drv.type = 'SUM'
    v = drv.variables.new(); v.name = "v"; v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'; v.targets[0].id = ctrl; v.targets[0].data_path = f'["{prop}"]'


def _wind_dir_nodes(N, L, ctrl):
    """World wind direction (unit XY) from the controller's Z rotation."""
    oi = N.new("GeometryNodeObjectInfo"); oi.inputs["Object"].default_value = ctrl
    vr = N.new("ShaderNodeVectorRotate"); vr.rotation_type = 'EULER_XYZ'
    vr.inputs["Vector"].default_value = (1.0, 0.0, 0.0)
    sep = N.new("ShaderNodeSeparateXYZ"); comb = N.new("ShaderNodeCombineXYZ")
    L.new(oi.outputs["Rotation"], sep.inputs[0]); L.new(sep.outputs["Z"], comb.inputs["Z"])     # yaw only
    L.new(comb.outputs[0], vr.inputs["Rotation"])
    return vr.outputs[0]


def deform_group(ctrl):
    name = "SIO_wind_deform"
    if bpy.data.node_groups.get(name):
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    I = ng.interface
    I.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    for nm, dv in (("Strength", 0.32), ("Frequency", 0.35), ("Gust Scale", 38.0), ("Gust Speed", 4.5), ("Stiffness", 1.0),
                   ("Height Mode", 0.0), ("Radius Ref", 4.0), ("Height Ref", 8.0)):
        s = I.new_socket(nm, in_out='INPUT', socket_type='NodeSocketFloat'); s.default_value = dv
    I.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    sp = N.new("GeometryNodeSetPosition"); L.new(gi.outputs["Geometry"], sp.inputs["Geometry"]); L.new(sp.outputs[0], go.inputs[0])
    pos = N.new("GeometryNodeInputPosition").outputs[0]
    sepp = N.new("ShaderNodeSeparateXYZ"); L.new(pos, sepp.inputs[0])
    def m(op, a, b=None, c=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b, c)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs[0]
    # weights
    r = m('SQRT', m('ADD', m('MULTIPLY', sepp.outputs["X"], sepp.outputs["X"]), m('MULTIPLY', sepp.outputs["Y"], sepp.outputs["Y"])))
    w_rad = m('POWER', m('MINIMUM', m('DIVIDE', r, gi.outputs["Radius Ref"]), 1.4), 1.6)
    w_h = m('POWER', m('MAXIMUM', m('DIVIDE', m('SUBTRACT', sepp.outputs["Z"], 1.6), gi.outputs["Height Ref"]), 0.0), 2.0)
    mixw = N.new("ShaderNodeMix"); mixw.data_type = 'FLOAT'
    L.new(gi.outputs["Height Mode"], mixw.inputs[0]); L.new(w_rad, mixw.inputs[2]); L.new(w_h, mixw.inputs[3])
    w = mixw.outputs[0]
    # time, object phase, world position of the object
    t = N.new("GeometryNodeInputSceneTime").outputs["Seconds"]
    selfo = N.new("GeometryNodeSelfObject"); oi = N.new("GeometryNodeObjectInfo"); oi.transform_space = 'ORIGINAL'
    L.new(selfo.outputs[0], oi.inputs["Object"])
    so = N.new("ShaderNodeSeparateXYZ"); L.new(oi.outputs["Location"], so.inputs[0])
    phase = m('ADD', m('MULTIPLY', so.outputs["X"], 0.37), m('MULTIPLY', so.outputs["Y"], 0.53))
    wdir = _wind_dir_nodes(N, L, bpy.data.objects["SIO_wind"])
    # travelling gust: noise sampled at (object pos - wind_dir * speed * t) / scale
    vs = N.new("ShaderNodeVectorMath"); vs.operation = 'SCALE'; L.new(wdir, vs.inputs[0])
    L.new(m('MULTIPLY', t, gi.outputs["Gust Speed"]), vs.inputs["Scale"])
    vsub = N.new("ShaderNodeVectorMath"); vsub.operation = 'SUBTRACT'; L.new(oi.outputs["Location"], vsub.inputs[0]); L.new(vs.outputs[0], vsub.inputs[1])
    vdiv = N.new("ShaderNodeVectorMath"); vdiv.operation = 'DIVIDE'; L.new(vsub.outputs[0], vdiv.inputs[0])
    cs = N.new("ShaderNodeCombineXYZ"); L.new(gi.outputs["Gust Scale"], cs.inputs["X"]); L.new(gi.outputs["Gust Scale"], cs.inputs["Y"]); L.new(gi.outputs["Gust Scale"], cs.inputs["Z"])
    L.new(cs.outputs[0], vdiv.inputs[1])
    gn = N.new("ShaderNodeTexNoise"); gn.inputs["Scale"].default_value = 1.0; gn.inputs["Detail"].default_value = 1.0
    L.new(vdiv.outputs[0], gn.inputs["Vector"])
    gust = m('MULTIPLY_ADD', gn.outputs["Fac"], 1.6, -0.3)                       # ~0.2 .. 1.1
    # base sway + flutter (per vertex phase from radius -> tips lag)
    sway = m('SINE', m('ADD', m('MULTIPLY', m('MULTIPLY', t, gi.outputs["Frequency"]), 2 * math.pi), m('ADD', phase, m('MULTIPLY', r, 0.35))))
    flut = m('SINE', m('ADD', m('MULTIPLY', t, 7.3), m('ADD', m('MULTIPLY', sepp.outputs["X"], 2.1), m('MULTIPLY', sepp.outputs["Y"], 1.7))))
    amt = m('DIVIDE', m('MULTIPLY', gi.outputs["Strength"], w), gi.outputs["Stiffness"])
    push = m('MULTIPLY', amt, m('ADD', m('MULTIPLY', gust, 0.75), m('MULTIPLY', sway, 0.35)))     # mostly downwind, oscillating
    # world offset -> object local (objects carry a random yaw)
    off = N.new("ShaderNodeVectorMath"); off.operation = 'SCALE'; L.new(wdir, off.inputs[0]); L.new(push, off.inputs["Scale"])
    vr = N.new("ShaderNodeVectorRotate"); vr.rotation_type = 'EULER_XYZ'; vr.invert = True
    L.new(off.outputs[0], vr.inputs["Vector"]); L.new(oi.outputs["Rotation"], vr.inputs["Rotation"])
    droop = m('MULTIPLY', m('MULTIPLY', amt, -0.22), m('ABSOLUTE', push))
    fl = m('MULTIPLY', m('MULTIPLY', amt, 0.05), flut)
    cz = N.new("ShaderNodeCombineXYZ"); L.new(m('ADD', droop, fl), cz.inputs["Z"])
    tot = N.new("ShaderNodeVectorMath"); tot.operation = 'ADD'; L.new(vr.outputs[0], tot.inputs[0]); L.new(cz.outputs[0], tot.inputs[1])
    L.new(tot.outputs[0], sp.inputs["Offset"])
    return ng


def add_deformers(ctrl):
    ng = deform_group(ctrl)
    n_palm = n_tree = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or not o.data.materials:
            continue
        mats = {m.name for m in o.data.materials if m}
        palm_crown = "EXT_palm_crown" in mats and o.name.startswith("EXT_palm_")
        island = o.name.startswith("EXT_ph_") and any(m.startswith("island_tree") for m in mats)
        if not (palm_crown or island):
            continue
        for md in [x for x in o.modifiers if x.name == "SIO_wind"]:
            o.modifiers.remove(md)
        md = o.modifiers.new("SIO_wind", 'NODES'); md.node_group = ng
        _drive(md, "Strength", ctrl, "strength", ng); _drive(md, "Frequency", ctrl, "gust_freq", ng)
        _drive(md, "Gust Scale", ctrl, "gust_scale", ng); _drive(md, "Gust Speed", ctrl, "gust_speed", ng)
        if palm_crown:
            _drive(md, "Stiffness", ctrl, "stiff_palm", ng); n_palm += 1
        else:
            _drive(md, "Stiffness", ctrl, "stiff_tree", ng)
            hid = next(i.identifier for i in ng.interface.items_tree if getattr(i, "in_out", None) == 'INPUT' and i.name == "Height Mode")
            getattr(md.properties.inputs, hid).value = 1.0
            href = next(i.identifier for i in ng.interface.items_tree if getattr(i, "in_out", None) == 'INPUT' and i.name == "Height Ref")
            getattr(md.properties.inputs, href).value = max(2.0, o.dimensions.z / max(o.scale.z, 1e-3))
            n_tree += 1
    return n_palm, n_tree


def _base(k):
    import re
    return re.sub(r"L\d$", "", k)


def scatter_wind(ctrl, tops=("SIO_veg_scatter",)):
    """Insert a tilt (Rotate Instances, local pivot = base) after each scatter layer's Instance on Points."""
    stiff = {"grass": "stiff_grass", "ground": "stiff_grass", "shrub": "stiff_shrub", "tree": "stiff_tree", "rock": None,
             "treemid": "stiff_tree", "treefar": "stiff_tree", "shrubfar": "stiff_shrub", "treebg": "stiff_tree"}
    gain = {"grass": 0.30, "ground": 0.18, "shrub": 0.10, "tree": 0.025, "treemid": 0.03, "treefar": 0.015, "shrubfar": 0.06, "treebg": 0.015}
    done = []
    keys = list(stiff)
    for t in tops:                                           # v6.5_OPT LOD layers ("treemidL1") inherit their base key
        for n in (bpy.data.node_groups[t].nodes if bpy.data.node_groups.get(t) else []):
            if n.type == 'GROUP' and n.node_tree and n.node_tree.name.startswith("SIO_veg_"):
                k = n.node_tree.name[len("SIO_veg_"):]
                if k not in keys and _base(k) in stiff:
                    keys.append(k)
    for key in keys:
        sprop = stiff[_base(key)]
        ng = bpy.data.node_groups.get(f"SIO_veg_{key}")
        if not ng or sprop is None or ng.nodes.get("sio_wind_rot"):
            continue
        N = ng.nodes; L = ng.links
        iop = next(n for n in N if n.type == 'INSTANCE_ON_POINTS')
        go = next(n for n in N if n.type == 'GROUP_OUTPUT')
        for s, dv in (("Strength", PROPS["strength"]), ("Stiffness", PROPS[sprop]), ("Gust Scale", PROPS["gust_scale"]),
                      ("Gust Speed", PROPS["gust_speed"]), ("Frequency", PROPS["gust_freq"])):
            if not any(getattr(i, "name", "") == s for i in ng.interface.items_tree):
                x = ng.interface.new_socket(s, in_out='INPUT', socket_type='NodeSocketFloat'); x.default_value = dv
        gi = next(n for n in N if n.type == 'GROUP_INPUT')
        def m(op, a, b=None):
            n = N.new("ShaderNodeMath"); n.operation = op
            for i, v in enumerate((a, b)):
                if v is None: continue
                if isinstance(v, (int, float)): n.inputs[i].default_value = v
                else: L.new(v, n.inputs[i])
            return n.outputs[0]
        t = N.new("GeometryNodeInputSceneTime").outputs["Seconds"]
        wdir = _wind_dir_nodes(N, L, ctrl)
        ipos = N.new("GeometryNodeInputPosition").outputs[0]
        vs = N.new("ShaderNodeVectorMath"); vs.operation = 'SCALE'; L.new(wdir, vs.inputs[0]); L.new(m('MULTIPLY', t, gi.outputs["Gust Speed"]), vs.inputs["Scale"])
        vsub = N.new("ShaderNodeVectorMath"); vsub.operation = 'SUBTRACT'; L.new(ipos, vsub.inputs[0]); L.new(vs.outputs[0], vsub.inputs[1])
        vdiv = N.new("ShaderNodeVectorMath"); vdiv.operation = 'SCALE'; L.new(vsub.outputs[0], vdiv.inputs[0]); L.new(m('DIVIDE', 1.0, gi.outputs["Gust Scale"]), vdiv.inputs["Scale"])
        gn = N.new("ShaderNodeTexNoise"); gn.inputs["Detail"].default_value = 1.0; L.new(vdiv.outputs[0], gn.inputs["Vector"])
        fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 0.35; fine.inputs["Detail"].default_value = 0.0
        vt = N.new("ShaderNodeVectorMath"); vt.operation = 'SCALE'; L.new(ipos, vt.inputs[0]); vt.inputs["Scale"].default_value = 1.0
        fine4 = fine; fine4.noise_dimensions = '4D'; L.new(vt.outputs[0], fine4.inputs["Vector"]); L.new(m('MULTIPLY', t, 1.3), fine4.inputs["W"])
        g = m('ADD', m('MULTIPLY', m('SUBTRACT', gn.outputs["Fac"], 0.35), 1.8), m('MULTIPLY', m('SUBTRACT', fine4.outputs["Fac"], 0.5), 0.8))
        ang = m('DIVIDE', m('MULTIPLY', m('MULTIPLY', g, gi.outputs["Strength"]), gain[_base(key)] / PROPS["strength"]), gi.outputs["Stiffness"])
        # rotation axis: perpendicular to the wind in XY -> tilt downwind
        axis = N.new("ShaderNodeVectorMath"); axis.operation = 'CROSS_PRODUCT'; axis.inputs[1].default_value = (0.0, 0.0, 1.0)
        L.new(wdir, axis.inputs[0])
        aa = N.new("FunctionNodeAxisAngleToRotation"); L.new(axis.outputs[0], aa.inputs["Axis"]); L.new(ang, aa.inputs["Angle"])
        rot = N.new("GeometryNodeRotateInstances"); rot.name = "sio_wind_rot"
        rot.inputs["Local Space"].default_value = False
        L.new(iop.outputs[0], rot.inputs["Instances"]); L.new(aa.outputs[0], rot.inputs["Rotation"])
        L.new(ipos, rot.inputs["Pivot Point"])
        L.new(rot.outputs[0], go.inputs[0])
        done.append(key)
    # drive the layer inputs from the controller (top-level scatter modifier exposes nothing -> drive the group nodes)
    for n in [n for t in tops if bpy.data.node_groups.get(t) for n in bpy.data.node_groups[t].nodes]:
        if n.type == 'GROUP' and n.node_tree and n.node_tree.name.startswith("SIO_veg_"):
            key = _base(n.node_tree.name[len("SIO_veg_"):])
            for s, prop in (("Strength", "strength"), ("Stiffness", stiff.get(key)), ("Gust Scale", "gust_scale"),
                            ("Gust Speed", "gust_speed"), ("Frequency", "gust_freq")):
                if prop and s in n.inputs:
                    fc = n.inputs[s].driver_add("default_value"); drv = fc.driver; drv.type = 'SUM'
                    v = drv.variables.new(); v.type = 'SINGLE_PROP'; v.targets[0].id_type = 'OBJECT'
                    v.targets[0].id = ctrl; v.targets[0].data_path = f'["{prop}"]'
    return done


def build(direction_deg=200.0):
    c = controller(direction_deg)
    p, t = add_deformers(c)
    s = scatter_wind(c)
    return dict(controller=c.name, palms=p, island_trees=t, scatter_layers=s)
