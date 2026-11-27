"""What the loaders call that is not stream loading: the stand-ins both the emulator check and the translated loaders use.

Addresses are TU67's. The emulator (tests/assets/zone_emu.py) and the translated loaders (load.py) replace exactly
these functions, with the same behaviour and memory layout, so their memory can be compared byte for byte.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

IMAGE = 0x140000000
STUB, STACK, TEB, TLS, POOL, BLOCKS, RET = 0x7FF000000000, 0x7FFE00000000, 0x7FFD0000, 0x7FFC0000, 0x600000000, 0x800000000, 0xDEAD0000
POOL_SIZE = 0x40000000

LOAD_ASSET_LIST = 0x1437608F0
INIT_STREAMS = 0x143760420
RESET_TRACKERS = 0x142DF10B0
READ = 0x143755EA0
ADD_ASSET = 0x143757490
SL_GET_STRING = 0x143BC1270
CANCEL_CHECKS = (0x143759410, 0x143759420)
# renderer and streaming work the loaders start after reading their data; none of it reads the stream (each was
# read before it was stubbed). address: what it is
SKIPPED = {
    0x1465F7050: "GPU buffer creation for an XSurface field (+0x18 of the 0x80 struct read by 142EA61D0)",
    0x1465F7490: "GPU buffers and views for XSurface vertex data (writes +0x158..+0x230 of each 0x238 entry)",
    0x14661A6F0: "renderer: create a GPU buffer from loaded data (out, ..., count, data, debug name, flags)",
    0x14661A800: "renderer: create a GPU buffer from loaded data (e.g. 'world posData' by 142EAB6F0)",
    0x14661A8D0: "renderer: create a GPU buffer from loaded data",
    0x14661AB10: "renderer: create an index buffer (u16 indices, e.g. 'bsp index buffer')",
    0x14661ABA0: "renderer: create an index buffer from a byte size",
    0x1466A4350: "renderer: create a texture (reads width/height/depth at +0xC/+0x10/+0xE, mips at +0x14)",
}
# the 19 wrappers around DB_AddXAsset, by the type each passes: each takes a pointer to the header pointer, adds
# the asset and replaces the pointer, then starts the type's renderer, sound or streaming setup (not reproduced)
WRAPPERS = {
    0x14311AA40: 0x17, 0x14311AA80: 0x18, 0x14311AAC0: 0x0C, 0x14311AB00: 0x73, 0x14311AB40: 0x1F,
    0x14311ABA0: 0x0D, 0x14311ABE0: 0x10, 0x14311AC10: 0x0F, 0x14311AC40: 0x11, 0x14311AC70: 0x0E,
    0x14311ACA0: 0x2C, 0x14311ACE0: 0x33, 0x14311AD10: 0x15, 0x14311AD70: 0x16, 0x14311ADC0: 0x14,
    0x14311AE20: 0x43, 0x14311AE60: 0x07, 0x14311AE90: 0x09,
}

BLOCK_COUNT = 8
COMMAND_BUFFER_VARS, COMMAND_BUFFER_SIZE = 0x14BCC42F0, 0x8000000


# C runtime functions the loaders call; hand-written assembly Ghidra cannot render, so they get their standard meaning
MEMCPY = 0x1474213E0          # memcpy(dst, src, n), e.g. from 142DFEDA0

# Bytes the game leaves uninitialised: their value is whatever was on its stack, so no reader can reproduce them and
# comparisons skip them (records/bugs.tsv B0001). Offsets inside each deferred command's data record and list entry.
UNDEFINED_COMMAND_DATA = range(0xC, 0x10)    # 142DFEDA0 copies [rsp+0x40..0x4F]; [rsp+0x4C] is never written
UNDEFINED_COMMAND_ENTRY = range(0xC, 0x10)   # 142DEDDA0 writes only the low 4 bytes of the 8-byte field at +8


def asset_types():
    rows = {}
    for line in (ROOT / "analysis/ModernWarfare_TU67/assets/asset_types.tsv").read_text().splitlines():
        f = line.split("\t")
        if line.startswith("#") or f[0] == "type":
            continue
        rows[int(f[0])] = (f[1], int(f[5], 16) if f[5] else 0)
    return rows
