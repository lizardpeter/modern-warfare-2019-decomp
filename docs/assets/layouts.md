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
not contain have no page yet. Traced so far: the patched `mp_t_gun_course` and the three character transient zones
(436 structs across 54 asset types). Re-run with more zones as the remaining archives arrive; types no zone
contains will be taken from their loader code.

Checked by hand against the code: `xanim` (docs/assets/animations.md) matches field for field, including which
counts are u8, u16 and u32.
