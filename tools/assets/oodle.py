#!/usr/bin/env python3
"""OodleLZ_Decompress from the game's own oo2core_7_win64.dll, run in Unicorn.

The zone and .xpak readers decompress with the exact library the game ships, so their output is the game's by
construction. Only OodleLZ_Decompress is called; DllMain never runs. Arguments match the zone stream's call in
TU67 (142DEF43B): fuzzSafe 1, no CRC check, verbosity 0, decoder memory supplied (0x6C0B8 bytes), thread phase 3.
The DLL is an original file (target.toml [support.oodle]): pass its path; its sha256 is checked.

    from oodle import Oodle; o = Oodle("oo2core_7_win64.dll"); raw = o.decompress(block, raw_size)
"""
import hashlib
import struct
import tomllib
from pathlib import Path

import pefile
from unicorn import UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_64, Uc
from unicorn.x86_const import (UC_X86_REG_GS_BASE, UC_X86_REG_R8, UC_X86_REG_R9, UC_X86_REG_RAX, UC_X86_REG_RCX,
                               UC_X86_REG_RDX, UC_X86_REG_RSP)

ROOT = Path(__file__).resolve().parents[2]
DECODER_MEMORY_SIZE = 0x6C0B8   # the game's own value (142DEF403)
MAX_BLOCK = 0x1000000


class Oodle:
    STUB, STACK, TEB, HEAP, RET = 0x7FF000000000, 0x7FFE00000000, 0x7FFD0000, 0x200000000, 0xDEAD0000

    def __init__(self, path):
        raw = Path(path).read_bytes()
        want = tomllib.loads((ROOT / "target.toml").read_text())["support"]["oodle"]["sha256"]
        if hashlib.sha256(raw).hexdigest() != want:
            raise SystemExit(f"{path}: sha256 differs from target.toml [support.oodle]")
        pe = pefile.PE(data=raw)
        mu = self.mu = Uc(UC_ARCH_X86, UC_MODE_64)
        base = pe.OPTIONAL_HEADER.ImageBase
        mu.mem_map(base, (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF)
        mu.mem_write(base, pe.get_memory_mapped_image())
        # every import answers 0 and is logged: the decompressor itself makes no calls when given decoder memory
        mu.mem_map(self.STUB, 0x10000)
        mu.mem_write(self.STUB, b"\xC3" * 0x10000)
        self.imports, self.calls = {}, []
        for imp in pe.DIRECTORY_ENTRY_IMPORT:
            for f in imp.imports:
                a = self.STUB + len(self.imports) * 16
                self.imports[a] = f.name.decode()
                mu.mem_write(f.address, struct.pack("<Q", a))
        mu.hook_add(UC_HOOK_CODE, self._on_import, begin=self.STUB, end=self.STUB + 0xFFFF)
        mu.mem_map(self.STACK - 0x100000, 0x200000)
        mu.mem_map(self.TEB, 0x10000)
        mu.mem_write(self.TEB + 0x30, struct.pack("<Q", self.TEB))
        mu.reg_write(UC_X86_REG_GS_BASE, self.TEB)
        mu.mem_map(self.HEAP, 4 * MAX_BLOCK)
        self.fn = base + next(e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name == b"OodleLZ_Decompress")

    def _on_import(self, mu, addr, size, ud):
        self.calls.append(self.imports.get(addr))
        mu.reg_write(UC_X86_REG_RAX, 0)

    def decompress(self, block: bytes, raw_size: int) -> bytes:
        """Decompress one block; raises if Oodle does not return exactly raw_size bytes (as the game checks)."""
        if len(block) > MAX_BLOCK or raw_size > MAX_BLOCK:
            raise ValueError("block too large")
        mu, src, dst, mem = self.mu, self.HEAP, self.HEAP + MAX_BLOCK, self.HEAP + 2 * MAX_BLOCK
        mu.mem_write(src, block)
        sp = self.STACK - 0x1000
        args = [1, 0, 0, 0, 0, 0, 0, mem, DECODER_MEMORY_SIZE, 3]
        mu.mem_write(sp, struct.pack("<Q", self.RET) + b"\0" * 0x20 + b"".join(struct.pack("<Q", a) for a in args))
        mu.reg_write(UC_X86_REG_RSP, sp)
        for reg, v in ((UC_X86_REG_RCX, src), (UC_X86_REG_RDX, len(block)), (UC_X86_REG_R8, dst), (UC_X86_REG_R9, raw_size)):
            mu.reg_write(reg, v)
        mu.emu_start(self.fn, self.RET)
        n = mu.reg_read(UC_X86_REG_RAX)
        if n != raw_size:
            raise ValueError(f"OodleLZ_Decompress returned {n}, expected {raw_size}")
        return bytes(mu.mem_read(dst, raw_size))
