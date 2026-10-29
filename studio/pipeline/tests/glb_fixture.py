"""A small GLB built in the test, so no model file is checked in: a box made of
triangles, with one material, one embedded PNG and, if asked, a node
transform."""

import json
import struct
import zlib


def png(width, height):
    """A flat grey PNG of the given size."""
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    rows = b"".join(b"\x00" + b"\x80\x80\x80" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def box_glb(size=(1.0, 2.0, 0.5), translation=None, scale=None, texture=(8, 4), name="box"):
    """A box `size` (x, y up, z) metres, sitting on y=0, as a GLB's bytes. 12 triangles."""
    sx, sy, sz = size
    corners = [(x, y, z) for x in (-sx / 2, sx / 2) for y in (0.0, sy) for z in (-sz / 2, sz / 2)]
    faces = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1),
             (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    positions = b"".join(struct.pack("<fff", *c) for c in corners)
    indices = b"".join(struct.pack("<HHH", *f) for f in faces)
    image = png(*texture) if texture else b""

    def pad(data):
        return data + b"\x00" * (-len(data) % 4)

    binary = pad(positions) + pad(indices)
    image_offset = len(binary)
    binary += pad(image)
    node = {"mesh": 0, "name": name}
    if translation:
        node["translation"] = list(translation)
    if scale:
        node["scale"] = list(scale)
    doc = {
        "asset": {"version": "2.0", "generator": "studio test fixture"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [node],
        "meshes": [{"name": name, "primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "material": 0}]}],
        "materials": [{"name": "grey", "pbrMetallicRoughness": {"baseColorFactor": [0.5, 0.5, 0.5, 1]}}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(corners), "type": "VEC3",
             "min": [-sx / 2, 0.0, -sz / 2], "max": [sx / 2, sy, sz / 2]},
            {"bufferView": 1, "componentType": 5123, "count": len(faces) * 3, "type": "SCALAR"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(positions), "target": 34962},
            {"buffer": 0, "byteOffset": len(pad(positions)), "byteLength": len(indices), "target": 34963},
        ],
        "buffers": [{"byteLength": len(binary)}],
    }
    if image:
        doc["bufferViews"].append({"buffer": 0, "byteOffset": image_offset, "byteLength": len(image)})
        doc["images"] = [{"name": "grey", "mimeType": "image/png", "bufferView": 2}]
        doc["textures"] = [{"source": 0}]
        doc["materials"][0]["pbrMetallicRoughness"]["baseColorTexture"] = {"index": 0}
    text = json.dumps(doc).encode("utf-8")
    text += b" " * (-len(text) % 4)
    body = (struct.pack("<II", len(text), 0x4E4F534A) + text
            + struct.pack("<II", len(binary), 0x004E4942) + binary)
    return struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body
