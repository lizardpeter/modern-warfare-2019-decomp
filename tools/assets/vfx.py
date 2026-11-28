#!/usr/bin/env python3
"""Read effects (vfx, type 44): emitters, their particle modules, graphs and the assets they use.
Rules: docs/assets/effects.md.

The module type names and sizes are the exe's own table at 1476DD3B0 (0x30 per type: +0x00 size, +0x08 name);
the layout of each module comes from its loader in the zone loader 142E07470.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

# type -> name, from the table at 1476DD3B0. 0..33 run when a particle is born, 34..57 every frame, 58..64 are
# tests that fire another effect.
MODULE_NAMES = (
    "InitAtlas", "InitAttributes", "InitBeam", "InitCameraOffset", "InitCloud", "InitDecal", "InitFlare",
    "InitGeoTrail", "InitKillWrapBox", "InitLightOmni", "InitLightSpot", "InitMaterial", "InitMirrorTexture",
    "InitModel", "InitOcclusionQuery", "InitOrientedSprite", "InitParticleSim", "InitPivot", "InitPlayerFacing",
    "InitRelativeVelocity", "InitRotation", "InitRotation3D", "InitRunner", "InitSound", "InitSpawn",
    "InitSpawnShapeBox", "InitSpawnShapeCylinder", "InitSpawnShapeEllipsoid", "InitSpawnShapeMesh",
    "InitSpawnShapeSphere", "InitTail", "InitVectorField", "InitVolumetric", "InitDismember",
    "Attractor", "AttractorGraph", "ColorGraph", "ColorLerp", "EmissionGraph", "EmissiveGraph", "ShaderGraph",
    "Force", "ForceGraph", "ForceDragGraph", "Gravity", "IntensityGraph", "TemperatureGraph",
    "ParentVelocityGraph", "PhysicsLight", "PhysicsRayCast", "PositionGraph", "RotationGraph", "RotationGraph3D",
    "ScaleByDistance", "SizeGraph", "SizeLerp", "VelocityGraph", "VectorFieldGraph",
    "TestAge", "TestBirth", "TestDeath", "TestGravity", "TestImpact", "TestPos", "TestTimeInState")
MODULE_SIZES = (
    0x40, 0x70, 0x80, 0x10, 0x10, 0x40, 0x90, 0x40, 0x30, 0x50, 0x60, 0xE0, 0x10, 0x20, 0x30, 0x20, 0x30, 0x30,
    0x10, 0x10, 0x20, 0x50, 0x70, 0x20, 0x20, 0xC0, 0xA0, 0xB0, 0x80, 0x80, 0x20, 0x30, 0x20, 0x10,
    0x30, 0xC0, 0x90, 0x30, 0x30, 0xB0, 0xD0, 0x30, 0x90, 0x30, 0x10, 0x30, 0x30, 0x30, 0x20, 0x30, 0x70, 0x30,
    0x70, 0x40, 0x90, 0x30, 0x90, 0x30,
    0x80, 0x70, 0x70, 0x80, 0x80, 0x80, 0x80)

# type -> (offset of the graph array in the module, number of graphs); from each module's loader.
GRAPHS = {0: (0x20, 2), 6: (0x50, 4), 24: (0x10, 1), 25: (0x60, 6), 26: (0x50, 5), 27: (0x50, 6), 29: (0x40, 4),
          35: (0x30, 8), 36: (0x10, 8), 38: (0x10, 2), 39: (0x10, 10), 40: (0x10, 12), 42: (0x30, 6),
          43: (0x10, 2), 45: (0x10, 2), 46: (0x10, 2), 47: (0x10, 2), 50: (0x10, 6), 51: (0x10, 2), 52: (0x10, 6),
          53: (0x10, 2), 54: (0x10, 6), 56: (0x10, 6), 57: (0x10, 2)}

# type -> offset of the module's asset list ({pointer, u32 count} of 0x20 entries, loader 142E06400). What an entry
# holds depends on the module type (142E06230), see ASSET_KIND.
ASSET_LISTS = {2: 0x60, 5: 0x10, 9: 0x08, 10: 0x08, 11: 0x10, 13: 0x10, 16: 0x08, 22: 0x50, 23: 0x10, 28: 0x38,
               31: 0x08, 48: 0x10, **{t: 0x58 for t in range(58, 65)}}
ASSET_KIND = {11: ("material",), 13: ("xmodel",), 28: ("xmodel",), 48: ("physicsfxpipeline", "physicsfxshape"),
              16: ("particlesimanimation",), 5: ("material", "material", "material"), 23: ("string",),
              31: ("vectorfield",), 9: ("lightdef",), 10: ("lightdef",)}   # every other list holds effects


@dataclass
class Key:
    time: float          # 0..1 over the particle's life
    value: float
    inv_dt: float        # 1 / (time - previous time); 0 for the first key


@dataclass
class Module:
    type: int
    name: str
    data: bytes                                  # the module body (MODULE_SIZES[type] bytes)
    graphs: list = field(default_factory=list)   # list of [Key]
    assets: list = field(default_factory=list)   # (kind, name)


@dataclass
class Emitter:
    init: list           # [Module], run at birth
    update: list         # [Module], run every frame
    tests: list          # [Module], spawn another effect when they pass
    data: bytes          # the 0xA0 emitter record


@dataclass
class Effect:
    name: str
    emitters: list       # [[Emitter]]: per emitter record, its states (usually one)


def _keys(read, p: int, n: int) -> list:
    if not p or not n:
        return []
    b = read(p, 16 * n)
    return [Key(*struct.unpack_from("<3f", b, 16 * i)) for i in range(n)]


def _string(read, p: int) -> str:
    out = bytearray()
    while p and len(out) < 256:
        c = read(p + len(out), 1)[0]
        if not c:
            break
        out.append(c)
    return out.decode("latin1")


def read_module(read, name_of, a: int) -> Module:
    """A module element is 0xF0 bytes (loader 142E066F0): +0x00 s16 type, +0x10 the module body."""
    t = struct.unpack("<h", read(a, 2))[0]
    body = a + 0x10
    m = Module(t, MODULE_NAMES[t] if 0 <= t < len(MODULE_NAMES) else f"type {t}", read(body, MODULE_SIZES[t]))
    if t in GRAPHS:
        o, n = GRAPHS[t]
        g = read(body + o, 16 * n)
        m.graphs = [_keys(read, *struct.unpack_from("<QI", g, 16 * i)) for i in range(n)]
    if t in ASSET_LISTS:
        p, n = struct.unpack("<QI", read(body + ASSET_LISTS[t], 12))
        kinds = ASSET_KIND.get(t, ("vfx",))
        for i in range(n if p else 0):
            e = read(p + 0x20 * i, 0x20)
            for j, k in enumerate(kinds):
                v = struct.unpack_from("<Q", e, 8 * j)[0]
                if v:
                    m.assets.append((k, _string(read, v) if k == "string" else name_of(v)))
    return m


def _modules(read, name_of, p: int, n: int) -> list:
    return [read_module(read, name_of, p + 0xF0 * i) for i in range(n if p else 0)]


def read_vfx(read, name_of, a: int) -> Effect:
    """Header 0x40 bytes (loader 142E08300): +0x00 name, +0x08 emitters (0xA0 each, count u32 +0x1C).
    Emitter (142E06150): +0x00 states (0x20 each, count u32 +0x08); a state's +0x00 points to three module lists
    {pointer, u32 count} at +0x00 (init), +0x10 (update), +0x20 (tests)."""
    h = read(a, 0x40)
    emitters = []
    ep, en = struct.unpack_from("<Q", h, 8)[0], struct.unpack_from("<I", h, 0x1C)[0]
    for i in range(en if ep else 0):
        e = read(ep + 0xA0 * i, 0xA0)
        sp, sn = struct.unpack_from("<QI", e, 0)
        states = []
        for k in range(sn if sp else 0):
            p = struct.unpack("<Q", read(sp + 0x20 * k, 8))[0]
            if not p:
                continue
            lists = read(p, 0x30)
            init, update, tests = (_modules(read, name_of, *struct.unpack_from("<QI", lists, o))
                                   for o in (0, 0x10, 0x20))
            states.append(Emitter(init, update, tests, e))
        emitters.append(states)
    return Effect(name_of(a), emitters)


def effects(zone_load):
    """Every effect in a loaded zone (load.ZoneLoad) that has emitters."""
    read, name_of = zone_load.mem.read, zone_load.name
    for t, h, _ in zone_load.assets:
        if zone_load.types[t][0] == "vfx":
            yield read_vfx(read, name_of, h)


def main():
    import argparse
    from pathlib import Path
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zone", type=Path)
    ap.add_argument("--oodle", default="oo2core_7_win64.dll")
    args = ap.parse_args()
    import load
    import zone
    from oodle import Oodle

    ff = args.zone.read_bytes()
    z = load.ZoneLoad(zone.decompress(ff, Oodle(args.oodle)), ff[:0x88])
    z.load()
    for fx in effects(z):
        if not fx.emitters:
            continue
        print(fx.name)
        for i, states in enumerate(fx.emitters):
            for s in states:
                for stage, mods in (("init", s.init), ("update", s.update), ("test", s.tests)):
                    for m in mods:
                        extra = [f"{len(g)}-key graph" for g in m.graphs if g] + [f"{k} {n}" for k, n in m.assets]
                        print(f"  emitter {i} {stage} {m.name}" + (": " + ", ".join(extra) if extra else ""))


if __name__ == "__main__":
    main()
