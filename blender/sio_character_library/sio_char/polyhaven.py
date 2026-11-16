"""Poly Haven (CC0) materials and HDRIs, two routes:

A) Live session via Blender MCP (search_assets / import_asset). NOTE: the MCP add-on stores downloads in the
   macOS temp folder and its "use Poly Haven" switch is a per-scene property, so after creating/opening a file:
       bpy.context.scene.blendermcp_use_polyhaven = True
   and after importing, call persist() so the .blend never points into /var/folders/.../T/.
B) Headless / no MCP: material("denim_fabric_05", res="1k") and hdri("poly_haven_studio") download once into the
   shared cache (CACHE) with retries, then build the shader. Re-runs reuse the cache (no network).
"""
import json, os, shutil, time, urllib.request
import bpy

CACHE = "/Users/mohammadalqurain/Documents/Remotion-MotionGraphics/src/videos/hasad-2026/opening/blender/v3/polyhaven_cache"
UA = {"User-Agent": "sio-blender-library"}
MAPS = {"Diffuse": ("diff", "sRGB"), "Rough": ("rough", "Non-Color"), "nor_gl": ("nor_gl", "Non-Color"),
        "Displacement": ("disp", "Non-Color"), "AO": ("ao", "Non-Color")}


def _get(url, timeout=60, tries=8):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception:
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"download failed after {tries} tries: {url}")


def _download(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = _get(url, timeout=120)
    with open(path + ".part", "wb") as f:
        f.write(data)
    os.replace(path + ".part", path)
    return path


def files(asset_id):
    p = os.path.join(CACHE, "_api", f"{asset_id}.json")
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(_get(f"https://api.polyhaven.com/files/{asset_id}", timeout=30))
    return json.load(open(p))


def info(asset_id):
    p = os.path.join(CACHE, "_api", f"{asset_id}_info.json")
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(_get(f"https://api.polyhaven.com/info/{asset_id}", timeout=30))
    return json.load(open(p))


def material(asset_id, res="1k", name=None, displacement=False):
    """Principled material from cached Poly Haven maps. Mapping uses object-space metres scaled to the
    asset's real-world size, so it tiles at life size on any object (no UV dependency)."""
    F = files(asset_id)
    size_m = (info(asset_id).get("dimensions") or [1000])[0] / 1000.0
    m = bpy.data.materials.get(name or f"PH_{asset_id}")
    if m:
        return m
    m = bpy.data.materials.new(name or f"PH_{asset_id}"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs[0], out.inputs[0])
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / size_m, 1 / size_m, 1 / size_m)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    for key, (short, cs) in MAPS.items():
        if key not in F or (key == "Displacement" and not displacement):
            continue
        entry = F[key].get(res) or F[key][sorted(F[key])[0]]
        fmt = "jpg" if "jpg" in entry else sorted(entry)[0]
        url = entry[fmt]["url"]
        path = _download(url, os.path.join(CACHE, "textures", asset_id, os.path.basename(url)))
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path, check_existing=True)
        t.image.colorspace_settings.name = cs; t.projection = 'BOX'; t.projection_blend = 0.25
        nt.links.new(mp.outputs[0], t.inputs[0])
        if key == "Diffuse":
            nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
        elif key == "Rough":
            nt.links.new(t.outputs["Color"], b.inputs["Roughness"])
        elif key == "nor_gl":
            nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(t.outputs["Color"], nm.inputs["Color"])
            nt.links.new(nm.outputs[0], b.inputs["Normal"])
        elif key == "Displacement":
            d = nt.nodes.new("ShaderNodeDisplacement"); d.inputs["Scale"].default_value = 0.002
            nt.links.new(t.outputs["Color"], d.inputs["Height"]); nt.links.new(d.outputs[0], out.inputs["Displacement"])
    m["polyhaven"] = f"https://polyhaven.com/a/{asset_id} (CC0)"
    return m


def hdri(asset_id, res="1k", strength=1.0, scene=None):
    F = files(asset_id)
    entry = F["hdri"].get(res) or F["hdri"][sorted(F["hdri"])[0]]
    url = entry["hdr"]["url"]
    path = _download(url, os.path.join(CACHE, "hdris", os.path.basename(url)))
    sc = scene or bpy.context.scene
    w = sc.world or bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(path, check_existing=True)
    bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = strength
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(env.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])
    w["polyhaven"] = f"https://polyhaven.com/a/{asset_id} (CC0)"
    return w


def fix_mcp_material(m, bump_strength=0.6):
    """MCP-imported materials wire the height map into Material Output > Displacement; Eevee/Cycles then
    displace real geometry (crumpled surfaces). Keep the detail as bump only."""
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    for l in list(out.inputs["Displacement"].links):
        nt.links.remove(l)
    try:
        m.displacement_method = 'BUMP'
    except Exception:
        pass
    nm = next((n for n in nt.nodes if n.type == 'NORMAL_MAP'), None)
    if nm:
        nm.inputs["Strength"].default_value = bump_strength
    return m


def persist(dest=CACHE):
    """Copy every image the MCP add-on left in the temp folder into the cache and repoint the .blend to it."""
    """(The add-on packs its downloads into the .blend and deletes the temp copy; this writes them to the shared
    cache instead, so files stay small and every project reuses the same maps.)"""
    moved = []
    for img in bpy.data.images:
        fp = bpy.path.abspath(img.filepath)
        if "blender_mcp_polyhaven" not in fp:
            continue
        sub = "hdris" if fp.lower().endswith((".hdr", ".exr")) else os.path.join("textures", "_mcp")
        target = os.path.join(dest, sub, os.path.basename(fp))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if not os.path.exists(target):
            if os.path.exists(fp):
                shutil.copy2(fp, target)
            elif img.packed_file:
                with open(target, "wb") as f:
                    f.write(img.packed_file.data)
            else:
                continue
        if img.packed_file:
            img.unpack(method='REMOVE')
        img.filepath = target
        img.reload()
        moved.append(target)
    return moved
