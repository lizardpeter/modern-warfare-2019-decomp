#!/usr/bin/env python3
"""Decode model surfaces (xmodelsurfs, type 0x0C) from a zone into plain meshes.

Every rule here is documented, with its evidence, in docs/assets/models.md. The zone is loaded by the translated
loaders (tools/assets/loaders/load.py), so only the original fastfile is needed.

    python3 tools/assets/xmodel.py <zone.ff> [--obj out_dir]     list surfaces, optionally write OBJ files
"""
from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "loaders"))

ABSENT = 0xFFFFFFFF


@dataclass
class Mesh:
    name: str
    positions: np.ndarray      # (n, 3) float
    normals: np.ndarray        # (n, 3)
    tangents: np.ndarray       # (n, 3)
    bitangent_sign: np.ndarray # (n,) +1 / -1: bitangent = sign * cross(normal, tangent)
    uvs: np.ndarray            # (n, 2)
    colours: np.ndarray | None # (n, 4) uint8 RGBA
    bones: np.ndarray          # (n, 8) bone indices (unused slots 0 with weight 0)
    weights: np.ndarray        # (n, 8)
    triangles: np.ndarray      # (t, 3), clockwise front faces


def _u32(s, o):
    return struct.unpack_from("<I", s, o)[0]


def positions(blob, s, nv):
    """+0x28: u64 per vertex, 21 bits per axis biased by 2^20; scale at +0xAC, offset at +0xA0."""
    p = np.frombuffer(blob, dtype=np.uint64, count=nv, offset=_u32(s, 0x28))
    q = np.stack([((p >> np.uint64(k)) & np.uint64(0x1FFFFF)).astype(np.float64) for k in (0, 21, 42)], 1)
    scale = np.array(struct.unpack_from("<3f", s, 0xAC))
    offset = np.array(struct.unpack_from("<3f", s, 0xA0))
    return (q - 2**20) / 2**20 * scale + offset


def tangent_frame(blob, s, nv):
    """+0x34: smallest-three quaternion, 10/10/9 bits, bit 29 bitangent sign, bits 30-31 the dropped component."""
    u = np.frombuffer(blob, dtype=np.uint32, count=nv, offset=_u32(s, 0x34)).astype(np.int64)
    a = ((u & 1023) / 511.5 - 1) / np.sqrt(2)
    b = (((u >> 10) & 1023) / 511.5 - 1) / np.sqrt(2)
    c = (((u >> 20) & 511) / 255.5 - 1) / np.sqrt(2)
    w = np.sqrt(np.clip(1 - a * a - b * b - c * c, 0, 1))
    largest = (u >> 30) & 3
    q = np.zeros((nv, 4))
    for i in range(4):
        m = largest == i
        q[m, i] = w[m]
        for k, comp in zip([k for k in range(4) if k != i], (a, b, c)):
            q[m, k] = comp[m]
    x, y, z, ww = q.T
    tangent = np.stack([1 - 2 * (y * y + z * z), 2 * (x * y + ww * z), 2 * (x * z - ww * y)], 1)
    normal = np.stack([2 * (x * z + ww * y), 2 * (y * z - ww * x), 1 - 2 * (x * x + y * y)], 1)
    sign = np.where((u >> 29) & 1, -1.0, 1.0)
    return normal, tangent, sign


def skin(s, influences):
    """+0x70 (byte size at +0x24): per influence group (8 x u16 vertex counts at +0x14, 1..8 bones), the first bone of
    every vertex as u32, then for each further bone one u32 {u16 bone, u16 weight / 65536} per vertex.
    The first bone's weight is 1 - the others."""
    groups = struct.unpack_from("<8H", s, 0x14)
    nv = sum(groups)
    w = np.frombuffer(influences, dtype=np.uint32)
    bones = np.zeros((nv, 8), np.int64)
    weights = np.zeros((nv, 8))
    pos = vert = 0
    for k, count in enumerate(groups):
        bones[vert:vert + count, 0] = w[pos:pos + count] & 0xFFFF
        for j in range(1, k + 1):
            e = w[pos + j * count:pos + (j + 1) * count]
            bones[vert:vert + count, j] = e & 0xFFFF
            weights[vert:vert + count, j] = (e >> 16) / 65536
        weights[vert:vert + count, 0] = 1 - weights[vert:vert + count, 1:].sum(1)
        pos += (k + 1) * count
        vert += count
    return bones, weights


def rigid(rigid_lists, bones, weights, start):
    """+0x68 (count u16 +0x08): rigid vertex lists, 8 bytes {u16 bone, u16 vertex count, u16 first triangle,
    u16 triangle count}; each list's vertices follow the previous one's and use one bone with weight 1.
    (+0xB8 holds one 0x18-byte box per list: 3 x f32 centre, 3 x f32 half size, *unverified*.)"""
    v = start
    for bone, count, _, _ in struct.iter_unpack("<4H", rigid_lists):
        bones[v:v + count, 0] = bone
        weights[v:v + count, 0] = 1.0
        v += count


