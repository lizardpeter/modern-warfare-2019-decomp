#!/usr/bin/env python3
"""Read streamed data from `.xpak` packs. Format: docs/assets/streaming.md.

    python3 tools/assets/xpak.py <pack.xpak>        print the header and the first index entries

`Pack(source)` takes a path or any object with `read(offset, size)`; `pack.item(key, size)` returns an item's
decoded bytes (the caller knows the decoded size: for images it is in the image header).
"""
from __future__ import annotations

import argparse
import struct
import sys
from bisect import bisect_left
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

MAGIC = 0x4950414B          # "KAPI" little-endian, i.e. IPAK
VERSION = 0xD
CHUNK_MAX = 0x3FFE0         # largest decoded size of one chunk (143C97CE0)
SIZE_MASK = 0x7FFFFFFFFFFFFFFF


class _FileSource:
    def __init__(self, path):
        self.f = open(path, "rb")

    def read(self, offset, size):
        self.f.seek(offset)
        return self.f.read(size)


class Pack:
    def __init__(self, source, oodle=None):
        self.src = _FileSource(source) if isinstance(source, (str, Path)) else source
        self.oodle = oodle
        h = self.src.read(0, 0x180)
        magic, _, version = struct.unpack_from("<IHH", h, 0)
        if magic != MAGIC or version != VERSION:
            raise ValueError(f"not an IPAK v{VERSION} pack (magic {magic:#x}, version {version})")
        (self.count, self.data_offset, self.data_size, _, self.index_offset,
         self.index_size) = struct.unpack_from("<6Q", h, 0x138)
        self._keys = self._entries = None

    def index(self):
        """Sorted list of (key, offset relative to the data, stored size)."""
        if self._entries is None:
            raw = self.src.read(self.index_offset, self.index_size)
            self._entries = [struct.unpack_from("<QQQ", raw, 24 * i) for i in range(self.index_size // 24)]
            self._keys = [e[0] for e in self._entries]
        return self._entries

    def find(self, key):
        self.index()
        i = bisect_left(self._keys, key)
        if i < len(self._keys) and self._keys[i] == key:
            _, off, size = self._entries[i]
            return off, size & SIZE_MASK
        return None

    def item(self, key, size):
        """Decode an item: 0x80-aligned chunk headers {u32 count <= 30, u32 output offset, count x u32 (compressed
        size | type << 24)}, the chunks following each header at +0x80, 4-aligned. Types: 0 stored, 6/7 Oodle,
        4/5 LZ4, 0xCF skipped. Each chunk decodes to min(remaining, 0x3FFE0) bytes."""
        found = self.find(key)
        if found is None:
            raise KeyError(f"{key:#x} not in this pack")
        off, stored = found
        b = self.src.read(self.data_offset + off, stored)
        out = bytearray(size)
        pos = 0
        while pos + 8 <= len(b):
            count, dest = struct.unpack_from("<II", b, pos)
            if count == 0:
                break
            if count > 30:
                raise ValueError(f"chunk header at {pos:#x} has {count} chunks")
            entries = struct.unpack_from(f"<{count}I", b, pos + 8)
            p = pos + 0x80
            for e in entries:
                csize, kind = e & 0xFFFFFF, e >> 24
                n = min(size - dest, CHUNK_MAX)
                if kind == 0:
                    out[dest:dest + csize] = b[p:p + csize]
                    dest += csize
                elif kind in (6, 7):
                    out[dest:dest + n] = self.oodle.decompress(b[p:p + csize], n)
                    dest += n
                elif kind in (4, 5):
                    import lz4.block     # 147248D50, as zone codec 4/5
                    out[dest:dest + n] = lz4.block.decompress(b[p:p + csize], uncompressed_size=n)
                    dest += n
                elif kind == 0xCF:
                    pass
                else:
                    raise ValueError(f"chunk type {kind} not handled")
                p = (p + csize + 3) & ~3
            pos = (p + 0x7F) & ~0x7F
        return bytes(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack")
    a = ap.parse_args()
    p = Pack(a.pack)
    print(f"{p.count} items, data {p.data_offset:#x}+{p.data_size:#x}, index {p.index_offset:#x}+{p.index_size:#x}")
    for k, off, size in p.index()[:10]:
        print(f"  {k:#018x} at {off:#x}, {size & SIZE_MASK:#x} bytes")


if __name__ == "__main__":
    main()
