"""The assembly plan: a layout file in, the bpy code for each step out. Stdlib
only, no Blender needed, so it is tested on its own.

    python studio/pipeline/bpy/assemble_plan.py check <assembly.json>
    python studio/pipeline/bpy/assemble_plan.py emit  <assembly.json> --step STEP --out DIR

A layout (assembly.json, in the run folder) names the models to bring in and
the scene around them:

    {
      "assets": [
        {"name": "lantern", "glb": "meshy/lantern-refine.glb", "target_height_m": 0.45,
         "location": [0, 0, 0], "rotation_deg": [0, 0, 30], "ground": true,
         "decimate": null, "lods": [0.5, 0.25]}
      ],
      "floor": {"size_m": 12, "color": [0.18, 0.18, 0.2]},
      "lights": "studio",
      "camera": "auto",
      "world": {"color": [0.05, 0.05, 0.06], "strength": 1.0},
      "render": {"engine": "cycles", "samples": 32, "resolution": [960, 540],
                 "file": "preview.png", "transparent": false},
      "export": {"blend": "scene.blend", "glb": "scene.glb", "include_floor": false}
    }

A model's path is relative to the layout's folder and must stay inside it, so
an assembly reads only what its run made or kept. Units are metres, Z up, as
Blender has them after its glTF import.

Each step (STEPS) is one self-contained piece of bpy code: the plan's values
are written into it, and it imports only bpy, mathutils, math and json. So the
same text runs in a headless Blender (bpy/assemble.py) and, through the Blender
MCP server's execute_blender_code, in the author's live Blender with the
server's safe mode on. It prints one `ROSW {json}` line saying what it did.

`emit` prints a step's code and writes nothing. Exit codes: 0 done, 1 the
layout is wrong, 2 usage error.
"""

import argparse
import inspect
import json
import math
import re
import sys
from pathlib import Path

EXIT_OK, EXIT_INVALID, EXIT_USAGE = 0, 1, 2
STEPS = ["import", "normalize", "lods", "stage", "save", "export", "render"]
NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,47}")
FILE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
ENGINES = {"cycles", "eevee", "workbench"}
LIGHT_TYPES = {"SUN", "AREA", "POINT", "SPOT"}
DEFAULTS = {
    "floor": {"size_m": 12.0, "color": [0.18, 0.18, 0.2]},
    "lights": "studio",
    "camera": "auto",
    "world": {"color": [0.05, 0.05, 0.06], "strength": 1.0},
    "render": {"engine": "cycles", "samples": 32, "resolution": [960, 540], "file": "preview.png",
               "transparent": False},
    "export": {"blend": "scene.blend", "glb": "scene.glb", "include_floor": False},
}


class Invalid(Exception):
    pass


# ── the math, shared with the bpy code ───────────────────────────────────────
# These functions are copied whole into the steps that need them (see
# step_code), so they use nothing but math and plain tuples.

def fit_scale(height, target):
    """The uniform scale that makes a model `target` metres tall."""
    if not target:
        return 1.0
    if height <= 1e-9:
        raise ValueError("the model has no height to scale")
    return target / height


def placement(lo, hi, location, ground):
    """How far to move a model whose world bounds are lo..hi so that its base
    centre (ground) or its centre (not ground) lands on `location`."""
    cx, cy, cz = ((lo[i] + hi[i]) / 2 for i in range(3))
    dz = location[2] - (lo[2] if ground else cz)
    return (location[0] - cx, location[1] - cy, dz)


def bounds_union(boxes):
    """One box around several (lo, hi) boxes."""
    lo = [min(b[0][i] for b in boxes) for i in range(3)]
    hi = [max(b[1][i] for b in boxes) for i in range(3)]
    return lo, hi


def auto_camera(lo, hi, lens_mm, aspect):
    """A three-quarter view from the front right, a little above, far enough
    that the whole box fits the frame with a margin."""
    centre = [(lo[i] + hi[i]) / 2 for i in range(3)]
    radius = max(math.sqrt(sum((hi[i] - lo[i]) ** 2 for i in range(3))) / 2, 0.05)
    # Blender fits its 36 mm sensor to the longer side, so the shorter side
    # has the narrower view, and the box must fit that one.
    half_side = 36.0 / 2 / lens_mm
    half_fov = math.atan(half_side / aspect if aspect >= 1 else half_side * aspect)
    distance = radius * 1.15 / math.sin(half_fov)
    direction = (0.62, -0.72, 0.32)
    norm = math.sqrt(sum(d * d for d in direction))
    eye = [centre[i] + direction[i] / norm * distance for i in range(3)]
    return eye, centre


