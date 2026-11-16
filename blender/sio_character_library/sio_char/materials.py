"""Reusable looks: skin tint, eyes, brows, hair strands, scalp cap, and a toon (cel) conversion.

Two render styles share the same character:
  - cinematic: MPFB Enhanced SSS skin + Principled hair (Eevee/Cycles)
  - toon:      materials.stylize_toon(objects)  -> Shader-to-RGB cel bands + inverted-hull outline (Eevee)
"""
import bpy
from . import util


def _group_input(mat, name, value):
    if not mat or not mat.use_nodes:
        return False
    for n in mat.node_tree.nodes:
        if n.type == 'GROUP' and name in n.inputs:
            n.inputs[name].default_value = value
            return True
    return False


def apply_character_looks(ch):
    P = ch.preset
    t = P.get("skin_tint")
    for s in ch.body.material_slots:
        m = s.material
        if t and m and any(k in m.name for k in ("body", "ears", "lips")):
            _group_input(m, "colorMixIn", (*t["color"], 1.0))
            _group_input(m, "colorMixInStrength", t["strength"])
            if "brightness" in t:
                _group_input(m, "Brightness", t["brightness"])
    for o in ch.parts.values():
        for s in o.material_slots:
            m = s.material
            if not m:
                continue
            if P.get("eye_color") and ("high-poly" in o.name or "low-poly" in o.name):
                _tint_eye(m, P["eye_color"])
            if any(k in o.name for k in ("eyebrow",)) and P.get("hair_color"):
                _darken(m, 0.25)


def _tint_eye(m, rgb):
    """MPFB eye textures are generic; multiply the iris colour toward the preset colour."""
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf or not bsdf.inputs["Base Color"].links or nt.nodes.get("sio_eye_tint"):
        return
    src = bsdf.inputs["Base Color"].links[0].from_socket
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.name = "sio_eye_tint"
    hsv.inputs["Saturation"].default_value = 0.0
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs["Factor"].default_value = 0.85
    mix.inputs[7].default_value = (rgb[0] * 3, rgb[1] * 3, rgb[2] * 3, 1)
    nt.links.new(src, hsv.inputs["Color"]); nt.links.new(hsv.outputs[0], mix.inputs[6])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])


def _darken(m, value):
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf or nt.nodes.get("sio_darken"):
        return
    h = nt.nodes.new("ShaderNodeHueSaturation"); h.name = "sio_darken"; h.inputs["Value"].default_value = value
    if bsdf.inputs["Base Color"].links:
        nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, h.inputs["Color"])
    else:
        h.inputs["Color"].default_value = bsdf.inputs["Base Color"].default_value
    nt.links.new(h.outputs[0], bsdf.inputs["Base Color"])


def hair_material(ch, H):
    col = ch.preset.get("hair_color", (0.03, 0.022, 0.018))
    name = f"{ch.name}_hair"
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Roughness"].default_value = 0.62
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.25
    if "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = 0.0
    info = nt.nodes.new("ShaderNodeHairInfo")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    k = H.get("color_tip_mult", 1.5)
    ramp.color_ramp.elements[0].color = (col[0] * 0.8, col[1] * 0.8, col[2] * 0.8, 1)
    ramp.color_ramp.elements[1].color = (col[0] * k, col[1] * k, col[2] * k, 1)
    nt.links.new(info.outputs["Intercept"], ramp.inputs[0])
    # per-strand random value variation
    rnd = nt.nodes.new("ShaderNodeMath"); rnd.operation = 'MULTIPLY_ADD'
    rnd.inputs[1].default_value = 0.35; rnd.inputs[2].default_value = 0.82
    nt.links.new(info.outputs["Random"], rnd.inputs[0])
    mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs["Factor"].default_value = 1
    nt.links.new(ramp.outputs[0], mul.inputs[6]); nt.links.new(rnd.outputs[0], mul.inputs[7])
    nt.links.new(mul.outputs[2], b.inputs["Base Color"])
    nt.links.new(b.outputs[0], out.inputs[0])
    hp = ch.preset.get("material_polish", {}).get("hair")
    if hp:
        b.inputs["Roughness"].default_value = hp.get("roughness", b.inputs["Roughness"].default_value)
        for k in ("Specular IOR Level", "Specular"):
            if k in b.inputs and "specular" in hp:
                b.inputs[k].default_value = hp["specular"]
    return m


