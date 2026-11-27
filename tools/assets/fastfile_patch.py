#!/usr/bin/env python3
"""Apply an IW8 fastfile patch (.fp) to its base zone (.ff): the decompressed zone data the game loads.

    python3 tools/assets/fastfile_patch.py <zone.ff> <zone.fp> <oo2core_7_win64.dll> [--out <zone.bin>]

Every rule is from TU67's decoder 143F212C0 (docs/assets/zones.md 7). The delta is VCDIFF (RFC 3284) from the base
zone's decompressed data to the patched zone's, with two extensions in the window indicator: 0x04, an extra varint
giving where the source read starts (the segment used is still source[pos:pos+len]); 0x08, a 4-byte checksum after
the window, XXH64 of the window's output seeded with the previous window's checksum (0 for the first), folded to
32 bits as hi ^ lo. Every checksum is verified, as the game does (DEV error 0x9A on mismatch).
"""
import struct
import sys
from pathlib import Path

import xxhash

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zone  # noqa: E402
from oodle import Oodle  # noqa: E402

PATCH_MAGIC = b"IWffd100"
PATCH_HEADER = 0x148          # 0x38 bytes of patch fields, the base header, the patched header
VCDIFF_MAGIC = b"\xD6\xC3\xC4"
NOOP, ADD, RUN, COPY = 0, 1, 2, 3


def default_code_table():
    """RFC 3284 section 5.6. The game builds its table at run time (1554E0EA0); every window checksum of a full
    patch matching is the check that the two agree."""
    t = [(RUN, 0, 0, NOOP, 0, 0)]
    t += [(ADD, s, 0, NOOP, 0, 0) for s in range(18)]
    for m in range(9):
        t.append((COPY, 0, m, NOOP, 0, 0))
        t += [(COPY, s, m, NOOP, 0, 0) for s in range(4, 19)]
    for m in range(6):
        t += [(ADD, a, 0, COPY, c, m) for a in range(1, 5) for c in range(4, 7)]
    for m in range(6, 9):
        t += [(ADD, a, 0, COPY, 4, m) for a in range(1, 5)]
    t += [(COPY, 4, m, ADD, 1, 0) for m in range(9)]
    assert len(t) == 256
    return t


TABLE = default_code_table()


def varint(d, p):
    v = 0
    while True:
        b = d[p]
        p += 1
        v = (v << 7) | (b & 0x7F)
        if not b & 0x80:
            return v, p


def decode_window(src, tgt_len, add, inst, addr):
    """One window: src is the source segment; COPY addresses past its end refer to this window's output."""
    near, near_i, same = [0] * 4, 0, [0] * 768
    out = bytearray()
    a_p = i_p = d_p = 0
    s_len = len(src)
    while i_p < len(inst):
        entry = TABLE[inst[i_p]]
        i_p += 1
        for typ, size, mode in (entry[:3], entry[3:]):
            if typ == NOOP:
                continue
            if size == 0:
                size, i_p = varint(inst, i_p)
            if typ == ADD:
                out += add[a_p:a_p + size]
                a_p += size
            elif typ == RUN:
                out += add[a_p:a_p + 1] * size
                a_p += 1
            else:
                here = s_len + len(out)
                if mode == 0:
                    a, d_p = varint(addr, d_p)
                elif mode == 1:
                    a, d_p = varint(addr, d_p)
                    a = here - a
                elif mode < 6:
                    a, d_p = varint(addr, d_p)
                    a += near[mode - 2]
                else:
                    a = same[(mode - 6) * 256 + addr[d_p]]
                    d_p += 1
                near[near_i] = a
                near_i = (near_i + 1) % 4
                same[a % 768] = a
                if a + size <= s_len:
                    out += src[a:a + size]
                elif a >= s_len and a - s_len + size <= len(out):
                    out += out[a - s_len:a - s_len + size]
                else:
                    for k in range(size):       # overlapping copy: byte by byte, as RFC 3284 requires
                        q = a + k
                        out.append(src[q] if q < s_len else out[q - s_len])
    if len(out) != tgt_len:
        raise ValueError(f"window produced {len(out)} bytes, expected {tgt_len}")
    return bytes(out)