def studio_lights(lo, hi):
    """Key, fill and rim area lights around the box, scaled to its size."""
    centre = [(lo[i] + hi[i]) / 2 for i in range(3)]
    size = max(max(hi[i] - lo[i] for i in range(3)), 0.1)
    reach = size * 2.2
    power = 120.0 * size * size
    return [
        {"name": "key", "type": "AREA", "location": [centre[0] + reach, centre[1] - reach, centre[2] + reach],
         "look_at": centre, "energy": power, "size": size},
        {"name": "fill", "type": "AREA", "location": [centre[0] - reach, centre[1] - reach * 0.6, centre[2] + reach * 0.4],
         "look_at": centre, "energy": power * 0.35, "size": size * 1.5},
        {"name": "rim", "type": "AREA", "location": [centre[0], centre[1] + reach, centre[2] + reach * 0.9],
         "look_at": centre, "energy": power * 0.6, "size": size},
    ]


SHARED = [fit_scale, placement, bounds_union, auto_camera, studio_lights]


# ── the layout ───────────────────────────────────────────────────────────────

def _vector(value, what, length=3):
    if (not isinstance(value, list) or len(value) != length
            or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value)):
        raise Invalid(f"{what} must be a list of {length} numbers")
    return [float(v) for v in value]


def _file(value, what):
    if not isinstance(value, str) or not FILE_RE.fullmatch(value):
        raise Invalid(f"{what} must be a plain file name, not `{value}`")
    return value


def _ratio(value, what):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 < value <= 1:
        raise Invalid(f"{what} must be a number in (0, 1]")
    return float(value)


