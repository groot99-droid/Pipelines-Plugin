"""Build the add-on manifests from the add-ons' published zips.

    python blender-addons/build_manifests.py <folder of zips>

The zips are the ones extensions.blender.org serves (each one's sha256 is in
sources.json). They are read with `ast` and `zipfile` only: nothing in them is
extracted, imported or run. CURATED says which operators become tools, NAMES and
OVERRIDES what a tool is called and which parameters it takes when the source
alone does not say. The manifests and sources.json are rewritten; review the diff.
"""

import ast
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
import warnings

if sys.version_info < (3, 11):
    sys.exit("build_manifests.py needs Python 3.11 or later (tomllib)")
import tomllib  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "plugins" / "blender" / "addon-tools"))
import server  # noqa: E402


PROPS = {"BoolProperty", "IntProperty", "FloatProperty", "StringProperty", "EnumProperty",
         "FloatVectorProperty", "IntVectorProperty", "BoolVectorProperty", "PointerProperty", "CollectionProperty"}


def lit(node):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def callname(node):
    f = node.func
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)


def prop(name, call):
    kind = callname(call)
    p = {"identifier": name, "kind": kind}
    for kw in call.keywords:
        if kw.arg in ("name", "description", "default", "min", "max", "soft_min", "soft_max", "size", "options", "subtype"):
            v = lit(kw.value)
            p[kw.arg] = sorted(v) if isinstance(v, set) else v
        elif kw.arg == "items":
            v = lit(kw.value)
            p["items"] = [i[0] for i in v] if isinstance(v, (list, tuple)) else "dynamic"
    return p


def parse(source):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(source)


def classes_in(tree, path):
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        attrs, props, methods = {}, [], set()
        for item in node.body:
            if isinstance(item, ast.Assign) and len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
                attrs[item.targets[0].id] = lit(item.value)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) \
                    and isinstance(item.annotation, ast.Call) and callname(item.annotation) in PROPS:
                props.append(prop(item.target.id, item.annotation))
            elif isinstance(item, ast.FunctionDef):
                methods.add(item.name)
        bases = [b.attr if isinstance(b, ast.Attribute) else getattr(b, "id", "") for b in node.bases]
        yield dict(cls=node.name, bases=bases, file=path, attrs=attrs, props=props, methods=sorted(methods),
                   doc=(ast.get_docstring(node) or "").strip())


def read_zip(zpath):
    z = zipfile.ZipFile(zpath)
    out = {"zip": Path(zpath).stem, "operators": [], "panels": [], "manifest": {}}
    for n in z.namelist():
        if n.endswith("blender_manifest.toml"):
            m = tomllib.loads(z.read(n).decode("utf-8"))
            out["manifest"] = {k: m.get(k) for k in ("id", "name", "version", "license")}
    for n in z.namelist():
        if not n.endswith(".py"):
            continue
        try:
            tree = parse(z.read(n).decode("utf-8", "replace"))
        except SyntaxError:
            continue
        for c in classes_in(tree, n):
            a = c["attrs"]
            if isinstance(a.get("bl_idname"), str) and "." in a["bl_idname"] and "Panel" not in " ".join(c["bases"]) \
                    and not any(b in ("Menu", "Header", "UIList", "PropertyGroup", "AddonPreferences") for b in c["bases"]):
                out["operators"].append(dict(idname=a["bl_idname"], label=a.get("bl_label"),
                    description=a.get("bl_description") or c["doc"], options=sorted(a["bl_options"]) if isinstance(a.get("bl_options"), set) else a.get("bl_options"),
                    methods=c["methods"], props=c["props"], file=c["file"], cls=c["cls"], bases=c["bases"]))
            elif "bl_space_type" in a:
                out["panels"].append(dict(label=a.get("bl_label"), space=a.get("bl_space_type"), region=a.get("bl_region_type"), category=a.get("bl_category")))
    return out


