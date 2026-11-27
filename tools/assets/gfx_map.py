#!/usr/bin/env python3
"""Read the world geometry of a map (gfx_map + gfx_map_trzone). Rules: docs/assets/maps.md.

    python3 tools/assets/gfx_map.py <zone.ff> [--fp zone.fp] [--oodle DLL] [--obj out.obj]

`world(zone_load)` returns one WorldGroup per vertex group: positions (float32), normals and tangents (the same
quaternion tangent frame as model surfaces), bitangent signs, lightmap UVs, colours, texture UVs per layer and the
surfaces drawn from the group (material name, triangles). `static_models(zone_load)` lists the placed models
(xmodel, origin, rotation, scale).
"""
from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "loaders"))
import xmodel  # noqa: E402

SURFACE_SIZE, GROUP_SIZE = 0x28, 0x58


@dataclass
class WorldSurface:
    material: str
    triangles: np.ndarray          # (t, 3) indices into the group's vertices, clockwise front faces
    flags: int
    bounds: tuple                  # (mins xyz, size xyz)


@dataclass
class WorldGroup:
    positions: np.ndarray
    normals: np.ndarray
    tangents: np.ndarray
    bitangent_sign: np.ndarray
    lightmap_uv: np.ndarray        # (n, 2)
    colours: np.ndarray | None     # (n, 4) RGBA8
    uvs: np.ndarray                # (n, layers, 2)
    layer_blend: list              # per layer after the first: (n, 4) uint8, *meaning unverified*
    surfaces: list = field(default_factory=list)


