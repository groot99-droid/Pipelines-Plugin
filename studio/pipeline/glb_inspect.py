"""What is in a GLB, read without Blender. Stdlib only.

    python studio/pipeline/glb_inspect.py <file.glb> [--budget tris=30000,mb=20,tex=2048,height=0.5-2.5] [--json]

It reads the binary glTF header, the JSON chunk and the image headers in the
BIN chunk, and reports: triangles per mesh and in all, vertices, materials,
textures and their sizes, the bounding box in the scene's own units (glTF is
metres, Y up) with every node's transform applied, the height, and whether the
model carries a skin or animations.

--budget turns the report into findings. Each limit is a maximum, except
`height`, which is a range in metres. A model over its budget exits 1, so a
review can say pass or fail per limit. It reads the file and writes nothing.

Exit codes: 0 read and within budget, 1 over budget, 2 not a GLB this can read.
"""

import argparse
import json
import math
import struct
import sys
from pathlib import Path

EXIT_OK, EXIT_OVER, EXIT_USAGE = 0, 1, 2
MAGIC, JSON_CHUNK, BIN_CHUNK = 0x46546C67, 0x4E4F534A, 0x004E4942
COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
IDENTITY = [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]


class NotGlb(Exception):
    pass


def read_glb(data):
    """(the glTF JSON, the BIN chunk or b"")."""
    if len(data) < 20:
        raise NotGlb("too short to be a GLB")
    magic, version, length = struct.unpack_from("<III", data, 0)
    if magic != MAGIC:
        raise NotGlb("no glTF magic; this is not a binary glTF file")
    if version != 2:
        raise NotGlb(f"glTF version {version}; only 2 is read")
    if length > len(data):
        raise NotGlb(f"the header says {length} bytes and the file has {len(data)}: it is cut short")
    offset, doc, binary = 12, None, b""
    while offset + 8 <= length:
        size, kind = struct.unpack_from("<II", data, offset)
        chunk = data[offset + 8: offset + 8 + size]
        if kind == JSON_CHUNK:
            try:
                doc = json.loads(chunk.decode("utf-8"))
            except ValueError as err:
                raise NotGlb(f"the JSON chunk does not parse: {err}")
        elif kind == BIN_CHUNK:
            binary = chunk
        offset += 8 + size + (-size % 4)
    if doc is None:
        raise NotGlb("no JSON chunk")
    return doc, binary


# ── transforms ───────────────────────────────────────────────────────────────

def multiply(a, b):
    """Two column-major 4x4 matrices, as glTF stores them."""
    return [sum(a[k * 4 + r] * b[c * 4 + k] for k in range(4)) for c in range(4) for r in range(4)]


def node_matrix(node):
    if "matrix" in node:
        return [float(v) for v in node["matrix"]]
    tx, ty, tz = node.get("translation", [0, 0, 0])
    x, y, z, w = node.get("rotation", [0, 0, 0, 1])
    sx, sy, sz = node.get("scale", [1, 1, 1])
    rotation = [1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w),
                2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w),
                2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y)]
    return [rotation[0] * sx, rotation[1] * sx, rotation[2] * sx, 0,
            rotation[3] * sy, rotation[4] * sy, rotation[5] * sy, 0,
            rotation[6] * sz, rotation[7] * sz, rotation[8] * sz, 0,
            tx, ty, tz, 1]


def apply(m, point):
    x, y, z = point
    return (m[0] * x + m[4] * y + m[8] * z + m[12],
            m[1] * x + m[5] * y + m[9] * z + m[13],
            m[2] * x + m[6] * y + m[10] * z + m[14])


def mesh_instances(doc):
    """(mesh index, world matrix) for every node that draws a mesh in the
    default scene. With no scene, every root node."""
    nodes = doc.get("nodes", [])
    scenes = doc.get("scenes", [])
    if scenes:
        roots = scenes[doc.get("scene", 0)].get("nodes", [])
    else:
        children = {c for n in nodes for c in n.get("children", [])}
        roots = [i for i in range(len(nodes)) if i not in children]
    found, stack = [], [(i, IDENTITY) for i in roots]
    seen = set()
    while stack:
        index, parent = stack.pop()
        if index in seen or index >= len(nodes):
            continue
        seen.add(index)
        node = nodes[index]
        world = multiply(parent, node_matrix(node))
        if "mesh" in node:
            found.append((node["mesh"], world))
        stack.extend((child, world) for child in node.get("children", []))
    return found


