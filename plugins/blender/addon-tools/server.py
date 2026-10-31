"""Named tools for the add-ons in the user's Blender, served over MCP.

MCP for Blender gives Claude one way into an add-on: free-form Python through
execute_blender_code. This server gives each add-on operator the user chooses a
tool of its own, with typed parameters, from a manifest the user keeps:

    <tools dir>/<addon>.json   (BLENDER_ADDON_TOOLS_DIR, default ~/.blender-addon-tools)

It talks to the same add-on socket as MCP for Blender (BLENDER_HOST, BLENDER_PORT,
default localhost:9876) and sends one `execute_code` command per call. The code
sent is built here from the manifest; the model only supplies argument values,
which are checked against the declared types and travel as a JSON literal, never
as code. A tool whose manifest says `code` runs that code: the manifest is the
user's, so read one before enabling it.

    python server.py                 serve over stdio (what .mcp.json runs)
    python server.py list            the add-ons enabled in the running Blender
    python server.py discover <mod>  write a draft manifest for one add-on
    python server.py check           validate the manifests and print their tools

Stdlib only. Python 3.10+.
"""

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

SERVER_NAME = "blender-addons"
SERVER_VERSION = "0.2.0"
PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")
MARKER = "ADDON_TOOLS "
TOOL_NAME = re.compile(r"^[a-z][a-z0-9_]{0,47}$")
OP_NAME = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
MODULE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$")
CONTEXTS = ("VIEW_3D", "FILE_BROWSER", "NODE_EDITOR", "IMAGE_EDITOR", "PROPERTIES", "OUTLINER")
PARAM_TYPES = ("string", "number", "integer", "boolean", "array")
PARAM_KEYS = {"type", "description", "enum", "default", "minimum", "maximum", "items", "minItems",
              "maxItems", "required", "prop"}
TOOL_KEYS = {"name", "description", "enabled", "read_only", "params", "op", "code", "context"}
LIBRARY_KINDS = ("objects", "collections", "materials", "worlds", "node_groups")


class Invalid(Exception):
    """A manifest, or a tool call's arguments, that cannot be used."""


class BlenderError(Exception):
    """Blender could not be reached, or the code sent to it failed."""


def tools_dir():
    return Path(os.environ.get("BLENDER_ADDON_TOOLS_DIR") or Path.home() / ".blender-addon-tools")


# ---------------------------------------------------------------------------
# Manifests


def check_param(tool, name, spec):
    where = f"{tool}: parameter `{name}`"
    if not TOOL_NAME.match(name):
        raise Invalid(f"{where}: names are lower-case letters, digits and underscores")
    if not isinstance(spec, dict) or spec.get("type") not in PARAM_TYPES:
        raise Invalid(f"{where}: `type` must be one of {', '.join(PARAM_TYPES)}")
    unknown = set(spec) - PARAM_KEYS
    if unknown:
        raise Invalid(f"{where}: unknown keys {', '.join(sorted(unknown))}")
    if spec["type"] == "array" and (not isinstance(spec.get("items"), dict)
                                    or spec["items"].get("type") not in ("string", "number", "integer", "boolean")):
        raise Invalid(f"{where}: an array needs `items` with a string, number, integer or boolean `type`")
    if "enum" in spec and (not isinstance(spec["enum"], list) or not spec["enum"]):
        raise Invalid(f"{where}: `enum` must be a non-empty list")
    if "prop" in spec and not TOOL_NAME.match(spec["prop"]):
        raise Invalid(f"{where}: `prop` must be an operator property identifier")
    if "default" in spec:
        validate_value(where, spec, spec["default"])


