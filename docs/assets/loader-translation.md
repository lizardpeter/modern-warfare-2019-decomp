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

**Results.** The translated loaders (tools/assets/loaders/) load these zones from the original files alone with
**every stream block and the asset pool byte for byte equal to the game's own code in the emulator**
(tests/assets/loaders_check.py: same reads, same assets in the same order, same script strings):

| Zone | Assets | Time (Python) |
|---|---|---|
| `mp_vh_c_s4_vm_mp_aus_lucas_02_lod0_tr` (viewmodel arms) | 77 | 2.9 s |
| `mp_bd_body_mp_western_t9esports_1_10_1_lod1_l15_tr` (body) | 73 | 2.7 s |
| `mp_hd_head_mp_eastern_golem_1_1_blendshape_l15_tr` (head) | 23 | 2.8 s |
| patched `mp_t_gun_course` (a whole map: 296 MB, 12,235 assets) | 12,235 | 164 s |

The only bytes skipped are 16 the game itself never initialises (records/bugs.tsv B0001): 142DFEDA0 copies a
stack block whose bytes `[rsp+0x4C..0x4F]` it never writes into each deferred command's record (+0xC..+0xF), and
142DEDDA0 writes only the low half of the list entry's 8-byte field at +8. Their value is whatever was on the stack.

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

**Global types.** The C text never declares globals, and a global's type decides what pointer arithmetic on it
means. In 142E45450 `DAT_14bce6f30 + 0x1a` is byte 0x68 (the code: `add rax, 0x68`) because the decompiler typed
that global `int *` there, while its recorded type is undefined8 and no typed local reveals it. Inferring such types
from the text would guess, so the decompiler is asked. The first three runs that asked recorded nothing,
because Decompile.java (copied from black-ops-3-decomp) turned the decompiler's syntax tree off for speed, and the
syntax tree is what carries the HighFunction and the tokens' varnodes and types; it is now on. Decompile.java now records, per function, every
variable token whose storage is memory (name, address, HighVariable kind, type) and every pointer addition in the
high p-code whose base is a global (`PTRADD`/`PTRSUB`, with the element size, which is exactly what `G + n` means);
publish.py writes them as `// global …` and `// ptradd …` lines above the function.

**Ghidra's pseudo-operators and widths.** `CONCATxy`, `SUBxy`, `ZEXTxy`, `SEXTxy` and partial accesses `v._N_M_` are
given their documented meaning; Ghidra's odd-sized integers (`uint3`, `undefined7`, …) keep their real width.
Library code Ghidra cannot render (the CRT's hand-written `memcpy` at 1474213E0) gets its standard meaning.

With them, the translation reads the decompiler's type for every global it uses (`// global` lines); `_DAT_` /
`uRam` names without one take the stored value's size, and other untyped globals Ghidra's recorded type. That fixed
the last divergence on `mp_t_gun_course` (asset 7,676, whose bone entries hold xanimcurve references: in 142E45450
`DAT_14bce6f30 + 0x1a` is byte 0x68). The `// ptradd` lines (element size of each pointer addition on a global) are
recorded too; the types alone were enough so far.

## Next

1. **No exe at run time.** The translated loaders still take the initial values of the globals they read before
   writing from the exe image; record those (and only those) as generated data, so the reader needs only the game's
   data files.
2. **Generate code instead of compiling at run time**, then port the generator's output to Rust for Forge. The
   stand-ins become the reader's own documented primitives (zones.md 8).
3. More zones as the remaining archives arrive (weapons: `common_mp`), each run through loaders_check.py.
4. Speed: 164 s for a 296 MB map in Python; the generated code should be much faster.
