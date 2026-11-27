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
    0x1467373D0: "renderer: create a reflection probe texture ('<raw reflection probe>', 256x256, 6 faces) and write its "
                 "handle to +8 of the probe",
    # shader stages from their bytecode (+0x18 data, +0x20 size), by the stage name each passes to 1465E8F00
    0x146724740: "renderer: create a compute shader from its bytecode (+0x18 data, +0x20 size)",
    0x146724770: "renderer: create a domain shader from its bytecode (+0x18 data, +0x20 size)",
    0x1467247A0: "renderer: create a shader of another stage (name at 1476B5620) from its bytecode",
    0x1467247D0: "renderer: create a pixel shader from its bytecode (+0x18 data, +0x20 size)",
    0x146724800: "renderer: create a vertex shader from its bytecode (+0x18 data, +0x20 size)",
    0x146724830: "renderer: an empty function (returns at once)",
    0x143C9F190: "runtime: run the registration callbacks of a loaded terrain piece (14311AE00 after it stores the "
                 "owner at +0x30; table 14A3E3CC0 by the kind at +0x3C, when +0x3D bit 2 is set)",
    0x146724840: "renderer: create the GPU constant buffers of a technique's passes (14661AF70); writes their handles "
                 "into the loaded data (+0x30 / +0x68 of each entry of +0x68), runtime values left zero here",
    0x1467249E0: "renderer: register a loaded image (142E85450's) with the image streamer (142FCE290); also sets "
                 "bit 0x8000 of the image's +0xC, a runtime flag left clear here",
    0x146590BC0: "renderer: decrypt a GPU buffer's debug name (XOR string at 14A483F58) and create the buffer",
    0x146590C50: "renderer: fill +0x130 with renderer pool indices (143118EC0 / 143118EA0: position in the renderer's "
                 "own resource pools) and create that GPU buffer, named by an XOR string at 14A483F28",
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


# What gets translated: the loader address ranges (target.toml commit_signatures) plus these helpers outside them
# that the loaders were measured to execute (all four checked zones; generate.py). A call to anything else is
# generated as a run-time error naming the function, so an untranslated path is reported, never skipped.
TRANSLATED_RANGES = ((0x142DE0000, 0x142EC0000), (0x14311A000, 0x14311F000), (0x143750000, 0x143770000))
TRANSLATED_OUTSIDE = {
    0x142FD53C0: "deferred-command data size from a header's count (142DFEDA0)",
    0x14311F170: "current stream-skip record (block, size) from 1527E22C8",
    0x143795BD0: "a load-mode flag (153642730)",
    0x1465F7110: "calls 1465F7490 (skipped GPU setup)",
    0x1465FBA40: "texture-format check wrapper around 1472161D0",
    0x146627410: "next deferred-command sequence number (157907158 + 1)",
    0x1466A38D0: "per-format value by texture type",
    0x1466A4340: "empty",
    0x1466A6210: "image flags check (+0x18)",
    0x1466A66B0: "image byte +0x32",
    0x1472161D0: "texture header magic check (0xD6000000 family)",
}

# Startup state the loaders depend on: DB init 1437591D0 calls 142DF1600, which points each block's offset tracker
# (14BCC4790 + 8 * block) at slot n of the tracker buffers (14BCC4860 + n * 0x6020) when the exe's table at
# 147B477C0 gives one (0x7FFFFFFF = none). In TU67 only block 5 has one, slot 0. The tracker records the alignment
# padding block 5 does not store (142DF1380) so offsets into it resolve (142DF0FE0); some zones need it.
SETUP_TRACKERS = 0x142DF1600
TRACKER_POINTERS, TRACKER_BUFFERS, TRACKER_SIZE = 0x14BCC4790, 0x14BCC4860, 0x6020
TRACKED_BLOCKS = {5: 0}       # block -> tracker slot (147B477C0)

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

# The CRT's table of C++ dynamic initializers (__xc_a..__xc_z; 7,012 entries). Many only store constants into
# globals (e.g. 140582BC0 sets the four-float vector 1.0 at 159B81B10, 140582BB0 the sign mask at 159B82100), which
# the game's math code reads; the emulator runs those (zone_emu.ZoneEmu.run_constant_initializers).
CRT_INITIALIZERS = (0x1475DB5E0, 7012)
