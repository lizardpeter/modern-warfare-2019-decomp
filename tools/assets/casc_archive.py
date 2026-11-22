#!/usr/bin/env python3
"""Walk a Battle.net CASC data archive (Data/data/data.NNN) and decode its BLTE entries. Standard library only.

    python3 tools/assets/casc_archive.py <data.NNN> [--extract-zones <dir>]

Prints one line per entry (archive offset, size, frames, what the content starts with). Names come later, from the
TVFS root and encoding table (both are entries in data.000); until then entries are identified by offset and kind.

Layout, measured on the TU63 install's data.000:
  - 0x1E0-byte archive header, then entries back to back.
  - entry: 16-byte encoding key (byte-reversed), u32 LE total entry size (header included), 2 bytes flags,
    8 bytes checksums; then a BLTE blob of size - 0x1E.
  - BLTE: 'BLTE', u32 BE header size (0: one frame, the rest of the blob), then u8 flags, u24 BE frame count,
    per frame u32 BE encoded size, u32 BE decoded size, 16-byte MD5; frames follow. Frame mode byte 'N' stored,
    'Z' zlib. Other modes ('E' encrypted, '4', 'F') are reported, not decoded.
"""
import struct
import sys
import zlib
from pathlib import Path

ARCHIVE_HEADER = 0x1E0
ENTRY_HEADER = 0x1E


def blte_frames(b: bytes):
    """Yield the decoded frames of one BLTE blob (None for a frame mode not decoded here)."""
    if b[:4] != b"BLTE":
        raise ValueError("not BLTE")
    hs = struct.unpack(">I", b[4:8])[0]
    if hs == 0:
        frames, p = [(len(b) - 8, None)], 8
    else:
        count = int.from_bytes(b[9:12], "big")
        frames, q = [], 12
        for _ in range(count):
            frames.append(struct.unpack(">II", b[q:q + 8]))
            q += 24
        p = hs
    for enc, dec in frames:
        fr = b[p:p + enc]
        p += enc
        if fr[:1] == b"N":
            yield fr[1:]
        elif fr[:1] == b"Z":
            yield zlib.decompress(fr[1:])
        else:
            yield None


def entries(data: bytes):
    """(offset, size, encoding key hex) for every entry of an archive."""
    pos = ARCHIVE_HEADER
    while pos + ENTRY_HEADER <= len(data):
        ekey = data[pos:pos + 16][::-1].hex()
        size = struct.unpack_from("<I", data, pos + 16)[0]
        if size < ENTRY_HEADER or data[pos + ENTRY_HEADER:pos + ENTRY_HEADER + 4] != b"BLTE":
            raise ValueError(f"entry at {pos:#x} is not followed by BLTE")
        yield pos, size, ekey
        pos += size


def content(data: bytes, pos: int, size: int) -> bytes | None:
    """Decoded content of an entry, or None if any frame uses a mode not decoded here."""
    parts = list(blte_frames(data[pos + ENTRY_HEADER:pos + size]))
    return None if any(p is None for p in parts) else b"".join(parts)


def main():
    path = Path(sys.argv[1])
    data = path.read_bytes()
    out = Path(sys.argv[sys.argv.index("--extract-zones") + 1]) if "--extract-zones" in sys.argv else None
    for pos, size, ekey in entries(data):
        c = content(data, pos, size)
        head = c[:8] if c is not None else b"?"
        print(f"{pos:#010x}\t{size}\t{ekey}\t{head!r}")
        if out and c is not None and c[:4] == b"IWff":
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{path.name}_{pos:08x}.ff").write_bytes(c)


if __name__ == "__main__":
    main()
