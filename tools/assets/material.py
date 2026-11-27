#!/usr/bin/env python3
"""Read materials (type 0x0B): their texture table and constants. Rules: docs/assets/materials.md.

A material whose name starts with ',' (as in map zones) is a reference: its contents are in another zone, e.g. the
map's `techsets_<map>` zone. Images are referenced by name; the image's own header (with its stream keys) is in the
zone that holds the full image (docs/assets/images.md).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

# texture slot -> meaning, measured from the names of the images used in each slot (techsets_mp_cave, 2,132
# materials). Layered materials repeat a slot for layers 0..4.
SLOTS = {**{i: f"colour, layer {i}" for i in range(5)},
         **{9 + i: f"normal, layer {i}" for i in range(5)},
         0x12: "emissive", 0x13: "emissive 2", 0x14: "emissive 3",
         **{0x1B + i: f"per-layer map defaulting to white, layer {i} (*unverified*: gloss / occlusion)" for i in range(5)},
         0x2D: "thermal",
         **{0x3B + i: f"per-layer map defaulting to black, layer {i} (*unverified*)" for i in range(5)},
         **{0x5F + i: f"displacement / height, layer {i}" for i in range(5)}}


@dataclass
class Material:
    name: str
    textures: list        # (slot, image name)
    constants: list       # (u32 id, 4 x f32)
    techset: int          # address of the techset asset (+0x40)


def read_material(read, name_of, a: int) -> Material:
    """Header 0x78 bytes (loader 142E84320): +0x1C u8 texture count, +0x1D u8 constant count, +0x40 techset,
    +0x48 textures (0x10 each: u8 slot at +0, image at +8), +0x50 constants (0x14 each: u32 id, 4 x f32)."""
    h = read(a, 0x78)
    q = lambda o: struct.unpack_from("<Q", h, o)[0]
    textures = []
    if h[0x1C] and q(0x48):
        t = read(q(0x48), 0x10 * h[0x1C])
        for i in range(h[0x1C]):
            textures.append((t[0x10 * i], name_of(struct.unpack_from("<Q", t, 0x10 * i + 8)[0]).lstrip(",")))
    constants = []
    if h[0x1D] and q(0x50):
        c = read(q(0x50), 0x14 * h[0x1D])
        for i in range(h[0x1D]):
            constants.append((struct.unpack_from("<I", c, 0x14 * i)[0], struct.unpack_from("<4f", c, 0x14 * i + 4)))
    return Material(name_of(a), textures, constants, q(0x40))