def resolve(layout, base, out):
    """The layout checked and filled in: absolute paths, every default."""
    if not isinstance(layout, dict):
        raise Invalid("the layout is a JSON object")
    known = {"assets", *DEFAULTS}
    extra = set(layout) - known
    if extra:
        raise Invalid(f"unknown key(s): {', '.join(sorted(extra))}. Known: {', '.join(sorted(known))}")
    base = Path(base).resolve()
    assets = layout.get("assets")
    if not isinstance(assets, list) or not assets:
        raise Invalid("`assets` lists at least one model")
    plan, names = {"assets": [], "out": str(Path(out).resolve())}, set()
    for index, asset in enumerate(assets):
        where = f"assets[{index}]"
        if not isinstance(asset, dict):
            raise Invalid(f"{where} is an object")
        allowed = {"name", "glb", "target_height_m", "scale", "location", "rotation_deg", "ground",
                   "decimate", "lods"}
        if set(asset) - allowed:
            raise Invalid(f"{where}: unknown key(s) {', '.join(sorted(set(asset) - allowed))}")
        name = asset.get("name")
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            raise Invalid(f"{where}.name is a slug: lower-case letters, digits, hyphens")
        if name in names:
            raise Invalid(f"{where}.name `{name}` is used twice")
        names.add(name)
        glb = asset.get("glb")
        if not isinstance(glb, str) or not glb:
            raise Invalid(f"{name}: `glb` is the model's path, relative to the layout")
        path = (base / glb).resolve()
        try:
            path.relative_to(base)
        except ValueError:
            raise Invalid(f"{name}: {glb} is outside the layout's folder")
        if path.suffix.lower() not in (".glb", ".gltf"):
            raise Invalid(f"{name}: {glb} is not a .glb or .gltf")
        target = asset.get("target_height_m")
        if target is not None and (not isinstance(target, (int, float)) or isinstance(target, bool) or target <= 0):
            raise Invalid(f"{name}: target_height_m is a height in metres, above 0")
        scale = asset.get("scale", 1.0)
        if target is not None and "scale" in asset:
            raise Invalid(f"{name}: give target_height_m or scale, not both")
        if not isinstance(scale, (int, float)) or isinstance(scale, bool) or scale <= 0:
            raise Invalid(f"{name}: scale is a number above 0")
        lods = asset.get("lods") or []
        if not isinstance(lods, list):
            raise Invalid(f"{name}: lods is a list of ratios")
        lods = [_ratio(r, f"{name}: each lod") for r in lods]
        if lods != sorted(lods, reverse=True) or len(set(lods)) != len(lods):
            raise Invalid(f"{name}: lods go from the most detail to the least, each once")
        ground = asset.get("ground", True)
        if not isinstance(ground, bool):
            raise Invalid(f"{name}: ground is true or false")
        decimate = asset.get("decimate")
        plan["assets"].append({
            "name": name, "glb": str(path),
            "target_height_m": float(target) if target is not None else None, "scale": float(scale),
            "location": _vector(asset.get("location", [0, 0, 0]), f"{name}: location"),
            "rotation_deg": _vector(asset.get("rotation_deg", [0, 0, 0]), f"{name}: rotation_deg"),
            "ground": ground,
            "decimate": _ratio(decimate, f"{name}: decimate") if decimate is not None else None,
            "lods": lods,
        })

    floor = layout.get("floor", DEFAULTS["floor"])
    if floor is not None:
        if not isinstance(floor, dict) or set(floor) - {"size_m", "color"}:
            raise Invalid("floor is null or {size_m, color}")
        floor = {"size_m": float(floor.get("size_m", DEFAULTS["floor"]["size_m"])),
                 "color": _vector(floor.get("color", DEFAULTS["floor"]["color"]), "floor.color")}
        if floor["size_m"] <= 0:
            raise Invalid("floor.size_m is above 0")
    plan["floor"] = floor

    lights = layout.get("lights", "studio")
    if lights != "studio":
        if not isinstance(lights, list):
            raise Invalid('lights is "studio" or a list of lights')
        checked = []
        for index, light in enumerate(lights):
            where = f"lights[{index}]"
            if not isinstance(light, dict) or light.get("type") not in LIGHT_TYPES:
                raise Invalid(f"{where}.type is one of {', '.join(sorted(LIGHT_TYPES))}")
            entry = {"name": str(light.get("name") or f"light-{index}"), "type": light["type"],
                     "location": _vector(light.get("location"), f"{where}.location"),
                     "energy": float(light.get("energy", 100)), "size": float(light.get("size", 1))}
            if "look_at" in light:
                entry["look_at"] = _vector(light["look_at"], f"{where}.look_at")
            else:
                entry["rotation_deg"] = _vector(light.get("rotation_deg", [0, 0, 0]), f"{where}.rotation_deg")
            checked.append(entry)
        lights = checked
    plan["lights"] = lights

    camera = layout.get("camera", "auto")
    if camera != "auto":
        if not isinstance(camera, dict):
            raise Invalid('camera is "auto" or {location, look_at, lens_mm}')
        camera = {"location": _vector(camera.get("location"), "camera.location"),
                  "look_at": _vector(camera.get("look_at"), "camera.look_at"),
                  "lens_mm": float(camera.get("lens_mm", 50))}
    plan["camera"] = camera
    plan["lens_mm"] = camera["lens_mm"] if isinstance(camera, dict) else 50.0

    world = {**DEFAULTS["world"], **(layout.get("world") or {})}
    plan["world"] = {"color": _vector(world["color"], "world.color"), "strength": float(world["strength"])}

    render = {**DEFAULTS["render"], **(layout.get("render") or {})}
    if set(render) - set(DEFAULTS["render"]):
        raise Invalid(f"render: unknown key(s) {', '.join(sorted(set(render) - set(DEFAULTS['render'])))}")
    if render["engine"] not in ENGINES:
        raise Invalid(f"render.engine is one of {', '.join(sorted(ENGINES))}")
    resolution = _vector(render["resolution"], "render.resolution", 2)
    if min(resolution) < 16 or max(resolution) > 7680:
        raise Invalid("render.resolution is between 16 and 7680 pixels a side")
    samples = render["samples"]
    if not isinstance(samples, int) or isinstance(samples, bool) or not 1 <= samples <= 4096:
        raise Invalid("render.samples is a whole number from 1 to 4096")
    plan["render"] = {"engine": render["engine"], "samples": samples,
                      "resolution": [int(v) for v in resolution],
                      "file": _file(render["file"], "render.file"), "transparent": bool(render["transparent"])}

    export = {**DEFAULTS["export"], **(layout.get("export") or {})}
    if set(export) - set(DEFAULTS["export"]):
        raise Invalid(f"export: unknown key(s) {', '.join(sorted(set(export) - set(DEFAULTS['export'])))}")
    plan["export"] = {"blend": _file(export["blend"], "export.blend"), "glb": _file(export["glb"], "export.glb"),
                      "include_floor": bool(export["include_floor"])}
    if not plan["export"]["blend"].endswith(".blend") or not plan["export"]["glb"].endswith(".glb"):
        raise Invalid("export.blend ends in .blend and export.glb in .glb")
    return plan


