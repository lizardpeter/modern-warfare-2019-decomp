#!/usr/bin/env python3
"""Read images (type 0x13). Header and stream rules: docs/assets/images.md.

`read_image(read, address)` parses a loaded image header; `Image.top_mip(fetch)` decodes the largest mip that the
caller can supply, where `fetch(key, size)` returns a streamed item's bytes (e.g. xpak.Pack.item) or None.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

# +0x14 format -> (Pillow BCn decoder number or "raw", bytes per 4x4 block or per pixel). Checked by decoding and
# looking at the result: 7, 35, 36, 41, 46, 47. 40 and 44 are *unverified* (by their place in the sequence).
FORMATS = {
    7: ("raw", 4),        # R8G8B8A8
    35: (1, 8),           # BC1
    36: (1, 8),           # BC1, sRGB (colour maps)
    40: (3, 16),          # BC3 sRGB, *unverified*
    41: (4, 8),           # BC4 (masks)
    46: (7, 16),          # BC7 (normal maps)
    47: (7, 16),          # BC7 sRGB (colour maps)
}


@dataclass
class Stream:
    key: int
    level: int
    end: int              # byte size of this and all smaller streams' mips
    width: int
    height: int


@dataclass
class Image:
    name: str
    format: int
    usage: int            # +0x2E: 6 colour, 7 normal, 3 masks, 0 other (measured)
    width: int
    height: int
    depth: int
    mips: int
    flags: int
    total: int            # +0x1C: byte size of all mips
    streams: list
    inline: bytes | None  # non-streamed images: the pixel data (+0xE0)

    def top_mip(self, fetch):
        """(width, height, RGBA bytes) of the largest available mip, or None."""
        from PIL import Image as PImage
        codec, unit = FORMATS.get(self.format, (None, None))
        if codec is None:
            return None
        for i in range(len(self.streams) - 1, -1, -1):
            s = self.streams[i]
            size = s.end - (self.streams[i - 1].end if i else 0)
            data = fetch(s.key, size) if s.key else None
            if not data:
                continue
            w, h = s.width, s.height
            if codec == "raw":
                im = PImage.frombytes("RGBA", (w, h), data[:w * h * 4])
            else:
                bw, bh = max(1, (w + 3) // 4), max(1, (h + 3) // 4)
                mode = {4: "L", 5: "RGB"}.get(codec, "RGBA")
                im = PImage.frombytes(mode, (bw * 4, bh * 4), data[:bw * bh * unit], "bcn", codec).crop((0, 0, w, h))
            return w, h, im.convert("RGBA").tobytes()
        return None


def read_image(read, a: int, name: str = "") -> Image:
    """Image header (0xE8 bytes, loader 142EAAFC0). +0x18 flags (0x40: streamed, 142EAB290), +0x1C total size,
    +0x14 format, +0x24/+0x26 width/height, +0x28 depth, +0x2E usage, +0x30 mip count, +0x32 stream count,
    +0x38 + 0x28 x i streams: {u64 key, ..., +0x20 u32 level | (end / 16) << 8, u16 width, u16 height}."""
    h = read(a, 0xE8)
    flags, total = struct.unpack_from("<II", h, 0x18)
    fmt = struct.unpack_from("<I", h, 0x14)[0]
    w, hh, depth = struct.unpack_from("<HHH", h, 0x24)
    streams = []
    for i in range(h[0x32]):
        o = 0x38 + 0x28 * i
        key = struct.unpack_from("<Q", h, o)[0]
        v, sw, sh = struct.unpack_from("<IHH", h, o + 0x20)
        streams.append(Stream(key, v & 0xFF, (v >> 8) * 16, sw, sh))
    inline = None
    if not flags & 0x40:
        p = struct.unpack_from("<Q", h, 0xE0)[0]
        inline = read(p, total) if p else None
    return Image(name, fmt, h[0x2E], w, hh, depth, struct.unpack_from("<H", h, 0x30)[0], flags, total, streams, inline)
