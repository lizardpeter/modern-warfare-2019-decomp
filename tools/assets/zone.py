#!/usr/bin/env python3
"""Read an IW8 zone (fastfile) and write its decompressed zone data. See docs/assets/zones.md.

    python3 tools/assets/zone.py <zone.ff> <oo2core_7_win64.dll> [--out <zone.bin>]

Prints the header fields and block statistics; with --out writes the decompressed data (the input to the asset
loaders). Every rule is from TU67's code (addresses in docs/assets/zones.md) and measured on the TU63 data.
"""
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oodle import Oodle  # noqa: E402

HEADER_SIZE = 0x88
SIGNED_SIZE = 0x8004          # 'IWffs100' block between the header and the stream (measured)
STREAM_START = HEADER_SIZE + SIGNED_SIZE
MAGICS = (b"IWffa100", b"IWffc100")   # 143754E50
VERSION = 11                           # 143754E5A
# 143754F20 / 142DEFEC0: header +0xC must equal this table (147602890) indexed by the zone kind (header byte 0x12)
FORMAT_VERSION = [0x10C1, 0x10C1, 0xFF3, 0xFF3, 0xFF3, 0xFF3, 0x10C1] + [0xFCD] * 10
CODEC_STORED, CODEC_OODLE = (1,), (6, 7)      # 142DEF29F; 4 and 5 use 147248D50 (unidentified), others DEV ERROR 0x298


@dataclass
class Header:
    magic: bytes
    version: int
    format_version: int
    kind: int
    size: int      # +0x20: decompressed zone size (equals the stream's own total)

    @property
    def format_ok(self) -> bool:
        return self.kind < len(FORMAT_VERSION) and FORMAT_VERSION[self.kind] == self.format_version


def header(z: bytes) -> Header:
    h = Header(z[:8], *struct.unpack_from("<II", z, 8), z[0x12], struct.unpack_from("<Q", z, 0x20)[0])
    if h.magic not in MAGICS or h.version != VERSION:
        raise ValueError(f"not an IW8 zone: {h.magic!r} version {h.version}")
    if z[HEADER_SIZE:HEADER_SIZE + 8] != b"IWffs100":
        raise ValueError("no IWffs100 block after the header")
    return h


def blocks(z: bytes):
    """Yield (offset, compressed size, decompressed size, check value) for each block, and the codec first."""
    p = STREAM_START
    total = struct.unpack_from("<I", z, p)[0]
    codec = z[p + 7]
    yield codec, total
    p += 8
    seen = 0
    while seen < total:
        cs, us, check = struct.unpack_from("<III", z, p)
        yield p + 12, cs, us, check
        seen += us
        p += 12 + cs + (-cs % 4)    # blocks are padded to 4 bytes (142DEF335)


def decompress(z: bytes, oodle: Oodle) -> bytes:
    it = blocks(z)
    codec, total = next(it)
    out = bytearray()
    for off, cs, us, _ in it:
        if codec in CODEC_OODLE:
            out += oodle.decompress(z[off:off + cs], us)
        elif codec in CODEC_STORED:
            out += z[off:off + cs]
        else:
            raise ValueError(f"codec {codec} not supported yet")
    if len(out) != total:
        raise ValueError(f"stream gave {len(out)} bytes, expected {total}")
    return bytes(out)


FOLLOWS = -2   # pointer value meaning "the pointed-to data follows inline in the stream" (measured)


def asset_list(data: bytes):
    """Parse the XAssetList at the start of decompressed zone data.

    Returns (script strings, [(asset type, header pointer value, offset of the asset entry)], offset after the list).
    Layout measured on 185 zones (docs/assets/zones.md 5): u32 string count, pad, string-array pointer, u32 asset
    count, pad, asset-array pointer; the string pointers inline, then each string inline (NUL-terminated) for
    pointers of -2; then the asset array, 16 bytes per asset (u32 type, pad, header pointer).
    """
    sc, sp, ac, ap = struct.unpack_from("<I4xqI4xq", data, 0)
    p = 0x20
    ptrs = [struct.unpack_from("<q", data, p + 8 * i)[0] for i in range(sc)] if sp == FOLLOWS else []
    p += 8 * len(ptrs)
    strings = []
    for v in ptrs:
        if v == FOLLOWS:
            e = data.index(b"\0", p)
            strings.append(data[p:e].decode("latin-1"))
            p = e + 1
        else:
            strings.append(None)
    assets = []
    if ap == FOLLOWS:
        for i in range(ac):
            t, h = struct.unpack_from("<I4xq", data, p)
            assets.append((t, h, p))
            p += 16
    return strings, assets, p


def main():
    z = Path(sys.argv[1]).read_bytes()
    h = header(z)
    print(f"{h.magic.decode()} version {h.version} kind {h.kind} format {h.format_version:#x} "
          f"({'accepted' if h.format_ok else 'REJECTED'} by TU67) size {h.size:#x}")
    data = decompress(z, Oodle(sys.argv[2]))
    if len(data) != h.size:
        raise SystemExit(f"decompressed {len(data):#x} bytes, header says {h.size:#x}")
    print(f"decompressed {len(data):#x} bytes")
    strings, assets, end = asset_list(data)
    print(f"{len(strings)} script strings, {len(assets)} assets; asset data from {end:#x}")
    if "--out" in sys.argv:
        Path(sys.argv[sys.argv.index("--out") + 1]).write_bytes(data)


if __name__ == "__main__":
    main()
