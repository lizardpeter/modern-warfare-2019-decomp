#!/usr/bin/env python3
"""Read raw files (type 0x2F) and compiled scripts (scriptfile). Rules: docs/assets/rawfiles.md."""
from __future__ import annotations

import struct
import zlib


def read_rawfile(read, a: int) -> bytes:
    """0x18 bytes (loader 142E7C0B0): name, u32 compressed size (+0x08), u32 size (+0x0C), zlib data (+0x10).
    A compressed size of 0 means the data is stored as is."""
    h = read(a, 0x18)
    csize, size = struct.unpack_from("<II", h, 8)
    p = struct.unpack_from("<Q", h, 0x10)[0]
    if not p:
        return b""
    data = read(p, csize or size)
    out = zlib.decompress(data) if csize else data
    if len(out) != size:
        raise ValueError(f"raw file is {len(out)} bytes, header says {size}")
    return out


def read_scriptfile(read, a: int):
    """0x28 bytes (loader 142E745B0): name, u32 compressed size (+0x08), u32 size (+0x0C), u32 bytecode size
    (+0x10), zlib-compressed header and string section (+0x18), bytecode (+0x20). Returns (section, bytecode)."""
    h = read(a, 0x28)
    csize, size, blen = struct.unpack_from("<III", h, 8)
    p, b = struct.unpack_from("<QQ", h, 0x18)
    section = zlib.decompress(read(p, csize)) if p and csize else b""
    if len(section) != size:
        raise ValueError(f"script section is {len(section)} bytes, header says {size}")
    return section, (read(b, blen) if b and blen else b"")
