#!/usr/bin/env python3
"""Load a zone with TU67's own loader code, run in Unicorn: the ground truth the Python readers are checked against.

    python3 tests/assets/zone_emu.py <unpacked TU67 exe> <zone.ff> <oo2core_7_win64.dll> [--fp <zone.fp>] [--limit N]

What runs as the game's code: the asset-list loader 1437608F0 and everything it calls, so every Load_<T>Ptr /
Load_<T>, the stream primitives (push/pop 1437606D0/143760620, align 142DF1380, offset resolution 142DFEF30 /
142DFEFA0, alias slots 1437604F0), the script-string and XString loaders. What is Python (docs/assets/zones.md 8):

- the file read 143755EA0 (copies the next bytes of the decompressed zone);
- DB_AddXAsset 143757490 (copies the header into a pool region and returns the copy, as for a new asset);
- SL_GetString 143BC1270 (returns 1-based indices into the strings in the order they are added);
- the per-asset cancel checks 143759410 / 143759420 (never cancel);
- the asset-specific wrappers around DB_AddXAsset that also start renderer or streaming work (`WRAPPERS`).

The zone's memory blocks are allocated from the header's block sizes (+0x30, 8 x u64) and handed to the game's own
stream init 143760420. Unknown calls into imports stop the run with the import's name.
"""
import argparse
import hashlib
import struct
import sys
import tomllib
from pathlib import Path

import pefile
from unicorn import UC_ARCH_X86, UC_HOOK_CODE, UC_HOOK_MEM_UNMAPPED, UC_MODE_64, Uc, UcError
from unicorn.x86_const import (UC_X86_REG_GS_BASE, UC_X86_REG_R8, UC_X86_REG_R9, UC_X86_REG_RAX, UC_X86_REG_RCX,
                               UC_X86_REG_RDX, UC_X86_REG_RIP, UC_X86_REG_RSP)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "assets"))
import zone  # noqa: E402
from oodle import Oodle  # noqa: E402

sys.path.insert(0, str(ROOT / "tools" / "assets" / "loaders"))
from stand_ins import *  # noqa: E402,F401,F403  addresses, stand-ins and layout shared with the translated loaders