def load(layout_path, out):
    path = Path(layout_path)
    try:
        layout = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise Invalid(f"{path}: {err}")
    return resolve(layout, path.parent, out)


def missing_models(plan):
    return [a["glb"] for a in plan["assets"] if not Path(a["glb"]).is_file()]


# ── the bpy code for each step ───────────────────────────────────────────────

PRELUDE = '''\
import json
import math
import bpy
from mathutils import Vector

PLAN = json.loads({plan!r})


def collection(name):
    found = bpy.data.collections.get(name)
    if found is None:
        found = bpy.data.collections.new(name)
    if found.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(found)
    return found


def meshes_of(root):
    return [o for o in root.children_recursive if o.type == "MESH"]


def world_bounds(objects):
    corners = [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    if not corners:
        return None
    lo = [min(c[i] for c in corners) for i in range(3)]
    hi = [max(c[i] for c in corners) for i in range(3)]
    return lo, hi


def triangles(objects):
    graph = bpy.context.evaluated_depsgraph_get()
    count = 0
    for o in objects:
        mesh = o.evaluated_get(graph).to_mesh()
        mesh.calc_loop_triangles()
        count += len(mesh.loop_triangles)
        o.evaluated_get(graph).to_mesh_clear()
    return count


def aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def report(step, **found):
    print("ROSW " + json.dumps(dict(step=step, **found)))


def find_root(name):
    for o in bpy.data.objects:
        if o.type == "EMPTY" and o.get("rosw_asset") == name:
            return o
    return None


def asset_root(name):
    root = find_root(name)
    if root is None:
        raise RuntimeError("no asset `" + name + "` in the scene: run the import step first")
    return root
'''