def load_manifest(path):
    """One add-on's manifest, checked. Returns (addon, [tool, ...]) with every tool,
    enabled or not."""
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Invalid(f"{Path(path).name}: not readable JSON ({e})")
    if not isinstance(doc, dict) or not isinstance(doc.get("addon"), str) or not MODULE_NAME.match(doc["addon"]):
        raise Invalid(f"{Path(path).name}: `addon` must be the add-on's module name")
    tools = doc.get("tools")
    if not isinstance(tools, list):
        raise Invalid(f"{Path(path).name}: `tools` must be a list")
    checked = []
    for tool in tools:
        if not isinstance(tool, dict) or not isinstance(tool.get("name"), str) or not TOOL_NAME.match(tool["name"]):
            raise Invalid(f"{Path(path).name}: every tool needs a `name` of lower-case letters, digits and "
                          "underscores, at most 48 characters")
        name = tool["name"]
        unknown = set(tool) - TOOL_KEYS
        if unknown:
            raise Invalid(f"{name}: unknown keys {', '.join(sorted(unknown))}")
        if ("op" in tool) == ("code" in tool):
            raise Invalid(f"{name}: give exactly one of `op` and `code`")
        if "op" in tool and (not isinstance(tool["op"], str) or not OP_NAME.match(tool["op"])):
            raise Invalid(f"{name}: `op` must be an operator id such as `object.select_all`")
        if "code" in tool:
            code = tool["code"]
            if isinstance(code, list) and all(isinstance(line, str) for line in code):
                tool = {**tool, "code": "\n".join(code)}
            elif not isinstance(code, str):
                raise Invalid(f"{name}: `code` must be a string or a list of lines")
            compile(tool["code"], name, "exec")
        if tool.get("context") is not None and tool["context"] not in CONTEXTS:
            raise Invalid(f"{name}: `context` must be one of {', '.join(CONTEXTS)}")
        params = tool.get("params", {})
        if not isinstance(params, dict):
            raise Invalid(f"{name}: `params` must be an object")
        for pname, spec in params.items():
            check_param(name, pname, spec)
        checked.append({**tool, "params": params, "addon": doc["addon"],
                        "enabled": tool.get("enabled", False) is True,
                        "read_only": tool.get("read_only", False) is True})
    return doc["addon"], checked


def load_tools(directory=None, include_disabled=False):
    """Every enabled tool across the manifests, by name. Errors name the file."""
    directory = Path(directory) if directory else tools_dir()
    found, problems = {}, []
    if directory.is_dir():
        for path in sorted(directory.glob("*.json")):
            if path.name.endswith(".draft.json"):
                continue
            try:
                _, tools = load_manifest(path)
            except (Invalid, SyntaxError) as e:
                problems.append(str(e))
                continue
            for tool in tools:
                if not (tool["enabled"] or include_disabled):
                    continue
                if tool["name"] in found or tool["name"] in BUILTINS:
                    problems.append(f"{path.name}: tool `{tool['name']}` is defined twice")
                    continue
                found[tool["name"]] = tool
    return found, problems


# ---------------------------------------------------------------------------
# Arguments


def validate_value(where, spec, value):
    kind = spec["type"]
    ok = {
        "string": lambda v: isinstance(v, str),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "array": lambda v: isinstance(v, list),
    }[kind]
    if not ok(value):
        raise Invalid(f"{where}: expected {kind}, got {type(value).__name__}")
    if kind == "array":
        for i, item in enumerate(value):
            validate_value(f"{where}[{i}]", spec["items"], item)
        if "minItems" in spec and len(value) < spec["minItems"]:
            raise Invalid(f"{where}: at least {spec['minItems']} items")
        if "maxItems" in spec and len(value) > spec["maxItems"]:
            raise Invalid(f"{where}: at most {spec['maxItems']} items")
    if "enum" in spec and value not in spec["enum"]:
        raise Invalid(f"{where}: must be one of {', '.join(map(str, spec['enum']))}")
    if "minimum" in spec and value < spec["minimum"]:
        raise Invalid(f"{where}: at least {spec['minimum']}")
    if "maximum" in spec and value > spec["maximum"]:
        raise Invalid(f"{where}: at most {spec['maximum']}")


def validate_args(tool, arguments):
    """The arguments a call may pass, with defaults filled in. Unknown names,
    missing required ones and wrong types are refused before Blender is touched."""
    arguments = arguments or {}
    if not isinstance(arguments, dict):
        raise Invalid("arguments must be an object")
    params = tool["params"]
    unknown = set(arguments) - set(params)
    if unknown:
        raise Invalid(f"unknown arguments: {', '.join(sorted(unknown))}")
    values = {}
    for name, spec in params.items():
        if name in arguments:
            validate_value(name, spec, arguments[name])
            values[name] = arguments[name]
        elif "default" in spec:
            values[name] = spec["default"]
        elif spec.get("required"):
            raise Invalid(f"`{name}` is required")
    return values


