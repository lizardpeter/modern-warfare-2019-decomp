#!/usr/bin/env python3
"""Check tools/assets/xanim.py against TU67's own animation evaluators, run in Unicorn.

    python3 tests/assets/xanim_check.py <unpacked TU67 exe> <zone.ff> <oo2core_7_win64.dll> [--fp <zone.fp>]

The zone is loaded by the game's loaders (zone_emu.ZoneEmu). Then, for every animation and several times t, the
game's evaluator for that case is called with weight 1, an identity bone map, no ignored bones and a zeroed
rotTransArray, as its dispatcher 144104C00 does for an ordinary (non-additive) animation:

- 1440FA240 (under 256 frame intervals) or 1440FEC20 (256 or more), arguments (parts, bone map, t, weight,
  rotTransArray, ignore mask);
- 1440F6600 at t = 1 or with no frames (the last key), arguments (parts, bone map, weight, rotTransArray, mask).

The rotTransArray the game accumulates must equal xanim.calc_parts bit for bit. For animations with root motion
(flags 2 or 4), 1440E9950 (parts, weight, t, out) must also equal xanim.calc_abs_delta.
"""
import argparse
import struct
import sys
from pathlib import Path

import numpy as np
from unicorn.x86_const import UC_X86_REG_XMM1, UC_X86_REG_XMM2, UC_X86_REG_XMM3

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "tools" / "assets"))
import xanim  # noqa: E402
import zone  # noqa: E402
import zone_emu  # noqa: E402
from oodle import Oodle  # noqa: E402

CALC_PARTS, CALC_PARTS_BIG, CALC_NON_LOOP_END = 0x1440FA240, 0x1440FEC20, 0x1440F6600
CALC_ABS_DELTA = 0x1440E9950
MODES = {1: {"last": 0x1440F4320, "small": 0x1440F7890, "big": 0x1440FBA80},    # dispatcher mode 1: blend
         2: {"last": 0x1440F57D0, "small": 0x1440F8F20, "big": 0x1440FD4B0}}    # mode 2: additive
TIMES = (0.0, 0.1, 0.25, 0.5, 0.731, 0.999, 1.0)


def f32_bits(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def game_calc(emu, header, nbones, t, scratch, mode=0, prior=None):
    mu = emu.mu
    bone_map, mask, out = scratch, scratch + 0x400, scratch + 0x800
    mu.mem_write(bone_map, struct.pack(f"<{nbones}H", *range(nbones)))
    mu.mem_write(mask, b"\0" * 0x40)
    mu.mem_write(out, prior.tobytes() if prior is not None else b"\0" * (0x20 * nbones))
    frames = struct.unpack("<H", mu.mem_read(header + 0x7E, 2))[0]
    w = 0.75 if mode else 1.0
    if t == 1.0 or frames == 0:
        mu.reg_write(UC_X86_REG_XMM2, f32_bits(w))      # its third argument is the weight
        emu.call(MODES[mode]["last"] if mode else CALC_NON_LOOP_END, header, bone_map, 0, out, mask)
    else:
        mu.reg_write(UC_X86_REG_XMM2, f32_bits(t))
        mu.reg_write(UC_X86_REG_XMM3, f32_bits(w))
        f = (MODES[mode]["small"] if frames < 0x100 else MODES[mode]["big"]) if mode else \
            (CALC_PARTS if frames < 0x100 else CALC_PARTS_BIG)
        emu.call(f, header, bone_map, 0, 0, out, mask)
    return np.frombuffer(bytes(mu.mem_read(out, 0x20 * nbones)), dtype=np.float32).reshape(-1, 8)


def game_delta(emu, header, t, scratch):
    mu = emu.mu
    out = scratch + 0x8000
    mu.mem_write(out, b"\0" * 0x20)
    mu.reg_write(UC_X86_REG_XMM1, f32_bits(1.0))
    mu.reg_write(UC_X86_REG_XMM2, f32_bits(t))
    emu.call(CALC_ABS_DELTA, header, 0, 0, out)
    return np.frombuffer(bytes(mu.mem_read(out, 0x20)), dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("exe")
    ap.add_argument("zone")
    ap.add_argument("oodle")
    ap.add_argument("--fp")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    ff = Path(a.zone).read_bytes()
    o = Oodle(a.oodle)
    if a.fp:
        import fastfile_patch
        fp = Path(a.fp).read_bytes()
        header, data = fastfile_patch.patch_header(fp)[1], fastfile_patch.patched(ff, fp, o)
    else:
        header, data = ff[:zone.HEADER_SIZE], zone.decompress(ff, o)
    emu = zone_emu.ZoneEmu(a.exe, data, header)
    emu.load()
    emu.run_constant_initializers()     # the evaluators read math constants set by static initializers
    scratch = emu.pool = (emu.pool + 0xFFF) & ~0xFFF
    emu.pool += 0x20000
    read = lambda p, n: bytes(emu.mu.mem_read(p, n))
    checked = failed = deltas = 0
    for t_, h, _ in emu.assets:
        if emu.types[t_][0] != "xanim":
            continue
        anim = xanim.read_xanim(read, h, emu.strings)
        n = len(anim.names)
        if n == 0:
            continue
        for t in TIMES:
            want = game_calc(emu, h, n, t, scratch)
            got = xanim.calc_parts(anim, t, bones=n)
            checked += 1
            if want.tobytes() != got.tobytes():
                failed += 1
                if failed <= 10:
                    bad = np.nonzero((want.view(np.uint32) != got.view(np.uint32)).any(1))[0]
                    print(f"{anim.name} t={t} ({anim.numframes} intervals, classes {anim.bone_count}): "
                          f"{len(bad)} bones differ, first {bad[0]}: game {want[bad[0]]} ours {got[bad[0]]}")
        for mode, t in [(m, t) for m in (1, 2) for t in TIMES]:   # on top of the animation's pose at t = 0.4
            base = xanim.calc_parts(anim, 0.4, bones=n)
            want = game_calc(emu, h, n, t, scratch, mode=mode, prior=base)
            got = xanim.calc_parts(anim, t, weight=0.75, bones=n, mode=mode, out=base.copy())
            checked += 1
            if want.tobytes() != got.tobytes():
                failed += 1
                if failed <= 10:
                    bad = np.nonzero((want.view(np.uint32) != got.view(np.uint32)).any(1))[0]
                    print(f"{anim.name} mode {mode} t={t}: {len(bad)} bones differ, first {bad[0]}: "
                          f"game {want[bad[0]]} ours {got[bad[0]]}")
        if anim.flags & (xanim.FLAG_DELTA_2D | xanim.FLAG_DELTA_3D):
            for t in TIMES:
                want, got = game_delta(emu, h, t, scratch), xanim.calc_abs_delta(anim, t)
                deltas += 1
                if want.tobytes() != got.tobytes():
                    failed += 1
                    if failed <= 10:
                        print(f"{anim.name} root motion t={t}: game {want} ours {got}")
        if a.limit and checked >= a.limit:
            break
    print(f"{checked} evaluations and {deltas} root-motion evaluations, {failed} differ")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
