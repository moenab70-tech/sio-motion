"""Build a full character from a JSON preset: MPFB body + skin + body parts + clothes + Rigify rig.

    ch = character.build("engineer_m01", location=(0, 0, 0))
    ch.body, ch.rig, ch.parts["male_casualsuit01"], ch.preset
"""
import bpy
from . import util, materials

BODYPARTS = [("eyes", "Eyes"), ("eyebrows", "Eyebrows"), ("eyelashes", "Eyelashes"),
             ("teeth", "Teeth"), ("tongue", "Tongue")]


class Character:
    def __init__(self, preset, body, rig, parts):
        self.preset, self.body, self.rig, self.parts = preset, body, rig, parts
        self.name = preset["name"]

    @classmethod
    def from_scene(cls, name):
        body = bpy.data.objects[f"{name}_body"]
        rig = util.find_rig(body)
        parts = {o.get("sio_part", o.name): o for o in bpy.data.objects if o.get("sio_owner") == name}
        return cls(util.load_preset("characters", body["sio_preset"]), body, rig, parts)


def build(preset_name, location=(0, 0, 0), collection=None):
    P = util.load_preset("characters", preset_name)
    HS, RS = util.mpfb("HumanService"), util.mpfb("RigService")
    name = P["name"]
    coll = collection or util.ensure_collection(f"CHR_{name}")
    before = set(bpy.data.objects)

    body = HS.create_human(scale=0.1, macro_detail_dict=P["macro"], feet_on_ground=True)
    body.name = f"{name}_body"
    body["sio_preset"] = preset_name
    body.use_shape_key_edit_mode = True

    rig_name = P.get("rig", "rigify.human")
    HS.add_builtin_rig(body, rig_name, import_weights=True)
    HS.set_character_skin(util.mpfb_asset("skins", P["skin"], "mhmat"), body, skin_type=P.get("skin_type", "ENHANCED_SSS"))

    parts = {}
    for kind, atype in BODYPARTS:
        if P.get(kind):
            parts[P[kind]] = HS.add_mhclo_asset(util.mpfb_asset(kind, P[kind]), body, asset_type=atype,
                                                subdiv_levels=0, set_up_rigging=True)
    for c in P.get("clothes", []):
        parts[c] = HS.add_mhclo_asset(util.mpfb_asset("clothes", c), body, asset_type="Clothes",
                                      subdiv_levels=1, set_up_rigging=True)

    rig = util.find_rig(body)
    if rig_name.startswith("rigify."):
        for o in bpy.context.selected_objects:
            o.select_set(False)
        bpy.context.view_layer.objects.active = rig
        rig.select_set(True)
        gen = RS.generate_rigify_rig(rig, meta_rig_action="delete")
        rig = gen or util.find_rig(body)
    rig.name = f"{name}_rig"

    for o in set(bpy.data.objects) - before:
        o["sio_owner"] = name
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    for key, o in parts.items():
        if o and o.name in bpy.data.objects:
            o["sio_part"] = key
    rig.location = location
    # Rigify widget meshes are display shapes only: keep them out of renders and out of the character collection
    wgt = util.ensure_collection("SIO_rig_widgets")
    for o in list(coll.objects):
        if o.name.startswith("WGT-"):
            coll.objects.unlink(o)
            if o.name not in wgt.objects:
                wgt.objects.link(o)
            o.hide_render = True
    wgt.hide_render = True; wgt.hide_viewport = True
    if P.get("corrective_smooth"):
        # smooths joint collapse at neck/shoulders/elbows after the armature (rest shape from ORCO)
        cs = body.modifiers.new("SIO_corrective_smooth", 'CORRECTIVE_SMOOTH')
        cs.smooth_type = 'LENGTH_WEIGHTED'
        cs.factor = P["corrective_smooth"].get("factor", 0.5); cs.iterations = P["corrective_smooth"].get("iterations", 6)
        cs.use_only_smooth = False
        names = [m.name for m in body.modifiers]
        # MPFB chains two Armature modifiers (the second is a multi-modifier "PV" pass): go after the LAST one
        arm_i = max(i for i, m in enumerate(body.modifiers) if m.type == 'ARMATURE')
        with bpy.context.temp_override(object=body, active_object=body):
            bpy.ops.object.modifier_move_to_index(modifier=cs.name, index=arm_i + 1)
        # bind the rest shape in the rest pose (keeps MPFB shape-key detail, unlike ORCO)
        rig.data.pose_position = 'REST'; bpy.context.view_layer.update()
        cs.rest_source = 'BIND'
        with bpy.context.temp_override(object=body, active_object=body):
            bpy.ops.object.correctivesmooth_bind(modifier=cs.name)
        rig.data.pose_position = 'POSE'; bpy.context.view_layer.update()

    ch = Character(P, body, rig, {k: v for k, v in parts.items() if v and v.name in bpy.data.objects})
    materials.apply_character_looks(ch)
    if P.get("material_polish"):
        materials.polish(ch, P["material_polish"])
    if P.get("rigid_skull"):
        from . import rig as rig_mod
        rig_mod.rigid_skull(body, P["rigid_skull"])
    if P.get("skin_realism"):
        materials.skin_realism(ch, P["skin_realism"])
    return ch
