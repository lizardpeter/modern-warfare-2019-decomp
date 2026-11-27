# Translating the zone loaders

Why: a zone has no index (docs/assets/zones.md 8), so a reader that works from the original files alone has to
load every asset type that can come before the one it wants. TU67 has 2,807 generated loader functions in
142DF0000–142EC0000; with no symbols, porting them by hand is not practical. They are machine-generated and regular,
so they are translated mechanically from Ghidra's decompiled C, and the result is checked byte for byte against
the game's own code running in the emulator (tests/assets/zone_emu.py). The Forge importer is generated from the
same translation: Forge reads only the original game files.

## What is in scope (measured on the published pseudocode)

- **858 functions** in that range are reachable from Load_XAssetList 1437608F0 through direct calls. Every one
  parses as C with pycparser after Ghidra's type names are declared.
- They contain 212 `goto`s, 670 loops and 12 `switch`es; partial-variable accesses (`x._0_4_`), `CONCAT` and
  similar Ghidra pseudo-operators are nearly absent (1 and 3 functions).
- The rest of the range is **not** loading:
  - 136 functions call 14375A8D0 and never read the stream: a marking pass over loaded assets (they walk asset
    pointers and record each asset once in a list at 153606FC0).
  - 645 functions read the stream but are reached only from **143760C30**, a second copy of Load_XAssetList used
    when 1534E04D0 is set. That path records every block advance (143760610 / 1437606A0) and replays them
    (14311E7C0: `{block u8, size u32}` records, the position moved without reading). The only direct write to
    1534E04D0 found clears it (14375B4B1); whether any retail path sets it is *unverified*. The emulator never
    reaches it.
- Calls leaving the loaders go to 49 functions: the DB_AddXAsset wrappers and renderer, sound and streaming setup
  (GPU buffers, textures, sound-bank registration). None reads the stream (each checked when the emulator stubbed
  it); the translation drops them, as the emulator does.

## How it works (prototype)

1. Each loader's pseudocode is parsed (pycparser) and compiled into Python closures, with every expression's C type
   resolved once: integer widths and signedness, pointer arithmetic scaled by the pointee size, Ghidra's `goto`s.
2. Globals of undefined type take the type Ghidra used in that function (from an uncast assignment to or from a
   typed local), else the data type Ghidra recorded for that address (`analysis/<build>/ghidra/symbols.tsv`). Both
   matter: `&DAT_153607178 + block * 2` is only right with 153607178's recorded 4-byte type.
3. The stream primitives (Load_Stream, push/pop, align, offsets, alias slots) run from their decompiled C too; only
   the same stand-ins as the emulator are Python (file read, DB_AddXAsset and wrappers, SL_GetString, cancel
   checks, renderer calls). Memory uses the emulator's addresses, so every block and the asset pool compare byte
   for byte.

The prototype loads correctly up to the first script string of a zone, then diverges. The cause is in the
decompiled C, not the translation: **calls that lose arguments**. 459 of the 8,393 calls in the reachable loaders
pass fewer arguments than the callee takes. Most are harmless (Load_Stream called with its "already read" flag and
no size), but some are not: after a −2 string marker, 142E44F10 calls `FUN_143760b30()` with no argument where
the code passes the string's field in RCX. Ghidra decompiled every function separately without committed
signatures, so each call's arguments were guessed from the caller alone.

**Fix:** the decompile stage now first commits the decompiler's own parameter and return types for the loader
range, the load primitives and the asset wrappers (tools/ghidra/CommitSignatures.java, ranges in target.toml
`commit_signatures`), then decompiles, so the published pseudocode has complete calls.

## Next

1. Re-run the decompile stage from the saved analysis and confirm the dropped arguments are gone.
2. Run the translated loaders on whole zones until every block and the pool equal the emulator's
   (`mp_vh_c_s4_vm_mp_aus_lucas_02_lod0_tr`, then the body and head zones, then `mp_t_gun_course`).
3. Generate the reader from the translation instead of interpreting it (Python first, then Rust for Forge), with
   the stand-ins replaced by the plain reader's own implementations of the primitives, each documented in
   zones.md 8.