BODIES = {
    "import": '''
done = []
for asset in PLAN["assets"]:
    if find_root(asset["name"]) is not None:
        done.append(dict(name=asset["name"], skipped="already in the scene"))
        continue
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=asset["glb"])
    new = [o for o in bpy.data.objects if o not in before]
    group = collection("rosw_" + asset["name"])
    root = bpy.data.objects.new("rosw_" + asset["name"], None)
    root["rosw_asset"] = asset["name"]
    group.objects.link(root)
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        group.objects.link(o)
        if o.parent is None:
            o.parent = root
    bpy.context.view_layer.update()
    bounds = world_bounds(meshes_of(root))
    done.append(dict(name=asset["name"], objects=len(new), meshes=len(meshes_of(root)),
                     triangles=triangles(meshes_of(root)),
                     size=[round(bounds[1][i] - bounds[0][i], 4) for i in range(3)] if bounds else None))
report("import", assets=done)
''',
    "normalize": '''
done = []
for asset in PLAN["assets"]:
    root = asset_root(asset["name"])
    root.location = (0.0, 0.0, 0.0)
    root.scale = (1.0, 1.0, 1.0)
    root.rotation_euler = [math.radians(a) for a in asset["rotation_deg"]]
    bpy.context.view_layer.update()
    bounds = world_bounds(meshes_of(root))
    if bounds is None:
        raise RuntimeError(asset["name"] + " has no mesh")
    lo, hi = bounds
    height = hi[2] - lo[2]
    factor = fit_scale(height, asset["target_height_m"]) if asset["target_height_m"] else asset["scale"]
    root.scale = (factor, factor, factor)
    bpy.context.view_layer.update()
    lo, hi = world_bounds(meshes_of(root))
    move = placement(lo, hi, asset["location"], asset["ground"])
    root.location = move
    bpy.context.view_layer.update()
    lo, hi = world_bounds(meshes_of(root))
    done.append(dict(name=asset["name"], source_height=round(height, 4), scale=round(factor, 6),
                     size=[round(hi[i] - lo[i], 4) for i in range(3)], base_z=round(lo[2], 4)))
report("normalize", assets=done)
''',
    "lods": '''
done = []
for asset in PLAN["assets"]:
    root = asset_root(asset["name"])
    meshes = meshes_of(root)
    if asset["decimate"]:
        for o in meshes:
            mod = o.modifiers.get("rosw_decimate") or o.modifiers.new("rosw_decimate", "DECIMATE")
            mod.ratio = asset["decimate"]
    entry = dict(name=asset["name"], triangles=triangles(meshes), lods=[])
    for level, ratio in enumerate(asset["lods"], start=1):
        label = "rosw_" + asset["name"] + "_LOD" + str(level)
        if bpy.data.collections.get(label) is not None:
            entry["lods"].append(dict(lod=label, skipped="already made"))
            continue
        group = collection(label)
        lod_root = bpy.data.objects.new(label, None)
        group.objects.link(lod_root)
        lod_root.matrix_world = root.matrix_world.copy()
        copies = []
        for o in meshes:
            twin = o.copy()
            group.objects.link(twin)
            twin.parent = None
            twin.matrix_world = o.matrix_world.copy()
            twin.parent = lod_root
            twin.matrix_parent_inverse = lod_root.matrix_world.inverted()
            mod = twin.modifiers.get("rosw_decimate") or twin.modifiers.new("rosw_decimate", "DECIMATE")
            mod.ratio = ratio * (asset["decimate"] or 1.0)
            copies.append(twin)
        entry["lods"].append(dict(lod=label, ratio=ratio, triangles=triangles(copies)))
        bpy.context.view_layer.layer_collection.children[label].exclude = True
    done.append(entry)
report("lods", assets=done)
''',
    "stage": '''
roots = [asset_root(a["name"]) for a in PLAN["assets"]]
boxes = [world_bounds(meshes_of(r)) for r in roots]
lo, hi = bounds_union([b for b in boxes if b])
scene = bpy.context.scene
made = []
if PLAN["floor"] and bpy.data.objects.get("rosw_floor") is None:
    half = PLAN["floor"]["size_m"] / 2
    mesh = bpy.data.meshes.new("rosw_floor")
    mesh.from_pydata([(-half, -half, 0), (half, -half, 0), (half, half, 0), (-half, half, 0)], [], [(0, 1, 2, 3)])
    floor = bpy.data.objects.new("rosw_floor", mesh)
    scene.collection.objects.link(floor)
    material = bpy.data.materials.new("rosw_floor")
    material.diffuse_color = PLAN["floor"]["color"] + [1.0]
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader is not None:
        shader.inputs["Base Color"].default_value = PLAN["floor"]["color"] + [1.0]
        shader.inputs["Roughness"].default_value = 0.8
    mesh.materials.append(material)
    made.append("floor")
lights = studio_lights(lo, hi) if PLAN["lights"] == "studio" else PLAN["lights"]
for spec in lights:
    name = "rosw_light_" + spec["name"]
    if bpy.data.objects.get(name) is not None:
        continue
    data = bpy.data.lights.new(name, spec["type"])
    data.energy = spec["energy"]
    if spec["type"] == "AREA":
        data.size = spec["size"]
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = spec["location"]
    if "look_at" in spec:
        aim(light, spec["look_at"])
    else:
        light.rotation_euler = [math.radians(a) for a in spec["rotation_deg"]]
    made.append(name)
width, height = PLAN["render"]["resolution"]
camera = bpy.data.objects.get("rosw_camera")
if camera is None:
    camera = bpy.data.objects.new("rosw_camera", bpy.data.cameras.new("rosw_camera"))
    scene.collection.objects.link(camera)
    made.append("camera")
camera.data.lens = PLAN["lens_mm"]
if PLAN["camera"] == "auto":
    eye, target = auto_camera(lo, hi, PLAN["lens_mm"], width / height)
else:
    eye, target = PLAN["camera"]["location"], PLAN["camera"]["look_at"]
camera.location = eye
aim(camera, target)
camera.data.clip_end = max(1000.0, sum((eye[i] - target[i]) ** 2 for i in range(3)) ** 0.5 * 4)
scene.camera = camera
if scene.world is None:
    scene.world = bpy.data.worlds.new("rosw_world")
scene.world.use_nodes = True
background = scene.world.node_tree.nodes.get("Background")
if background is not None:
    background.inputs[0].default_value = PLAN["world"]["color"] + [1.0]
    background.inputs[1].default_value = PLAN["world"]["strength"]
scene.unit_settings.system = "METRIC"
report("stage", made=made, bounds=dict(min=[round(v, 4) for v in lo], max=[round(v, 4) for v in hi]),
       camera=[round(v, 4) for v in eye])
''',
    "save": '''
target = PLAN["out"] + "/" + PLAN["export"]["blend"]
bpy.ops.wm.save_as_mainfile(filepath=target, copy=True)
report("save", file=PLAN["export"]["blend"])
''',
    "export": '''
lod_names = set()
for a in PLAN["assets"]:
    for level in range(1, len(a["lods"]) + 1):
        lod_names.add("rosw_" + a["name"] + "_LOD" + str(level))
for o in bpy.context.view_layer.objects:
    o.select_set(False)
chosen = []
for a in PLAN["assets"]:
    root = asset_root(a["name"])
    for o in [root] + list(root.children_recursive):
        if not any(c.name in lod_names for c in o.users_collection):
            o.select_set(True)
            chosen.append(o.name)
floor = bpy.data.objects.get("rosw_floor")
if floor is not None and PLAN["export"]["include_floor"]:
    floor.select_set(True)
    chosen.append(floor.name)
target = PLAN["out"] + "/" + PLAN["export"]["glb"]
bpy.ops.export_scene.gltf(filepath=target, export_format="GLB", use_selection=True)
report("export", file=PLAN["export"]["glb"], objects=len(chosen))
''',
    "render": '''
scene = bpy.context.scene
settings = PLAN["render"]
if settings["engine"] == "cycles":
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = settings["samples"]
elif settings["engine"] == "eevee":
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
else:
    scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x, scene.render.resolution_y = settings["resolution"]
scene.render.resolution_percentage = 100
scene.render.film_transparent = settings["transparent"]
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = PLAN["out"] + "/" + settings["file"]
if scene.camera is None:
    raise RuntimeError("no camera: run the stage step first")
bpy.ops.render.render(write_still=True)
report("render", file=settings["file"], engine=scene.render.engine, resolution=settings["resolution"])
''',
}

