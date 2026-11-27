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
not contain have no page yet. Traced so far: the patched `mp_t_gun_course` and every zone of the five archives on
hand (data.000, .006, .016, .017, .047) that loads as it is: 3,108 of 3,128, mostly transient zones (character
bodies and heads, weapon and attachment models, vehicles, co-op). Result: 451 structs across 55 asset types. Re-run
with more zones as the remaining archives arrive; types no zone contains will be taken from their loader code.

Not loaded (the game's own loaders fail on them too, so it is not the translation):

- 16 transient zones whose loading runs past the end of their data: nine Cold War (`t9`) weapon attachments and
  seven character bodies (e.g. `mp_aw_att_wm_ar_t9fasthandling_receiver_lod1_s2_l23_tr`,
  `mp_bd_body_mp_western_kyle_4_1_lod0_l15_tr`). Same header version and kind as zones that load; no patch file.
  Inside the first xmodelsurfs the loader converts index-buffer data as an offset. *Unknown*; the leading guess is
  zones built for 1.63 whose surface struct changed by 1.67 (the target exe), to be tested with the TU63 exe.
- 3 dedicated-server zones (`srv_cp_*`) compressed with codec 5, which tools/assets/zone.py does not decode yet.

Checked by hand against the code: `xanim` (docs/assets/animations.md) matches field for field, including which
counts are u8, u16 and u32.

**Startup state found on the way.** Block 5 has an offset tracker the game sets up at start (DB init 1437591D0 →
142DF1600, from the exe's per-block table at 147B477C0: only block 5, slot 0). It records the alignment padding block
5 does not store, so offsets into it resolve (142DF0FE0). The emulator and the translated loaders both lacked it, and
matched each other byte for byte anyway; they now both set it (the emulator by running 142DF1600 itself). Every
checked zone still passes.
