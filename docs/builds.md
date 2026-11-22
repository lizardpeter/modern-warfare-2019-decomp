# Builds

Every build is hashed and listed in target.toml. Game files are still being uploaded to R2 under `mw2019/`; each
new build gets an entry here and in target.toml once hashed.

## ModernWarfare_BNet (retail target)

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

Use: the final target. No symbol build of IW8 is known; names come from strings, asset/dvar/command tables,
community research (docs/prior-art.md, to write) and, if one turns up, a symbol build of a later IW engine game.

### What the exe tells us up front

- The asset-type name table is at 146F1D670 (an array of 122 string pointers, `physicslibrary` … `assetlist`,
  followed by each type's default asset name). The order is the XAssetType enum. Listed in docs/assets.md.
