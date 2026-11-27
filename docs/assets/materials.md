# Materials (type 0x0B)

Measured on `techsets_mp_cave` (2,144 materials, 2,132 with textures); read by `tools/assets/material.py`.
Status: texture table and slot meanings (from image names) decoded; constants located, their ids not yet named;
techsets and shaders not started.

**Where the full materials are.** In map zones (`mp_t_gun_course`) every one of the 1,654 materials is a reference
(name starting with `,`, the rest of the header zero). The full materials of a map are in its `techsets_<map>` zone,
whose images are in turn references by name (`,name`, usage 0, no streams): the image headers with their stream keys
are in the map zone. So a material's texture is found by **name**: material → slot → image name → the image header
of that name → its streams (docs/assets/images.md). `techsets_mp_t_gun_course` is in archive data.065, not uploaded
yet.

## Header (0x78 bytes; loader 142E84320)

| Off | Size | Field | Source |
|---|---|---|---|
| +0x00 | ptr | name | XString |
| +0x1C | u8 | **texture count** | 142E84320 (count of +0x48) |
| +0x1D | u8 | **constant count** | measured: +0x50 holds this many 0x14-byte entries |
| +0x40 | asset | techset | layouts |
| +0x48 | ptr | **textures**, 0x10 each: u8 slot at +0x00, image at +0x08 | layouts; measured |
| +0x50 | ptr | **constants**, 0x14 each: u32 id, 4 × f32 | layouts (0x14 elements); measured: 53 distinct ids |
| +0x58 | asset | decalvolumematerial | layouts |

## Texture slots (measured from the names of the images in each slot)

| Slot | Meaning | Names seen (count) |
|---|---|---|
| 0x00–0x04 | colour, layers 0–4 | `_c` (1,804 in layer 0) |
| 0x09–0x0D | normal, layers 0–4 | `_n` (2,035), `identitynormal` |
| 0x12–0x14 | emissive | `_e` |
| 0x1B–0x1F | a per-layer map whose default is white | `white` (974 in layer 1), `_c`, `$white`, `_sdf` |
| 0x2D | thermal | `thermalmap` |
| 0x3B–0x3F | a per-layer map whose default is black | `$black` (2,037 in layer 0) |
| 0x5F–0x63 | displacement / height, layers 0–4 | `_d`, `_h` |
| 0x7E, 0x80 | `_m`, `_r`, `sheen` | *unverified* |

Image names combine channels: `x_c&x_s~<hash>` is one texture made from a colour map and another map (`&`), with a
hash suffix (`~`).