def surface_mesh(name, blob, s, influences, rigid_lists=b""):
    nv = struct.unpack_from("<H", s, 2)[0]
    nt = struct.unpack_from("<H", s, 4)[0]
    normal, tangent, sign = tangent_frame(blob, s, nv)
    uv = np.frombuffer(blob, dtype=np.float16, count=2 * nv, offset=_u32(s, 0x30)).reshape(-1, 2).astype(np.float32)
    colours = None
    if _u32(s, 0x40) != ABSENT:
        colours = np.frombuffer(blob, dtype=np.uint8, count=4 * nv, offset=_u32(s, 0x40)).reshape(-1, 4)
    tris = np.frombuffer(blob, dtype=np.uint16, count=3 * nt, offset=_u32(s, 0x38)).reshape(-1, 3)
    bones = np.zeros((nv, 8), np.int64)
    weights = np.zeros((nv, 8))
    skinned_bones, skinned_weights = skin(s, influences)
    bones[:len(skinned_bones)] = skinned_bones
    weights[:len(skinned_weights)] = skinned_weights
    # blended vertices first, then the rigid lists (order of a surface with both is *unverified*)
    rigid(rigid_lists, bones, weights, len(skinned_bones))
    return Mesh(name, positions(blob, s, nv), normal, tangent, sign, uv, colours, bones, weights, tris)


@dataclass
class Skeleton:
    names: list[str]
    parents: np.ndarray        # (n,) parent index, -1 for roots
    local_rotations: np.ndarray    # (n, 4) quaternion x, y, z, w (identity for roots)
    local_translations: np.ndarray # (n, 3) in the parent's space
    world_rotations: np.ndarray    # (n, 4) bind pose
    world_translations: np.ndarray # (n, 3)


def skeleton(zone_load, header):
    """xmodel bones (loader 142EA4830). Bone count = u8 +0x14 + u16 +0x16; roots = u8 +0x15 come first.
    +0x98 u32 script-string names; for each non-root bone: +0xA0 u8 distance back to its parent, +0xA8 4 x s16
    quaternion / 32767, +0xB0 3 x f32 translation; +0xC0 0x20 bytes per bone: world quaternion, world translation,
    f32 2.0 (bind pose; recomputing it from the local values matches exactly, measured)."""
    z = zone_load
    q = lambda a: struct.unpack("<Q", z.mem.read(a, 8))[0]
    hd = z.mem.read(header, 0x2B0)
    n = hd[0x14] + struct.unpack_from("<H", hd, 0x16)[0]
    roots = hd[0x15]
    nr = n - roots
    ids = np.frombuffer(z.mem.read(q(header + 0x98), 4 * n), np.uint32)
    names = [z.strings[i - 1] if 0 < i <= len(z.strings) else f"#{i}" for i in ids]
    back = np.frombuffer(z.mem.read(q(header + 0xA0), nr), np.uint8).astype(np.int64)
    parents = np.full(n, -1)
    parents[roots:] = np.arange(roots, n) - back
    lq = np.tile([0.0, 0.0, 0.0, 1.0], (n, 1))
    lq[roots:] = np.frombuffer(z.mem.read(q(header + 0xA8), 8 * nr), np.int16).reshape(-1, 4) / 32767
    lt = np.zeros((n, 3))
    lt[roots:] = np.frombuffer(z.mem.read(q(header + 0xB0), 12 * nr), np.float32).reshape(-1, 3)
    base = np.frombuffer(z.mem.read(q(header + 0xC0), 32 * n), np.float32).reshape(-1, 8)
    return Skeleton(names, parents, lq, lt, base[:, :4].astype(np.float64), base[:, 4:7].astype(np.float64))


def meshes(zone_load):
    """Yield (xmodelsurfs name, [Mesh per surface]) for every xmodelsurfs asset of a loaded zone."""
    z = zone_load
    q = lambda a: struct.unpack("<Q", z.mem.read(a, 8))[0]
    for t, h, _ in z.assets:
        if z.types[t][0] != "xmodelsurfs":
            continue
        shared = q(h + 0x30)
        blob = z.mem.read(q(shared), _u32(z.mem.read(shared + 8, 4), 0))
        count = struct.unpack("<H", z.mem.read(h + 0x38, 2))[0]
        base, out = q(h + 8), []
        for i in range(count):
            a = base + i * 0xD0
            s = z.mem.read(a, 0xD0)
            influences = z.mem.read(q(a + 0x70), _u32(s, 0x24)) if q(a + 0x70) else b""
            lists = z.mem.read(q(a + 0x68), 8 * struct.unpack_from("<H", s, 8)[0]) if q(a + 0x68) else b""
            out.append(surface_mesh(f"{z.name(h)}#{i}", blob, s, influences, lists))
        yield z.name(h), out


def write_obj(mesh: Mesh, path: Path):
    with open(path, "w") as f:
        for p in mesh.positions:
            f.write(f"v {p[0]:.5f} {p[1]:.5f} {p[2]:.5f}\n")
        for t in mesh.uvs:
            f.write(f"vt {t[0]:.6f} {1 - t[1]:.6f}\n")
        for n in mesh.normals:
            f.write(f"vn {n[0]:.5f} {n[1]:.5f} {n[2]:.5f}\n")
        for a, b, c in mesh.triangles.astype(int) + 1:
            # clockwise front faces in the game; OBJ expects counter-clockwise
            f.write(f"f {a}/{a}/{a} {c}/{c}/{c} {b}/{b}/{b}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zone")
    ap.add_argument("--oodle", default="oo2core_7_win64.dll")
    ap.add_argument("--obj", type=Path)
    args = ap.parse_args()
    import load
    import zone
    from oodle import Oodle

    ff = open(args.zone, "rb").read()
    z = load.ZoneLoad(zone.decompress(ff, Oodle(args.oodle)), ff[:0x88])
    z.load()
    for name, surfaces in meshes(z):
        for m in surfaces:
            print(f"{m.name}: {len(m.positions)} vertices, {len(m.triangles)} triangles, {len(set(m.bones[:, 0].tolist()))} first bones")
            if args.obj:
                args.obj.mkdir(parents=True, exist_ok=True)
                write_obj(m, args.obj / (m.name.replace("#", "_") + ".obj"))


if __name__ == "__main__":
    main()