# Which shared functions each step uses.
USES = {"normalize": [fit_scale, placement], "stage": [bounds_union, auto_camera, studio_lights]}


def step_code(plan, step):
    """The whole bpy code for one step, with the plan written into it."""
    if step not in BODIES:
        raise Invalid(f"no step `{step}`. Steps: {', '.join(STEPS)}")
    shared = "\n\n".join(inspect.getsource(f) for f in USES.get(step, []))
    head = PRELUDE.format(plan=json.dumps(plan, sort_keys=True))
    return (f"# ROSW assemble step `{step}`, generated by studio/pipeline/bpy/assemble_plan.py\n"
            + head + ("\n\n" + shared if shared else "") + "\n" + BODIES[step])


# ── the command line ─────────────────────────────────────────────────────────

def main(argv=None):
    parser = argparse.ArgumentParser(prog="assemble_plan.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check", help="check a layout and say what it will do")
    p.add_argument("layout")
    p.add_argument("--out", help="the output folder (default: blender/ beside the layout)")
    p = sub.add_parser("emit", help="print one step's bpy code")
    p.add_argument("layout")
    p.add_argument("--step", required=True, choices=STEPS)
    p.add_argument("--out", help="the output folder (default: blender/ beside the layout)")
    args = parser.parse_args(argv)
    out = args.out or str(Path(args.layout).resolve().parent / "blender")
    try:
        plan = load(args.layout, out)
    except Invalid as problem:
        print(f"invalid   {problem}", file=sys.stderr)
        return EXIT_INVALID
    if args.command == "emit":
        print(step_code(plan, args.step))
        return EXIT_OK
    missing = missing_models(plan)
    for asset in plan["assets"]:
        size = (f"to {asset['target_height_m']} m tall" if asset["target_height_m"]
                else f"at scale {asset['scale']}")
        print(f"asset     {asset['name']}: {Path(asset['glb']).name}, {size}, "
              f"{'on the ground' if asset['ground'] else 'centred'} at {asset['location']}"
              + (f", decimate {asset['decimate']}" if asset["decimate"] else "")
              + (f", LODs {asset['lods']}" if asset["lods"] else ""))
    print(f"scene     floor {'none' if not plan['floor'] else str(plan['floor']['size_m']) + ' m'}, "
          f"lights {plan['lights'] if isinstance(plan['lights'], str) else len(plan['lights'])}, "
          f"camera {plan['camera'] if isinstance(plan['camera'], str) else 'set'}")
    print(f"render    {plan['render']['engine']}, {plan['render']['samples']} samples, "
          f"{plan['render']['resolution'][0]}x{plan['render']['resolution'][1]} -> {plan['render']['file']}")
    print(f"writes    {plan['out']}/: {plan['export']['blend']}, {plan['export']['glb']}, {plan['render']['file']}")
    for path in missing:
        print(f"missing   {path}", file=sys.stderr)
    return EXIT_INVALID if missing else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