def cap_material(ch, H):
    col = ch.preset.get("hair_color", (0.03, 0.022, 0.018))
    a = H["scalp_cap"].get("alpha", 1.0)
    name = f"{ch.name}_cap_{H['name']}"
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (col[0] * 0.9, col[1] * 0.9, col[2] * 0.9, 1)
    b.inputs["Roughness"].default_value = 0.7
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "hair_w"
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.15; mr.inputs["From Max"].default_value = 0.85
    mr.inputs["To Max"].default_value = a
    nt.links.new(at.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs[0], b.inputs["Alpha"])
    nt.links.new(b.outputs[0], out.inputs[0])
    try:
        m.surface_render_method = 'DITHERED'
    except Exception:
        pass
    return m


# ------------------------------------------------------------------ toon style
def stylize_toon(objects, shadow=(0.42, 0.32, 0.52), outline=0.0016, outline_color=(0.08, 0.05, 0.05)):
    """Convert materials to 3-band cel shading (Eevee) and add an inverted-hull outline.

    Keeps each material's base colour/texture; lighting is quantised through Shader-to-RGB.
    Non-destructive: the original output is kept on a muted 'cinematic' Material Output.
    """
    ink = bpy.data.materials.get("SIO_Ink") or bpy.data.materials.new("SIO_Ink")
    ink.use_nodes = True
    ink.use_backface_culling = True
    e = next((n for n in ink.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if e:
        e.inputs["Base Color"].default_value = (*outline_color, 1); e.inputs["Roughness"].default_value = 1
    done = set()
    for ob in objects:
        if ob.type not in ('MESH', 'CURVES'):
            continue
        if any(k in ob.name for k in ("high-poly", "low-poly", "eyelash")):
            continue                                  # keep the layered eye/cornea shaders
        if ob.type == 'CURVES':
            for m in ob.data.materials:
                if m and m.name not in done:
                    _cel(m, shadow); done.add(m.name)
            continue
        for s in ob.material_slots:
            m = s.material
            if m and m.name not in done and m.use_nodes and m.name != "SIO_Ink":
                _cel(m, shadow); done.add(m.name)
        if outline and not ob.modifiers.get("SIO_Outline"):
            ob.data.materials.append(ink)
            sol = ob.modifiers.new("SIO_Outline", 'SOLIDIFY')
            sol.thickness = -outline; sol.offset = 1; sol.use_flip_normals = True
            sol.material_offset = len(ob.data.materials) - 1; sol.use_rim = False
    return done


def _base_color_socket(nt):
    b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if b:
        return (b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None,
                tuple(b.inputs["Base Color"].default_value))
    g = next((n for n in nt.nodes if n.type == 'GROUP'), None)
    if g:  # MPFB skin group: reuse its diffuse texture
        tex = next((n for n in g.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image and "diffuse" in n.image.name.lower()), None)
        if tex:
            t = nt.nodes.new("ShaderNodeTexImage"); t.image = tex.image
            return t.outputs["Color"], (0.8, 0.6, 0.5, 1)
    return None, (0.8, 0.8, 0.8, 1)


def _cel(m, shadow):
    nt = m.node_tree
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None)
    if not out or nt.nodes.get("sio_cel") or not out.inputs["Surface"].links:
        return
    shader = out.inputs["Surface"].links[0].from_socket
    base_sock, base_val = _base_color_socket(nt)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB"); s2r.name = "sio_cel"
    nt.links.new(shader, s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(s2r.outputs[0], bw.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = 'CONSTANT'
    el = ramp.color_ramp.elements
    el[0].position = 0.0; el[0].color = (*shadow, 1)
    el[1].position = 0.08; el[1].color = (0.82, 0.74, 0.72, 1)
    e3 = el.new(0.32); e3.color = (1.08, 1.0, 0.95, 1)
    nt.links.new(bw.outputs[0], ramp.inputs[0])
    mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs["Factor"].default_value = 1
    if base_sock:
        nt.links.new(base_sock, mul.inputs[6])
    else:
        mul.inputs[6].default_value = base_val
    nt.links.new(ramp.outputs[0], mul.inputs[7])
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mul.outputs[2], em.inputs[0])
    toon_out = nt.nodes.new("ShaderNodeOutputMaterial"); toon_out.name = "sio_toon_output"
    nt.links.new(em.outputs[0], toon_out.inputs["Surface"])
    toon_out.is_active_output = True


# ------------------------------------------------------------------ v2.1 polish (preset key "material_polish")
def polish(ch, spec):
    """Small, measured material refinements (no new textures):
    skin  -> less clearcoat (no plastic sheen), slightly rougher, a bit more subsurface
    cloth -> cotton sheen, matte roughness, softer normal map
    hair  -> roughness / specular for natural highlights."""
    sk = spec.get("skin", {})
    for s in ch.body.material_slots:
        m = s.material
        if m and any(k in m.name for k in ("body", "ears", "lips")):
            for key, name in (("clearcoat", "Clearcoat"), ("roughness", "Roughness"), ("sss", "SSS strength"),
                              ("pore_strength", "Pore strength")):
                if key in sk:
                    _group_input(m, name, sk[key])
    cl = spec.get("cloth", {})
    for o in ch.parts.values():
        if not any(k in o.name for k in ("suit", "shoes", "shirt", "pants")):
            continue
        for s in o.material_slots:
            m = s.material
            if not m or not m.use_nodes:
                continue
            b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if not b:
                continue
            shoes = "shoes" in o.name
            if "roughness" in cl and not shoes and not b.inputs["Roughness"].links:
                b.inputs["Roughness"].default_value = cl["roughness"]
            if "sheen" in cl and not shoes:
                for k in ("Sheen Weight", "Sheen"):
                    if k in b.inputs:
                        b.inputs[k].default_value = cl["sheen"]
                if "Sheen Roughness" in b.inputs:
                    b.inputs["Sheen Roughness"].default_value = 0.5
            nm = next((n for n in m.node_tree.nodes if n.type == 'NORMAL_MAP'), None)
            if nm and "normal_strength" in cl:
                nm.inputs["Strength"].default_value = cl["normal_strength"]
    hr = spec.get("hair", {})
    m = bpy.data.materials.get(f"{ch.name}_hair")
    if m and hr:
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b:
            if "roughness" in hr:
                b.inputs["Roughness"].default_value = hr["roughness"]
            for k in ("Specular IOR Level", "Specular"):
                if k in b.inputs and "specular" in hr:
                    b.inputs[k].default_value = hr["specular"]


# ------------------------------------------------------------------ v2.3 skin realism (procedural, on the MPFB skin)
def skin_realism(ch, spec):
    """Upgrade the MPFB Enhanced-SSS skin group in place (per character) - no environment textures:
      - pores: Voronoi pits (scale ~ pores/m) + the existing fine noise bump, object-space so density is real
      - micro roughness variation (noise) instead of one flat roughness -> breaks the plastic sheen
      - low-frequency colour variation (redness/blotches) + very fine pigment noise, both a few % only
      - physically sized subsurface radius (red > green > blue, mm range) and lower specular
    spec keys (all optional): pores, pore_depth, rough_min, rough_max, color_var, sss_weight, sss_radius_mm, specular."""
    targets = [s.material for s in ch.body.material_slots if s.material and any(k in s.material.name for k in ("body", "ears", "lips"))]
    done = set()
    for m in targets:
        g = next((n for n in m.node_tree.nodes if n.type == 'GROUP'), None)
        if not g or g.node_tree.name in done:
            continue
        lips = "lips" in m.name
        _skin_tree(g.node_tree, spec, lips)
        done.add(g.node_tree.name)
        for key, name in (("sss_weight_input", "SSS strength"),):
            if key in spec and name in g.inputs:
                g.inputs[name].default_value = spec[key]
    return done


def _skin_tree(nt, spec, lips=False):
    if nt.nodes.get("sio_skin_v23"):
        return
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    marker = nt.nodes.new("NodeFrame"); marker.name = "sio_skin_v23"; marker.label = "SIO skin v2.3"
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # --- colour variation on top of the diffuse chain
    base_link = b.inputs["Base Color"].links[0]
    src = base_link.from_socket
    nlow = nt.nodes.new("ShaderNodeTexNoise"); nlow.inputs["Scale"].default_value = 9.0; nlow.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], nlow.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cv = spec.get("color_var", 0.06)
    ramp.color_ramp.elements[0].color = (1.0 + cv * 0.6, 1.0 - cv * 0.4, 1.0 - cv * 0.5, 1)   # slightly redder
    ramp.color_ramp.elements[1].color = (1.0 - cv * 0.3, 1.0 - cv * 0.15, 1.0 - cv * 0.1, 1)  # slightly cooler/paler
    nt.links.new(nlow.outputs["Fac"], ramp.inputs[0])
    nfine = nt.nodes.new("ShaderNodeTexNoise"); nfine.inputs["Scale"].default_value = 900.0
    nt.links.new(tc.outputs["Object"], nfine.inputs["Vector"])
    fr = nt.nodes.new("ShaderNodeMapRange"); fr.inputs["To Min"].default_value = 1.0 - cv * 0.5; fr.inputs["To Max"].default_value = 1.0
    nt.links.new(nfine.outputs["Fac"], fr.inputs["Value"])
    m1 = nt.nodes.new("ShaderNodeMix"); m1.data_type = 'RGBA'; m1.blend_type = 'MULTIPLY'; m1.inputs["Factor"].default_value = 1
    nt.links.new(src, m1.inputs[6]); nt.links.new(ramp.outputs[0], m1.inputs[7])
    m2 = nt.nodes.new("ShaderNodeMix"); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'; m2.inputs["Factor"].default_value = 1
    nt.links.new(m1.outputs[2], m2.inputs[6]); nt.links.new(fr.outputs[0], m2.inputs[7])
    nt.links.new(m2.outputs[2], b.inputs["Base Color"])
    # --- roughness variation (replaces the flat group-input roughness)
    nr = nt.nodes.new("ShaderNodeTexNoise"); nr.inputs["Scale"].default_value = spec.get("rough_scale", 60.0); nr.inputs["Detail"].default_value = 3
    nt.links.new(tc.outputs["Object"], nr.inputs["Vector"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = spec.get("rough_min", 0.42) + (0.05 if lips else 0)
    rr.inputs["To Max"].default_value = spec.get("rough_max", 0.62)
    nt.links.new(nr.outputs["Fac"], rr.inputs["Value"])
    for l in list(b.inputs["Roughness"].links):
        nt.links.remove(l)
    nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    # --- pores: Voronoi pits feeding a second bump stacked on the existing normal chain
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = 'F1'
    vor.inputs["Scale"].default_value = spec.get("pores", 1400.0) * (0.6 if lips else 1.0)
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    pr = nt.nodes.new("ShaderNodeMapRange"); pr.inputs["From Max"].default_value = 0.35
    nt.links.new(vor.outputs["Distance"], pr.inputs["Value"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = spec.get("pore_depth", 0.18) * (0.5 if lips else 1.0)
    bump.inputs["Distance"].default_value = spec.get("pore_distance", 0.0004)
    nt.links.new(pr.outputs[0], bump.inputs["Height"])
    if b.inputs["Normal"].links:
        nt.links.new(b.inputs["Normal"].links[0].from_socket, bump.inputs["Normal"])
    nt.links.new(bump.outputs[0], b.inputs["Normal"])
    if spec.get("relief"):          # mid-frequency skin relief (fine creases / unevenness) stacked on the pores
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 220.0; nz.inputs["Detail"].default_value = 6
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        b2 = nt.nodes.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = spec["relief"] * (0.5 if lips else 1.0)
        b2.inputs["Distance"].default_value = 0.001
        nt.links.new(nz.outputs["Fac"], b2.inputs["Height"]); nt.links.new(bump.outputs[0], b2.inputs["Normal"])
        nt.links.new(b2.outputs[0], b.inputs["Normal"])
    # --- subsurface: physically sized radius, specular
    rad = spec.get("sss_radius_mm", (3.6, 1.4, 0.7))
    for l in list(b.inputs["Subsurface Radius"].links):
        nt.links.remove(l)
    b.inputs["Subsurface Radius"].default_value = rad
    if "Subsurface Scale" in b.inputs:
        b.inputs["Subsurface Scale"].default_value = 0.001          # radius given in millimetres
    if "sss_weight" in spec:
        for l in list(b.inputs["Subsurface Weight"].links):
            nt.links.remove(l)
        b.inputs["Subsurface Weight"].default_value = spec["sss_weight"]
    for k in ("Specular IOR Level",):
        if k in b.inputs:
            b.inputs[k].default_value = spec.get("specular", 0.38)
