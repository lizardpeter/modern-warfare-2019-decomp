#!/usr/bin/env python3
"""Load a zone with the translated loaders: TU67's decompiled C, compiled to Python (docs/assets/loader-translation.md).

    python3 tools/assets/loaders/load.py <unpacked TU67 exe> <zone.ff> <oo2core_7_win64.dll> [--fp <zone.fp>]

Everything that reads the zone is the game's own code as Ghidra decompiled it (analysis/ModernWarfare_TU67/
pseudocode), run with the decompiler's types; only the stand-ins in stand_ins.py are Python, the same ones the
emulator check uses. Memory uses the emulator's addresses so the two compare byte for byte (tests/assets/
loaders_check.py).

The exe is still needed for one thing: the initial contents of the globals the loaders read before writing them.
Recording those values so the reader needs only the game's data files is the next step.
"""
import struct
import sys
from pathlib import Path

import pefile

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import stand_ins as S  # noqa: E402
from c_model import Mem  # noqa: E402
from compiler import Machine  # noqa: E402
from source import pseudocode, recorded_types  # noqa: E402

_SOURCE = None


def image_backing(exe_path):
    pe = pefile.PE(exe_path, fast_load=True)
    secs = [(S.IMAGE + s.VirtualAddress, s.get_data()) for s in pe.sections]

    def backing(a, n):
        for base, d in secs:
            if base <= a < base + len(d):
                return (d[a - base:a - base + n] + bytes(n))[:n]
        return None
    return backing


class ZoneLoad:
    def __init__(self, exe_path, data, header):
        global _SOURCE
        if _SOURCE is None:
            _SOURCE = (pseudocode(), recorded_types())
        src, rec = _SOURCE
        self.mem = Mem(image_backing(exe_path))
        self.data, self.pos = data, 0
        self.types = S.asset_types()
        self.strings, self.assets = [], []
        self.pool = S.POOL + 0x1000
        sizes = struct.unpack_from('<8Q', header, 0x30)
        blocks, addr = [], S.BLOCKS
        for size in sizes:
            blocks.append((addr, size))
            addr += (size + 0x10000 + 0xFFFF) & ~0xFFFF
        self.blocks = blocks
        table = self.pool
        self.pool += 0x100
        self.mem.write(table, b''.join(struct.pack('<QQ', a, s) for a, s in blocks))
        self.command_buffer, self.command_list = self.pool, self.pool + S.COMMAND_BUFFER_SIZE
        self.mem.write(S.COMMAND_BUFFER_VARS, struct.pack('<QIIIIQ', self.command_buffer, S.COMMAND_BUFFER_SIZE,
                                                          0, 0, 0, self.command_list))
        self.pool += S.COMMAND_BUFFER_SIZE + 0x400 * 16
        hooks = {S.READ: self._read, S.ADD_ASSET: self._add, S.SL_GET_STRING: self._sl, S.MEMCPY: self._memcpy}
        for a in S.CANCEL_CHECKS + tuple(S.SKIPPED):
            hooks[a] = lambda m, args: 0
        for a, t in S.WRAPPERS.items():
            hooks[a] = lambda m, args, t=t: self._wrapper(t, args)
        self.machine = Machine(self.mem, src.get, hooks, rec)
        self.machine.call(S.INIT_STREAMS, [table])
        self.machine.call(S.RESET_TRACKERS, [])

    # --- stand-ins (stand_ins.py) ---
    def _read(self, m, args):
        dst, n = args[0], args[1]
        if self.pos + n > len(self.data):
            raise EOFError(f'read of {n:#x} at {self.pos:#x} passes the end of the zone ({len(self.data):#x})')
        self.mem.write(dst, self.data[self.pos:self.pos + n])
        self.pos += n
        return 0

    def _copy(self, typ, header):
        size = self.types[typ][1]
        self.pool = (self.pool + 15) & ~15
        c = self.pool
        self.mem.write(c, self.mem.read(header, size))
        self.pool += size
        self.assets.append((typ, c, self.pos))
        return c

    def _add(self, m, args):
        return self._copy(args[0] & 0xFFFFFFFF, struct.unpack('<Q', self.mem.read(args[1], 8))[0])

    def _wrapper(self, t, args):
        pp = args[0]
        self.mem.write(pp, struct.pack('<Q', self._copy(t, struct.unpack('<Q', self.mem.read(pp, 8))[0])))
        return 0

    def _sl(self, m, args):
        p = args[0]
        s = bytearray()
        while (c := self.mem.read(p + len(s), 1)[0]) != 0:
            s.append(c)
        self.strings.append(s.decode('latin-1'))
        return len(self.strings)

    def _memcpy(self, m, args):
        d, s, n = args[:3]
        self.mem.write(d, self.mem.read(s, n))
        return d

    def load(self):
        dst = self.pool
        self.pool += 0x100
        return self.machine.call(S.LOAD_ASSET_LIST, [0, dst, 0, 0])

    def name(self, header):
        p = struct.unpack('<Q', self.mem.read(header, 8))[0]
        b = self.mem.read(p, 256)
        return b.split(b'\0')[0].decode('latin-1') if p and b'\0' in b else None


def main():
    import argparse
    import time
    import zone
    from oodle import Oodle
    ap = argparse.ArgumentParser()
    ap.add_argument('exe')
    ap.add_argument('zone')
    ap.add_argument('oodle')
    ap.add_argument('--fp')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    ff = Path(a.zone).read_bytes()
    o = Oodle(a.oodle)
    if a.fp:
        import fastfile_patch
        fp = Path(a.fp).read_bytes()
        header, data = fastfile_patch.patch_header(fp)[1], fastfile_patch.patched(ff, fp, o)
    else:
        header, data = ff[:zone.HEADER_SIZE], zone.decompress(ff, o)
    t = time.time()
    z = ZoneLoad(a.exe, data, header)
    z.load()
    print(f'{len(z.strings)} script strings, {len(z.assets)} assets, stream at {z.pos:#x} of {len(data):#x}, '
          f'{time.time() - t:.1f} s')
    for i, (typ, h, end) in enumerate(z.assets if a.all else z.assets[:40]):
        print(f'{i:5d}\t{z.types[typ][0]}\t{z.name(h)}\t{end:#x}')


if __name__ == '__main__':
    main()