class ZoneEmu:
    def __init__(self, exe_path, data: bytes, header: bytes):
        raw = Path(exe_path).read_bytes()
        want = next(b for b in tomllib.loads((ROOT / "target.toml").read_text())["build"]
                    if b["id"] == "ModernWarfare_TU67")["unpacked_sha256"]
        if hashlib.sha256(raw).hexdigest() != want:
            raise SystemExit(f"{exe_path}: not the unpacked TU67 exe (target.toml unpacked_sha256)")
        pe = pefile.PE(data=raw, fast_load=True)
        mu = self.mu = Uc(UC_ARCH_X86, UC_MODE_64)
        mu.mem_map(IMAGE, (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF)
        for s in pe.sections:
            d = s.get_data()
            if d:
                mu.mem_write(IMAGE + s.VirtualAddress, d[:s.Misc_VirtualSize] if s.Misc_VirtualSize else d)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
        mu.mem_map(STUB, 0x10000)
        mu.mem_write(STUB, b"\xC3" * 0x10000)
        self.imports = {}
        for imp in pe.DIRECTORY_ENTRY_IMPORT:
            for f in imp.imports:
                a = STUB + len(self.imports) * 16
                self.imports[a] = (imp.dll.decode() + "!" + (f.name.decode() if f.name else f"#{f.ordinal}"))
                mu.mem_write(f.address, struct.pack("<Q", a))
        mu.mem_map(STACK - 0x200000, 0x400000)
        mu.mem_map(TEB, 0x10000)
        mu.mem_map(TLS, 0x10000)
        mu.mem_write(TEB + 0x30, struct.pack("<Q", TEB))
        mu.mem_write(TEB + 0x58, struct.pack("<Q", TLS))            # ThreadLocalStoragePointer
        mu.mem_write(TLS, struct.pack("<Q", TLS + 0x1000) * 64)     # every TLS index -> one zeroed block
        mu.reg_write(UC_X86_REG_GS_BASE, TEB)
        mu.mem_map(POOL, POOL_SIZE)
        self.pool = POOL + 0x1000

        self.data, self.pos = data, 0
        self.types = asset_types()
        self.strings = []
        self.assets = []       # (type, header address in the pool, stream position after the asset)

        # blocks: sizes from the zone header, each mapped page-aligned at its own address
        sizes = struct.unpack_from("<8Q", header, 0x30)
        self.blocks, addr = [], BLOCKS
        for size in sizes:
            self.blocks.append((addr, size))
            if size:
                mu.mem_map(addr, (size + 0xFFFF) & ~0xFFFF)
            addr += (size + 0x10000 + 0xFFFF) & ~0xFFFF
        table = self.pool
        self.pool += 0x100
        mu.mem_write(table, b"".join(struct.pack("<QQ", a, s) for a, s in self.blocks))

        hooks = {READ: self._read, ADD_ASSET: self._add, SL_GET_STRING: self._sl_get_string}
        hooks.update({a: self._never for a in CANCEL_CHECKS})
        hooks.update({a: self._never for a in SKIPPED})
        for a, t in WRAPPERS.items():
            hooks[a] = lambda mu, t=t: self._wrapper(mu, t)
        self.hooks = hooks
        for a in hooks:
            mu.hook_add(UC_HOOK_CODE, self._dispatch, begin=a, end=a)
        mu.hook_add(UC_HOOK_CODE, self._on_import, begin=STUB, end=STUB + 0xFFFF)
        mu.hook_add(UC_HOOK_MEM_UNMAPPED, self._unmapped)
        # the zone's deferred commands: gfx_map_trzone and others queue world data (142DFEDA0, 142DFEC80). Data goes
        # to a buffer (142DEDDA0: base 14BCC42F0, u32 capacity 14BCC42F8, u32 used 14BCC42FC; DEV ERROR 0x1A4F when
        # full), the 16-byte command to a list (142DEDE00: u32 count 14BCC4300, array 14BCC4308, at most 0x400 entries,
        # else DEV ERROR 0x1A51)
        self.command_buffer, self.command_list = self.pool, self.pool + COMMAND_BUFFER_SIZE
        mu.mem_write(COMMAND_BUFFER_VARS, struct.pack("<QIIIIQ", self.command_buffer, COMMAND_BUFFER_SIZE, 0, 0, 0,
                                                      self.command_list))
        self.pool += COMMAND_BUFFER_SIZE + 0x400 * 16
        self.call(INIT_STREAMS, table)
        self.call(RESET_TRACKERS)

    # --- calling convention helpers ---
    def call(self, fn, *args):
        mu = self.mu
        sp = STACK - 0x10000
        mu.mem_write(sp, struct.pack("<Q", RET) + b"\0" * 0x20 + b"".join(struct.pack("<Q", a) for a in args[4:]))
        mu.reg_write(UC_X86_REG_RSP, sp)
        for reg, v in zip((UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9), args):
            mu.reg_write(reg, v)
        mu.emu_start(fn, RET)
        return mu.reg_read(UC_X86_REG_RAX)

    def _ret(self, mu, value=None):
        sp = mu.reg_read(UC_X86_REG_RSP)
        mu.reg_write(UC_X86_REG_RIP, struct.unpack("<Q", mu.mem_read(sp, 8))[0])
        mu.reg_write(UC_X86_REG_RSP, sp + 8)
        if value is not None:
            mu.reg_write(UC_X86_REG_RAX, value)

    def _dispatch(self, mu, addr, size, ud):
        self.hooks[addr](mu)

    def q(self, a):
        return struct.unpack("<Q", self.mu.mem_read(a, 8))[0]

    # --- Python stand-ins ---
    def _read(self, mu):
        dst, n = mu.reg_read(UC_X86_REG_RCX), mu.reg_read(UC_X86_REG_RDX)
        if self.pos + n > len(self.data):
            raise EOFError(f"read of {n:#x} at {self.pos:#x} passes the end of the zone ({len(self.data):#x})")
        mu.mem_write(dst, self.data[self.pos:self.pos + n])
        self.pos += n
        self._ret(mu)

    def _copy_header(self, typ, header):
        size = self.types[typ][1]
        self.pool = (self.pool + 15) & ~15
        copy = self.pool
        if self.pool + size > POOL + POOL_SIZE:
            raise MemoryError("asset pool full")
        self.mu.mem_write(copy, bytes(self.mu.mem_read(header, size)))
        self.pool += size
        self.assets.append((typ, copy, self.pos))
        if self.limit and len(self.assets) >= self.limit:
            self.mu.emu_stop()
        return copy

    def _add(self, mu):
        typ, pheader = mu.reg_read(UC_X86_REG_RCX) & 0xFFFFFFFF, mu.reg_read(UC_X86_REG_RDX)
        self._ret(mu, self._copy_header(typ, self.q(pheader)))

    def _wrapper(self, mu, typ):
        pp = mu.reg_read(UC_X86_REG_RCX)
        mu.mem_write(pp, struct.pack("<Q", self._copy_header(typ, self.q(pp))))
        self._ret(mu)

    def _sl_get_string(self, mu):
        p = mu.reg_read(UC_X86_REG_RCX)
        s = bytearray()
        while (c := mu.mem_read(p + len(s), 1)[0]) != 0:
            s.append(c)
        self.strings.append(s.decode("latin-1"))
        self._ret(mu, len(self.strings))

    def _never(self, mu):
        self._ret(mu, 0)

    def _on_import(self, mu, addr, size, ud):
        name = self.imports.get(addr, hex(addr))
        if name.endswith(("!AcquireSRWLockExclusive", "!ReleaseSRWLockExclusive", "!memset", "!memcpy")):
            raise RuntimeError(f"import {name} reached: not expected inside the loaders")
        raise RuntimeError(f"import {name} called; {self.where()}")

    def where(self):
        """Return addresses on the stack (the call chain, innermost first), the stream position, the last asset."""
        sp = self.mu.reg_read(UC_X86_REG_RSP)
        stack = bytes(self.mu.mem_read(sp, min(0x40000, STACK - 0x10000 - sp + 8)))
        chain = [v for (v,) in struct.iter_unpack("<Q", stack[:len(stack) & ~7]) if 0x140001000 <= v < 0x14A000000]
        last = self.types[self.assets[-1][0]][0] if self.assets else None
        return (f"stream at {self.pos:#x}, {len(self.assets)} assets added (last {last}); "
                f"chain {' '.join(f'{v:X}' for v in chain[:24])}")

    def _unmapped(self, mu, access, address, size, value, ud):
        rip = mu.reg_read(UC_X86_REG_RIP)
        print(f"unmapped access {address:#x} (size {size}) at {rip:#x}, stream at {self.pos:#x}", file=sys.stderr)
        return False

    def cstr(self, a, limit=256):
        try:
            b = bytes(self.mu.mem_read(a, limit))
        except UcError:
            return None
        return b.split(b"\0")[0].decode("latin-1") if b"\0" in b else None

    def name(self, header):
        """The asset's name, for the types whose header starts with their name (most; *unverified* for the rest)."""
        return self.cstr(self.q(header))

    # --- the zone ---
    def load(self, limit=0):
        self.limit = limit
        dst = self.pool
        self.pool += 0x100
        try:
            r = self.call(LOAD_ASSET_LIST, 0, dst, 0, 0)
        except UcError as e:
            raise RuntimeError(f"{e} at {self.mu.reg_read(UC_X86_REG_RIP):X}; {self.where()}") from None
        self.list_header = bytes(self.mu.mem_read(dst, 0x20))
        return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("exe")
    ap.add_argument("zone")
    ap.add_argument("oodle")
    ap.add_argument("--fp")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--all", action="store_true", help="list every asset added (index, type, name, header, end)")
    ap.add_argument("--decompressed", help="the zone's decompressed (and patched) data, e.g. from "
                    "fastfile_patch.py --out, instead of decompressing again")
    a = ap.parse_args()
    ff = Path(a.zone).read_bytes()
    o = Oodle(a.oodle)
    if a.fp:
        import fastfile_patch
        fp = Path(a.fp).read_bytes()
        header = fastfile_patch.patch_header(fp)[1]
        data = Path(a.decompressed).read_bytes() if a.decompressed else fastfile_patch.patched(ff, fp, o)
    else:
        header = ff[:zone.HEADER_SIZE]
        data = Path(a.decompressed).read_bytes() if a.decompressed else zone.decompress(ff, o)
    if len(data) != struct.unpack_from("<Q", header, 0x20)[0]:
        raise SystemExit("the decompressed data's size differs from the header's")
    emu = ZoneEmu(a.exe, data, header)
    emu.load(a.limit)
    types = emu.types
    print(f"{len(emu.strings)} script strings, {len(emu.assets)} assets added, stream at {emu.pos:#x} of {len(data):#x}")
    for i, (t, h, end) in enumerate(emu.assets):
        if a.all or i < 40:
            print(f"{i:5d}\t{types[t][0]}\t{emu.name(h)}\t{h:#x}\t{end:#x}")


if __name__ == "__main__":
    main()
