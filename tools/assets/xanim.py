#!/usr/bin/env python3
"""Read animations (XAnimParts, type 7) and evaluate them as TU67 does. Rules: docs/assets/animations.md.

    python3 tools/assets/xanim.py <zone.ff> [--oodle DLL] [--sample T]     list the zone's animations

`read_xanim(read, address, strings)` reads one loaded XAnimParts (read(address, n) -> bytes; strings: the zone's
script strings, 1-based ids). `calc_parts(anim, t, weight)` is the game's evaluator into a rotTransArray (per bone
[quat x, y, z, w, trans x, y, z, trans weight] of float32, not normalised); `sample(anim, t)` gives each bone's unit
local rotation and translation offset.
"""
from __future__ import annotations

import argparse
import struct
import sys
from bisect import bisect_right
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "loaders"))

F32 = np.float32
QUAT_SCALE = F32(3.051851e-05)      # 1 / 32767
COARSE = 0x40                       # from this many keys, 256+ frame animations split their frame index table

# bone classes, in the order of the counts at +0x81..+0x89 and of the bone names
NO_QUAT, HALF_QUAT, FULL_QUAT, HALF_QUAT_ONE, FULL_QUAT_ONE, SMALL_TRANS, TRANS, TRANS_ONE, NO_TRANS = range(9)


@dataclass
class XAnim:
    name: str
    numframes: int                 # frame intervals: numframes + 1 frames
    framerate: float
    frequency: float
    flags: int
    bone_count: tuple              # 9 classes (+0x81..+0x89)
    names: list
    notify: list
    data_byte: bytes
    data_short: list               # u16
    data_int: bytes                # float32
    random_data_short: list        # i16
    random_data_byte: bytes
    random_data_int: bytes
    indices: list                  # u8 under 256 frames, else u16
    delta: dict | None = None      # root motion: {"trans", "quat2", "quat"}, each None or a dict (read_delta)
    raw: dict = field(default_factory=dict)


def read_xanim(read, a: int, strings=None) -> XAnim:
    h = read(a, 0xA8)
    q = lambda o: struct.unpack_from("<Q", h, o)[0]
    numframes = struct.unpack_from("<H", h, 0x7E)[0]
    big = numframes >= 0x100
    total = h[0x8A]

    def arr(p, n, unit, fmt=None):
        if not p or n <= 0:
            return b"" if fmt is None else []
        d = read(p, n * unit)
        return d if fmt is None else list(struct.unpack(f"<{n}{fmt}", d))

    def name(i):
        return strings[i - 1] if strings and 0 < i <= len(strings) else i

    names = [name(x) for x in arr(q(0x08), total, 4, "I")]
    notify = []
    if q(0x48):
        for i in range(h[0x8B]):
            nid, t = struct.unpack("<If", read(q(0x48) + 8 * i, 8))
            notify.append((name(nid), t))
    cname = bytearray()
    p = q(0)
    while p:
        c = read(p, 1)[0]
        if not c:
            break
        cname.append(c)
        p += 1
    return XAnim(
        name=cname.decode("latin1"), numframes=numframes,
        framerate=struct.unpack_from("<f", h, 0x6C)[0], frequency=struct.unpack_from("<f", h, 0x70)[0],
        flags=h[0x80], bone_count=tuple(h[0x81:0x8A]), names=names, notify=notify,
        data_byte=arr(q(0x10), struct.unpack_from("<I", h, 0x74)[0], 1),
        data_short=arr(q(0x18), struct.unpack_from("<H", h, 0x78)[0], 2, "H"),
        data_int=arr(q(0x20), struct.unpack_from("<H", h, 0x7A)[0], 4),
        random_data_short=arr(q(0x28), struct.unpack_from("<I", h, 0x60)[0], 2, "h"),
        random_data_byte=arr(q(0x30), struct.unpack_from("<I", h, 0x64)[0], 1),
        random_data_int=arr(q(0x38), struct.unpack_from("<H", h, 0x7C)[0], 4),
        indices=arr(q(0x40), struct.unpack_from("<I", h, 0x68)[0], 2 if big else 1, "H" if big else "B"),
        delta=read_delta(read, q(0x58), big) if q(0x58) else None,
        raw={"address": a})