def input_schema(params):
    props, required = {}, []
    for name, spec in params.items():
        props[name] = {k: v for k, v in spec.items() if k not in ("required", "prop")}
        if spec.get("required"):
            required.append(name)
    schema = {"type": "object", "properties": props, "additionalProperties": False}
    if required:
        schema["required"] = required
    return schema


# ---------------------------------------------------------------------------
# The code sent to Blender. ARGS arrives as a JSON string literal; nothing the
# model passes is ever spliced into the code text.

PRELUDE = '''import json
import bpy
import addon_utils

ARGS = json.loads({args!r})
_FOUND = {{}}


def report(**found):
    _FOUND.update(found)


def area_override(space):
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == space:
                region = next((r for r in area.regions if r.type == "WINDOW"), None)
                return dict(window=window, area=area, region=region)
    raise RuntimeError("this tool needs a " + space + " area open in Blender")


def addon_enabled(module):
    enabled = bpy.context.preferences.addons.keys()
    if module in enabled:
        return True
    if module.startswith("bl_ext."):
        # An extension's module names the repository it came from
        # (bl_ext.blender_org.<id>, bl_ext.user_default.<id>); any of them will do.
        tail = module.rsplit(".", 1)[1]
        if any(k.startswith("bl_ext.") and k.rsplit(".", 1)[1] == tail for k in enabled):
            return True
    return bool(addon_utils.check(module)[1])

'''

FINISH = '''
print({marker!r} + json.dumps(_FOUND, default=str))
'''

OP_BODY = '''if not addon_enabled({module!r}):
    raise RuntimeError("the add-on `" + {module!r} + "` is not enabled in this Blender")
_before = set(bpy.data.objects.keys())
_kwargs = {{{prop_map}}}
_kwargs = {{k: v for k, v in _kwargs.items() if v is not None}}
{call}
report(result=sorted(_result), new_objects=sorted(set(bpy.data.objects.keys()) - _before))
'''

CODE_BODY = '''if not addon_enabled({module!r}):
    raise RuntimeError("the add-on `" + {module!r} + "` is not enabled in this Blender")
{code}
'''


def tool_code(tool, values):
    """The whole script for one call."""
    head = PRELUDE.format(args=json.dumps(values))
    if "op" in tool:
        prop_map = ", ".join(f"{spec.get('prop', name)!r}: ARGS.get({name!r})"
                             for name, spec in tool["params"].items())
        call = f"_result = bpy.ops.{tool['op']}('EXEC_DEFAULT', **_kwargs)"
        if tool.get("context"):
            call = (f"with bpy.context.temp_override(**area_override({tool['context']!r})):\n"
                    f"    {call}")
        body = OP_BODY.format(module=tool["addon"], prop_map=prop_map, call=call)
    else:
        code = tool["code"]
        if tool.get("context"):
            code = (f"with bpy.context.temp_override(**area_override({tool['context']!r})):\n"
                    + "\n".join("    " + line for line in code.splitlines()))
        body = CODE_BODY.format(module=tool["addon"], code=code)
    return head + body + FINISH.format(marker=MARKER)


# Built-in tools: they need no manifest. The library pair reads any asset library
# set in Blender's preferences, which is how the Poly Haven add-on stores what it
# downloads; the inspect pair is how a manifest is drafted.

ADDONS_LIST = '''
mods = []
for mod in addon_utils.modules(refresh=False):
    name = mod.__name__
    info = addon_utils.module_bl_info(mod)
    mods.append(dict(module=name, name=info.get("name", name), version=".".join(map(str, info.get("version", ()))),
                     enabled=addon_enabled(name)))
import sys
seen = set(m["module"] for m in mods)
for name in bpy.context.preferences.addons.keys():
    # Enabled from somewhere addon_utils does not scan (a path set by hand).
    if name not in seen:
        info = getattr(sys.modules.get(name), "bl_info", {}) or {}
        mods.append(dict(module=name, name=info.get("name", name),
                         version=".".join(map(str, info.get("version", ()))), enabled=True))
if not ARGS.get("include_disabled"):
    mods = [m for m in mods if m["enabled"]]
report(addons=sorted(mods, key=lambda m: m["name"].lower()))
'''

