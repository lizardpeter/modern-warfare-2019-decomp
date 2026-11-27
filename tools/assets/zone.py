#!/usr/bin/env python3
"""Read an IW8 zone (fastfile) and write its decompressed zone data. See docs/assets/zones.md.

    python3 tools/assets/zone.py <zone.ff> <oo2core_7_win64.dll> [--out <zone.bin>]

Prints the header fields and the asset list size; with --out writes the decompressed data (the input to the asset
loaders). Every SHA-256 of the file's hash chain is verified. A zone whose header is older than its kind's format
version needs its .fp patch applied (not implemented yet) to be the zone the game loads. Every rule is from TU67's
code (addresses in docs/assets/zones.md) and measured on the TU63 data.
"""
import hashlib
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oodle import Oodle  # noqa: E402

HEADER_SIZE = 0x88
UNIT = 0x4000                 # the file after the header is read in 0x4000-byte units (142DED8E0)
UNITS_PER_TABLE = 0x200       # data units covered by one hash table (142DED590: counter wraps at 0x201)
LEVEL1 = 0x170                # in the signed unit: 192 SHA-256 hashes, one per hash table
LEVEL1_COUNT = 192
MAGICS = (b"IWffa100", b"IWffc100")   # 143754E50
VERSION = 11                           # 143754E5A
# 143754F20 / 142DEFEC0: the patched header's +0xC must equal this table (147602890) indexed by the zone kind
# (header byte 0x12); a zone with a .fp patch is checked with the patch's header (docs/assets/zones.md 7)
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
    return h


def stream(z: bytes, name: str | None = None) -> bytes:
    """The zone's data: the file after the header, without the signed unit and hash tables, every unit verified.

    Layout from 142DED8E0 / 142DED590 (docs/assets/zones.md 3): 0x4000-byte units from the end of the header. Unit 0
    is the signed unit (`IWffs100`; SHA-256 of bytes 0x12C..0x1970 at +0xC; the zone name at +0x12C; at +0x170, 192
    SHA-256 hashes of the hash tables). Then repeatedly: one hash table (512 SHA-256 hashes), then up to 512 data units,
    each hashing to its entry. Raises on any mismatch, as the game does. `name`, if given, must equal the name in the
    signed unit (the game compares it with the zone it asked for). The RSA-style signature at +0x2C is not checked.
    """
    signed = z[HEADER_SIZE:HEADER_SIZE + UNIT]
    if signed[:8] != b"IWffs100":
        raise ValueError("no IWffs100 signed unit after the header")
    if hashlib.sha256(signed[0x12C:0x1970]).digest() != signed[0xC:0x2C]:
        raise ValueError("signed unit: hash of its table does not match")
    zname = signed[0x12C:0x16C].split(b"\0")[0].decode("latin-1")
    if name is not None and zname != name:
        raise ValueError(f"signed unit names zone {zname!r}, expected {name!r}")
    level1 = signed[LEVEL1:LEVEL1 + 32 * LEVEL1_COUNT]
    out, p, t = [], HEADER_SIZE + UNIT, 0
    while p < len(z):
        if t >= LEVEL1_COUNT:
            raise ValueError("more hash tables than the signed unit lists")
        table = z[p:p + UNIT]
        if hashlib.sha256(table).digest() != level1[32 * t:32 * t + 32]:
            raise ValueError(f"hash table {t} at {p:#x} does not match the signed unit")
        p += UNIT
        for i in range(UNITS_PER_TABLE):
            if p >= len(z):
                break
            unit = z[p:p + UNIT]
            if hashlib.sha256(unit).digest() != table[32 * i:32 * i + 32]:
                raise ValueError(f"data unit at {p:#x} does not match hash table {t} entry {i}")
            out.append(unit)
            p += UNIT
        t += 1
    return b"".join(out)


STREAM_MAGIC = b"\x02IWC"     # the first 4 bytes of the data (measured on every zone read)


def blocks(z: bytes):
    """Yield (offset, compressed size, decompressed size, check value) for each block, and the codec first.
    Offsets are into stream(z), not the file."""
    z = stream(z)
    if z[:4] != STREAM_MAGIC:
        raise ValueError(f"data does not start with {STREAM_MAGIC!r}")
    p = 4
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
    z = stream(z)
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
          f"({'current' if h.format_ok else 'needs its .fp patch'}) size {h.size:#x}")
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