def read_delta(read, p, big: bool):
    """The delta part (+0x58, 0x18 bytes: translation, 2D rotation, 3D rotation; loaders 142E53740, 142E53E70,
    142E53840, 142E538E0). Each part starts with u16 keys - 1; 0 means one value inline at +8 (3 x f32, 2 x s16,
    4 x s16). Otherwise the translation has mins (3 x f32 at +8), size (+0x14) and a key pointer (+0x20), the
    rotations a key pointer at +8; the frame index table (keys entries, u8 or u16 as the animation's) follows the
    header (translation +0x28, rotations +0x10). Translation keys are 3 x u8 when the byte at +2 is set, else
    3 x u16; rotation keys 2 or 4 x s16."""
    u16 = lambda a: struct.unpack("<H", read(a, 2))[0]
    q = lambda a: struct.unpack("<Q", read(a, 8))[0]

    def idx(a, n):
        return list(read(a, n + 1)) if not big else list(struct.unpack(f"<{n + 1}H", read(a, 2 * n + 2)))
    out = {"trans": None, "quat2": None, "quat": None}
    t = q(p)
    if t:
        size, small = u16(t), read(t + 2, 1)[0]
        if not size:
            out["trans"] = {"frame0": struct.unpack("<3f", read(t + 8, 12))}
        else:
            keys = list(read(q(t + 0x20), 3 * (size + 1))) if small else \
                list(struct.unpack(f"<{3 * (size + 1)}H", read(q(t + 0x20), 6 * (size + 1))))
            out["trans"] = {"mins": struct.unpack("<3f", read(t + 8, 12)), "size": struct.unpack("<3f", read(t + 0x14, 12)),
                            "small": bool(small), "indices": idx(t + 0x28, size), "keys": keys}
    for off, comps, key in ((8, 2, "quat2"), (0x10, 4, "quat")):
        r = q(p + off)
        if not r:
            continue
        size = u16(r)
        if not size:
            out[key] = {"frame0": struct.unpack(f"<{comps}h", read(r + 8, 2 * comps))}
        else:
            out[key] = {"indices": idx(r + 0x10, size),
                        "keys": list(struct.unpack(f"<{comps * (size + 1)}h", read(q(r + 8), 2 * comps * (size + 1))))}
    return out


def _find(table, frame):
    i = bisect_right(table, frame) - 1
    return max(0, min(i, len(table) - 2))


class _Cursor:
    def __init__(self, anim):
        self.a, self.db, self.ds, self.di, self.rs, self.rb, self.ix = anim, 0, 0, 0, 0, 0, 0

    def byte(self):
        self.db += 1
        return self.a.data_byte[self.db - 1]

    def short(self):
        self.ds += 1
        return self.a.data_short[self.ds - 1]

    def floats(self, n):
        v = struct.unpack_from(f"<{n}f", self.a.data_int, self.di)
        self.di += 4 * n
        return [F32(x) for x in v]


def _interval(c, n, frame, frame_f, last):
    """A keyed part's frame index table (n + 1 entries for n + 1 keys) -> (key, fraction); `last` takes key n."""
    a = c.a
    if a.numframes < 0x100:
        table = list(a.data_byte[c.db:c.db + n + 1])
        c.db += n + 1
    elif n < COARSE:
        table = a.data_short[c.ds:c.ds + n + 1]
        c.ds += n + 1
    else:
        m = ((n - 1) >> 8) + 2
        coarse = a.data_short[c.ds:c.ds + m]
        c.ds += m
        full = a.indices[c.ix:c.ix + n + 1]
        c.ix += n + 1
        if last:
            return n, None
        j = _find(coarse, frame)
        fine = full[256 * j:256 * j + min(n - 256 * j, 256) + 1]
        k = _find(fine, frame)
        lo, hi = fine[k], fine[k + 1]
        return 256 * j + k, (frame_f - F32(lo)) / F32(int(hi) - int(lo))
    if last:
        return n, None
    i = _find(table, frame)
    return i, (frame_f - F32(table[i])) / F32(int(table[i + 1]) - int(table[i]))


