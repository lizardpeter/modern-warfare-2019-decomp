# Models (xmodel, type 9) and their surfaces (xmodelsurfs, type 0x0C)

Characters are xmodels: bodies, heads, arms and gear come from the transient zones (`mp_bd_*`, `mp_hd_*`, `mp_vh_*`),
which load as they are (docs/assets/layouts.md). Structure (sizes, pointers, counts) is in the generated layout pages
`analysis/ModernWarfare_TU67/assets/layouts/xmodel.md` and `xmodelsurfs.md`; this page decodes what the fields
mean. Every rule names the function it comes from or says "measured on <zone>"; the rest is *unverified*.

Status (measured): vertex and triangle counts, positions and their scale, triangle indices, UVs, vertex colours,
the tangent frame (normal, tangent, bitangent sign), skin weights (blended and rigid) and the skeleton. The reader is
`tools/assets/xmodel.py` (meshes, skeletons, OBJ export); it decodes all 2,512 surfaces of 257 zones sampled
(characters, heads, view hands, attachments, map props) with every vertex's weights summing to 1 and every index in
range. Still open: +0x2C (a second direction, below), +0x3C, and the meaning of several header fields.

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
| +0x00 | u16 | flags: 0x43 on the body's surfaces, 0x02 / 0x12 / 0x00 on head surfaces | *meaning unknown* |
| +0x02 | u16 | **vertex count** (21,953 for surface 0) | equals the blended plus rigid vertices; every per-vertex stream's size divided by it is a whole number |
| +0x04 | u16 | **triangle count** (34,454) | measured: indices of exactly this many triangles cover every vertex |
| +0x06 | u16 | 0 on the body, 617 on one head surface | *unknown* |
| +0x08 | u16 | **rigid vertex list count** (the +0x68 and +0xB8 arrays) | layouts; below |
| +0x10 | u32 | hash-like value | *unknown* |
| +0x14 | 8 × u16 | **blended vertex counts by influence count**, 1 to 8 bones (body surface 0: 6,935 + 7,144 + 4,073 + 3,801; a head surface uses 6 groups) | measured: the +0x70 size is Σ (k × count_k) × 4 on every surface |
| +0x24 | u32 | **byte size of the +0x70 influence array** (194,584 on surface 0) | layouts (count field of +0x70); measured |
| +0x28..+0x50 | u32 each | offsets into the shared data, 0xFFFFFFFF = absent | measured |
| +0x28 | u32 | **positions**: 8 bytes per vertex (below) | measured |
| +0x2C | u32 | 4 bytes per vertex: a second direction (octahedral, 9 + 9 bits) and two 7-bit values | measured, below; *meaning unverified* |
| +0x30 | u32 | **UVs**: 2 × half-float per vertex, all within 0–1 on surface 0 | measured |
| +0x34 | u32 | **tangent frame**: one quaternion per vertex | measured, below |
| +0x38 | u32 | **triangle indices**: u16, 3 per triangle, clockwise front faces. The region reserves 12 bytes per triangle on the body; the second half is all zero there | measured: the largest index is vertex count − 1; geometric normals from clockwise winding agree with the decoded normals (median dot 0.997) |
| +0x3C | u32 | a stream that is not per vertex: 12,944 bytes on body surface 0, 56–312 on the small ones; 24-byte records whose last 12 bytes are often `0xE0080200, 0, 0xFF7FFFFF` | *unknown* (per-cluster data?) |
| +0x40 | u32 | **vertex colour**: RGBA8 per vertex (255, 255, 255 and alpha varying on surface 0) | measured |
| +0x44..+0x50 | u32 | further stream offsets, absent (0xFFFFFFFF) on every surface measured | |
| +0x58 | ptr | 0x10-byte struct with a byte array | layouts |
| +0x58 | ptr | 0x10 bytes: the shared-data descriptor again (`{data, size}`) | measured |
| +0x60 | ptr | u32 per vertex (count +0x02) | layouts; absent on the surfaces measured |
| +0x68 | ptr | **rigid vertex lists**, 8 bytes each (count +0x08) | below |
| +0x70 | ptr | **blended influences** (byte size +0x24) | below |
| +0x78 | ptr | subdivision info (0x80 bytes, 142EA61D0) → levels of 0x238 bytes (142EA6280) | below |
| +0x8C | f32 | 1.53125 (as xmodelsurfs +0x48) | *unknown* |
| +0xA0 | 3 × f32 | position offset (0, 0, 0 on the body) | *unverified*, by its place before the scale |
| +0xAC | 3 × f32 | **position scale** per axis (95.6441 × 3 on the body; the xmodel header repeats it at +0x38..+0x40) | measured |
| +0xB8 | ptr | one 0x18-byte entry per rigid list (count +0x08): 6 × f32, a box (centre, half size?) | layouts; *meaning unverified* |
| +0xC0 | ptr | 0x20-byte struct | layouts |

