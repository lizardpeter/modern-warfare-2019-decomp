#!/usr/bin/env python3
"""Check the translated loaders against the game's own code: load a zone both ways, compare all of memory.

    python3 tests/assets/loaders_check.py <unpacked TU67 exe> <zone.ff> <oo2core_7_win64.dll> [--fp <zone.fp>]
        [--decompressed <data>]

Passes when both read the zone to its end, add the same assets with the same script strings, and every stream block
and the asset pool are byte for byte equal, except the bytes the game leaves uninitialised (stand_ins.py,
records/bugs.tsv B0001).
"""
import argparse
import struct
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'assets'))
sys.path.insert(0, str(ROOT / 'tools' / 'assets' / 'loaders'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import stand_ins as S  # noqa: E402
import zone  # noqa: E402
import zone_emu  # noqa: E402
from load import ZoneLoad  # noqa: E402
from oodle import Oodle  # noqa: E402


def undefined_bytes(z):
    """Addresses of the bytes the game never initialises: in each queued deferred command (stand_ins.py)."""
    out = set()
    count = struct.unpack('<I', z.mem.read(S.COMMAND_BUFFER_VARS + 0x10, 4))[0]
    for i in range(count):
        entry = z.command_list + 16 * i
        out.update(entry + k for k in S.UNDEFINED_COMMAND_ENTRY)
        record = struct.unpack('<Q', z.mem.read(entry, 8))[0]
        out.update(record + k for k in S.UNDEFINED_COMMAND_DATA)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('exe')
    ap.add_argument('zone')
    ap.add_argument('oodle')
    ap.add_argument('--fp')
    ap.add_argument('--decompressed')
    a = ap.parse_args()
    ff = Path(a.zone).read_bytes()
    if a.fp:
        import fastfile_patch
        header = fastfile_patch.patch_header(Path(a.fp).read_bytes())[1]
        data = (Path(a.decompressed).read_bytes() if a.decompressed
                else fastfile_patch.patched(ff, Path(a.fp).read_bytes(), Oodle(a.oodle)))
    else:
        header = ff[:zone.HEADER_SIZE]
        data = Path(a.decompressed).read_bytes() if a.decompressed else zone.decompress(ff, Oodle(a.oodle))
    t = time.time()
    z = ZoneLoad(a.exe, data, header)
    z.load()
    print(f'translated loaders: {len(z.assets)} assets, stream {z.pos:#x} of {len(data):#x}, {time.time() - t:.1f} s')
    e = zone_emu.ZoneEmu(a.exe, data, header)
    e.load()
    print(f'game code (emulator): {len(e.assets)} assets, stream {e.pos:#x}')
    ok = z.pos == e.pos == len(data) and z.strings == e.strings and \
        [(t, p) for t, _, p in z.assets] == [(t, p) for t, _, p in e.assets]
    skip = undefined_bytes(z)
    regions = [(f'block {k}', base, size) for k, (base, size) in enumerate(z.blocks) if size]
    regions.append(('pool', S.POOL, z.pool - S.POOL))
    for name, base, size in regions:
        x, y = z.mem.read(base, size), bytes(e.mu.mem_read(base, size))
        bad = [i for i in range(size) if x[i] != y[i] and base + i not in skip] if x != y else []
        print(f'{name}: {"equal" if not bad else f"{len(bad)} bytes differ, first at {base + bad[0]:#x}"}'
              f'{f" ({sum(1 for i in range(size) if base + i in skip)} undefined bytes skipped)" if x != y else ""}')
        ok = ok and not bad
    print('PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
