# Builds

Every build is hashed and listed in target.toml. Game files are still being uploaded to R2 under `mw2019/`; each
new build gets an entry here and in target.toml once hashed.

| id | kind | what |
|---|---|---|
| ModernWarfare_TU67 | retail (target) | Battle.net title update 67, the last update |
| ModernWarfare_TU63 | related | Battle.net 1.63.3.12428344: the exe of the uploaded install, whose data this repo reads |

## ModernWarfare_TU67 (retail target)

| | |
|---|---|
| R2 | `mw2019/exes/Battle.net Binaries (Modern Warfare 1.67)/ModernWarfare.exe` |
| Exe | 328,969,712 bytes, sha256 `de1e9a5e…c6ad7edf0f` |
| Version | title update 67: strings `unified_large_playlist_tu67.aggr`, `general_8_67`; the version resource only says 1.0 |
| Build date | link time 2024-05-13 20:53:26 UTC; compile date string `May 13 2024 13:03:17`. Later than the September 2023 1.67 patch notes: this is the last TU67 exe Battle.net shipped |
| PDB record | `e:\iw8\game\pc_dx12\game_dx12_ship.pdb`, GUID 0EC2F360-9741-4C0F-858D-55E76AEB36D8, age 2 (PDB not available) |
| Compiler | same as TU63: cl 19.28.29918 dominant (3,871 objects), linker 14.28, LTCG |
| Signature | Activision Publishing Inc; signed Authenticode digest equals the file's: an unmodified original |
| Protection | Arxan, same stub as TU63 (docs/arxan.md) |

Sections: `.text` 140001000+0x75D8800 (game code, 6% larger than TU63's), `.rdata` 1475DA000, `.data` 147AFB000,
`.pdata` 159E48000 (127,829 entries, TU63 126,634), `.text` 15A192000+0x7D7C800 (Arxan).

### TU67 against TU63

Measured on the two decrypted images:

- **Warzone is still in the code.** Every Warzone-related string in TU63 (`br_*` modes and sounds, gulag, armor
  plates, buy stations, `mp_escape`/Rebirth, battle royale) is present in TU67; TU67 adds one (`br_circle_proximity_lp`).
  The update that took Warzone offline did it on the server and playlist side, not by removing code.
- **Same data formats.** The asset-type name table is identical (122 types; TU63 146F1D670, TU67 147627730). The
  zone-header checks are the same code apart from relocated addresses: magics `IWffa100`, `IWffc100`, `IWffs100`,
  version field 11, and the per-format version table indexed by header byte 0x12
  (0x10C1, 0x10C1, 0xFF3, 0xFF3, 0xFF3, 0xFF3, 0x10C1, 0xFCD…) has the same values. So TU67 reads TU63's zones.
  *Unverified* beyond the header: whether individual asset structs changed size. That is settled when the asset
  readers run TU67's own loaders on the TU63 data (docs/assets.md).
- **What did change** (strings only in TU67): first-party store and transaction-receipt errors
  (`FirstPartyBadRequestError`, `TransactionReceiptAlreadyOpenedError`, `ExchangeConfigNotFound`, `pc_first_party`),
  the TU and date strings. Roughly 1,200 more functions in `.pdata`, not yet located.

Use: the final target. The data files come from the TU63 install, which matches TU67 in format; where a later patch
changed a zone's content (not its format), the TU63 file is what we have.

## ModernWarfare_TU63 (related)

| | |
|---|---|
| R2 | `mw2019/Call of Duty Modern Warfare 1.63 by purrplee/Call of Duty Modern Warfare/ModernWarfare.exe` (the uploader's folder name) |
| Exe | 308,422,128 bytes, sha256 `9eec0328…e806b56063` |
| Version | 1.63.3.12428344 (`.build.info` / `.product.db`: Battle.net product `odin`, branch eu, tags cp mp sp survival) |
| Link time | 2022-09-13 20:51:44 UTC |
| PDB record | `e:\workspace\iw8\game\pc_dx12\game_dx12_ship.pdb`, GUID 520C9102-599D-40A8-AC07-682F1844674D, age 2 (PDB not available) |
| Compiler | VS2019 16.9: Rich header dominated by cl 19.28.29918 (3,862 objects), linker 14.28; POGO debug record, so LTCG/PGO |
| Signature | Activision Publishing Inc (DigiCert G4 code-signing CA); the signed sha256 Authenticode digest `c7359c3c…c7871331` equals the file's: an unmodified original |
| Protection | Arxan, see docs/arxan.md |
| Platform | Battle.net (`Modern Warfare Launcher.exe`, `bootstrapper.exe`, CASC data), D3D12 (`d3d12.dll`, `dxil.dll`, `dxilconv7.dll` shipped beside it), DLSS (`nvngx_dlss.dll`), Oodle 7 (`oo2core_7_win64.dll`), Bink 2, Discord Game SDK, AMD AGS, Ansel/GFE, Ricochet anti-cheat driver `brynhildr.sys` |

One exe covers multiplayer, campaign, Spec Ops and Warzone.

Sections (from the PE header):

| section | VA | virtual size | notes |
|---|---|---:|---|
| .text | 140001000 | 0x6ED8000 (111 MB) | game code, encrypted on disk |
| .rdata | 146ED9000 | 0x512E00 | |
| .data | 1473EC000 | 0x122DD2E4 (291 MB, 62 MB on disk) | |
| .pdata | 1596CA000 | 0x173000 | 126,634 runtime-function entries |
| _RDATA | 15983D000 | 0x16800 | |
| .rsrc | 159854000 | 0x167A00 | |
| .reloc | 1599BC000 | 0x45C00 | |
| .idata | 159A02000 | 0x6400 | |
| .text | 159A09000 | 0x70FE000 (113 MB) | Arxan's own code |

Use: the exe of the install whose data was uploaded, so it is the exact match for that data if a format question
ever separates the two builds. Its Ghidra run was started and stopped once TU67 became the target (the unpack in CI
reproduced the pinned hash and the Arxan block was dropped); analyse it when it is needed.

No symbol build of IW8 is known; names come from strings, asset/dvar/command tables, community research
(docs/prior-art.md, to write) and, if one turns up, a symbol build of a later IW engine game.