### Positions

**Checked visually**: unpacking every surface of `body_mp_western_t9esports_1_12_1_lod1_pc` with these rules
(positions at +0x28 with the scale at +0xAC and offset at +0xA0, triangles from +0x38) and rendering the result gives
the character's body (hooded top, gloves, knee pads, holster, boots; the head is a separate model): 22,854 vertices,
35,840 triangles, extent −7.0…16.5 × −20.6…20.5 × 0…63.6.

Each vertex is a u64 with 21 bits per axis: x = bits 0–20, y = bits 21–41, z = bits 42–62 (bit 63 clear on every
vertex measured), each biased by 2^20: `position = (packed − 2^20) / 2^20 × scale + offset`.

Measured on surface 0 of the body: the vertical axis starts exactly at 2^20 − 1 (the feet) and reaches 63.6 units;
x spans −6.9 to +16.5 and y ±20.5; consecutive vertices are close together (median step 0.4% of the range). The
same 21-bit unpacking, `(float)(int)field × scale + offset`, is in the CPU function 14718C480 (fields of its struct:
offset at +0x10, scale at +0x20, positions at +0x78, u16 indices at +0x80); which struct that is, is *unverified*.

### Tangent frame (+0x34)

Measured on every surface of the body and 2,512 surfaces in all: a 32-bit "smallest three" quaternion.

- bits 30–31: which of x, y, z, w was dropped (it is the largest and is rebuilt as √(1 − a² − b² − c²));
- bits 0–9 and 10–19: the first two stored components, `(v / 511.5 − 1) / √2`;
- bits 20–28: the third, 9 bits, `(v / 255.5 − 1) / √2`;
- bit 29: the **bitangent sign**.

The stored components fill the remaining slots in x, y, z, w order. Of the rotation the quaternion describes, the
**Z axis is the normal** (median |dot| with the geometric normal 0.997 on body surface 0) and the **X axis the
tangent** (median dot 0.976 with dP/du from the UVs); `bitangent = cross(normal, tangent)`, negated when bit 29 is
set (bit 29 = 0 agrees with dP/dv on 99.3% of triangles, bit 29 = 1 disagrees on 99.4%). Reading bits 20–29 as a
10-bit component instead gives component sums above the 0.75 a smallest-three encoding allows (0.861), which is how
bit 29 was found.

### The second direction (+0x2C)

Bits 0–8 and 9–17 are an octahedral direction (`x = v / 511 × 2 − 1`, the usual wrap for the lower hemisphere);
bits 18–24 and 25–31 are two 7-bit values. The direction is close to the normal (median dot 0.87 on body surface 0,
0.96–0.998 on small surfaces) but not equal to it, and it departs from the normal exactly where the two 7-bit values
say so: where bits 18–24 are 112–127 (body surface 0, 7,283 vertices) the median dot is 0.965, falling steadily to
0.31 at 16–31; where bits 25–31 are 0–15 it is 0.973, falling to 0.19 at 112–127. It is not the normal averaged over
split vertices (checked). A bent normal with an occlusion amount and a cone width (baked ambient occlusion) fits
these measurements, but that reading is *unverified* until a shader or the CPU code that reads it is found.

### Skinning

Vertices are stored blended first, grouped by influence count, then rigid.

**Blended** (+0x70, byte size +0x24, counts at +0x14): for each group k = 1..8 with `count_k` vertices, first
`count_k` u32 holding each vertex's first bone (low 16 bits; the high 16 are 0), then for each further influence
j = 2..k another `count_k` u32 `{u16 bone, u16 weight}` (structure of arrays: all vertices' second bone, then all
third bones, …). Weights are `/ 65536`; the first bone's weight is `1 − Σ others`. Measured on the body: the stored
weights descend within every vertex (array-of-structures order does not: 51% / 20% for 3 and 4 bones), the largest
two-bone sum is exactly 32768 (½), neighbouring vertices share their first bone 93% of the time (5% for random
pairs), and vertices lie a median 5.3 units from their dominant bone's bind position against 29.7 for a random bone.