ADDON_INSPECT = '''
module = ARGS["module"]


def ours(cls):
    name = getattr(cls, "__module__", "") or ""
    return name == module or name.startswith(module + ".")


def walk(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from walk(sub)


def prop_info(p):
    info = dict(identifier=p.identifier, type=p.type, name=p.name, description=p.description,
                hidden=bool(getattr(p, "is_hidden", False)), skip_save=bool(getattr(p, "is_skip_save", False)))
    if getattr(p, "is_array", False):
        info["array_length"] = p.array_length
        info["default"] = list(p.default_array)
    elif p.type in ("BOOLEAN", "INT", "FLOAT", "STRING"):
        info["default"] = p.default
    if p.type in ("INT", "FLOAT"):
        info["min"], info["max"] = p.hard_min, p.hard_max
    if p.type == "ENUM":
        info["flag"] = bool(p.is_enum_flag)
        info["items"] = [i.identifier for i in p.enum_items]
        info["default"] = sorted(p.default_flag) if p.is_enum_flag else p.default
    return info


if not addon_enabled(module):
    raise RuntimeError("the add-on `" + module + "` is not enabled in this Blender")
import sys
info = getattr(sys.modules.get(module), "bl_info", {}) or {}
for mod in addon_utils.modules(refresh=False):
    if mod.__name__ == module:
        info = addon_utils.module_bl_info(mod)
operators, seen = [], set()
for cls in walk(bpy.types.Operator):
    idname = getattr(cls, "bl_idname", "") or ""
    if not ours(cls) or "." not in idname or idname in seen:
        continue
    seen.add(idname)
    category, name = idname.split(".", 1)
    try:
        rna = getattr(getattr(bpy.ops, category), name).get_rna_type()
    except (AttributeError, KeyError):
        continue
    operators.append(dict(
        idname=idname, label=getattr(cls, "bl_label", ""),
        description=(getattr(cls, "bl_description", "") or (cls.__doc__ or "")).strip(),
        options=sorted(getattr(cls, "bl_options", set()) or set()),
        properties=[prop_info(p) for p in rna.properties if p.identifier != "rna_type"]))
panels = []
for cls in walk(bpy.types.Panel):
    if ours(cls):
        panels.append(dict(label=getattr(cls, "bl_label", ""), space=getattr(cls, "bl_space_type", ""),
                           region=getattr(cls, "bl_region_type", ""), category=getattr(cls, "bl_category", "")))
report(module=module, name=info.get("name", module), version=".".join(map(str, info.get("version", ()))),
       operators=sorted(operators, key=lambda o: o["idname"]), panels=panels)
'''

LIBRARY_LIST = '''
import os

libraries = list(bpy.context.preferences.filepaths.asset_libraries)
lib = next((l for l in libraries if l.name == ARGS["library"]), None)
if lib is None:
    raise RuntimeError("no asset library named `" + ARGS["library"] + "`; libraries: "
                       + ", ".join(l.name for l in libraries))
root = bpy.path.abspath(lib.path)
kinds = list(%(kinds)r) if ARGS["kind"] == "all" else [ARGS["kind"]]
query = ARGS["query"].lower()
found, files = [], 0
for folder, dirs, names in os.walk(root):
    dirs.sort()
    for file in sorted(names):
        if not file.endswith(".blend") or len(found) >= ARGS["limit"]:
            continue
        files += 1
        path = os.path.join(folder, file)
        relative = os.path.relpath(path, root).replace(os.sep, "/")
        with bpy.data.libraries.load(path, assets_only=True) as (source, _):
            for kind in kinds:
                for name in getattr(source, kind):
                    if query and query not in name.lower() and query not in relative.lower():
                        continue
                    if len(found) < ARGS["limit"]:
                        found.append(dict(kind=kind, name=name, file=relative))
report(library=lib.name, root=root, files_read=files, assets=found, truncated=len(found) >= ARGS["limit"])
''' % {"kinds": LIBRARY_KINDS}