def world(zone_load):
    z = zone_load
    q = lambda a: struct.unpack("<Q", z.mem.read(a, 8))[0]
    u32 = lambda a: struct.unpack("<I", z.mem.read(a, 4))[0]
    gfx = trzone = None
    for t, h, _ in z.assets:
        name = z.types[t][0]
        if name == "gfx_map":
            gfx = h
        elif name == "gfx_map_trzone" and trzone is None:
            trzone = h
    if gfx is None or trzone is None:
        return []
    # gfx_map_trzone +0x10: {u32 posData size, u32 auxData size, posData, auxData, ..., +0x98 u32 index count,
    # +0xA0 u16 indices} (142EAB6F0: "world posData", "world auxData", "bsp index buffer")
    pos = z.mem.read(q(trzone + 0x18), u32(trzone + 0x10))
    aux = z.mem.read(q(trzone + 0x20), u32(trzone + 0x14))
    indices = np.frombuffer(z.mem.read(q(trzone + 0xB0), 2 * u32(trzone + 0xA8)), np.uint16)
    nsurf, ngroup = u32(gfx + 0xC8), u32(gfx + 0xCC)
    surfaces = z.mem.read(q(gfx + 0x100), SURFACE_SIZE * nsurf)
    bounds = np.frombuffer(z.mem.read(q(gfx + 0x110), 0x18 * nsurf), np.float32).reshape(-1, 6)
    groups = np.frombuffer(z.mem.read(q(gfx + 0x148), GROUP_SIZE * ngroup), np.uint32).reshape(-1, GROUP_SIZE // 4)
    counts = {}
    for i in range(nsurf):
        _, _, nv, _, _, _, g = struct.unpack_from("<IfHHIQI", surfaces, i * SURFACE_SIZE)
        counts[g] = nv
    out = []
    for g, row in enumerate(groups):
        nv = counts.get(g, 0)
        layers = int(row[1])
        P = np.frombuffer(pos, np.float32, count=3 * nv, offset=int(row[2])).reshape(-1, 3)
        frame = np.frombuffer(aux, np.uint32, count=nv, offset=int(row[3]))
        N, T, sign = xmodel.unpack_tangent_frame(frame)
        lm = np.frombuffer(aux, np.float32, count=2 * nv, offset=int(row[4])).reshape(-1, 2) if row[4] else np.zeros((nv, 2))
        col = np.frombuffer(aux, np.uint8, count=4 * nv, offset=int(row[5])).reshape(-1, 4) if row[5] else None
        uv = np.frombuffer(aux, np.float32, count=2 * layers * nv, offset=int(row[6])).reshape(nv, layers, 2)
        blend = [np.frombuffer(aux, np.uint8, count=4 * nv, offset=int(row[7 + k])).reshape(-1, 4)
                 for k in range(layers - 1) if row[7 + k]]
        out.append(WorldGroup(P, N, T, sign, lm, col, uv, blend))
    for i in range(nsurf):
        off, _, nv, nt, base, material, g, _, flags, _ = struct.unpack_from("<IfHHIQIIII", surfaces, i * SURFACE_SIZE)
        tris = indices[base:base + 3 * nt].reshape(-1, 3)
        mname = z.name(material) if material else ""
        b = bounds[i]
        out[g].surfaces.append(WorldSurface(mname, tris, flags, (tuple(b[:3]), tuple(b[3:]))))
    return out


@dataclass
class StaticModel:
    model: str                     # xmodel name
    model_header: int              # the xmodel's address in the loaded zone
    origin: tuple
    rotation: tuple                # quaternion x, y, z, w
    scale: float
    bounds: tuple                  # world box: centre xyz, half size xyz


def static_models(zone_load):
    """Placed models of a map (gfx_map +0x190, loader 142EA37B0). Counts at +0x190: u32 [0] smodel surfaces,
    [1] models, [2] instances. +0x1D0: per model 0x10 bytes {xmodel, u16 flags, u16 first smodel surface};
    +0x1E0 ("collections"): per instance-run 0x10 bytes {u32 first instance, u32 count, u32 model, u32 flags};
    +0x1F8: per run 0x18 bytes, world box centre and half size; +0x2E0: per instance 0x18 bytes, origin as
    3 x s32 / 4096, rotation as 4 x u16 (v - 0x8000) / 32767 in x, y, z, w order, f32 scale."""
    z = zone_load
    q = lambda a: struct.unpack("<Q", z.mem.read(a, 8))[0]
    gfx = next((h for t, h, _ in z.assets if z.types[t][0] == "gfx_map"), None)
    if gfx is None:
        return []
    counts = struct.unpack("<3I", z.mem.read(gfx + 0x190, 12))
    nmodels, ninst = counts[1], counts[2]
    models = [struct.unpack_from("<Q", z.mem.read(q(gfx + 0x1D0) + 0x10 * i, 8))[0] for i in range(nmodels)]
    runs = np.frombuffer(z.mem.read(q(gfx + 0x1E0), 0x10 * ninst), np.uint32).reshape(-1, 4)
    boxes = np.frombuffer(z.mem.read(q(gfx + 0x1F8), 0x18 * ninst), np.float32).reshape(-1, 6)
    place = np.frombuffer(z.mem.read(q(gfx + 0x2E0), 0x18 * ninst), np.uint8).reshape(-1, 0x18)
    origin = place[:, :12].copy().view(np.int32).reshape(-1, 3) / 4096.0
    rot = (place[:, 12:20].copy().view(np.uint16).reshape(-1, 4).astype(np.float64) - 0x8000) / 32767.0
    scale = place[:, 20:24].copy().view(np.float32).ravel()
    out = []
    for r, (first, count, mi, _) in enumerate(runs):
        xh = models[mi]
        for i in range(first, first + count):
            out.append(StaticModel(z.name(xh), xh, tuple(origin[i]), tuple(rot[i]), float(scale[i]),
                                   (tuple(boxes[r, :3]), tuple(boxes[r, 3:]))))
    return out


def write_obj(groups, path):
    with open(path, "w") as f:
        base = 1
        for gi, g in enumerate(groups):
            if not g.surfaces:
                continue
            f.write(f"o group{gi}\n")
            for p in g.positions:
                f.write(f"v {p[0]:.3f} {p[1]:.3f} {p[2]:.3f}\n")
            for t in g.uvs[:, 0]:
                f.write(f"vt {t[0]:.5f} {1 - t[1]:.5f}\n")
            for n in g.normals:
                f.write(f"vn {n[0]:.4f} {n[1]:.4f} {n[2]:.4f}\n")
            for s in g.surfaces:
                f.write(f"usemtl {s.material}\n")
                for a, b, c in s.triangles.astype(int) + base:
                    f.write(f"f {a}/{a}/{a} {c}/{c}/{c} {b}/{b}/{b}\n")
            base += len(g.positions)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zone")
    ap.add_argument("--fp")
    ap.add_argument("--oodle", default="oo2core_7_win64.dll")
    ap.add_argument("--obj", type=Path)
    a = ap.parse_args()
    import load
    import zone
    from oodle import Oodle

    ff = open(a.zone, "rb").read()
    o = Oodle(a.oodle)
    if a.fp:
        import fastfile_patch
        fp = open(a.fp, "rb").read()
        header, data = fastfile_patch.patch_header(fp)[1], fastfile_patch.patched(ff, fp, o)
    else:
        header, data = ff[:zone.HEADER_SIZE], zone.decompress(ff, o)
    z = load.ZoneLoad(data, header)
    z.load()
    groups = world(z)
    print(f"{len(groups)} vertex groups, {sum(len(g.positions) for g in groups)} vertices, "
          f"{sum(len(s.triangles) for g in groups for s in g.surfaces)} triangles, "
          f"{len({s.material for g in groups for s in g.surfaces})} materials")
    placed = static_models(z)
    print(f"{len(placed)} static models of {len({m.model for m in placed})} kinds")
    if a.obj:
        write_obj(groups, a.obj)


if __name__ == "__main__":
    main()
