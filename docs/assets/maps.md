# Maps: world geometry and placed models (gfx_map, gfx_map_trzone)

How a map's drawn world is stored, measured on `mp_t_gun_course` (patched; the one complete map whose patch is in
the archives uploaded so far) and read by `tools/assets/gfx_map.py`. Structure (sizes, pointers, counts) is in the
generated pages `analysis/ModernWarfare_TU67/assets/layouts/gfx_map.md` and `gfx_map_trzone.md`; this page says what
the fields mean. Every rule names the function it comes from or says "measured"; the rest is *unverified*.

Status: world surfaces (positions, triangles, tangent frames, lightmap UVs, colours, texture UVs per layer,
materials) and placed models (model, origin, rotation, scale) are decoded and checked against the geometry. Not yet:
lighting, collision (col_map), entities (map_ents), the per-area transient zones' own surface lists (they need their
map's base zone, whose patch is not uploaded), and models whose surfaces are streamed (`.xpak`): **1,579 of the
1,985 model surface sets in `mp_t_gun_course` are streamed**, so the streamed data is needed before a map is
complete.

## Vertex and index buffers (gfx_map_trzone +0x10, 0xC8 bytes; loader 142EAB6F0)

| Off | Field | Source |
|---|---|---|
| +0x00 | u32 size of the position data | 142EAB6F0 (byte count of +0x08) |
| +0x04 | u32 size of the attribute data | 142EAB6F0 |
| +0x08 | **position data** ("world posData") | 142EAB6F0 creates a GPU buffer named so |
| +0x10 | **attribute data** ("world auxData") | as above |
| +0x18, +0x58 | GPU buffer descriptions of the two | 142E43E00 |
| +0x98 | u32 index count | 142EAB6F0 |
| +0xA0 | **u16 indices** ("bsp index buffer") | 142EAB6F0 |

In `mp_t_gun_course`: 1,786,804 bytes of positions (4 bytes of zeros, then 148,900 × 3 × f32), 5,500,844 bytes of
attributes and 325,533 indices; every vertex and index is used by exactly the surfaces below.

## Surfaces (gfx_map +0x100, 0x28 bytes each, count u32 +0xC8)

| Off | Size | Field | Evidence (measured) |
|---|---|---|---|
| +0x00 | u32 | byte offset of the group's first position in the position data | equals the group's +0x08; consecutive groups differ by 12 × vertex count |
| +0x04 | f32 | *unknown* (219.7, 326.0, …; a size?) | |
| +0x08 | u16 | the group's vertex count | every index of the surface is below it |
| +0x0A | u16 | **triangle count** | |
| +0x0C | u32 | **first index** | each surface starts where the previous one ends (0, 36, 264, …) |
| +0x10 | ptr | **material** | names such as `,tw/metal_painted_corrugated_gray` |
| +0x18 | u32 | **vertex group** (index into +0x148) | |
| +0x20 | u32 | flags (0x41, 0x45, 0x47, 0x07) | *meaning unknown* |

+0x110 holds one 0x18-byte box per surface (3 × f32 mins, 3 × f32 size). Indices are relative to the group's first
vertex; triangles are clockwise. All 1,312 surfaces of `mp_t_gun_course` resolve (108,511 triangles), and a top view
of the result shows the training course with its terrain.

## Vertex groups (gfx_map +0x148, 0x58 bytes each, count u32 +0xCC)

| Off | Field | Per vertex | Evidence (measured) |
|---|---|---|---|
| +0x04 | u32 layer count L (1–5) | | decides how many UV sets and blend streams follow |
| +0x08 | offset of the positions in the position data | 3 × f32 | |
| +0x0C | **tangent frame** in the attribute data | u32 | the same quaternion encoding as model surfaces (docs/assets/models.md): its Z axis agrees with the geometric normal (median dot 1.0, 96% above 0.9) and its X axis with dP/du (median 0.95) |
| +0x10 | **lightmap UV** | 2 × f32 | values in 0–1; all zero on unlit groups |
| +0x14 | **colour** (0 = none) | RGBA8 | |
| +0x18 | **texture UVs**, one per layer, interleaved per vertex (`v0 L0, v0 L1, …, v1 L0, …`) | L × 2 × f32 | sizes 8, 16, 24, 32 × vertices for L = 1–4; read layer-major instead, neighbouring vertices' UVs are 24× further apart |
| +0x1C, +0x20, +0x24, +0x28 | one stream per layer after the first | 4 bytes | present exactly for layers 2..L; values like `ff807fff`: per-layer blend, *unverified* |
| +0x38..+0x44 | rarer 4-byte streams (25, 3, 8, 6 groups) | 4 bytes | *unknown* |

## Placed models (gfx_map +0x190; loader 142EA37B0)

| Off | Field | Source |
|---|---|---|
| +0x190 | u32 smodel-surface count (2,083) | 142EA37B0: count of +0x298 (0x20 each, "smodelSurfData") |
| +0x194 | u32 **model count** (512) | count of +0x1D0 and +0x418 (0x40 each) |
| +0x198 | u32 **instance count** (9,778) | count of +0x1E0, +0x1F8, +0x2E0 and others |
| +0x1D0 | per model, 0x10 bytes: **xmodel**, u16 flags, u16 first smodel surface | 142EA37B0; measured: every pointer is an xmodel, the u16 rises to 2,080 |
| +0x1E0 | per run ("collections"), 0x10 bytes: u32 **first instance**, u32 count, u32 **model index**, u32 flags | 142EA37B0 names the buffer; measured: counts sum to 9,778, every model index below 512 |
| +0x1F8 | per run, 0x18 bytes: world box centre and half size | measured: 99.6% of instance origins lie within their run's box |
| +0x2E0 | per instance, 0x18 bytes: **origin** 3 × s32 / 4096; **rotation** 4 × u16, `(v − 0x8000) / 32767`, x, y, z, w; **scale** f32 | measured: the rotations have unit length (1.0000–1.0001); scales 0.15–7.0 (73% 1.0); transforming a model's own vertices by them reproduces the run's box exactly (243 instances whose model surfaces are in the zone, centre error 0) |