LIBRARY_IMPORT = '''
import os

libraries = list(bpy.context.preferences.filepaths.asset_libraries)
lib = next((l for l in libraries if l.name == ARGS["library"]), None)
if lib is None:
    raise RuntimeError("no asset library named `" + ARGS["library"] + "`")
root = os.path.realpath(bpy.path.abspath(lib.path))
path = os.path.realpath(os.path.join(root, ARGS["file"]))
if os.path.commonpath([root, path]) != root or not path.endswith(".blend") or not os.path.isfile(path):
    raise RuntimeError("`" + ARGS["file"] + "` is not a .blend inside the library")
kind, name = ARGS["kind"], ARGS["name"]
with bpy.data.libraries.load(path, link=ARGS["link"], assets_only=True) as (source, target):
    if name not in getattr(source, kind):
        raise RuntimeError("no " + kind[:-1] + " `" + name + "` marked as an asset in " + ARGS["file"])
    setattr(target, kind, [name])
block = getattr(target, kind)[0]
scene = bpy.context.scene
placed = []
if kind == "objects":
    scene.collection.objects.link(block)
    placed.append(block.name)
elif kind == "collections":
    if ARGS["link"]:
        holder = bpy.data.objects.new(block.name, None)
        holder.instance_type = "COLLECTION"
        holder.instance_collection = block
        scene.collection.objects.link(holder)
        placed.append(holder.name)
    else:
        scene.collection.children.link(block)
        placed.extend(o.name for o in block.all_objects)
elif kind == "materials":
    for object_name in ARGS["apply_to"]:
        target_object = bpy.data.objects.get(object_name)
        if target_object is None or target_object.data is None or not hasattr(target_object.data, "materials"):
            raise RuntimeError("no object with materials named `" + object_name + "`")
        target_object.data.materials.clear()
        target_object.data.materials.append(block)
        placed.append(object_name)
elif kind == "worlds" and ARGS["set_world"]:
    scene.world = block
    placed.append(scene.name)
report(imported=block.name, kind=kind, linked=ARGS["link"], placed=placed)
'''

BUILTINS = {
    "addons_list": {
        "description": "List the add-ons in the connected Blender (module, name, version). Use the module "
                       "name with addon_inspect.",
        "read_only": True, "code": ADDONS_LIST, "addon": None,
        "params": {"include_disabled": {"type": "boolean", "default": False,
                                        "description": "Also list installed add-ons that are switched off."}},
    },
    "addon_inspect": {
        "description": "Every operator an enabled add-on registers, with its properties (type, default, "
                       "range, enum items), and the add-on's panels. Read-only; the raw material for a "
                       "manifest. Changes nothing in Blender.",
        "read_only": True, "code": ADDON_INSPECT, "addon": None,
        "params": {"module": {"type": "string", "required": True,
                              "description": "The add-on's module name, from addons_list."}},
    },
    "library_list": {
        "description": "List the assets in an asset library from Blender's preferences (for example the "
                       "`Poly Haven` library the Poly Haven add-on fills): kind, name and the .blend file "
                       "they are in. Read-only.",
        "read_only": True, "code": LIBRARY_LIST, "addon": None,
        "params": {
            "library": {"type": "string", "required": True, "description": "The library's name in Preferences."},
            "kind": {"type": "string", "enum": ["all", *LIBRARY_KINDS], "default": "all"},
            "query": {"type": "string", "default": "", "description": "Part of the asset name or folder."},
            "limit": {"type": "integer", "default": 50, "minimum": 1, "maximum": 500},
        },
    },
    "library_import": {
        "description": "Append or link one asset from an asset library into the open scene. Objects and "
                       "collections are placed in the scene, a material can replace the materials of named "
                       "objects, a world can become the scene's world. Check the result with get_scene_info "
                       "and look.",
        "read_only": False, "code": LIBRARY_IMPORT, "addon": None,
        "params": {
            "library": {"type": "string", "required": True},
            "file": {"type": "string", "required": True, "description": "The `file` from library_list."},
            "name": {"type": "string", "required": True},
            "kind": {"type": "string", "enum": list(LIBRARY_KINDS), "required": True},
            "link": {"type": "boolean", "default": False,
                     "description": "Link instead of append (keeps the library file as the source)."},
            "apply_to": {"type": "array", "items": {"type": "string"}, "default": [],
                         "description": "materials: objects whose materials it replaces."},
            "set_world": {"type": "boolean", "default": True, "description": "worlds: make it the scene's world."},
        },
    },
}