CURATED = {
 "act_game_asset_creation_toolset": "object.act_export object.act_create_palette object.act_delete_unused_materials object.act_delete_duplicated_materials object.act_align object.act_clear_normals object.act_calc_normals object.act_obj_name_to_mesh_name object.act_collection_name_to_obj_name object.act_select_negative_scaled_objects object.act_cleanup_empties object.act_numbering object.act_lod_to_objname object.act_remove_lod_from_objname object.act_uv_clear object.act_uv_add object.act_mark_seams_from_uv object.act_material_to_viewport object.act_random_viewport_color object.act_clear_vc",
 "asset_optimizer": "mesh.batch_optimize mesh.dual_uv_unwrap mesh.generate_lods mesh.auto_decimate mesh.smart_vertex_merge",
 "auto_scale_fps": "anim.enable_auto_fps_scale anim.disable_auto_fps_scale",
 "bake_to_single_material": "object.bake_to_single_material",
 "cad2cube": "import_scene.cad2cube_dxf",
 "easy_arrangement": "object.easy_arrangement_apply object.easy_arrangement_reset",
 "easy_clouds": "easyclouds.create_cloud easyclouds.create_layer easyclouds.create_sphere",
 "easy_pivot": "msp.bake_pivot msp.reset_pivot msp.pivot_to_active",
 "easy_tree": "object.add_tree_tool object.hide_tree_leaves object.show_tree_leaves",
 "easymesh_batch_exporter": "mesh.batch_export mesh.load_export_preset mesh.clear_export_indicators",
 "formula_to_nodes": "node.formula_generate node.formula_generate_script node.formula_check",
 "io_scene_psk_psa": "psk.import_file psa.import_all psk.export psa.export",
 "marchingcube": "mesh.primitive_marching_cube_add",
 "ns_toolkit_mesh_cleanup_pro": "object.tris_to_quads_merge ns_toolkit.highlight_topology ns_toolkit.clear_highlight",
 "omi_physics_body_gltf_extension": "object.omi_physics_auto_fit object.omi_physics_bake_scale object.omi_physics_validate_scene object.omi_physics_reset_defaults",
 "photo_relief": "photo_relief.create",
 "proto_game_asset_tools": "prototools.batch_export prototools.quick_export_mesh prototools.quick_export_mesh_and_animations prototools.quick_export_allactions prototools.quick_export_curaction prototools.apply_all_modifiers_keep_shape_keys prototools.apply_active_modifier_keep_shape_keys prototools.vertex_group_to_vertex_color prototools.fill_vertex_color prototools.timelinetoaction",
 "step_importer": "import_scene.step step.cleanup_selected",
 "terrainmixer": "object.replace_with_terrain object.add_tm_world object.fix_clipping_distance terrainmixer.render_with_baking_settings terrainmixer.setup_asset_library",
 "texture_pipeline_studio": "tps.run tps.convert_to_udim tps.lod_swap",
 "topology_doctor": "mesh.analyze_topo_ultimate",
 "ue_groom_importer": "import_scene.unreal_groom",
 "SuperDuperBatchExporter": "export_mesh.batch batch_export.list_add batch_export.list_add_collection batch_export.clear_list",
}
# Short tool-name prefixes (tool names are at most 48 characters).
PREFIX = {"act_game_asset_creation_toolset": "act", "asset_optimizer": "optimizer", "auto_scale_fps": "fps",
 "bake_to_single_material": "bake", "cad2cube": "cad2cube", "easy_arrangement": "arrange", "easy_clouds": "clouds",
 "easy_pivot": "pivot", "easy_tree": "tree", "easymesh_batch_exporter": "easymesh", "formula_to_nodes": "formula",
 "io_scene_psk_psa": "unreal", "marchingcube": "marching", "ns_toolkit_mesh_cleanup_pro": "cleanup",
 "omi_physics_body_gltf_extension": "omi", "photo_relief": "relief", "proto_game_asset_tools": "proto",
 "step_importer": "step", "terrainmixer": "terrain", "texture_pipeline_studio": "tps", "topology_doctor": "topo",
 "ue_groom_importer": "groom", "SuperDuperBatchExporter": "sdbe"}
