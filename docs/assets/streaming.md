# Streamed data (`.xpak`)

Model surfaces, image mips and other large data are not in the zones but in `.xpak` files. Measured on the install's
CASC data; the reading code is in 1445D9xxx (the header check below). Status: the **container** (header, index) and the **chunk format** are decoded (`tools/assets/xpak.py`). Images
store their keys in their header and decode (docs/assets/images.md); how a streamed model surface finds its key is
not yet known.

## How much is streamed

`mp_t_gun_course`: 1,579 of its 1,985 model surface sets have the "streamed" flag (bit 0 of the u32 at +0x0C of the
xmodelsurfs shared-data struct, docs/assets/models.md); their data pointer field holds 0 in the loaded zone (the
loader 142EB0430 / 142E46380 reads those 8 bytes in place, as a stream key). So the key is not stored in the asset
itself; the zone's `streaminginfo` asset (+0x30 count, +0x38 list of pointers to the streamed shared-data structs;
+0x08 / +0x18 the same for images) lists what is streamed, and the key is filled in at run time (*how is not yet
known*).

## Files

4,910 `.xpak` files; most are 32 KiB placeholders (per-zone and per-language names such as `mp_t_gun_course.xpak`).
The data is in about 100 large packs: `pak_base_volNNN` and `pak_magma1_volNNN` (1.08 GB each), `pak_launch*`,
`pak_mp` (2.9 GB), `pak_coremp`, `pak_compatmpcp` (16.6 GB), language variants. Each is stored in CASC as parts of
about 996 MB, often in different archives.

## Header (first 0x1000 bytes; checked by the function at 1445D9A00)

| Off | Field | Evidence |
|---|---|---|
| +0x00 | `IPAK` (u32 0x4950414B) | else DEV ERROR 0x157D (1445D9A00) |
| +0x06 | u16 version 0xD | checked by the same function |
| +0x08 | u64 1 | measured |
| +0x10 | u64 file size | measured (0x40650000 for `pak_base_vol006`) |
| +0x138 | u64 entry count | measured; read by 1445D9A00 (+0x138..+0x160 are copied into its pack table) |
| +0x140 | u64 data offset (0x8000) | measured |
| +0x148 | u64 data size | measured: data offset + size ends at or before the index |
| +0x150 | u64 entry count again; 0 marks an empty pack | 1445D9A00 skips packs with 0 here |
| +0x158 | u64 **index offset** | measured |
| +0x160 | u64 **index size** | measured: index size / 24 = entries (one less than +0x138 in some language packs) |

## Index (24 bytes per entry, sorted by key)

`{u64 key, u64 offset, u64 size | 0x8000000000000000}`, e.g. in `pak_escape4`: key 0x152A4A96E773B at 0x34EC6500,
size 0x5280. The 17 packs whose index is in the uploaded archives hold 28,659 keys. Of the keys stored in `mp_t_gun_course`,
all are image stream keys (3,377 found: 3,224 at image +0x38, the rest at +0x60/+0x88/+0xB0); no model surface
key is stored anywhere in that zone's memory, and xmodelsurfs +0x10 (a 64-bit hash) is not one either.

## Items (DecompressSingleBlock, 143C97CE0)

An entry's offset is relative to the data offset (+0x140). An item is a series of 0x80-byte-aligned **chunk headers**,
each followed by its chunks:

| Off | Field |
|---|---|
| +0x00 | u32 chunk count, at most 30 (0x1E) |
| +0x04 | u32 output offset of the first chunk |
| +0x08 + 4 × i | chunk i: compressed size (low 24 bits), type (high byte) |

The chunks follow the header at +0x80, each 4-byte aligned. Each decodes to `min(remaining output, 0x3FFE0)` bytes:
type 0 is stored, 4 and 5 are LZ4 (147248D50), 6 and 7 Oodle (`OodleLZ_Decompress`, the data starting `8C 06`, i.e.
Kraken), 0xCF is skipped. The output size is not in the pack: the caller knows it (for a streamed model surface set,
the size field of its shared-data struct). Measured on `pak_escape4`: item 0xF72EB0126C649 is one Oodle chunk of
3,249 bytes that decodes to 5,360, starting with u16 triangle indices 0, 1, 2, … — a model surface blob like the
in-zone ones (docs/assets/models.md).

## Next

1. Find where the run-time key comes from (the code that consumes `streaminginfo` +0x38 / the shared-data struct of
   a streamed surface). It is not FNV-1a of the asset name (tested on `mp_escape4_00002_tr`).
2. Most packs a map needs (`pak_mp`, the `pak_base_vol*` second parts) have their index in archives not uploaded yet
   (data.030–.044, .050 on).