def builtin_code(name, values):
    return PRELUDE.format(args=json.dumps(values)) + BUILTINS[name]["code"] + FINISH.format(marker=MARKER)


# ---------------------------------------------------------------------------
# Talking to Blender


def blender_address():
    host = os.environ.get("BLENDER_HOST", "localhost")
    try:
        port = int(os.environ.get("BLENDER_PORT", "9876"))
    except ValueError:
        raise BlenderError("BLENDER_PORT is not a port number")
    return host, port


def send_code(code, timeout=None):
    """Run code in Blender through the MCP for Blender add-on and return what it
    printed. Each call opens its own connection."""
    timeout = timeout or float(os.environ.get("BLENDER_ADDON_TOOLS_TIMEOUT", "300"))
    host, port = blender_address()
    try:
        conn = socket.create_connection((host, port), timeout=10)
    except OSError as e:
        raise BlenderError(f"cannot reach Blender at {host}:{port} ({e.strerror or e}). In Blender, open the "
                           "MCP for Blender sidebar tab and click Connect to MCP server.")
    with conn:
        conn.settimeout(timeout)
        conn.sendall(json.dumps({"type": "execute_code", "params": {"code": code}}).encode("utf-8"))
        buffer = b""
        while True:
            try:
                chunk = conn.recv(65536)
            except socket.timeout:
                raise BlenderError(f"Blender did not answer within {timeout:.0f} s")
            if not chunk:
                raise BlenderError("Blender closed the connection without an answer")
            buffer += chunk
            try:
                reply = json.loads(buffer.decode("utf-8"))
                break
            except (ValueError, UnicodeDecodeError):
                continue
    if reply.get("status") == "error":
        message = reply.get("message", "unknown error")
        try:
            detail = json.loads(message)
            # Only the frames in the code this server sent say where it failed.
            frames = [line.strip() for line in detail.get("traceback", "").splitlines()
                      if line.strip().startswith('File "<string>"')]
            message = f"{detail.get('exception_type', 'Error')}: {detail.get('message', '')}"
            if frames:
                where = frames[-1].replace('File "<string>", ', "")
                message += f" ({where} of the sent code)"
        except (ValueError, AttributeError):
            pass
        raise BlenderError(message)
    result = reply.get("result") or {}
    return result.get("result", "") if isinstance(result, dict) else str(result)


def parse_output(printed):
    """What the script reported, and anything else it printed."""
    found, other = None, []
    for line in printed.splitlines():
        if line.startswith(MARKER):
            found = json.loads(line[len(MARKER):])
        else:
            other.append(line)
    return found, "\n".join(other).strip()


def run_tool(name, arguments, tools):
    if name in BUILTINS:
        tool = BUILTINS[name]
        values = validate_args(tool, arguments)
        code = builtin_code(name, values)
    elif name in tools:
        tool = tools[name]
        values = validate_args(tool, arguments)
        code = tool_code(tool, values)
    else:
        raise Invalid(f"no tool `{name}`")
    found, other = parse_output(send_code(code))
    out = dict(found or {})
    if other:
        out["printed"] = other[-4000:]
    return out


# ---------------------------------------------------------------------------
# MCP over stdio (newline-delimited JSON-RPC 2.0)


def tool_listing(tools):
    listed = []
    for name, tool in [*BUILTINS.items(), *tools.items()]:
        entry = {"name": name, "description": tool.get("description") or name,
                 "inputSchema": input_schema(tool["params"])}
        entry["annotations"] = {"readOnlyHint": tool["read_only"], "destructiveHint": not tool["read_only"]}
        listed.append(entry)
    return listed