def apply(delta: bytes, source: bytes) -> bytes:
    if delta[:3] != VCDIFF_MAGIC or delta[3] != 0:
        raise ValueError("not VCDIFF")
    if delta[4] & 0xF3:                      # 143F212C0: header indicator bits other than 0x04/0x08 are rejected
        raise ValueError(f"header indicator {delta[4]:#x} not supported")
    out, p, seed, n = [], 5, 0, 0
    while p < len(delta):
        ind = delta[p]
        p += 1
        if ind & 2:      # 143F212C0: (ind & 3) == 3 gives DEV ERROR 0x94, 2 (VCD_TARGET) gives 0x95
            raise ValueError(f"window {n}: target-sourced windows are rejected by the game")
        src = b""
        if ind & 1:
            s_len, p = varint(delta, p)
            s_pos, p = varint(delta, p)
            if ind & 4:
                _read_from, p = varint(delta, p)  # where the game starts its source read; does not change the segment
            src = source[s_pos:s_pos + s_len]
            if len(src) != s_len:
                raise ValueError(f"window {n}: source segment past the end of the base")
        d_len, p = varint(delta, p)
        body = p
        t_len, p = varint(delta, p)
        if delta[p] != 0:
            raise ValueError(f"window {n}: compressed sections are rejected by the game (0x98)")
        p += 1
        a_len, p = varint(delta, p)
        i_len, p = varint(delta, p)
        c_len, p = varint(delta, p)
        add = delta[p:p + a_len]
        inst = delta[p + a_len:p + a_len + i_len]
        addr = delta[p + a_len + i_len:p + a_len + i_len + c_len]
        if p + a_len + i_len + c_len != body + d_len:
            raise ValueError(f"window {n}: section lengths do not add up to the delta length")
        t = decode_window(src, t_len, add, inst, addr)
        p = body + d_len
        if ind & 8:
            h = xxhash.xxh64(t, seed).intdigest()
            check = (h >> 32) ^ (h & 0xFFFFFFFF)
            stored = struct.unpack_from("<I", delta, p)[0]
            if check != stored:
                raise ValueError(f"window {n}: checksum {check:#010x}, stored {stored:#010x}")
            seed = check
            p += 4
        out.append(t)
        n += 1
    return b"".join(out)


def patch_header(fp: bytes):
    if fp[:8] != PATCH_MAGIC or struct.unpack_from("<I", fp, 0xC)[0] != 4:
        raise ValueError("not an IW8 fastfile patch")
    return fp[0x38:0xC0], fp[0xC0:PATCH_HEADER]


def delta_of(fp: bytes, oodle: Oodle) -> bytes:
    """The decompressed VCDIFF of a data patch: the same unit layout and block stream as a zone, after 0x148 bytes."""
    shifted = fp[PATCH_HEADER - zone.HEADER_SIZE:]      # zone.stream() expects units to start at HEADER_SIZE
    return zone.decompress(shifted, oodle)


def patched(ff: bytes, fp: bytes, oodle: Oodle) -> bytes:
    """The patched zone's decompressed data."""
    old, new = patch_header(fp)
    if ff[:zone.HEADER_SIZE] != old:
        raise ValueError("the patch is not for this base zone (header differs: DEV ERROR 0x1799)")
    base = zone.decompress(ff, oodle)
    if len(fp) <= PATCH_HEADER:
        return base                                       # header-only patch
    data = apply(delta_of(fp, oodle), base)
    want = struct.unpack_from("<Q", new, 0x20)[0]
    if len(data) != want:
        raise ValueError(f"patched data is {len(data):#x} bytes, the patched header says {want:#x}")
    return data


def main():
    ff, fp = Path(sys.argv[1]).read_bytes(), Path(sys.argv[2]).read_bytes()
    data = patched(ff, fp, Oodle(sys.argv[3]))
    strings, assets, end = zone.asset_list(data)
    print(f"patched zone: {len(data):#x} bytes, {len(strings)} script strings, {len(assets)} assets")
    if "--out" in sys.argv:
        Path(sys.argv[sys.argv.index("--out") + 1]).write_bytes(data)


if __name__ == "__main__":
    main()
