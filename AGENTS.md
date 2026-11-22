# Working in modern-warfare-2019-decomp

Decompilation of Call of Duty: Modern Warfare (2019) (IW8, PC, x64), and a complete description of its asset
formats. Read this before changing anything.

The structure, method and tools come from `lizardpeter/black-ops-3-decomp` (BO3, x64), which took them from
`lizardpeter/ghosts-decomp` (Ghosts) and `lizardpeter/black-ops-1-decomp` (BO1). This repo owns its own copy of the
tools and adapts them; there is no shared toolkit. Comments in the copied tools still use BO3/Ghosts examples where
they describe what a mechanism was built for.

## Goals

1. **Faithful decomp** of the final Battle.net build, function by function, verified against the original.
2. **Every asset format decoded** (weapons, attachments, animations, models, textures, materials and shaders,
   audio, effects, movement and physics settings, maps): documented from the code that reads them and checked
   against the game, so `lizardpeter/Rust-test` (Forge) can import them. See docs/assets.md.
3. **Enhanced build**, later: the faithful code plus documented changes (docs/roadmap.md).

## The one rule: generated vs authored

Every file is exactly one of these. They never share a folder.

| Kind | Where | Who writes it |
|---|---|---|
| **Generated** | `analysis/<build>/`, `analysis/graph/`, `STATUS.md` | Only the scripts in `tools/`. Never hand-edit. Re-running the pipeline on the same input reproduces it. |
| **Authored** | `src/`, `include/`, `tests/`, `docs/`, `records/` | People and agents. |

If a generated file is wrong, fix the script that wrote it and re-run. Don't patch the output.

## Layout

```
target.toml          builds (sha256 + R2 key of each original file), project id, protection
analysis/<build>/    GENERATED per build
  functions.tsv        every function: address, size, name, signature, bytes hash, decompile status
  unpack/              how the protected build was unpacked (log, sections changed, image hash)
  ghidra/              Ghidra exports (functions, callgraph, symbols, strings, types.h) + saved project (split tar)
  pseudocode/<group>.c Ghidra decompiler output, grouped by original source file once known
  disasm/<group>.asm   disassembly, same grouping
  match/               cross-build identifications with evidence and confidence
  logs/                pipeline logs
records/             AUTHORED small facts; the only input to the graph besides analysis/
  functions.tsv        status of each reconstructed function, per build
  names.tsv            identifications in builds without symbols: name, method, evidence, confidence
  bugs.tsv             everything worth fixing, for the enhanced build
src/ include/        AUTHORED faithful reconstruction, mirroring the original source tree
enhanced/            AUTHORED (once needed) overrides for the enhanced build, same layout as src/
tests/differential/  differential tests (x64 Unicorn harness)
tests/assets/        checks of the asset readers against the game's own loaders
docs/<topic>.md      method notes and per-build findings. Topic names, never dates.
docs/assets/<kind>.md one file per asset type: layout, the function each rule comes from, what Forge needs
tools/               pipeline scripts (unpack/, ghidra/, pdb/, match/, graph/, recon/, assets/)
```

Folder and file names describe *what*, never *when*. Dates belong in commit messages.

## Asset formats

Every rule in `docs/assets/` names the function (address) it comes from, or says "measured on <file>"; anything
else is marked *unverified*. The reference readers in `tools/assets/` are plain Python and are checked against the
game's own loaders run in the emulator (as ghosts-decomp does for fastfiles). The Forge importer is a port of
these readers into Rust-test; IW8-specific code stays inside that importer (Rust-test's rule: game-specific code
never enters the generic renderer or engine).

## Faithful and enhanced

`src/` is the **faithful** decomp: original behaviour, bugs included, verified function by function. The
**enhanced** build is the faithful code plus overrides from `enhanced/` (security, bugfix, modernize, feature),
each recorded in `records/patches.tsv`; both are created with the first enhancement. Never fix a bug in `src/`.
DRM, anti-cheat (Ricochet/`brynhildr.sys`) and Arxan code are in neither build.

**Everything worth fixing goes in `records/bugs.tsv`**, the enhanced build's fix queue: not only outright bugs,
but anything in the original that should be fixed or improved. Columns: id (`B` + 4 digits), build, va, function,
source, kind, priority (`high` for security, crashes and gameplay-visible problems, else `medium` or `low`),
description, evidence (the reproducing test, or the code/disassembly; say whether a current caller can trigger
it), enhanced (`planned`, `fixed <patch id>`, or `keep` when the original behaviour is wanted). Kinds: `security`,
`crash`, `hang`, `logic`, `ub`, `robustness`, `limit`, `precision`, `performance`, `quality`. The faithful code
keeps it all; security issues are also written up in docs/security.md. Plain float rounding that changes nothing
visible isn't a finding.

## Addresses

x64 virtual addresses at the image base 0x140000000, written as 9 upper-case hex digits without `0x`
(`146D19AEC`). Every tool uses that form.

## Protected builds

A build with `protection = "arxan"` in target.toml has encrypted code on disk. It is unpacked by
`tools/unpack/arxan.py`, and Ghidra analyses the unpacked image, never the raw file. The unpacked image is
generated, never stored: its sha256 is pinned in target.toml (`unpacked_sha256`) so anyone can reproduce it.
See docs/arxan.md.

## Function status ladder

Every function in `records/functions.tsv` has exactly one status:

`located -> named -> typed -> decompiled -> compiles -> matches -> integrated`

- `located`: entry and size known (Ghidra; `.pdata` gives every non-leaf function's bounds on x64)
- `named`: original name known (a recorded identification in records/names.tsv)
- `typed`: original prototype known
- `decompiled`: authored source exists in `src/`
- `compiles`: that source builds in CI
- `matches`: passes the differential test against the original
- `integrated`: linked into the runnable reconstruction

`matches` needs a passing automated test; CI fails if a record claims more than the tests show. A
function kept below `matches` on purpose carries a note saying why. `STATUS.md` and the graph are both
computed from this file. Don't track progress anywhere else.

Every cross-build identification records its method, evidence and confidence. Never match on address
position across differently linked builds.

## Graph

Graph `re_iw8` on the Graph DB is **derived**. `tools/graph/sync.py` turns `records/` plus
`analysis/<build>/functions.tsv` into a MERGE-by-key import set under `analysis/graph/`, loaded with the
Graph DB `bulk_import_file` tool (import folder `iw8/` on the Graph DB machine). Never write ad-hoc Cypher to
the graph; change records and re-sync. The graph holds identity, relationships and status only, with no code text.

## Originals

The game files are never committed. They live in R2 under the keys in `target.toml`, and the pipeline
verifies their sha256 before use. Helpers for reading the bucket are not part of this repo.