def handle(message, directory=None):
    """One JSON-RPC message in, one reply (or None for a notification) out."""
    method, ident = message.get("method"), message.get("id")
    if ident is None:
        return None
    try:
        if method == "initialize":
            asked = (message.get("params") or {}).get("protocolVersion")
            result = {"protocolVersion": asked if asked in PROTOCOLS else PROTOCOLS[0],
                      "capabilities": {"tools": {}},
                      "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            tools, problems = load_tools(directory)
            for problem in problems:
                print(f"{SERVER_NAME}: {problem}", file=sys.stderr)
            result = {"tools": tool_listing(tools)}
        elif method == "tools/call":
            params = message.get("params") or {}
            tools, _ = load_tools(directory)
            try:
                out = run_tool(params.get("name"), params.get("arguments"), tools)
                result = {"content": [{"type": "text", "text": json.dumps(out, indent=2)}], "isError": False}
            except (Invalid, BlenderError) as e:
                result = {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
        else:
            return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32601, "message": f"no method {method}"}}
    except Exception as e:  # a bad manifest or an unexpected reply must not end the server
        return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32603, "message": str(e)}}
    return {"jsonrpc": "2.0", "id": ident, "result": result}


def serve(stdin=sys.stdin, stdout=sys.stdout, directory=None):
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "not JSON"}}
        else:
            reply = handle(message, directory)
        if reply is not None:
            stdout.write(json.dumps(reply) + "\n")
            stdout.flush()


# ---------------------------------------------------------------------------
# Drafting a manifest


def slug(module):
    last = module.split(".")[-1].lower()
    return re.sub(r"[^a-z0-9_]+", "_", last).strip("_") or "addon"


def draft_param(prop):
    """A manifest parameter for one operator property, or None if it has none."""
    kind = prop["type"]
    spec = {"description": (prop.get("description") or prop.get("name") or "").strip()}
    if kind in ("POINTER", "COLLECTION") or prop.get("hidden"):
        return None
    scalar = {"BOOLEAN": "boolean", "INT": "integer", "FLOAT": "number", "STRING": "string"}
    if kind == "ENUM":
        if not prop.get("items"):
            # A dynamic enum: its items depend on context, so it is offered as text.
            spec["type"] = "string"
            spec["description"] = (spec["description"] + " (items depend on the scene)").strip()
        elif prop.get("flag"):
            spec.update(type="array", items={"type": "string", "enum": prop["items"]})
        else:
            spec.update(type="string", enum=prop["items"])
    elif "array_length" in prop:
        if kind not in scalar or kind == "STRING":
            return None
        spec.update(type="array", items={"type": scalar[kind]}, minItems=prop["array_length"],
                    maxItems=prop["array_length"])
    elif kind in scalar:
        spec["type"] = scalar[kind]
        if kind in ("INT", "FLOAT"):
            for key, bound in (("minimum", "min"), ("maximum", "max")):
                value = prop.get(bound)
                if value is not None and abs(value) < 2 ** 31 - 1:
                    spec[key] = round(value, 6) if kind == "FLOAT" else value
    else:
        return None
    if "default" in prop:
        default = prop["default"]
        if spec["type"] == "number" and isinstance(default, int):
            default = float(default)
        try:
            validate_value(prop["identifier"], spec, default)
            spec["default"] = default
        except Invalid:
            pass
    if not spec["description"]:
        del spec["description"]
    return spec


def draft_manifest(inspected):
    """A manifest from addon_inspect's report: one tool per operator, every one
    switched off for the user to review."""
    prefix = slug(inspected["module"])
    spaces = [p["space"] for p in inspected.get("panels", []) if p.get("space") in CONTEXTS]
    context = max(set(spaces), key=spaces.count) if spaces else None
    tools, names = [], set()
    for op in inspected["operators"]:
        base = re.sub(r"[^a-z0-9_]+", "_", op["idname"].split(".", 1)[1].lower()).strip("_")
        name = f"{prefix}_{base}"[:48].rstrip("_")
        while name in names or name in BUILTINS:
            name = name[:45] + f"_{len(names) % 100:02d}"
        names.add(name)
        params = {}
        for prop in op["properties"]:
            spec = draft_param(prop)
            if spec is not None and TOOL_NAME.match(prop["identifier"]):
                params[prop["identifier"]] = spec
        tool = {"name": name, "enabled": False, "read_only": False,
                "description": op["description"] or op["label"] or op["idname"],
                "op": op["idname"], "params": params}
        if context:
            tool["context"] = context
        tools.append(tool)
    return {"addon": inspected["module"], "name": inspected.get("name"), "seen_version": inspected.get("version"),
            "note": "Drafted by `server.py discover`. Every tool is off: read each one, set `enabled` "
                    "to true for the ones to use, mark the ones that change nothing `read_only`.",
            "tools": tools}