# Hand-set parameters, read from each operator's execute(): (zip, op) -> {param: spec or None to drop}
OVERRIDES = {
 ("act_game_asset_creation_toolset", "object.act_align"): {
   "mode": {"type": "string", "enum": ["MIN", "MAX", "MID", "CURSOR", "COORDINATE"], "required": True,
            "description": "Where the origin goes along the axis (COORDINATE uses the panel's coordinate)"},
   "axis": {"type": "string", "enum": ["X", "Y", "Z"], "required": True}},
 # The file browser's folder and file list; filepath names the one file.
 ("cad2cube", "import_scene.cad2cube_dxf"): {"directory": None, "files": None},
 ("io_scene_psk_psa", "psk.import_file"): {"bdk_repository_id": None},
}
NAMES = {"psk.import_file": "unreal_psk_import", "psa.import_all": "unreal_psa_import_all",
 "psk.export": "unreal_psk_export", "psa.export": "unreal_psa_export",
 "object.hide_tree_leaves": "tree_hide_leaves", "object.show_tree_leaves": "tree_show_leaves",
 "object.add_tree_tool": "tree_add", "mesh.analyze_topo_ultimate": "topo_analyze",
 "import_scene.cad2cube_dxf": "cad2cube_import_dxf", "import_scene.step": "step_import",
 "import_scene.unreal_groom": "groom_import", "mesh.primitive_marching_cube_add": "marching_cube_add",
 "photo_relief.create": "relief_create", "object.bake_to_single_material": "bake_to_single_material",
 "export_mesh.batch": "sdbe_export", "tps.run": "tps_assign_textures",
 "terrainmixer.render_with_baking_settings": "terrain_bake", "object.replace_with_terrain": "terrain_replace_with_terrain"}
FILE_OPS = {"ImportHelper": "The file to import (absolute path)", "ExportHelper": "The file to write (absolute path)"}
KIND = {"BoolProperty": "BOOLEAN", "IntProperty": "INT", "FloatProperty": "FLOAT", "StringProperty": "STRING",
        "EnumProperty": "ENUM", "FloatVectorProperty": "FLOAT", "IntVectorProperty": "INT", "BoolVectorProperty": "BOOLEAN",
        "PointerProperty": "POINTER", "CollectionProperty": "COLLECTION"}


def all_classes(z):
    out = {}
    for n in z.namelist():
        if n.endswith(".py"):
            try:
                tree = parse(z.read(n).decode("utf-8", "replace"))
            except SyntaxError:
                continue
            for c in classes_in(tree, n):
                out.setdefault(c["cls"], c)
    return out


def props_of(cls, classes, seen=()):
    """The class's properties, with those of base classes from the same add-on first."""
    props = {}
    for b in cls["bases"]:
        if b in classes and b not in seen:
            props.update(props_of(classes[b], classes, seen + (b,)))
    props.update({p["identifier"]: p for p in cls["props"]})
    return props


def to_rna(p):
    kind = KIND.get(p["kind"])
    if kind is None:
        return None
    r = {"identifier": p["identifier"], "type": kind, "name": p.get("name") or "",
         "description": p.get("description") or "", "hidden": "HIDDEN" in (p.get("options") or [])}
    if kind == "ENUM":
        items = p.get("items")
        r["items"] = items if isinstance(items, list) else []
        r["flag"] = "ENUM_FLAG" in (p.get("options") or [])
    if p["kind"].endswith("VectorProperty"):
        r["array_length"] = p.get("size") if isinstance(p.get("size"), int) else 3
    for k in ("min", "max"):
        if isinstance(p.get(k), (int, float)) and not isinstance(p.get(k), bool):
            r[k] = p[k]
    if "default" in p and p["default"] is not None:
        d = p["default"]
        r["default"] = list(d) if isinstance(d, tuple) else d
        if kind == "ENUM" and r.get("flag") and isinstance(d, list):
            r["default"] = sorted(d)
    return r


