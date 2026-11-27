# Images (type 0x13)

Image headers are in the zones; their pixels are mostly streamed from `.xpak` packs (docs/assets/streaming.md).
Measured on `mp_t_gun_course` (5,134 images); read by `tools/assets/image.py` with `tools/assets/xpak.py`.
Status: header, streams and the main pixel formats decoded; **3,224 images whose packs are uploaded decode to the
expected textures** (colour, normal and mask maps checked by eye). Not yet: the 0x10-byte data at +0xD8, cube and
array images, and the formats not met yet.

## Header (0xE8 bytes; loader 142EAAFC0)

| Off | Size | Field | Evidence |
|---|---|---|---|
| +0x00 | ptr | name | XString (142E45CC0) |
| +0x14 | u32 | **format** (below) | measured |
| +0x18 | u32 | flags; **0x40 = streamed** | 142EAB290: with 0x40 the 8 bytes at +0xE0 are a stream key read in place, else +0xE0 points to `+0x1C` bytes of pixels |
| +0x1C | u32 | **byte size of all mips** | 142EAB290 (non-streamed); measured equal to the last stream's end |
| +0x24, +0x26 | u16 | **width, height** | measured: equal to the last stream's dimensions |
| +0x28 | u16 | depth (1) | measured |
| +0x2E | u8 | usage: 6 colour, 7 normal, 3 masks, 0 other, … | measured against name suffixes (`_c`, `_n`, …) |
| +0x30 | u16 | mip count | measured (8 for 64×128, 12 for 1024×2048) |
| +0x32 | u8 | **stream count** (up to 4) | 1445E07A0 loops over them |
| +0x38 + 0x28 × i | 0x28 | **streams**, smallest first | 1445E07A0 looks each key up in the pack index |
| +0xD8 | 0x10 | shared `{ptr, u32 size}` of 256–512 bytes | 142EAB0C0; *meaning unknown* (not the smallest stream) |
| +0xE0 | ptr | pixels of a non-streamed image (60 of 5,134) | 142EAB290 |

Stream (0x28 bytes): +0x00 u64 **key** into the packs; +0x20 u32 `level | (end / 16) << 8`, where `end` is the
byte size of this stream's mips plus all smaller streams'; +0x24 u16 width and +0x26 u16 height of the stream's
largest mip. A stream's item holds `end − previous end` bytes: its mips from the largest down. Measured on
`building_door_wood_worn_out_01_c`: ends 43,728 / 174,800 / 699,088 / 2,796,240 for 128×256 … 1024×2048, and the
first stream's item decodes with exactly 43,728 bytes as Oodle's output size (any other size fails).

## Formats (+0x14)

| Value | Format | Evidence |
|---|---|---|
| 7 | R8G8B8A8 | decoded (a 320×430 store image) |
| 35 | BC1 | decoded |
| 36 | BC1, used for colour maps (sRGB) | decoded; 1,751 of 2,230 are colour or "other" usage |
| 40 | 1 byte per pixel; BC3 sRGB by its place | *unverified* |
| 41 | BC4 | decoded: masks; BC1 gives noise |
| 44 | *unknown* | one image |
| 46 | BC7, normal maps | decoded: 481 of 491 have usage 7; BC5 gives noise |
| 47 | BC7, colour maps (sRGB) | decoded |

Bytes per pixel measured from the stream sizes: 0.5 for 35, 36, 41; 1.0 for 40, 46, 47; 4 for 7.