def _add_rotation(out, b, v, w):
    """Weighted add of quaternion v to the bone's accumulator, flipped into the accumulator's hemisphere: the sign
    of (x·ax + y·ay) + (z·az + w·aw) in float32, -0 counting as negative (1440FA240)."""
    acc = out[b, :4]
    d = (v[0] * acc[0] + v[1] * acc[1]) + (v[2] * acc[2] + v[3] * acc[3])
    neg = np.signbit(d)
    for j in range(4):
        x = -v[j] if neg else v[j]
        out[b, j] = x * w + acc[j]


IDENTITY = (F32(0.0), F32(0.0), F32(0.0), F32(1.0))


def _apply_rotation(out, b, v, w):
    """Additive rotation (dispatcher mode 2: 1440F57D0, 1440F8F20, 1440FD4B0): the key is moved into the w >= 0
    hemisphere, blended from the identity by the weight, normalised, and multiplied onto the accumulator,
    `acc = acc * n`. Accumulator components that are exactly 0 count as the identity's (blendvps on == 0)."""
    s = F32(-1.0) if np.signbit(v[3] + F32(0.0) + F32(0.0)) else F32(1.0)
    one_minus = F32(1.0) - w
    u = [(s * w) * v[j] + one_minus * IDENTITY[j] for j in range(4)]
    length = np.sqrt((u[0] * u[0] + u[1] * u[1]) + (u[2] * u[2] + u[3] * u[3]), dtype=F32)
    n = [u[j] / length for j in range(4)]
    a = [IDENTITY[j] if out[b, j] == 0 else out[b, j] for j in range(4)]
    d = (n[0] * a[0] + n[1] * a[1]) + (n[2] * a[2] + F32(0.0))
    out[b, 0] = (n[2] * a[1] - n[1] * a[2]) + (a[3] * n[0] + n[3] * a[0])
    out[b, 1] = (n[0] * a[2] - n[2] * a[0]) + (a[3] * n[1] + n[3] * a[1])
    out[b, 2] = (n[1] * a[0] - n[0] * a[1]) + (a[3] * n[2] + n[3] * a[2])
    out[b, 3] = a[3] * n[3] - d


def _blend_rotation(out, b, v, w):
    """Blend toward the key (dispatcher mode 1: 1440F4320, 1440F7890, 1440FBA80): the key takes the sign of
    (x·ax + y·ay) + (z·az + w·aw), then `acc = (key - acc) × weight + acc` per component."""
    acc = out[b, :4].copy()
    d = (acc[0] * v[0] + acc[1] * v[1]) + (acc[2] * v[2] + acc[3] * v[3])
    neg = np.signbit(d)
    for j in range(4):
        k = -v[j] if neg else v[j]
        out[b, j] = (k - acc[j]) * w + acc[j]


def _blend_translation(out, b, v, w):
    acc = out[b, 4:8].copy()
    for j in range(4):
        out[b, 4 + j] = (v[j] - acc[j]) * w + acc[j]


