# Asset layouts

Every struct each asset type is made of, from the game's own loaders: `tools/assets/layouts.py` writes
`analysis/ModernWarfare_TU67/assets/layouts.tsv` and one page per asset type in
`analysis/ModernWarfare_TU67/assets/layouts/` (generated; regenerate after adding zones). These pages give the
**structure**: sizes, pointers and what they lead to, counts, strings, script strings, asset references. What the
plain data fields mean is decoded per type in `docs/assets/<type>.md`, from the code that uses them.

## How it is derived

The zone is loaded with the generated reader (docs/assets/loader-translation.md), which runs the game's loaders
exactly, while recording:

- **Every call to Load_Stream 143760AE0, by call site.** Every loader passes it the address and size of the data it
  fills, also when that data was already read as part of its parent (flag 1), so the calls list every struct
  instance. A call site whose size is a constant in the code reads a **struct** of that size; one whose size is
  computed reads an **array**, whose element size is the multiplier in the same expression (`count * 4` → 4). Sites
  are named `<loader>#<n>`, the n-th Load_Stream call in that loader's code (just `<loader>` when it has one).
- **Pointer fields, exactly.** The loaders set a pointer field to the stream position just before the child is read
  there (`field = pos; Load_Child(...)`): each read is linked to the struct field that last received its address,
  in the latest instance of a loader on the call stack containing it. That gives the field's offset, the call
  site of what it leads to, and the number of bytes.
- **Count fields.** For each pointer field, a header field (u8, u16 or u32) equal on every instance to the element
  count (bytes / element size). A count is only claimed if the counts vary between instances, since a constant
  could be matched by any field holding the same value; "a single element" means every instance had exactly one.
- **Script-string fields**: the fields passed to Load_ScriptString 143760D10.
- From the loaded memory: **asset references** (a field holding another asset's header address), **strings**
  (pointing at text), and **shared** pointers: fields pointing at data loaded earlier rather than read for them.
  The game stores identical data once and points to it (`mp_t_gun_course`'s `little_bird_mp` weapon has 20 such
  fields from +0x38 to +0x130 pointing at one shared definition).

Instances read into the temporary block (asset headers) are taken from the copy DB_AddXAsset made in the pool,
since the block is reused by the next asset. Asset types are attributed from asset_types.tsv: an asset's header is
its struct loader's constant-size site of the header's size; the structs below it are named
`<type>+<offset>` after the first field seen pointing to them. Arrays are named by element (`u16[]`); they are
shared by many types.

## Coverage

Only what the traced zones contain is listed: a field never non-zero in them is not shown, and asset types they do
not contain have no page yet. Traced so far: every zone stored entirely in the archives uploaded so far (data.000–.033,
.035–.037 and .045–.049) with its patch where it has one: 13,653 of 14,811 load (the rest below), mostly transient zones
(character bodies and heads, weapon and attachment models, vehicles, co-op and map pieces, techsets). Result: 480
structs across 61 asset types. Weapons, most map assets and the shared assets are in `common_mp` and the base map
zones, whose patches are in archives not uploaded yet (data.030–.044, .050 on, e.g. `common_mp.fp` in data.066); types
no zone contains will be taken from their loader code.

Not loaded (the game's own loaders fail on them too, so it is not the translation):

- 1,148 transient zones with models (598 `mp_ay`, 161 `mp_aw`, 143 `mp_az`, 127 `mp_bd`, 62 `mp_av`, 34 `mp_wv`, …;
  e.g. `mp_bd_body_mp_western_kyle_4_1_lod0_l15_tr`) whose **surfaces are 0xC0 bytes, not the 0xD0 both exes read**
  (142EA58B0 reads `count × 0xD0`; TU63's copy at 142925E90 is the same code, and so are the surface and subdivision
  loaders, 1429262D0 / 1429267B0 / 142926860). Measured on the kyle body: its 25 surfaces start every 0xC0 bytes
  (each starts `flags 0x43, vertex count, triangle count`; the next one begins at +0xC0 of the previous), and fields
  sit 4 bytes earlier than in the 0xD0 form — the influence-group counts at +0x10 (44 + 173 + 333 + 1,264 = 1,814 =
  the vertex count), the influence byte size at +0x20 (Σ k × count_k × 4 = 25,780) — so read as 0xD0 the stream
  goes wrong at the second surface. The zone header is the same version (0xFCD) and kind as zones that load. So
  these are zones in a surface format neither exe loads: an older build's, left in the install (the game would not
  load them either). Reading them needs the 0xC0 layout worked out in full (*not done*).
- 4 `dummy_*` zones with no signed unit after the header.

Checked by hand against the code: `xanim` (docs/assets/animations.md) matches field for field, including which
counts are u8, u16 and u32.

**Startup state found on the way.** Block 5 has an offset tracker the game sets up at start (DB init 1437591D0 →
142DF1600, from the exe's per-block table at 147B477C0: only block 5, slot 0). It records the alignment padding block
5 does not store, so offsets into it resolve (142DF0FE0). The emulator and the translated loaders both lacked it, and
matched each other byte for byte anyway; they now both set it (the emulator by running 142DF1600 itself). Every
checked zone still passes.