def headless_run(code, blender):
    """Run code in a background Blender (with the user's add-ons) and return what it printed."""
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "inspect.py"
        script.write_text(code, encoding="utf-8")
        done = subprocess.run([blender, "-b", "--python-exit-code", "1", "--python", str(script)],
                              capture_output=True, text=True, timeout=600)
    if done.returncode != 0:
        raise BlenderError("Blender failed:\n" + (done.stderr or done.stdout)[-2000:])
    return done.stdout


def inspect_addon(module, blender=None):
    code = builtin_code("addon_inspect", {"module": module})
    printed = headless_run(code, blender) if blender else send_code(code)
    found, _ = parse_output(printed)
    if not found:
        raise BlenderError("the inspection printed no report")
    return found


def find_blender(given):
    if given:
        return given
    return os.environ.get("BLENDER_BIN") or shutil.which("blender")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("serve", help="serve over stdio (the default)")
    listing = sub.add_parser("list", help="the add-ons enabled in the connected Blender")
    listing.add_argument("--all", action="store_true", help="also list disabled ones")
    discover = sub.add_parser("discover", help="write a draft manifest for one add-on")
    discover.add_argument("module", help="the add-on's module name (from `list`)")
    discover.add_argument("--out", help="folder for the draft (default: the tools folder)")
    discover.add_argument("--headless", action="store_true", help="use a background Blender instead of the open one")
    discover.add_argument("--blender", help="the Blender executable for --headless (or BLENDER_BIN)")
    check = sub.add_parser("check", help="validate the manifests and print their tools")
    check.add_argument("--dir", help="the tools folder (default: BLENDER_ADDON_TOOLS_DIR)")
    args = parser.parse_args(argv)

    try:
        if args.command in (None, "serve"):
            serve()
            return 0
        if args.command == "list":
            found, _ = parse_output(send_code(builtin_code("addons_list", {"include_disabled": args.all})))
            for addon in (found or {}).get("addons", []):
                state = "" if addon["enabled"] else "  (off)"
                print(f"{addon['module']:40}  {addon['name']} {addon['version']}{state}")
            return 0
        if args.command == "discover":
            if not MODULE_NAME.match(args.module):
                raise Invalid(f"`{args.module}` is not a module name")
            blender = find_blender(args.blender) if args.headless else None
            if args.headless and not blender:
                raise BlenderError("no Blender found: pass --blender or set BLENDER_BIN")
            draft = draft_manifest(inspect_addon(args.module, blender))
            out = Path(args.out) if args.out else tools_dir()
            out.mkdir(parents=True, exist_ok=True)
            target = out / f"{slug(args.module)}.json"
            if target.exists():
                # Never touch a manifest in use; drafts are not loaded until renamed.
                target = out / f"{slug(args.module)}.draft.json"
            if target.exists():
                raise Invalid(f"{target} already exists; move it before drafting again")
            target.write_text(json.dumps(draft, indent=2) + "\n", encoding="utf-8")
            print(f"wrote {target}: {len(draft['tools'])} operators, all switched off")
            return 0
        if args.command == "check":
            tools, problems = load_tools(args.dir, include_disabled=True)
            for name, tool in tools.items():
                state = "on " if tool["enabled"] else "off"
                kind = "read" if tool["read_only"] else "edit"
                print(f"{state} {kind}  {name:40}  {tool.get('op') or 'code'}  ({tool['addon']})")
            for problem in problems:
                print(f"error: {problem}", file=sys.stderr)
            return 1 if problems else 0
    except (Invalid, BlenderError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