def calc_parts(anim: XAnim, t: float, weight: float = 1.0, bones: int | None = None, anim_to_model=None,
               mode: int = 0, out=None):
    """mode 0: ordinary (weighted sum); mode 1: blend toward this animation; mode 2: additive (rotations
    multiplied on). The dispatcher 144104C00 picks the mode."""
    total = sum(anim.bone_count[:NO_TRANS + 1]) if anim.bone_count else 0
    total = max(total, len(anim.names))
    if anim_to_model is None:
        anim_to_model = list(range(len(anim.names)))
    if out is None:
        out = np.zeros((bones if bones is not None else max(anim_to_model, default=-1) + 1, 8), dtype=F32)
    w = F32(weight)
    last = t == 1.0 or anim.numframes == 0
    tf = F32(t)
    frame_f = F32(anim.numframes) * tf
    frame = int(frame_f)
    c = _Cursor(anim)
    bc = anim.bone_count
    zero = F32(0.0)
    part = 0
    add = (_add_rotation, _blend_rotation, _apply_rotation)[mode]
    for _ in range(bc[NO_QUAT]):
        b = anim_to_model[part]
        if mode == 0:
            out[b, 3] = (-w if out[b, 3] < 0 else w) + out[b, 3]
        elif mode == 1:
            for j in range(4):
                out[b, j] = (IDENTITY[j] - out[b, j]) * w + out[b, j]
        part += 1
    for group, comps in ((HALF_QUAT, 2), (FULL_QUAT, 4)):
        for _ in range(bc[group]):
            b = anim_to_model[part]
            n = c.short()
            i, f = _interval(c, n, frame, frame_f, last)
            keys = anim.random_data_short[c.rs:c.rs + comps * (n + 1)]
            c.rs += comps * (n + 1)
            k0 = [F32(x) * QUAT_SCALE for x in keys[comps * i:comps * i + comps]]
            if last:
                v = k0
            else:
                k1 = [F32(x) * QUAT_SCALE for x in keys[comps * (i + 1):comps * (i + 1) + comps]]
                v = [(k1[j] - k0[j]) * f + k0[j] for j in range(comps)]
            if comps == 2:
                z0 = zero if last else f * zero + zero
                v = [z0, z0] + v
            add(out, b, v, w)
            part += 1
    for group, comps in ((HALF_QUAT_ONE, 2), (FULL_QUAT_ONE, 4)):
        for _ in range(bc[group]):
            b = anim_to_model[part]
            v = [F32(struct.unpack("<h", struct.pack("<H", c.short()))[0]) * QUAT_SCALE for _ in range(comps)]
            if comps == 2:
                v = [zero, zero] + v
            add(out, b, v, w)
            part += 1
    for group in (SMALL_TRANS, TRANS):
        for _ in range(bc[group]):
            b = anim_to_model[c.byte()]
            n = c.short()
            i, f = _interval(c, n, frame, frame_f, last)
            mins = c.floats(3)
            size = c.floats(3)
            if group == SMALL_TRANS:
                keys = list(anim.random_data_byte[c.rb:c.rb + 3 * (n + 1)])
                c.rb += 3 * (n + 1)
            else:
                keys = [x & 0xFFFF for x in anim.random_data_short[c.rs:c.rs + 3 * (n + 1)]]
                c.rs += 3 * (n + 1)
            k0 = [F32(x) for x in keys[3 * i:3 * i + 3]]
            if last:
                v = [k0[j] * size[j] + mins[j] for j in range(3)]
            else:
                k1 = [F32(x) for x in keys[3 * (i + 1):3 * (i + 1) + 3]]
                v = [((k1[j] - k0[j]) * f + k0[j]) * size[j] + mins[j] for j in range(3)]
            if mode == 1:
                _blend_translation(out, b, v + [F32(1.0)], w)
                continue
            for j in range(3):
                out[b, 4 + j] = w * v[j] + out[b, 4 + j]
            out[b, 7] = w * F32(1.0) + out[b, 7]
    for _ in range(bc[TRANS_ONE]):
        b = anim_to_model[c.byte()]
        v = c.floats(3)
        if mode == 1:
            _blend_translation(out, b, v + [F32(1.0)], w)
            continue
        for j in range(3):
            out[b, 4 + j] = w * v[j] + out[b, 4 + j]
        out[b, 7] = w + out[b, 7]
    for _ in range(bc[NO_TRANS]):
        b = anim_to_model[c.byte()]
        if mode == 1:
            _blend_translation(out, b, [F32(0.0), F32(0.0), F32(0.0), F32(1.0)], w)
            continue
        out[b, 7] = w + out[b, 7]
    return out


FLAG_LOOP, FLAG_DELTA_2D, FLAG_DELTA_3D = 1, 2, 4    # +0x80


def _delta_key(d, frame, frame_f):
    table = d["indices"]
    i = _find(table, frame)
    return i, (frame_f - F32(table[i])) / F32(int(table[i + 1]) - int(table[i]))


def _delta_rot(anim, t, comps):
    d = anim.delta[("quat2" if comps == 2 else "quat")] if anim.delta else None
    if d is None:
        return [F32(0.0)] * (comps - 1) + [F32(32767.0)]
    if "frame0" in d:
        return [F32(x) for x in d["frame0"]]
    keys, n = d["keys"], len(d["indices"]) - 1
    if t == 1.0 or anim.numframes == 0:
        return [F32(x) for x in keys[comps * n:comps * n + comps]]
    frame_f = F32(anim.numframes) * F32(t)
    i, f = _delta_key(d, int(frame_f), frame_f)
    k0, k1 = keys[comps * i:comps * i + comps], keys[comps * (i + 1):comps * (i + 1) + comps]
    return [F32(int(k1[j]) - int(k0[j])) * f + F32(k0[j]) for j in range(comps)]


