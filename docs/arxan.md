# Arxan

Both `ModernWarfare.exe` builds (TU67, the target, and TU63) are Arxan-protected with the same stub. The details
below were measured on TU63; TU67's are in the table at the end.

TU63's exe is Arxan-protected: on disk the game's `.text` (0x6ED8000 bytes) and a second `.text` of
0x70FE000 bytes holding Arxan's own code are encrypted (entropy 7.99 and 7.97). Ghidra analyses the decrypted image,
never the raw file.

`tools/unpack/arxan.py` (from black-ops-3-decomp, unchanged apart from names) emulates the stub in Unicorn and writes
the decrypted image. The image is generated, not stored: its sha256 is pinned in target.toml (`unpacked_sha256`).

## Same as BO3

- The PE entry (146D19AEC) is the VS2019 `mainCRTStartup` with its tail patched by Arxan:
  `sub rsp,28h; call 140B1D42D; nop; jmp 15F141C81`. The unpacker leaves the entry point as it is.
- The stub calls `GetSystemInfo`, then `VirtualProtect` on every section (RWX), decrypts, and the run stops at the
  first ordinary runtime call: `GetSystemTimeAsFileTime` from 146D1DEE2 (`__security_init_cookie`).
- No `rdtsc` calls were made (0), and no other APIs.

## Result

Measured locally (one uninterrupted `emu_start`, ~7 min):

| section | changed bytes | entropy before | after |
|---|---:|---:|---:|
| .text (game) | 112,346,386 | 7.99 | 6.99 |
| .rdata | 22,682 | 5.94 | 5.93 |
| .data | 0 | 0.26 | 0.26 |
| .pdata | 220 | 7.25 | 7.25 |
| _RDATA | 558 | 5.61 | 5.60 |
| .rsrc | 184 | 7.33 | 7.33 |
| .reloc | 271 | 5.49 | 5.48 |
| .idata | 4,341 | 4.74 | 4.85 |
| .text (Arxan) | 106,289,467 | 7.97 | 7.30 |

Unlike BO3, `.rdata` and `.data` are barely touched: the encryption is almost all code.

**Ranges of the game `.text` still at high entropy afterwards** (4 KB blocks above 7.7): about 5 MB in 25 ranges, the
largest 141C69000+0x2C9000, 1439BC000+0xB0000, 141F9F000…1420E8000, 14330B000+0x14000. The stub did rewrite these
bytes, and `.pdata` has no function in 141C69000+0x2C9000 and only a handful in the others, so they are most likely
data kept in `.text` (or a second, runtime-only layer) rather than code the unpacker missed. *Unverified*: identify
what reads them once Ghidra has the image.

## In Ghidra

Arxan's section (159A09000–160B07000) is as large as the game's code. target.toml lists it in `exclude` with
`ghidra_drop_excluded = true`, so `tools/ghidra/DropBlocks.java` removes that block before auto-analysis (BO3 instead
analysed it and filtered 333k fragments out afterwards; here that would double a run that is already the largest
of these projects). Arxan's inserted calls and jumps in game code then point at missing memory, which is correct:
they are not game code and are in neither build.

## TU67

Same stub, same behaviour: entry 14741A28C is the patched CRT entry, `VirtualProtect` on every section, stop at
`GetSystemTimeAsFileTime`, no `rdtsc`. ~8 min locally; two runs gave the same image (pinned in target.toml).

| section | changed bytes | entropy before | after |
|---|---:|---:|---:|
| .text (game) | 119,301,392 | 7.99 | 7.00 |
| .rdata | 22,784 | 5.93 | 5.93 |
| .data | 0 | 0.26 | 0.26 |
| .pdata | 397 | 7.19 | 7.19 |
| _RDATA | 510 | 5.61 | 5.61 |
| .rsrc | 279 | 1.92 | 1.92 |
| .reloc | 203 | 5.48 | 5.48 |
| .idata | 4,264 | 4.85 | 4.93 |
| .text (Arxan) | 118,205,591 | 7.97 | 7.32 |

TU67's Arxan section (15A192000, 0x7D7C800) is not page-aligned in size; DropBlocks.java accepts the block whether
Ghidra keeps that size or rounds it to the page.
