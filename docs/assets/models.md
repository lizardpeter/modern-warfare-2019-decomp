# Models (xmodel, type 9) and their surfaces (xmodelsurfs, type 0x0C)

Characters are xmodels: bodies, heads, arms and gear come from the transient zones (`mp_bd_*`, `mp_hd_*`, `mp_vh_*`),
which load as they are (docs/assets/layouts.md). Structure (sizes, pointers, counts) is in the generated layout pages
`analysis/ModernWarfare_TU67/assets/layouts/xmodel.md` and `xmodelsurfs.md`; this page decodes what the fields
mean. Every rule names the function it comes from or says "measured on <zone>"; the rest is *unverified*.

Status: surfaces' vertex counts, the position stream and its scale are decoded (measured); the other vertex streams,
the index format, skin weights and the model's LOD and bone fields are next.

## How rendering uses them

TU67 uploads mesh data into one **unified vertex buffer** ("Unified Vertex Physical Buffer", "Unified Vertex Page
Table", "Unif Vert Buffer": decrypted strings, tools/strings_encrypted.py) and its shaders read the raw streams at
the surfaces' offsets, so the CPU code mostly never unpacks vertices; formats are decoded from the data and from the
few CPU users (below). Surfaces can also carry **subdivision-surface** data (OpenSubdiv-style patches).

## xmodelsurfs (0x60 bytes)

| Off | Field | Source |
|---|---|---|
| +0x00 | name | XString (layouts) |
| +0x08 | surfaces: `count` × 0xD0 | 142EA58B0: read `u16 +0x38 × 0xD0`, then 142EA5CF0 per surface |
| +0x30 | shared data: 0x10 bytes `{u64 data, u32 size, u32 flags}` | 142EA58B0 → 142EA60F0: reads `size` bytes at `data`; when `flags & 1` the data is streamed instead and 142EB0430 reads an 8-byte stream key |
| +0x38 | u16 surface count | 142EA58B0 |
| +0x48 | f32 1.53125 on the body measured, also in each LOD entry of the xmodel (+0x104, +0x144, …) and the surface (+0x8C) | measured; *unknown* |

The shared data is one blob holding every vertex stream of every surface of the LOD (0xF2390 bytes for the body
measured); each surface points into it with offsets.

## Surface (0xD0 bytes)

Measured on `body_mp_western_t9esports_1_12_1_lod1_pc` (`mp_bd_body_mp_western_t9esports_1_10_1_lod1_l15_tr`, 6 surfaces):

| Off | Size | Field | Evidence |
|---|---|---|---|
| +0x00 | u16 | flags (0x43 on every surface measured) | *meaning unknown* |
| +0x02 | u16 | **vertex count** (21,953 for surface 0) | equals the sum of +0x14..+0x1A, and every per-vertex stream's size divided by it is a whole number |
| +0x04 | u32 | **triangle count** (34,454) | *unverified* until the index stream is decoded |
| +0x10 | u32 | hash-like value | *unknown* |
| +0x14 | 4 × u16 | vertex counts by bone-influence count (6,935 + 7,144 + 4,073 + 3,801 = 21,953) | sum measured on every surface; which count is which is *unverified* |
| +0x24..+0x50 | u32 each | offsets into the shared data, 0xFFFFFFFF = absent | measured |
| +0x28 | u32 | **positions**: 8 bytes per vertex (below) | measured |
| +0x2C, +0x30, +0x34, +0x40 | u32 | streams of 4 bytes per vertex (gaps between offsets are exactly 4 × vertex count) | *which is which: unknown* (normal/tangent frame, UV, colour, second UV are the usual set) |
| +0x24 | u32 | a stream of 218,864 bytes for 21,953 vertices: not a whole number of bytes per vertex, so variable-size (skin weights or indices) | *unknown* |
| +0x58 | ptr | 0x10-byte struct with a byte array | layouts |
| +0x60, +0x68, +0x70 | ptr | arrays: u32 (count at +0x02 as u16), u64 (count at +0x08), bytes (count at +0x24) | layouts |
| +0x78 | ptr | subdivision info (0x80 bytes, 142EA61D0) → levels of 0x238 bytes (142EA6280) | below |
| +0x8C | f32 | 1.53125 (as xmodelsurfs +0x48) | *unknown* |
| +0xA0 | 3 × f32 | position offset (0, 0, 0 on the body) | *unverified*, by its place before the scale |
| +0xAC | 3 × f32 | **position scale** per axis (95.6441 × 3 on the body; the xmodel header repeats it at +0x38..+0x40) | measured |
| +0xB8 | ptr | array of 0x18-byte entries, count at +0x08 | layouts |
| +0xC0 | ptr | 0x20-byte struct | layouts |

### Positions

Each vertex is a u64 with 21 bits per axis: x = bits 0–20, y = bits 21–41, z = bits 42–62 (bit 63 clear on every
vertex measured), each biased by 2^20: `position = (packed − 2^20) / 2^20 × scale + offset`.

Measured on surface 0 of the body: the vertical axis starts exactly at 2^20 − 1 (the feet) and reaches 63.6 units;
x spans −6.9 to +16.5 and y ±20.5; consecutive vertices are close together (median step 0.4% of the range). The
same 21-bit unpacking, `(float)(int)field × scale + offset`, is in the CPU function 14718C480 (fields of its struct:
offset at +0x10, scale at +0x20, positions at +0x78, u16 indices at +0x80); which struct that is, is *unverified*.

## Subdivision surfaces

+0x78 of a surface leads to a 0x80-byte struct whose +0x00 points to subdivision levels of 0x238 bytes. The renderer
(1465F7490, skipped when loading) builds one GPU buffer per array of a level and names them (decrypted):
`regularPatchIndices`, `regularPatchFlags`, `regularPatchCones`, `faceIndices`, `facePoints`, `edgePoints`,
`vertexPoints`, `normals`, `transitionPoints` (each with a `…View`). Sizes it uses: the level's u32 at +0x0C × 32 for
the buffer at +0x58 (+0x98 view), (+0x0C + 3) & ~3 × 4 for +0x60, +0x1C rounded to 16 for +0x68, (+0x20 + 1) & ~1 × 8
for +0x70, +0x34 rounded to 16 for +0x78, +0x3C rounded to 16 for +0x80; +0x08 × 12 bytes at +0x50.