**Rigid** (+0x68, count +0x08): 8-byte lists `{u16 bone, u16 vertex count, u16 first triangle, u16 triangle count}`;
the lists' vertices follow each other with weight 1. Measured on head surfaces: a surface with no blended vertices
has lists `(29, 145, 0, 276)`, `(28, 145, 276, 276)`, covering its 290 vertices and 552 triangles. Surfaces with both
kinds were not found in the zones sampled, so their order (blended before rigid) is *unverified*.

## xmodel (0x2B0 bytes; loader 142EA4830)

| Off | Size | Field | Source |
|---|---|---|---|
| +0x08 | u16 | **surface count over all LODs** (42 = 6 × 7 on the body): size of +0xD8 and +0x268 | 142EA4830 (count of both arrays) |
| +0x0A | u8 | LOD count (6 on the body) | measured; *unverified* |
| +0x11 | u8 | count of the u32 array at +0x90 | 142EA4830 |
| +0x14 | u8 | bones with part classification (98 on the body) | 142EA4830: size of +0xB8 |
| +0x15 | u8 | **root bone count** (1) | 142EA4830 |
| +0x16 | u16 | further bones (77); **bone count = +0x14 + +0x16** (175) | 142EA4830 |
| +0x18 | u8 | count of +0x288 | 142EA4830 |
| +0x28 | f32 | 63.76 on the body: radius? | *unverified* |
| +0x38 | 3 × f32 | position scale, as the surfaces' +0xAC | measured |
| +0x98 | ptr | **bone names**: u32 script-string index per bone | 142EA4830 (142E46280, count = bones); measured: `tag_origin`, `tag_sync`, `j_mainroot`, `j_spinelower`, … |
| +0xA0 | ptr | **parents**: u8 per non-root bone, how far back the parent is (`parent = index − value`) | 142EA4830 (count bones − roots); measured |
| +0xA8 | ptr | **local rotations**: 4 × s16 per non-root bone, quaternion x, y, z, w `/ 32767` | count (bones − roots) × 4; measured |
| +0xB0 | ptr | **local translations**: 3 × f32 per non-root bone, in the parent's space | count (bones − roots) × 3; measured |
| +0xB8 | ptr | u8 per classified bone (+0x14): part classification | 142EA4830; *meaning of values unverified* |
| +0xC0 | ptr | **bind pose**: 0x20 bytes per bone, world quaternion (4 × f32), world translation (3 × f32), f32 2.0 | 142EA4830 (element 0x20, count = bones); measured: composing the local values down the hierarchy reproduces every bone's world rotation and translation exactly (175 bones) |
| +0xD8 | ptr | u64 per surface (+0x08): material references | 142EA4830; *unverified* that they are materials |
| +0xE0 + 0x40 × lod | 0x40 | **LOD entries** (6) | layouts: an xmodelsurfs asset at +0x00 and its surfaces at +0x08 |
| +0x260 | ptr | 0x1C bytes per bone | 142EA4830; *unknown* |
| +0x268 | ptr | u32 per surface | 142EA4830; *unknown* |
| +0x270, +0x280 | asset | physicsasset, xmodeldetailcollision | layouts |

LOD entry (0x40), measured on the body: +0x00 xmodelsurfs, +0x08 its surfaces, +0x10 f32 **LOD distance**
(96.8, 185.4, 267.1, …), +0x14 u16 7 and +0x16 u16 0 / 7 / 14 (surfaces per LOD and the first surface's index into
+0xD8, *unverified*), +0x24 f32 1.53125.

## Subdivision surfaces

+0x78 of a surface leads to a 0x80-byte struct whose +0x00 points to subdivision levels of 0x238 bytes. The renderer
(1465F7490, skipped when loading) builds one GPU buffer per array of a level and names them (decrypted):
`regularPatchIndices`, `regularPatchFlags`, `regularPatchCones`, `faceIndices`, `facePoints`, `edgePoints`,
`vertexPoints`, `normals`, `transitionPoints` (each with a `…View`). Sizes it uses: the level's u32 at +0x0C × 32 for
the buffer at +0x58 (+0x98 view), (+0x0C + 3) & ~3 × 4 for +0x60, +0x1C rounded to 16 for +0x68, (+0x20 + 1) & ~1 × 8
for +0x70, +0x34 rounded to 16 for +0x78, +0x3C rounded to 16 for +0x80; +0x08 × 12 bytes at +0x50.