def _delta_pos(anim, t):
    d = anim.delta["trans"] if anim.delta else None
    if d is None:
        return [F32(0.0)] * 3
    if "frame0" in d:
        return [F32(x) for x in d["frame0"]]
    keys, n = d["keys"], len(d["indices"]) - 1
    mins, size = [F32(x) for x in d["mins"]], [F32(x) for x in d["size"]]
    if t == 1.0 or anim.numframes == 0:
        return [size[j] * F32(keys[3 * n + j]) + mins[j] for j in range(3)]
    frame_f = F32(anim.numframes) * F32(t)
    i, f = _delta_key(d, int(frame_f), frame_f)
    k0, k1 = keys[3 * i:3 * i + 3], keys[3 * (i + 1):3 * (i + 1) + 3]
    return [((F32(k1[j]) - F32(k0[j])) * f + F32(k0[j])) * size[j] + mins[j] for j in range(3)]


def calc_abs_delta(anim: XAnim, t: float, weight: float = 1.0):
    """Root motion from the start to time t (1440E9950): [rot x, y, z, w, weight, pos x, y, z] of float32, the
    rotation as keys x weight / 32767 (not normalised). Only animations whose flags have a 2D (2) or 3D (4) root
    rotation add anything."""
    out = np.zeros(8, dtype=F32)
    w = F32(weight)
    if anim.flags & FLAG_DELTA_2D:
        rot = [None, None] + _delta_rot(anim, t, 2)
    elif anim.flags & FLAG_DELTA_3D:
        rot = _delta_rot(anim, t, 4)
        for j in range(2):
            out[j] = rot[j] * w * QUAT_SCALE + out[j]
    else:
        return out
    for j in (2, 3):
        out[j] = rot[j] * w * QUAT_SCALE + out[j]
    out[4] = w + out[4]
    pos = _delta_pos(anim, t)
    for j in range(3):
        out[5 + j] = w * pos[j] + out[5 + j]
    return out


def sample_delta(anim: XAnim, t: float):
    """Root motion at time t: (unit quaternion, translation), or None for an animation without."""
    d = calc_abs_delta(anim, t)
    if not d[4]:
        return None
    q = [float(x) for x in d[:4]]
    n = sum(x * x for x in q) ** 0.5 or 1.0
    return tuple(x / n for x in q), tuple(float(x) / float(d[4]) for x in d[5:8])


def sample(anim: XAnim, t: float):
    """Per animation bone: (unit quaternion or None, translation offset or None) at normalised time t."""
    mats = calc_parts(anim, t)
    out = []
    for i in range(len(anim.names)):
        q = [float(x) for x in mats[i, :4]]
        n = sum(x * x for x in q) ** 0.5
        tw = float(mats[i, 7])
        out.append((tuple(x / n for x in q) if n > 0 else None,
                    tuple(float(x) / tw for x in mats[i, 4:7]) if tw > 0 else None))
    return out


def animations(zone_load):
    z = zone_load
    for t, h, _ in z.assets:
        if z.types[t][0] == "xanim":
            yield read_xanim(z.mem.read, h, z.strings)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zone")
    ap.add_argument("--oodle", default="oo2core_7_win64.dll")
    ap.add_argument("--sample", type=float)
    args = ap.parse_args()
    import load
    import zone
    from oodle import Oodle

    ff = open(args.zone, "rb").read()
    z = load.ZoneLoad(zone.decompress(ff, Oodle(args.oodle)), ff[:0x88])
    z.load()
    for a in animations(z):
        print(f"{a.name}: {a.numframes + 1} frames at {a.framerate} fps, {len(a.names)} bones, classes {a.bone_count}")
        if args.sample is not None:
            for name, (q, tr) in zip(a.names, sample(a, args.sample)):
                print(f"    {name}: rotation {q} translation {tr}")


if __name__ == "__main__":
    main()