def build(zips, out):
    """Write one manifest per curated add-on into out/manifests, and out/sources.json."""
    previous = json.loads((out / "sources.json").read_text()) if (out / "sources.json").exists() else {}
    (out / "manifests").mkdir(parents=True, exist_ok=True)
    sources = {}
    for zid, ops in CURATED.items():
        zpath = zips / f"{zid}.zip"
        z = zipfile.ZipFile(zpath)
        info = read_zip(zpath)
        classes = all_classes(z)
        panels = [p["space"] for p in info["panels"] if p.get("space") in server.CONTEXTS]
        ctx = max(set(panels), key=panels.count) if panels else None
        tools = []
        for opname in ops.split():
            op = next(o for o in info["operators"] if o["idname"] == opname)
            cls = classes[op["cls"]]
            params = {}
            for helper, desc in FILE_OPS.items():
                if helper in op["bases"]:
                    params["filepath"] = {"type": "string", "description": desc, "required": True}
            for ident, p in props_of(cls, classes).items():
                if ident in params or ident == "filter_glob":
                    continue
                rna = to_rna(p)
                spec = server.draft_param(rna) if rna else None
                if spec is not None and server.TOOL_NAME.match(ident):
                    params[ident] = spec
            if "filepath" in params:
                params["filepath"]["required"] = True
                params["filepath"].pop("default", None)
            for ident, spec in OVERRIDES.get((zid, opname), {}).items():
                if spec is None:
                    params.pop(ident, None)
                else:
                    params[ident] = spec
            base = re.sub(r"[^a-z0-9_]+", "_", opname.split(".", 1)[1].lower()).strip("_")
            base = re.sub(rf"^({PREFIX[zid]}_|act_|omi_physics_|easy_arrangement_|primitive_)", "", base)
            name = NAMES.get(opname) or f"{PREFIX[zid]}_{base}"[:48].rstrip("_")
            label = (op["label"] or "").strip().rstrip(".").strip()
            desc = (op["description"] or "").strip()
            text = label if not desc or desc.lower() == label.lower() else f"{label}: {desc}"
            if not text.endswith("."):
                text += "."
            text += " Settings that are not parameters here come from the add-on's panel."
            tool = {"name": name, "description": text, "enabled": False, "op": opname, "params": params}
            octx = ctx if ctx in ("VIEW_3D", "NODE_EDITOR") else None
            if octx:
                tool["context"] = octx
            tools.append(tool)
            for k, s in params.items():
                if s["type"] == "string" and "enum" not in s and k != "filepath":
                    print(f"   free text: {zid} {opname} {k}")
        m = info["manifest"]
        manifest = {"addon": f"bl_ext.blender_org.{m['id']}", "seen_version": m["version"], "tools": tools}
        (out / "manifests" / f"{PREFIX[zid]}.json").write_text(json.dumps(manifest, indent=2) + "\n")
        server.load_manifest(out / "manifests" / f"{PREFIX[zid]}.json")
        sources[m["id"]] = {"name": m["name"], "version": m["version"], "license": m["license"],
            "sha256": hashlib.sha256(zpath.read_bytes()).hexdigest(),
            "page": previous.get(m["id"], {}).get("page")
                    or f"https://extensions.blender.org/add-ons/{m['id'].replace('_', '-').lower()}/",
            "manifest": f"{PREFIX[zid]}.json",
            "operators": sorted({o["idname"] for o in info["operators"]})}
        print(f"{zid:34} {len(tools):2} tools")
    (out / "sources.json").write_text(json.dumps(sources, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(Path(sys.argv[1]), HERE)