# ── images ───────────────────────────────────────────────────────────────────

def image_size(raw):
    """(width, height) of a PNG, JPEG or WebP, or None."""
    if raw[:8] == b"\x89PNG\r\n\x1a\n" and len(raw) >= 24:
        return struct.unpack(">II", raw[16:24])
    if raw[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(raw):
            if raw[i] != 0xFF:
                i += 1
                continue
            marker = raw[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", raw[i + 5: i + 9])
                return width, height
            i += 2 + struct.unpack(">H", raw[i + 2: i + 4])[0]
        return None
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP" and len(raw) >= 30:
        if raw[12:16] == b"VP8 ":
            w, h = struct.unpack("<HH", raw[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if raw[12:16] == b"VP8L":
            bits = int.from_bytes(raw[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if raw[12:16] == b"VP8X":
            return int.from_bytes(raw[24:27], "little") + 1, int.from_bytes(raw[27:30], "little") + 1
    return None


# ── the report ───────────────────────────────────────────────────────────────

def primitive_triangles(doc, primitive):
    accessors = doc.get("accessors", [])
    mode = primitive.get("mode", 4)
    if "indices" in primitive:
        count = accessors[primitive["indices"]]["count"]
    elif "POSITION" in primitive.get("attributes", {}):
        count = accessors[primitive["attributes"]["POSITION"]]["count"]
    else:
        return 0
    if mode == 4:
        return count // 3
    if mode in (5, 6):
        return max(count - 2, 0)
    return 0  # points and lines draw no triangles


def inspect(data, size_bytes=None):
    doc, binary = read_glb(data)
    accessors = doc.get("accessors", [])
    meshes = doc.get("meshes", [])
    per_mesh = []
    for index, mesh in enumerate(meshes):
        tris = sum(primitive_triangles(doc, p) for p in mesh.get("primitives", []))
        verts = sum(accessors[p["attributes"]["POSITION"]]["count"]
                    for p in mesh.get("primitives", []) if "POSITION" in p.get("attributes", {}))
        per_mesh.append({"mesh": mesh.get("name") or f"mesh {index}", "triangles": tris, "vertices": verts})
    instances = mesh_instances(doc)
    low, high = [math.inf] * 3, [-math.inf] * 3
    drawn_tris = 0
    for mesh_index, world in instances:
        if mesh_index >= len(meshes):
            continue
        drawn_tris += per_mesh[mesh_index]["triangles"]
        for primitive in meshes[mesh_index].get("primitives", []):
            position = primitive.get("attributes", {}).get("POSITION")
            if position is None or "min" not in accessors[position]:
                continue
            a, b = accessors[position]["min"], accessors[position]["max"]
            for corner in ((x, y, z) for x in (a[0], b[0]) for y in (a[1], b[1]) for z in (a[2], b[2])):
                for axis, value in enumerate(apply(world, corner)):
                    low[axis] = min(low[axis], value)
                    high[axis] = max(high[axis], value)
    bbox = None
    if low[0] != math.inf:
        bbox = {"min": [round(v, 4) for v in low], "max": [round(v, 4) for v in high],
                "size": [round(h - l, 4) for l, h in zip(low, high)]}
    views = doc.get("bufferViews", [])
    images = []
    for index, image in enumerate(doc.get("images", [])):
        size = None
        if "bufferView" in image and image["bufferView"] < len(views):
            view = views[image["bufferView"]]
            start = view.get("byteOffset", 0)
            size = image_size(binary[start: start + view["byteLength"]])
        images.append({"image": image.get("name") or f"image {index}",
                       "mime": image.get("mimeType", "?"), "size": list(size) if size else None})
    return {
        "bytes": size_bytes if size_bytes is not None else len(data),
        "generator": doc.get("asset", {}).get("generator"),
        "triangles": drawn_tris if instances else sum(m["triangles"] for m in per_mesh),
        "meshes": per_mesh,
        "instances": len(instances),
        "materials": [m.get("name") or f"material {i}" for i, m in enumerate(doc.get("materials", []))],
        "textures": len(doc.get("textures", [])),
        "images": images,
        "bbox": bbox,
        "height_m": bbox["size"][1] if bbox else None,  # glTF is Y up
        "skins": len(doc.get("skins", [])),
        "animations": [a.get("name") or f"animation {i}" for i, a in enumerate(doc.get("animations", []))],
        "extensions_required": doc.get("extensionsRequired", []),
    }


def parse_budget(text):
    budget = {}
    for item in filter(None, (text or "").split(",")):
        key, sep, value = item.partition("=")
        key = key.strip()
        if not sep or key not in ("tris", "mb", "tex", "height"):
            raise ValueError(f"budget item `{item}`: write tris=N, mb=N, tex=N or height=LOW-HIGH")
        if key == "height":
            low, sep, high = value.partition("-")
            budget[key] = (float(low), float(high) if sep else float(low))
        else:
            budget[key] = float(value)
    return budget


def findings(report, budget):
    """(limit, passed, what was found) for each limit in the budget."""
    out = []
    if "tris" in budget:
        out.append(("tris", report["triangles"] <= budget["tris"],
                    f"{report['triangles']} triangles, budget {int(budget['tris'])}"))
    if "mb" in budget:
        mb = report["bytes"] / (1024 * 1024)
        out.append(("mb", mb <= budget["mb"], f"{mb:.2f} MB, budget {budget['mb']:g}"))
    if "tex" in budget:
        sides = [max(i["size"]) for i in report["images"] if i["size"]]
        largest = max(sides, default=0)
        unread = sum(1 for i in report["images"] if not i["size"])
        out.append(("tex", largest <= budget["tex"] and not unread,
                    f"largest texture {largest}px, budget {int(budget['tex'])}"
                    + (f"; {unread} image(s) whose size could not be read" if unread else "")))
    if "height" in budget:
        low, high = budget["height"]
        height = report["height_m"]
        out.append(("height", height is not None and low <= height <= high,
                    f"height {height} m, wanted {low:g}-{high:g} m"))
    return out


def describe(path, report):
    lines = [f"file       {path}  ({report['bytes'] / (1024 * 1024):.2f} MB, {report['generator'] or 'no generator'})",
             f"triangles  {report['triangles']} drawn, in {len(report['meshes'])} mesh(es), {report['instances']} instance(s)"]
    for mesh in report["meshes"]:
        lines.append(f"  mesh     {mesh['mesh']}: {mesh['triangles']} tris, {mesh['vertices']} verts")
    lines.append(f"materials  {len(report['materials'])}: {', '.join(report['materials']) or 'none'}")
    lines.append(f"textures   {report['textures']}, images: "
                 + (", ".join(f"{i['size'][0]}x{i['size'][1]}" if i["size"] else f"{i['mime']} (size unread)"
                              for i in report["images"]) or "none"))
    if report["bbox"]:
        size = report["bbox"]["size"]
        lines.append(f"bbox       {size[0]} x {size[1]} x {size[2]} (x, y up, z), min {report['bbox']['min']}")
    else:
        lines.append("bbox       none: no positions with min and max")
    lines.append(f"rig        {report['skins']} skin(s); animations: {', '.join(report['animations']) or 'none'}")
    if report["extensions_required"]:
        lines.append(f"requires   {', '.join(report['extensions_required'])}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="glb_inspect.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file")
    parser.add_argument("--budget", help="tris=N,mb=N,tex=N,height=LOW-HIGH")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    path = Path(args.file)
    try:
        budget = parse_budget(args.budget)
        report = inspect(path.read_bytes(), path.stat().st_size)
    except (OSError, ValueError, NotGlb, KeyError, IndexError, struct.error) as err:
        print(f"error     {path}: {err}", file=sys.stderr)
        return EXIT_USAGE
    checked = findings(report, budget)
    if args.json:
        report["findings"] = [{"limit": k, "pass": ok, "found": what} for k, ok, what in checked]
        print(json.dumps(report, indent=2))
    else:
        print(describe(path, report))
        for key, ok, what in checked:
            print(f"{'pass' if ok else 'OVER':<10} {key}: {what}")
    return EXIT_OK if all(ok for _, ok, _ in checked) else EXIT_OVER


if __name__ == "__main__":
    sys.exit(main())
