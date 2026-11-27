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
   matter: `&DAT_153607178 + block * 2` is only right with 153607178's recorded 4-byte type. A name Ghidra writes
   as `_DAT_x` or `uRam…` is an access of another size than the symbol recorded there (Ghidra's own warning:
   "Globals starting with '_' overlap smaller symbols at the same address"), so its size is the stored value's:
   143760420 writes the 8-byte block bases as `_DAT_153607110 = param_1[4]` over a 1-byte symbol.
3. The stream primitives (Load_Stream, push/pop, align, offsets, alias slots) run from their decompiled C too; only
   the same stand-ins as the emulator are Python (file read, DB_AddXAsset and wrappers, SL_GetString, cancel
   checks, renderer calls). Memory uses the emulator's addresses, so every block and the asset pool compare byte
   for byte.

**Results.** After the signature fix below, the translated loaders load these zones from the original files with
**every block and the asset pool byte for byte equal to the game's own code in the emulator**:

| Zone | Assets | Time (Python) |
|---|---|---|
| `mp_vh_c_s4_vm_mp_aus_lucas_02_lod0_tr` (viewmodel arms) | 77 | 1.1 s |
| `mp_bd_body_mp_western_t9esports_1_10_1_lod1_l15_tr` (body) | 73 | 1.0 s |
| `mp_hd_head_mp_eastern_golem_1_1_blendshape_l15_tr` (head) | 23 | 1.1 s |

The patched `mp_t_gun_course` diverges at read 55,507 (stream 0x2A0AB1, inside an xmodelsurfs): see the second
signature problem below.

**Signature problem 1: calls that lose arguments.** In the first published pseudocode, 459 of the 8,393 calls in
the reachable loaders passed fewer arguments than the callee takes. Most were harmless (Load_Stream called with
its "already read" flag and no size), but not all: after a −2 string marker, 142E44F10 called `FUN_143760b30()` with
no argument where the code passes the string's field in RCX. Ghidra had decompiled every function separately
without committed signatures, so each call's arguments were guessed from the caller alone. Fix: the decompile stage
first commits the decompiler's own parameter and return types for the loader range, the load primitives and the
asset wrappers (tools/ghidra/CommitSignatures.java, ranges in target.toml `commit_signatures`). After it: 1 such
call left, to a renderer function the translation drops.

**Signature problem 2: pass-through parameters.** 142EA60F0 passes its RCX (the "already read" flag) untouched to
142EB0430, which hands it to Load_Stream; its caller sets `ecx = 1` (142EA5D7D). Committed in address order, it was
decompiled before 142EB0430's parameter was known, so it was committed as taking nothing (`in_RCX` in its body) and
its caller dropped the 1: the translation then read 8 bytes the game does not. Five reachable loaders show such an
`in_RCX` (142E06230, 142E2E0A0, 142E2E6D0, 142EA60F0, 142EAB290). Fix: commit callees before their callers
(post-order over the calls inside the ranges).

## Next

1. Re-decompile with callee-first signatures; confirm no reachable loader has an `in_` argument register.
2. Continue on `mp_t_gun_course` until every block and the pool equal the emulator's.
3. Generate the reader from the translation instead of interpreting it (Python first, then Rust for Forge), with
   the stand-ins replaced by the plain reader's own implementations of the primitives, each documented in
   zones.md 8.
